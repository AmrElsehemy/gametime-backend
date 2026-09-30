from typing import Literal

from fastapi import FastAPI, Request, Response, status
from pydantic import BaseModel

from .exactly_one_config import ExactlyOneRemoteConfig, load_exactly_one_config
from .settings import Settings


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    service: str
    version: str
    environment: str


def create_app(settings: Settings) -> FastAPI:
    # Loads only this environment's config: an unknown environment or an
    # invalid file stops startup instead of serving 503s behind a green
    # /health, and a broken staging file cannot take production down.
    exactly_one_config = load_exactly_one_config(settings.environment)
    is_production = settings.environment == "production"

    app = FastAPI(
        title="Game Time Control Plane",
        version=settings.version,
        docs_url=None if is_production else "/docs",
        redoc_url=None,
        openapi_url=None if is_production else "/openapi.json",
    )

    @app.get("/health", response_model=HealthResponse, tags=["system"])
    def health() -> HealthResponse:
        return HealthResponse(
            service=settings.service_name,
            version=settings.version,
            environment=settings.environment,
        )

    @app.get(
        "/v1/games/exactly-one/config",
        response_model=ExactlyOneRemoteConfig,
        tags=["games"],
    )
    def exactly_one_config_endpoint(request: Request, response: Response):
        etag = exactly_one_config.etag()
        cache_control = "public, max-age=300, stale-if-error=86400"

        if request.headers.get("if-none-match") == etag:
            return Response(
                status_code=status.HTTP_304_NOT_MODIFIED,
                headers={
                    "ETag": etag,
                    "Cache-Control": cache_control,
                },
            )

        response.headers["ETag"] = etag
        response.headers["Cache-Control"] = cache_control
        response.headers["X-GameTime-Config-Version"] = exactly_one_config.config_version
        return exactly_one_config

    return app


app = create_app(Settings.from_environment())
