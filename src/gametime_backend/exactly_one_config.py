from __future__ import annotations

import hashlib
import json
from importlib.resources import files
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, ValidationError


class DailyChallengeOverride(BaseModel):
    model_config = ConfigDict(extra="forbid")

    level_id: str
    challenge_version: str


class ExactlyOneRemoteConfig(BaseModel):
    # A misspelled kill-switch key must fail validation, not fall back to a default.
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal[1] = 1
    config_version: str = Field(min_length=1)
    minimum_client_config_version: int = Field(default=1, ge=1)
    rewarded_ads_enabled: bool = False
    rewarded_hint_enabled: bool = False
    bonus_reward_enabled: bool = False
    disabled_level_ids: list[str] = Field(default_factory=list)
    support_url: HttpUrl | None = None
    daily_challenge: DailyChallengeOverride | None = None

    def canonical_json(self) -> str:
        return self.model_dump_json(exclude_none=False)

    def etag(self) -> str:
        digest = hashlib.sha256(self.canonical_json().encode("utf-8")).hexdigest()
        return f'"{digest}"'


class ExactlyOneConfigError(RuntimeError):
    pass


SUPPORTED_ENVIRONMENTS = ("development", "staging", "production")


def validate_exactly_one_config_payload(
    payload: dict[str, Any],
    *,
    environment: str,
) -> ExactlyOneRemoteConfig:
    try:
        config = ExactlyOneRemoteConfig.model_validate(payload)
    except ValidationError as exc:
        raise ExactlyOneConfigError(
            f"Exactly One config for {environment} failed schema validation: {exc}"
        ) from exc

    if len(config.disabled_level_ids) != len(set(config.disabled_level_ids)):
        raise ExactlyOneConfigError(
            f"Exactly One config for {environment} contains duplicate disabled level IDs"
        )

    return config


def _resource_for(environment: str):
    if environment not in SUPPORTED_ENVIRONMENTS:
        raise ExactlyOneConfigError(f"Unsupported Game Time environment: {environment}")

    return (
        files("gametime_backend")
        .joinpath("config")
        .joinpath("exactly-one")
        .joinpath(f"{environment}.json")
    )


def load_exactly_one_config(environment: str) -> ExactlyOneRemoteConfig:
    resource = _resource_for(environment)

    try:
        payload = json.loads(resource.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        raise ExactlyOneConfigError(
            f"Exactly One config for {environment} could not be loaded: {exc}"
        ) from exc

    return validate_exactly_one_config_payload(payload, environment=environment)


def validate_all_exactly_one_configs() -> dict[str, ExactlyOneRemoteConfig]:
    return {
        environment: load_exactly_one_config(environment)
        for environment in SUPPORTED_ENVIRONMENTS
    }
