from __future__ import annotations

import hashlib
import json
from importlib.resources import files
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl, ValidationError


class DailyChallengeOverride(BaseModel):
    level_id: str
    challenge_version: str


class NineRemoteConfig(BaseModel):
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


class NineConfigError(RuntimeError):
    pass


SUPPORTED_ENVIRONMENTS = ("development", "staging", "production")


def _resource_for(environment: str):
    if environment not in SUPPORTED_ENVIRONMENTS:
        raise NineConfigError(f"Unsupported Game Time environment: {environment}")

    return (
        files("gametime_backend")
        .joinpath("config")
        .joinpath("nine")
        .joinpath(f"{environment}.json")
    )


def load_nine_config(environment: str) -> NineRemoteConfig:
    resource = _resource_for(environment)

    try:
        payload = json.loads(resource.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        raise NineConfigError(
            f"Nine config for {environment} could not be loaded: {exc}"
        ) from exc

    try:
        config = NineRemoteConfig.model_validate(payload)
    except ValidationError as exc:
        raise NineConfigError(
            f"Nine config for {environment} failed schema validation: {exc}"
        ) from exc

    if len(config.disabled_level_ids) != len(set(config.disabled_level_ids)):
        raise NineConfigError(
            f"Nine config for {environment} contains duplicate disabled level IDs"
        )

    return config


def validate_all_nine_configs() -> dict[str, NineRemoteConfig]:
    return {
        environment: load_nine_config(environment)
        for environment in SUPPORTED_ENVIRONMENTS
    }
