# Game Time Control Plane

## Purpose
A deliberately small optional backend for operating Knowlly Games titles. It is not a gameplay server.

## v1 responsibilities
- versioned remote config
- feature flags
- kill switches
- level/config distribution where justified
- support intake / diagnostic references
- environment/version metadata

## Required behavior
- games ship with bundled defaults
- config is validated before use
- cache last-known-good config
- failures fall back safely
- core gameplay remains offline

## Candidate future capabilities
- LiveOps/event definitions
- App Store server notifications
- economy configuration and integrity checks
- experiment assignment
- portfolio telemetry aggregation
- lightweight operations/admin APIs

## Explicit non-goals
- proprietary login/account system
- multiplayer game server
- server-authoritative ordinary gameplay
- mandatory connectivity
- giant admin application before a proven need
