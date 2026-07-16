"""Tests for the NvidiaAIClient module."""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from config.settings import Settings
from scripts.ai_client import (
    AIResponse,
    APIKeyMissingError,
    APIRequestError,
    APIResponseError,
    NvidiaAIClient,
)


class TestAIClientInit:
    """Tests for AI client initialization."""

    def test_init_with_api_key(self, settings: Settings) -> None:
        """Client should initialize with a valid API key."""
        client = NvidiaAIClient(settings)
        assert client._settings.has_api_key is True

    def test_init_without_api_key(self, settings_no_api_key: Settings) -> None:
        """Client should initialize but flag missing API key."""
        client = NvidiaAIClient(settings_no_api_key)
        assert client._settings.has_api_key is False


class TestAPIKeyValidation:
    """Tests for API key requirement enforcement."""

    def test_generate_summary_without_key_raises(
        self, settings_no_api_key: Settings
    ) -> None:
        """Calling generate_summary without API key should raise."""
        client = NvidiaAIClient(settings_no_api_key)
        with pytest.raises(APIKeyMissingError):
            client.generate_summary("test notes")

    def test_generate_weekly_without_key_raises(
        self, settings_no_api_key: Settings
    ) -> None:
        """Calling generate_weekly_analysis without API key should raise."""
        client = NvidiaAIClient(settings_no_api_key)
        with pytest.raises(APIKeyMissingError):
            client.generate_weekly_analysis("logs", {"days": 5})


class TestResponseParsing:
    """Tests for API response parsing."""

    def test_parse_valid_response(
        self, mock_ai_response: dict[str, Any]
    ) -> None:
        """Should correctly parse a valid API response."""
        result = NvidiaAIClient._parse_response(mock_ai_response)
        assert isinstance(result, AIResponse)
        assert "AI Summary" in result.content
        assert result.usage["total_tokens"] == 150

    def test_parse_empty_choices_raises(self) -> None:
        """Should raise APIResponseError for empty choices."""
        with pytest.raises(APIResponseError):
            NvidiaAIClient._parse_response({"choices": []})

    def test_parse_empty_content_raises(self) -> None:
        """Should raise APIResponseError for empty content."""
        data = {
            "choices": [{"message": {"content": ""}, "finish_reason": "stop"}]
        }
        with pytest.raises(APIResponseError):
            NvidiaAIClient._parse_response(data)

    def test_parse_malformed_response_raises(self) -> None:
        """Should raise APIResponseError for malformed data."""
        with pytest.raises(APIResponseError):
            NvidiaAIClient._parse_response({"invalid": "data"})


class TestAPIRequests:
    """Tests for API request handling with mocked HTTP."""

    @patch("scripts.ai_client.requests.Session.post")
    def test_successful_request(
        self,
        mock_post: MagicMock,
        settings: Settings,
        mock_ai_response: dict[str, Any],
    ) -> None:
        """Successful API call should return parsed AIResponse."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_ai_response
        mock_post.return_value = mock_response

        client = NvidiaAIClient(settings)
        result = client.generate_summary("Test notes about Python development")
        assert isinstance(result, AIResponse)
        assert "AI Summary" in result.content

    @patch("scripts.ai_client.requests.Session.post")
    def test_auth_failure_raises(
        self, mock_post: MagicMock, settings: Settings
    ) -> None:
        """HTTP 401 should raise APIRequestError about authentication."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_post.return_value = mock_response

        client = NvidiaAIClient(settings)
        with pytest.raises(APIRequestError, match="Authentication failed"):
            client.generate_summary("test")

    @patch("scripts.ai_client.requests.Session.post")
    def test_model_not_found_raises(
        self, mock_post: MagicMock, settings: Settings
    ) -> None:
        """HTTP 404 should raise APIRequestError about model."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not found"
        mock_post.return_value = mock_response

        client = NvidiaAIClient(settings)
        with pytest.raises(APIRequestError, match="not found"):
            client.generate_summary("test")

    @patch("scripts.ai_client.time.sleep")
    @patch("scripts.ai_client.requests.Session.post")
    def test_retry_on_server_error(
        self,
        mock_post: MagicMock,
        mock_sleep: MagicMock,
        settings: Settings,
        mock_ai_response: dict[str, Any],
    ) -> None:
        """Should retry on 500 errors and succeed on subsequent attempt."""
        error_response = MagicMock()
        error_response.status_code = 500
        error_response.text = "Internal Server Error"

        success_response = MagicMock()
        success_response.status_code = 200
        success_response.json.return_value = mock_ai_response

        mock_post.side_effect = [error_response, success_response]

        client = NvidiaAIClient(settings)
        result = client.generate_summary("test")
        assert isinstance(result, AIResponse)
        assert mock_post.call_count == 2


class TestContextManager:
    """Tests for context manager protocol."""

    def test_context_manager(self, settings: Settings) -> None:
        """Should support with-statement usage."""
        with NvidiaAIClient(settings) as client:
            assert client._settings.has_api_key is True
