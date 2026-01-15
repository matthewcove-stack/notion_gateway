#!/usr/bin/env python3
import json
import os
import sys
import time
import uuid
from urllib import request, error


def get_token():
    token = os.environ.get("BOOTSTRAP_BEARER_TOKEN") or os.environ.get("API_BEARER_TOKEN")
    if not token:
        raise RuntimeError("Missing BOOTSTRAP_BEARER_TOKEN or API_BEARER_TOKEN")
    return token


def webhook_base():
    base_url = os.environ.get("SMOKE_BASE_URL", "http://n8n:5678").rstrip("/")
    prefix = os.environ.get("SMOKE_WEBHOOK_PREFIX", "").strip("/")
    if prefix:
        return f"{base_url}/webhook/{prefix}"
    return f"{base_url}/webhook"


def post_json(path, payload, token):
    url = f"{webhook_base()}{path}"
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(url, data=data, method="POST")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")

    try:
        with request.urlopen(req, timeout=60) as resp:
            body = resp.read().decode("utf-8")
            return resp.status, body
    except error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8")


def envelope(request_id, actor, payload, idempotency_key=None):
    body = {
        "request_id": request_id,
        "actor": actor,
        "payload": payload,
    }
    if idempotency_key:
        body["idempotency_key"] = idempotency_key
    return body


def parse_json(body):
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return None


def assert_ok(status, body, label):
    if status != 200:
        raise RuntimeError(f"{label} failed with HTTP {status}: {body}")
    data = parse_json(body)
    if not data or data.get("status") != "ok":
        raise RuntimeError(f"{label} returned error: {body}")
    return data


def run_bootstrap(token):
    payload = envelope(
        request_id=str(uuid.uuid4()),
        actor="smoke",
        idempotency_key="smoke-bootstrap",
        payload={"schema_version": 1, "rebuild": False},
    )
    status, body = post_json("/v1/os/bootstrap", payload, token)
    data = assert_ok(status, body, "bootstrap")
    created = data["data"]["created"]
    return created


def run_search(token):
    payload = envelope(
        request_id=str(uuid.uuid4()),
        actor="smoke",
        payload={"query": "OS", "limit": 5, "types": ["page", "database"]},
    )
    status, body = post_json("/v1/notion/search", payload, token)
    data = assert_ok(status, body, "search")
    return data["data"]["results"]


def run_db_schema(token, key):
    payload = envelope(
        request_id=str(uuid.uuid4()),
        actor="smoke",
        payload={"database_key": key},
    )
    status, body = post_json("/v1/notion/db/schema", payload, token)
    data = assert_ok(status, body, "db_schema")
    return data["data"]


def run_db_sample(token, key):
    payload = envelope(
        request_id=str(uuid.uuid4()),
        actor="smoke",
        payload={"database_key": key, "limit": 3},
    )
    status, body = post_json("/v1/notion/db/sample", payload, token)
    data = assert_ok(status, body, "db_sample")
    return data["data"]["results"]


def run_task_create(token):
    key = "smoke-task-create"
    task = {
        "title": f"Smoke Task {int(time.time())}",
        "status": "Todo",
        "priority": "Low",
        "tags": ["smoke"],
        "notes": "Smoke test create",
    }
    payload = envelope(
        request_id=str(uuid.uuid4()),
        actor="smoke",
        idempotency_key=key,
        payload={"task": task},
    )
    status, body = post_json("/v1/notion/tasks/create", payload, token)
    data = assert_ok(status, body, "tasks_create")

    replay = envelope(
        request_id=str(uuid.uuid4()),
        actor="smoke",
        idempotency_key=key,
        payload={"task": task},
    )
    status2, body2 = post_json("/v1/notion/tasks/create", replay, token)
    data2 = assert_ok(status2, body2, "tasks_create_replay")

    if data["data"]["created"] is not True:
        raise RuntimeError("tasks_create expected created=true")
    if data2["data"]["created"] is not False:
        raise RuntimeError("tasks_create replay expected created=false")

    return data["data"]["notion_page_id"]


def run_task_update(token, page_id):
    key = "smoke-task-update"
    patch = {
        "status": "In Progress",
        "notes_append": "Smoke update append",
    }
    payload = envelope(
        request_id=str(uuid.uuid4()),
        actor="smoke",
        idempotency_key=key,
        payload={"notion_page_id": page_id, "patch": patch},
    )
    status, body = post_json("/v1/notion/tasks/update", payload, token)
    data = assert_ok(status, body, "tasks_update")

    replay = envelope(
        request_id=str(uuid.uuid4()),
        actor="smoke",
        idempotency_key=key,
        payload={"notion_page_id": page_id, "patch": patch},
    )
    status2, body2 = post_json("/v1/notion/tasks/update", replay, token)
    data2 = assert_ok(status2, body2, "tasks_update_replay")

    if data["data"]["updated"] is not True:
        raise RuntimeError("tasks_update expected updated=true")
    if data2["data"]["updated"] is not False:
        raise RuntimeError("tasks_update replay expected updated=false")


def main():
    token = get_token()
    command = sys.argv[1] if len(sys.argv) > 1 else "all"

    if command == "bootstrap":
        created = run_bootstrap(token)
        print(f"bootstrap created={created}")
        return

    if command == "search":
        results = run_search(token)
        print(f"search results={len(results)}")
        return

    if command == "tasks":
        page_id = run_task_create(token)
        print(f"tasks_create page_id={page_id}")
        run_task_update(token, page_id)
        print("tasks_update ok")
        return

    if command == "db":
        schema = run_db_schema(token, "tasks")
        print(f"db_schema id={schema['database_id']}")
        sample = run_db_sample(token, "tasks")
        print(f"db_sample rows={len(sample)}")
        return

    if command != "all":
        raise RuntimeError(f"Unknown command: {command}")

    created = run_bootstrap(token)
    print(f"bootstrap created={created}")
    results = run_search(token)
    print(f"search results={len(results)}")
    page_id = run_task_create(token)
    print(f"tasks_create page_id={page_id}")
    run_task_update(token, page_id)
    print("tasks_update ok")
    schema = run_db_schema(token, "tasks")
    print(f"db_schema id={schema['database_id']}")
    sample = run_db_sample(token, "tasks")
    print(f"db_sample rows={len(sample)}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(str(exc))
        sys.exit(1)
