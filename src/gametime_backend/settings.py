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
        return cls(
            service_name=os.getenv("GAMETIME_SERVICE_NAME", cls.service_name),
            environment=os.getenv("GAMETIME_ENVIRONMENT", cls.environment),
            version=os.getenv("GAMETIME_VERSION", cls.version),
        )
