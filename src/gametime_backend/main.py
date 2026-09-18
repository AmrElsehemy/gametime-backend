from typing import Literal

from fastapi import FastAPI, HTTPException, Request, Response, status
from pydantic import BaseModel

from .nine_config import NineRemoteConfig, validate_all_nine_configs
from .settings import Settings


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    service: str
    version: str
    environment: str


settings = Settings.from_environment()
nine_configs = validate_all_nine_configs()

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


@app.get(
    "/v1/games/nine/config",
    response_model=NineRemoteConfig,
    tags=["games"],
)
def nine_config(request: Request, response: Response):
    config = nine_configs.get(settings.environment)
    if config is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Nine remote config is not published for this environment",
        )

    etag = config.etag()
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
    response.headers["X-GameTime-Config-Version"] = config.config_version
    return config
