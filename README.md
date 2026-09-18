# Game Time Backend

A deliberately small **control-plane backend** for Knowlly Games.

This is **not** a gameplay server and games must not depend on it to launch or play core content.

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
