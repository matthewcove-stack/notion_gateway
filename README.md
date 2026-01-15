# Notion OS Kernel

Production-grade Notion "OS" kernel that bootstraps a canonical workspace, provisions deterministic schemas, and exposes stable HTTPS JSON endpoints for ChatGPT in standard user mode.

## What this repo is for

- Define the canonical workspace model and system databases
- Specify stable API contracts and idempotent workflows
- Keep Notion as the state store while n8n executes changes

See `INTENT.md` for the full specification.

## High-level endpoints

- `POST /v1/os/bootstrap`
- `POST /v1/notion/search`
- `POST /v1/notion/tasks/create`
- `POST /v1/notion/tasks/update`
- `POST /v1/notion/db/schema`
- `POST /v1/notion/db/sample`

## How to run locally

1) Create a local env file:

```bash
cp .env.example .env
```

2) Edit `.env` and set:

- `N8N_BASIC_AUTH_USER` / `N8N_BASIC_AUTH_PASSWORD`
- `N8N_ENCRYPTION_KEY` (32+ chars)
- `NOTION_API_KEY` (Notion internal integration token)
- `BOOTSTRAP_BEARER_TOKEN` (shared secret for bootstrap endpoint)

3) Start n8n + Postgres:

```bash
docker compose up -d
```

The compose file mounts `./schemas` into the container at `/files/schemas`.

4) Open the editor:

```
http://localhost:5678
```

## How to import the workflow

1) In n8n, go to Workflows -> Import from File.
2) Select `n8n/workflows/v1_os_bootstrap.json`.
3) Save and activate the workflow.

The webhook endpoint will be:

```
POST http://localhost:5678/webhook/v1/os/bootstrap
```

Include header:

```
Authorization: Bearer <BOOTSTRAP_BEARER_TOKEN>
```

## Smoke test

```bash
export BOOTSTRAP_BEARER_TOKEN=your_token
export BASE_URL=http://localhost:5678/webhook
./scripts/smoke_bootstrap.sh
./scripts/smoke_bootstrap_repeat.sh
```

## Repository layout

- `INTENT.md` - Canonical spec and requirements
- `schemas/` - Schema-as-code JSON definitions
- `n8n/workflows/` - Exported n8n workflow JSON
- `scripts/` - Local helper scripts
- `docs/` - Supplemental docs
- `.github/` - Issue templates and CI
