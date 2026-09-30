import pytest
from fastapi.testclient import TestClient

from gametime_backend.main import app
from gametime_backend.exactly_one_config import (
    ExactlyOneConfigError,
    load_exactly_one_config,
    validate_all_exactly_one_configs,
    validate_exactly_one_config_payload,
)


def test_all_packaged_environments_are_schema_valid() -> None:
    configs = validate_all_exactly_one_configs()

    assert set(configs) == {"development", "staging", "production"}
    assert all(config.schema_version == 1 for config in configs.values())
    assert all(config.config_version for config in configs.values())


def test_production_defaults_fail_closed() -> None:
    config = load_exactly_one_config("production")

    assert config.rewarded_ads_enabled is False
    assert config.rewarded_hint_enabled is False
    assert config.bonus_reward_enabled is False
    assert config.disabled_level_ids == []
    assert config.daily_challenge is None


def test_endpoint_returns_cacheable_versioned_development_config() -> None:
    response = TestClient(app).get("/v1/games/exactly-one/config")

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
    first = client.get("/v1/games/exactly-one/config")

    second = client.get(
        "/v1/games/exactly-one/config",
        headers={"If-None-Match": first.headers["etag"]},
    )

    assert second.status_code == 304
    assert second.content == b""
    assert second.headers["etag"] == first.headers["etag"]
    assert "stale-if-error=86400" in second.headers["cache-control"]


def test_config_etag_is_deterministic() -> None:
    first = load_exactly_one_config("development")
    second = load_exactly_one_config("development")

    assert first.etag() == second.etag()


def test_duplicate_disabled_levels_are_rejected() -> None:
    payload = {
        "schema_version": 1,
        "config_version": "test.1",
        "disabled_level_ids": ["v1-041", "v1-041"],
    }

    with pytest.raises(ExactlyOneConfigError, match="duplicate disabled level IDs"):
        validate_exactly_one_config_payload(payload, environment="test")


def test_unknown_schema_version_is_rejected() -> None:
    payload = {
        "schema_version": 2,
        "config_version": "future.1",
    }

    with pytest.raises(ExactlyOneConfigError, match="failed schema validation"):
        validate_exactly_one_config_payload(payload, environment="test")


def test_unknown_environment_is_not_silently_mapped() -> None:
    with pytest.raises(ExactlyOneConfigError, match="Unsupported Game Time environment"):
        load_exactly_one_config("mystery")


def test_misspelled_kill_switch_key_is_rejected() -> None:
    payload = {
        "schema_version": 1,
        "config_version": "test.1",
        "disabled_level_id": ["v1-041"],
    }

    with pytest.raises(ExactlyOneConfigError, match="failed schema validation"):
        validate_exactly_one_config_payload(payload, environment="test")


def test_unknown_daily_challenge_key_is_rejected() -> None:
    payload = {
        "schema_version": 1,
        "config_version": "test.1",
        "daily_challenge": {
            "level_id": "v1-006",
            "challenge_version": "1",
            "levelid": "v1-007",
        },
    }

    with pytest.raises(ExactlyOneConfigError, match="failed schema validation"):
        validate_exactly_one_config_payload(payload, environment="test")
