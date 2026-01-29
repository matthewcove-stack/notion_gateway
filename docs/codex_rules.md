# Codex Rules — notion_gateway

- Do not change endpoint paths without explicit intent.
- Treat schema JSON under `schemas/` as authoritative source for workspace model.
- Any workflow change must preserve idempotency and be reflected in smoke tests.
- Prefer adding new workflows to `_core/` only when necessary; keep naming deterministic.
