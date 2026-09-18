from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Settings:
    service_name: str = "gametime-backend"
    environment: str = "development"
    version: str = "0.1.0"

    @classmethod
    def from_environment(cls) -> "Settings":
        defaults = cls()
        return cls(
            service_name=os.getenv("GAMETIME_SERVICE_NAME", defaults.service_name),
            environment=os.getenv("GAMETIME_ENVIRONMENT", defaults.environment),
            version=os.getenv("GAMETIME_VERSION", defaults.version),
        )
