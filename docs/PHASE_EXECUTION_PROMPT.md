# Phase Execution Prompt — notion_gateway

Implement only the requested phase.

For Phase 1:
- Verify tasks create/update are idempotent (request_id).
- Ensure responses include stable IDs.
- Keep contracts stable; if you must change them, update notion_assistant_contracts + bump VERSION.

Run:
- `docker compose up -d`
- `docker compose run --rm smoke all`

Update `docs/current_state.md` when behaviour changes.
