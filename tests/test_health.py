from fastapi.testclient import TestClient

from gametime_backend.main import app
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
