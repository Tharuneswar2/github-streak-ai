"""NVIDIA NIM API client for AI-powered text generation.

Provides a clean interface to the NVIDIA NIM chat completions API
(OpenAI-compatible) with retry logic, error handling, and rate limiting.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any

import requests

from config.constants import (
    DEFAULT_REQUEST_TIMEOUT,
    MAX_RETRIES,
    MONTHLY_INSIGHTS_SYSTEM_PROMPT,
    NVIDIA_CHAT_ENDPOINT,
    RETRY_BACKOFF_FACTOR,
    SUMMARY_SYSTEM_PROMPT,
    WEEKLY_ANALYSIS_SYSTEM_PROMPT,
)
from config.settings import Settings, get_settings

logger = logging.getLogger(__name__)


class AIClientError(Exception):
    """Base exception for AI client errors."""


class APIKeyMissingError(AIClientError):
    """Raised when the NVIDIA API key is not configured."""


class APIRequestError(AIClientError):
    """Raised when an API request fails after all retries."""


class APIResponseError(AIClientError):
    """Raised when the API returns an unexpected response format."""


@dataclass
class AIResponse:
    """Structured response from the AI model.

    Attributes:
        content: The generated text content.
        model: The model used for generation.
        usage: Token usage statistics.
        finish_reason: Why the model stopped generating.
    """

    content: str
    model: str = ""
    usage: dict[str, int] = field(default_factory=dict)
    finish_reason: str = ""


class NvidiaAIClient:
    """Client for the NVIDIA NIM chat completions API.

    Uses the OpenAI-compatible endpoint at integrate.api.nvidia.com.
    Includes automatic retry with exponential backoff for transient failures.

    Example:
        >>> client = NvidiaAIClient()
        >>> response = client.generate_summary("Today I fixed a bug in the parser...")
        >>> print(response.content)
    """

    def __init__(self, settings: Settings | None = None) -> None:
        """Initialize the AI client.

        Args:
            settings: Application settings. If None, loads from environment.
        """
        self._settings = settings or get_settings()
        self._base_url = self._settings.nvidia_base_url.rstrip("/")
        self._session = requests.Session()
        self._session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
        })
        if self._settings.has_api_key:
            self._session.headers["Authorization"] = f"Bearer {self._settings.nvidia_api_key}"

    def _ensure_api_key(self) -> None:
        """Raise an error if the API key is not configured."""
        if not self._settings.has_api_key:
            raise APIKeyMissingError(
                "NVIDIA_API_KEY is not set. Please configure it in your .env file "
                "or environment variables. See .env.example for details."
            )

    def _make_request(
        self,
        messages: list[dict[str, str]],
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> AIResponse:
        """Send a chat completion request to the NVIDIA NIM API.

        Implements retry with exponential backoff for transient failures
        (network errors, 429, 500, 502, 503, 504).

        Args:
            messages: List of message dicts with 'role' and 'content' keys.
            temperature: Override the default temperature.
            max_tokens: Override the default max tokens.

        Returns:
            AIResponse with the generated content.

        Raises:
            APIKeyMissingError: If the API key is not configured.
            APIRequestError: If all retry attempts fail.
            APIResponseError: If the response format is unexpected.
        """
        self._ensure_api_key()

        url = f"{self._base_url}{NVIDIA_CHAT_ENDPOINT}"
        payload: dict[str, Any] = {
            "model": self._settings.model,
            "messages": messages,
            "temperature": temperature if temperature is not None else self._settings.ai_temperature,
            "max_tokens": max_tokens if max_tokens is not None else self._settings.max_tokens,
        }

        last_error: Exception | None = None
        retryable_status_codes = {429, 500, 502, 503, 504}

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                logger.debug(
                    "API request attempt %d/%d to %s", attempt, MAX_RETRIES, url
                )
                response = self._session.post(
                    url, json=payload, timeout=DEFAULT_REQUEST_TIMEOUT
                )

                if response.status_code == 200:
                    return self._parse_response(response.json())

                if response.status_code in retryable_status_codes:
                    wait_time = RETRY_BACKOFF_FACTOR ** attempt
                    logger.warning(
                        "API returned %d, retrying in %.1fs (attempt %d/%d)",
                        response.status_code,
                        wait_time,
                        attempt,
                        MAX_RETRIES,
                    )
                    last_error = APIRequestError(
                        f"API returned HTTP {response.status_code}: {response.text[:500]}"
                    )
                    time.sleep(wait_time)
                    continue

                # Non-retryable error
                error_detail = response.text[:500]
                if response.status_code == 401:
                    raise APIRequestError(
                        f"Authentication failed (HTTP 401). Check your NVIDIA_API_KEY. "
                        f"Detail: {error_detail}"
                    )
                if response.status_code == 404:
                    raise APIRequestError(
                        f"Model or endpoint not found (HTTP 404). Check your MODEL setting. "
                        f"Detail: {error_detail}"
                    )
                raise APIRequestError(
                    f"API request failed with HTTP {response.status_code}: {error_detail}"
                )

            except requests.exceptions.Timeout:
                wait_time = RETRY_BACKOFF_FACTOR ** attempt
                logger.warning(
                    "Request timed out, retrying in %.1fs (attempt %d/%d)",
                    wait_time,
                    attempt,
                    MAX_RETRIES,
                )
                last_error = APIRequestError(
                    f"Request timed out after {DEFAULT_REQUEST_TIMEOUT}s"
                )
                time.sleep(wait_time)

            except requests.exceptions.ConnectionError as exc:
                wait_time = RETRY_BACKOFF_FACTOR ** attempt
                logger.warning(
                    "Connection error, retrying in %.1fs (attempt %d/%d): %s",
                    wait_time,
                    attempt,
                    MAX_RETRIES,
                    exc,
                )
                last_error = APIRequestError(f"Connection error: {exc}")
                time.sleep(wait_time)

            except (APIKeyMissingError, APIRequestError):
                raise

            except requests.exceptions.RequestException as exc:
                last_error = APIRequestError(f"Unexpected request error: {exc}")
                logger.error("Unexpected request error: %s", exc)
                break

        raise APIRequestError(
            f"All {MAX_RETRIES} retry attempts failed. Last error: {last_error}"
        )

    @staticmethod
    def _parse_response(data: dict[str, Any]) -> AIResponse:
        """Parse the API response JSON into an AIResponse.

        Args:
            data: Raw JSON response from the API.

        Returns:
            Parsed AIResponse.

        Raises:
            APIResponseError: If the response structure is unexpected.
        """
        try:
            choices = data.get("choices", [])
            if not choices:
                raise APIResponseError("API response contains no choices.")

            message = choices[0].get("message", {})
            content = message.get("content", "").strip()
            if not content:
                raise APIResponseError("API response contains empty content.")

            return AIResponse(
                content=content,
                model=data.get("model", ""),
                usage=data.get("usage", {}),
                finish_reason=choices[0].get("finish_reason", ""),
            )
        except (KeyError, IndexError, TypeError) as exc:
            raise APIResponseError(
                f"Failed to parse API response: {exc}. Raw data: {str(data)[:500]}"
            ) from exc

    def generate_summary(self, raw_notes: str) -> AIResponse:
        """Convert raw developer notes into a professional markdown summary.

        Args:
            raw_notes: Unformatted text notes from the developer.

        Returns:
            AIResponse containing the formatted summary.
        """
        messages = [
            {"role": "system", "content": SUMMARY_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    "Convert the following raw developer notes into a clean, professional "
                    "markdown summary. Include:\n"
                    "1. A concise summary paragraph\n"
                    "2. Key takeaways as bullet points\n"
                    "3. Action items for follow-up\n\n"
                    f"--- RAW NOTES ---\n{raw_notes}\n--- END NOTES ---"
                ),
            },
        ]
        logger.info("Generating AI summary for %d characters of notes", len(raw_notes))
        return self._make_request(messages)

    def generate_weekly_analysis(
        self,
        daily_logs: str,
        stats: dict[str, Any],
    ) -> AIResponse:
        """Generate an AI analysis for a weekly report.

        Args:
            daily_logs: Concatenated daily log content for the week.
            stats: Dictionary of weekly statistics (commits, hours, etc.).

        Returns:
            AIResponse containing the weekly analysis.
        """
        stats_text = "\n".join(f"- {key}: {value}" for key, value in stats.items())
        messages = [
            {"role": "system", "content": WEEKLY_ANALYSIS_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    "Analyze this developer's weekly activity and provide:\n"
                    "1. Productivity assessment\n"
                    "2. Key accomplishments\n"
                    "3. Learning patterns observed\n"
                    "4. Areas for improvement\n"
                    "5. Specific recommendations for next week\n\n"
                    f"--- STATISTICS ---\n{stats_text}\n\n"
                    f"--- DAILY LOGS ---\n{daily_logs}\n--- END LOGS ---"
                ),
            },
        ]
        logger.info("Generating weekly analysis")
        return self._make_request(messages)

    def generate_monthly_insights(
        self,
        monthly_data: str,
        stats: dict[str, Any],
    ) -> AIResponse:
        """Generate AI insights for a monthly report.

        Args:
            monthly_data: Concatenated weekly reports or daily logs for the month.
            stats: Dictionary of monthly statistics.

        Returns:
            AIResponse containing the monthly insights.
        """
        stats_text = "\n".join(f"- {key}: {value}" for key, value in stats.items())
        messages = [
            {"role": "system", "content": MONTHLY_INSIGHTS_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    "Review this developer's monthly progress and provide:\n"
                    "1. Overall growth assessment\n"
                    "2. Skill development trends\n"
                    "3. Consistency analysis\n"
                    "4. Strategic recommendations\n"
                    "5. Goals suggestion for next month\n\n"
                    f"--- STATISTICS ---\n{stats_text}\n\n"
                    f"--- MONTHLY DATA ---\n{monthly_data}\n--- END DATA ---"
                ),
            },
        ]
        logger.info("Generating monthly insights")
        return self._make_request(messages)

    def close(self) -> None:
        """Close the underlying HTTP session."""
        self._session.close()

    def __enter__(self) -> NvidiaAIClient:
        """Support context manager protocol."""
        return self

    def __exit__(self, *args: object) -> None:
        """Close session on context exit."""
        self.close()
