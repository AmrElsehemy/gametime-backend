# Exactly One Remote Config Contract

Exactly One remains an **offline-first game**. This endpoint can change operational behavior, but it can never become a prerequisite for launching, playing, saving progress, completing bundled levels, or finishing the onboarding flow.

Public product name: **Exactly One**. The internal codename, API route, configuration paths, and model identifiers retain `nine` for compatibility. Never use that codename as player-facing product copy.

## Endpoint

```http
GET /v1/games/nine/config
```

The service selects the checked-in config for its own `GAMETIME_ENVIRONMENT` (`development`, `staging`, or `production`). Clients do not select an environment through the request.

## Schema v1

```json
{
  "schema_version": 1,
  "config_version": "2026-09-18.production.1",
  "minimum_client_config_version": 1,
  "rewarded_ads_enabled": false,
  "rewarded_hint_enabled": false,
  "bonus_reward_enabled": false,
  "disabled_level_ids": [],
  "support_url": null,
  "daily_challenge": null
}
```

Supported operational controls:

- `rewarded_ads_enabled` — global rewarded-ad kill switch
- `rewarded_hint_enabled` — whether an ad-backed hint offer may be surfaced
- `bonus_reward_enabled` — whether optional reward multiplication is enabled
- `disabled_level_ids` — removes a known-broken bundled level from normal selection without downloading executable content
- `support_url` — optional operational override once the real support URL is public
- `daily_challenge` — optional future override containing a bundled `level_id` and challenge version

No field contains executable gameplay code and no player identity is required.

## Publishing rule

Configuration is checked into source and validated by `NineRemoteConfig` before the app can serve it. All supported environment files are loaded during application startup/import. Invalid schema, malformed JSON, duplicate disabled-level IDs, or an unsupported schema version causes validation to fail instead of silently serving a bad document.

Production starts with reward features **off**. They are enabled only after the corresponding iOS feature and policy/privacy work are production-ready.

## HTTP caching

Successful responses include:

```http
ETag: "..."
Cache-Control: public, max-age=300, stale-if-error=86400
X-GameTime-Config-Version: 2026-09-18.production.1
```

Clients should send `If-None-Match` on refresh. Matching versions return `304 Not Modified`.

## iOS fallback contract

Exactly One must bundle safe defaults in the app. Client resolution order is:

1. launch immediately with bundled defaults
2. read the last known-good cached remote config if its schema is supported
3. refresh remote config opportunistically
4. accept a response only after schema/version validation
5. persist the new document as last known-good
6. on timeout, transport failure, 5xx, invalid JSON, unsupported schema, or incompatible config version: keep using bundled/cached safe values

Remote config must never block the main thread or gate game startup.

### Bundled safe defaults

Until a feature is intentionally activated, the client should assume:

```text
rewarded_ads_enabled = false
rewarded_hint_enabled = false
bonus_reward_enabled = false
disabled_level_ids = []
daily_challenge = none
```

A disabled level affects level selection only; it must not corrupt an existing save. If a player's current level becomes disabled, the client should advance to the next available bundled level while preserving completed-level history.

## Change process

For an operational change:

1. edit the target environment JSON
2. increment `config_version`
3. run tests/schema validation
4. review the diff as production configuration, not as application code
5. deploy the backend
6. verify endpoint headers/body
7. observe clients before promoting the same change to production

A later admin UI may automate this workflow, but v1 deliberately uses version-controlled configuration so every change is reviewable and reversible.
