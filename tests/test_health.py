import pytest
from fastapi.testclient import TestClient

from gametime_backend.main import app, create_app
from gametime_backend.nine_config import NineConfigError
from gametime_backend.settings import Settings


def test_health_returns_versioned_service_metadata() -> None:
    response = TestClient(app).get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "gametime-backend",
        "version": "0.1.0",
        "environment": "development",
    }


def test_settings_are_environment_driven(monkeypatch) -> None:
    monkeypatch.setenv("GAMETIME_SERVICE_NAME", "gametime-control-test")
    monkeypatch.setenv("GAMETIME_ENVIRONMENT", "test")
    monkeypatch.setenv("GAMETIME_VERSION", "9.9.9")

    settings = Settings.from_environment()

    assert settings.service_name == "gametime-control-test"
    assert settings.environment == "test"
    assert settings.version == "9.9.9"


def test_unset_environment_fails_closed_to_production(monkeypatch) -> None:
    monkeypatch.delenv("GAMETIME_ENVIRONMENT", raising=False)

    assert Settings.from_environment().environment == "production"


def test_production_app_hides_schema_and_serves_fail_closed_config() -> None:
    client = TestClient(create_app(Settings(environment="production")))

    assert client.get("/openapi.json").status_code == 404
    assert client.get("/docs").status_code == 404

    config = client.get("/v1/games/nine/config").json()
    assert config["config_version"] == "2026-09-18.production.1"
    assert config["rewarded_ads_enabled"] is False


def test_non_production_app_keeps_schema_for_development() -> None:
    client = TestClient(create_app(Settings(environment="development")))

    assert client.get("/openapi.json").status_code == 200


def test_unknown_environment_refuses_to_start() -> None:
    with pytest.raises(NineConfigError, match="Unsupported Game Time environment"):
        create_app(Settings(environment="prod"))
