"""Application settings loaded from environment variables.

Uses pydantic-settings to provide validated, type-safe configuration.
All secrets are loaded from .env files — never hardcoded.
"""

from __future__ import annotations

import logging
from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application-wide configuration.

    Values are loaded from environment variables and .env files.
    Required fields will raise a validation error if missing.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- NVIDIA NIM API ---
    nvidia_api_key: str = Field(
        default="",
        description="NVIDIA NIM API key for AI-powered features.",
    )
    model: str = Field(
        default="nvidia/nemotron-3-ultra-550b-a55b",
        description="NVIDIA model identifier for chat completions.",
    )
    nvidia_base_url: str = Field(
        default="https://integrate.api.nvidia.com/v1",
        description="Base URL for the NVIDIA NIM API.",
    )
    max_tokens: int = Field(
        default=2048,
        ge=64,
        le=8192,
        description="Maximum tokens for AI responses.",
    )
    ai_temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Temperature for AI generation (0 = deterministic, 2 = creative).",
    )

    # --- Paths ---
    project_root: Path = Field(
        default_factory=lambda: Path.cwd(),
        description="Root directory of the project.",
    )
    timezone: str = Field(
        default="UTC",
        description="Timezone for log dates.",
    )

    @field_validator("nvidia_api_key")
    @classmethod
    def warn_if_empty_api_key(cls, value: str) -> str:
        """Warn if the API key is empty — AI features will be disabled."""
        if not value.strip():
            logger.warning(
                "NVIDIA_API_KEY is not set. AI-powered features will be disabled. "
                "Set it in your .env file or environment variables."
            )
        return value.strip()

    @property
    def logs_dir(self) -> Path:
        """Path to the logs directory."""
        return self.project_root / "logs"

    @property
    def reports_dir(self) -> Path:
        """Path to the reports directory."""
        return self.project_root / "reports"

    @property
    def templates_dir(self) -> Path:
        """Path to the Jinja2 templates directory."""
        return self.project_root / "templates"

    @property
    def dashboard_dir(self) -> Path:
        """Path to the dashboard directory."""
        return self.project_root / "dashboard"

    @property
    def has_api_key(self) -> bool:
        """Check whether a valid API key is configured."""
        return bool(self.nvidia_api_key)

    def ensure_directories(self) -> None:
        """Create all required directories if they don't exist."""
        for directory in (self.logs_dir, self.reports_dir, self.templates_dir, self.dashboard_dir):
            directory.mkdir(parents=True, exist_ok=True)


@lru_cache(maxsize=1)
def get_settings(project_root: Optional[str] = None) -> Settings:
    """Return a cached singleton Settings instance.

    Args:
        project_root: Override the project root path. If None, uses cwd.

    Returns:
        Validated Settings instance.
    """
    kwargs: dict[str, str] = {}
    if project_root is not None:
        kwargs["project_root"] = project_root
    return Settings(**kwargs)
