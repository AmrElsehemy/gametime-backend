import pytest
from fastapi.testclient import TestClient

from gametime_backend.main import app
from gametime_backend.nine_config import (
    NineConfigError,
    load_nine_config,
    validate_all_nine_configs,
    validate_nine_config_payload,
)


def test_all_packaged_environments_are_schema_valid() -> None:
    configs = validate_all_nine_configs()

    assert set(configs) == {"development", "staging", "production"}
    assert all(config.schema_version == 1 for config in configs.values())
    assert all(config.config_version for config in configs.values())


def test_production_defaults_fail_closed() -> None:
    config = load_nine_config("production")

    assert config.rewarded_ads_enabled is False
    assert config.rewarded_hint_enabled is False
    assert config.bonus_reward_enabled is False
    assert config.disabled_level_ids == []
    assert config.daily_challenge is None


def test_endpoint_returns_cacheable_versioned_development_config() -> None:
    response = TestClient(app).get("/v1/games/nine/config")

    assert response.status_code == 200
    body = response.json()
    assert body["schema_version"] == 1
    assert body["config_version"] == "2026-09-18.dev.1"
    assert body["rewarded_ads_enabled"] is False
    assert response.headers["etag"].startswith('"')
    assert "max-age=300" in response.headers["cache-control"]
    assert "stale-if-error=86400" in response.headers["cache-control"]
    assert response.headers["x-gametime-config-version"] == body["config_version"]


def test_endpoint_honors_if_none_match() -> None:
    client = TestClient(app)
    first = client.get("/v1/games/nine/config")

    second = client.get(
        "/v1/games/nine/config",
        headers={"If-None-Match": first.headers["etag"]},
    )

    assert second.status_code == 304
    assert second.content == b""
    assert second.headers["etag"] == first.headers["etag"]
    assert "stale-if-error=86400" in second.headers["cache-control"]


def test_config_etag_is_deterministic() -> None:
    first = load_nine_config("development")
    second = load_nine_config("development")

    assert first.etag() == second.etag()


def test_duplicate_disabled_levels_are_rejected() -> None:
    payload = {
        "schema_version": 1,
        "config_version": "test.1",
        "disabled_level_ids": ["v1-041", "v1-041"],
    }

    with pytest.raises(NineConfigError, match="duplicate disabled level IDs"):
        validate_nine_config_payload(payload, environment="test")


def test_unknown_schema_version_is_rejected() -> None:
    payload = {
        "schema_version": 2,
        "config_version": "future.1",
    }

    with pytest.raises(NineConfigError, match="failed schema validation"):
        validate_nine_config_payload(payload, environment="test")


def test_unknown_environment_is_not_silently_mapped() -> None:
    with pytest.raises(NineConfigError, match="Unsupported Game Time environment"):
        load_nine_config("mystery")
