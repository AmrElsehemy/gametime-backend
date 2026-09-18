from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel

from .settings import Settings


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    service: str
    version: str
    environment: str


settings = Settings.from_environment()

app = FastAPI(
    title="Game Time Control Plane",
    version=settings.version,
    docs_url="/docs" if settings.environment != "production" else None,
    redoc_url=None,
)


@app.get("/health", response_model=HealthResponse, tags=["system"])
def health() -> HealthResponse:
    return HealthResponse(
        service=settings.service_name,
        version=settings.version,
        environment=settings.environment,
    )
