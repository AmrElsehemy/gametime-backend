# Game Time Backend

A deliberately small **control-plane backend** for Knowlly Games.

This is **not** a gameplay server and games must not depend on it to launch or play core content.

## Current stack

- Python 3.12+
- FastAPI
- Pydantic response models
- pytest
- GitHub Actions

## Run locally

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
uvicorn gametime_backend.main:app --reload
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

Expected shape:

```json
{
  "status": "ok",
  "service": "gametime-backend",
  "version": "0.1.0",
  "environment": "development"
}
```

## Test

```bash
pytest
```

## Configuration

Bootstrap configuration is environment-driven:

- `GAMETIME_SERVICE_NAME`
- `GAMETIME_ENVIRONMENT`
- `GAMETIME_VERSION`

Secrets must never be committed. `.env` files are ignored.

## Initial responsibilities

- remote configuration
- feature flags / kill switches
- level/config distribution where needed
- support intake / diagnostic references
- environment/version metadata

## Later, only when justified

- LiveOps/event configuration
- App Store server notifications
- economy configuration and integrity checks
- experiment assignment
- portfolio telemetry aggregation

## Non-goals for v1

- custom user accounts
- multiplayer game servers
- server-authoritative core gameplay
- giant admin platform
- mandatory online connectivity

Every remote capability must have bundled defaults and graceful offline behavior.

See `docs/CONTROL_PLANE.md` for the control-plane contract and boundaries.
