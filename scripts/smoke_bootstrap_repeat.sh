#!/usr/bin/env bash
set -euo pipefail

: "${BOOTSTRAP_BEARER_TOKEN:?Set BOOTSTRAP_BEARER_TOKEN}"

BASE_URL="${BASE_URL:-http://localhost:5678/webhook}"
IDEMPOTENCY_KEY="${IDEMPOTENCY_KEY:-bootstrap-smoke}"
REQUEST_ID=$(python - <<'PY'
import uuid
print(uuid.uuid4())
PY
)

payload=$(cat <<JSON
{
  "request_id": "${REQUEST_ID}",
  "idempotency_key": "${IDEMPOTENCY_KEY}",
  "actor": "smoke_test",
  "payload": { "schema_version": 1, "rebuild": false }
}
JSON
)

response=$(curl -s -w "\n%{http_code}" \
  -X POST "${BASE_URL}/v1/os/bootstrap" \
  -H "Authorization: Bearer ${BOOTSTRAP_BEARER_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "${payload}")

http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

echo "HTTP ${http_code}"
echo "$body"

BOOTSTRAP_BODY="$body" python - <<'PY'
import json
import os
import sys

body = os.environ.get('BOOTSTRAP_BODY')
if not body:
    sys.exit(1)

try:
    data = json.loads(body)
except json.JSONDecodeError as exc:
    print(f"Failed to parse JSON response: {exc}")
    sys.exit(1)

created = data.get('data', {}).get('created')
if created is False:
    print('created=false confirmed')
    sys.exit(0)

print(f"Expected created=false but got: {created}")
sys.exit(1)
PY
