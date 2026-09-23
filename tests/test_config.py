import pytest

from aveli.config import ConfigurationError, ProductionSettings


def valid_env():
    return {
        "TYPESAFE_API_KEY": "typesafe-secret",
        "TYPESAFE_MODEL": "jev-1.13.0",
        "TEXT_MODEL_API_KEY": "text-secret",
        "TEXT_MODEL_BASE_URL": "https://models.example/v1",
        "TEXT_MODEL": "mercury-2.5",
        "TEXT_MODEL_REASONING": "none",
        "AVELI_EXTERNAL_DATA_APPROVED": "true",
        "AVELI_AUDIT_DIR": "/tmp/aveli-audit",
    }


def test_production_settings_parse_valid_environment():
    settings = ProductionSettings.from_env(valid_env())
    assert settings.typesafe_model == "jev-1.13.0"
    assert settings.text_model == "mercury-2.5"
    assert "secret" not in repr(settings)


@pytest.mark.parametrize(
    ("key", "value", "message"),
    [
        ("AVELI_EXTERNAL_DATA_APPROVED", "false", "data approval"),
        ("TYPESAFE_MODEL", "jev-latest", "pinned"),
        ("TEXT_MODEL", "provider/latest", "pinned"),
        ("TYPESAFE_API_KEY", "", "TYPESAFE_API_KEY"),
        ("TEXT_MODEL_BASE_URL", "http://models.example/v1", "HTTPS"),
    ],
)
def test_production_settings_fail_closed(key, value, message):
    environment = valid_env()
    environment[key] = value
    with pytest.raises(ConfigurationError, match=message):
        ProductionSettings.from_env(environment)
