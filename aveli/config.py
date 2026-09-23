"""Validated configuration for the internal production boundary."""

from dataclasses import dataclass, field
from pathlib import Path
from types import MappingProxyType
from typing import Mapping
from urllib.parse import urlparse


class ConfigurationError(ValueError):
    """Production configuration is missing or unsafe."""


def _required(environment: Mapping[str, str], name: str) -> str:
    value = environment.get(name, "").strip()
    if not value:
        raise ConfigurationError(f"{name} is required")
    return value


def _pinned_model(environment: Mapping[str, str], name: str) -> str:
    value = _required(environment, name)
    if value.lower().endswith("latest"):
        raise ConfigurationError(f"{name} must be pinned to an exact model version")
    return value


def _absolute_directory(environment: Mapping[str, str], name: str) -> Path:
    path = Path(_required(environment, name)).expanduser()
    if not path.is_absolute():
        raise ConfigurationError(f"{name} must be an absolute path")
    return path


@dataclass(frozen=True)
class ProductionSettings:
    """Provider settings accepted for an isolated production job."""

    typesafe_api_key: str = field(repr=False)
    typesafe_model: str
    text_model_api_key: str = field(repr=False)
    text_model_base_url: str
    text_model: str
    text_model_reasoning: str
    external_data_approved: bool
    audit_dir: Path = Path("artifacts/audit")
    typesafe_base_url: str = "https://api.typesafe.ai/v1"

    @classmethod
    def from_env(cls, environment: Mapping[str, str]) -> "ProductionSettings":
        approved = environment.get("AVELI_EXTERNAL_DATA_APPROVED", "").strip().lower() == "true"
        if not approved:
            raise ConfigurationError(
                "External provider data approval is required; set AVELI_EXTERNAL_DATA_APPROVED=true only after review"
            )
        typesafe_base_url = environment.get("TYPESAFE_BASE_URL", "https://api.typesafe.ai/v1").strip().rstrip("/")
        typesafe_parsed = urlparse(typesafe_base_url)
        if typesafe_parsed.scheme != "https" or not typesafe_parsed.hostname:
            raise ConfigurationError("TYPESAFE_BASE_URL must be an HTTPS URL")
        base_url = _required(environment, "TEXT_MODEL_BASE_URL").rstrip("/")
        parsed = urlparse(base_url)
        if parsed.scheme != "https" or not parsed.hostname:
            raise ConfigurationError("TEXT_MODEL_BASE_URL must be an HTTPS URL")
        return cls(
            typesafe_api_key=_required(environment, "TYPESAFE_API_KEY"),
            typesafe_model=_pinned_model(environment, "TYPESAFE_MODEL"),
            text_model_api_key=_required(environment, "TEXT_MODEL_API_KEY"),
            text_model_base_url=base_url,
            text_model=_pinned_model(environment, "TEXT_MODEL"),
            text_model_reasoning=environment.get("TEXT_MODEL_REASONING", "none").strip() or "none",
            external_data_approved=True,
            audit_dir=_absolute_directory(environment, "AVELI_AUDIT_DIR"),
            typesafe_base_url=typesafe_base_url,
        )

    def provider_environment(self) -> Mapping[str, str]:
        return MappingProxyType(
            {
                "TYPESAFE_API_KEY": self.typesafe_api_key,
                "TYPESAFE_MODEL": self.typesafe_model,
                "TYPESAFE_BASE_URL": self.typesafe_base_url,
                "TEXT_MODEL_API_KEY": self.text_model_api_key,
                "TEXT_MODEL_BASE_URL": self.text_model_base_url,
                "TEXT_MODEL": self.text_model,
                "TEXT_MODEL_REASONING": self.text_model_reasoning,
            }
        )
