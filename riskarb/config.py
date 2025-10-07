"""Configuration helpers for the risk arbitrage tracker."""
from __future__ import annotations

import os
from dataclasses import dataclass


class MissingAPIKeyError(RuntimeError):
    """Raised when a required API key is not provided."""


@dataclass(frozen=True)
class APISettings:
    """Container for all remote API configuration."""

    financial_modeling_prep_key: str

    @staticmethod
    def from_env() -> "APISettings":
        """Load API settings from environment variables.

        Returns
        -------
        APISettings
            Settings populated from the current environment.

        Raises
        ------
        MissingAPIKeyError
            If a required API key is not present.
        """

        key = os.getenv("FMP_API_KEY")
        if not key:
            raise MissingAPIKeyError(
                "Set the FMP_API_KEY environment variable with your Financial Modeling "
                "Prep API token."
            )
        return APISettings(financial_modeling_prep_key=key)
