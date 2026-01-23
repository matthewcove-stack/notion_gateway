# AGENTS.md

Codex guidance for this repo.

## What this repo is

Notion OS kernel backed by n8n workflows and Postgres. Exposes HTTPS JSON endpoints.

## Quick commands

- Setup: `cp .env.example .env`
- Run: `docker compose up -d`
- Smoke tests: `docker compose run --rm smoke all`

## Safe to edit

- `schemas/`
- `docs/`
- `scripts/`
- `README.md`
- `INTENT.md`

## Avoid or be careful

- `n8n/workflows/` and `n8n/workflows/_core/` are exported workflow JSON. Prefer editing in n8n UI and re-exporting.
- `docker-compose.yml` unless needed for behavior changes

## Contracts

- JSON schemas live in `..\notion_assistant_contracts\schemas\v1\`.
- Examples live in `..\notion_assistant_contracts\examples\`.
