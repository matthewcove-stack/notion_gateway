# notion_gateway — Phases

## Phase 0 (done)
- Kernel endpoints and schema-as-code
- n8n workflow exports and local compose
- Basic smoke test harness

## Phase 1 (kernel responsibilities)
- Confirm and enforce idempotency for task create/update using request_id
- Ensure response payload includes the created/updated task ID in a stable field
- Ensure error responses are consistent and machine-readable

## Phase 2 (later)
- Expanded entity support (CRM, knowledge capture, finance)
- More rigorous contract tests against notion_assistant_contracts
