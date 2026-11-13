from collections import defaultdict
from hashlib import sha256
from hmac import digest
import secrets
import subprocess
from pathlib import Path
import json
import re
import sqlite3
import sys

if sys.argv[1] == "reopen":
    with sqlite3.connect(sys.argv[2]) as db:
        print(json.dumps(dict(db.execute("SELECT key, counts FROM request"))))
    raise SystemExit(0)

trial, target = map(Path, sys.argv[1:])
run_key = secrets.token_bytes(32)
verified = (trial / "verified-replay.json").read_bytes()
assert verified == (trial / "feasibility.json").read_bytes()
receipt = json.loads(verified)
session = (trial / "session-id.txt").read_text().strip()
folder = Path.home() / ".claude" / "projects" / re.sub(r"[^A-Za-z0-9]", "-", str(trial / "project"))
parent = folder / f"{session}.jsonl"
child, = (folder / session / "subagents").glob("agent-*.jsonl")
telemetry = trial / "telemetry.json"
for label, path in {"parent": parent, "child": child, "telemetry": telemetry, "wire": trial / "wire.jsonl"}.items():
    assert sha256(path.read_bytes()).hexdigest() == receipt["artifact_sha256"][label]
expected = {}
child_order = []
for raw in child.read_bytes().splitlines():
    row = json.loads(raw)
    if row.get("type") == "assistant" and (key := row.get("requestId")) and key not in child_order:
        child_order.append(key)
assert len(child_order) == 2
fields = ("input_tokens", "output_tokens", "cache_read_tokens", "cache_creation_tokens", "cost_usd_micros")
for location in (parent, child):
    for line in location.read_bytes().splitlines():
        row = json.loads(line)
        if row.get("type") == "assistant" and (key := row.get("requestId")):
            label = "parent" if location == parent else "child"
            assert expected.setdefault(key, label) == label

requests = []
versions = set()
control = []
agent_prompts = set()
for batch in json.loads(telemetry.read_bytes()):
    for resource in batch["resourceLogs"]:
        attrs = {a["key"]: next(iter(a["value"].values())) for a in resource["resource"]["attributes"]}
        versions.add((attrs.get("os.type"), attrs.get("service.version")))
        for scope in resource["scopeLogs"]:
            for record in scope["logRecords"]:
                values = {a["key"]: next(iter(a["value"].values())) for a in record["attributes"]}
                for name in ("prompt", "prompt_text"):
                    assert not values.get(name) or values[name].lower() == "<redacted>"
                assert not ({"tool_input", "tool_output", "tool_content", "tool_details"} & values.keys())
                if values.get("event.name") != "api_request":
                    continue
                assert values["session.id"] == session
                request = values["request_id"]
                assert expected[request] == ("child" if values.get("agent_id") else "parent")
                if values.get("agent_id"):
                    agent_prompts.add(values["prompt.id"])
                control.append((values["prompt.id"], request))
                requests.append((digest(run_key, request.encode(), "sha256").hex(), tuple(int(values[k]) for k in fields),
                                 expected[request]))
assert versions == {("darwin", "2.1.318")} and len(agent_prompts) == 1
control_request, = (key for prompt, key in control if prompt not in agent_prompts)
for raw in parent.read_bytes().splitlines():
    row = json.loads(raw)
    if row.get("requestId") == control_request:
        assert all(item.get("type") != "tool_use" for item in row["message"].get("content", []))
assert len(expected) == len(requests) == 5
assert sum(r[2] == "child" for r in requests) == 2

database = target / "scratch-reconciliation.sqlite3"
with sqlite3.connect(database) as db:
    db.execute("CREATE TABLE IF NOT EXISTS request (key TEXT PRIMARY KEY, counts TEXT NOT NULL)")
    db.execute("DELETE FROM request")

def store(rows):
    with sqlite3.connect(database) as db:
        for key, counters, group in rows:
            payload = json.dumps([counters, group])
            seen = db.execute("SELECT counts FROM request WHERE key=?", (key,)).fetchone()
            if seen is None:
                db.execute("INSERT INTO request VALUES (?,?)", (key, payload))
            elif seen[0] != payload:
                raise ValueError("conflicting duplicate")
        return dict(db.execute("SELECT key, counts FROM request"))

first_child = next(row for row in requests if row[0] == digest(run_key, child_order[0].encode(), "sha256").hex())
retained = [r for r in requests if r != first_child]
expected_keys = {r[0] for r in requests}
partial = store(retained + retained)
assert len(partial) == 4 and expected_keys - partial.keys() == {first_child[0]}
after_reopen = json.loads(subprocess.check_output([sys.executable, __file__, "reopen", str(database)], text=True))
assert after_reopen == partial and store(retained) == partial
complete = store([first_child] + requests)
assert complete.keys() == expected_keys
assert store(requests) == complete
try:
    store([(first_child[0], tuple(x + 1 for x in first_child[1]), "child")])
except ValueError:
    pass
else:
    raise AssertionError("contradictory duplicate was accepted")
assert store([]) == complete
totals = defaultdict(lambda: [0] * len(fields))
for serialized in complete.values():
    counts, label = json.loads(serialized)
    for index, count in enumerate(counts):
        totals[label][index] += count
assert sum(totals["child"]) > 0
report = {
    "schema": "aitm.claude-coverage-replay/v1",
    "surface": receipt["surface"],
    "mode": "offline replay of the independently hashed receiver-side loopback OTLP POST bodies through a disposable durable reference join",
    "input_receipt_sha256": sha256(verified).hexdigest(),
    "native_child_order_confirmed": True,
    "control_request_had_no_tool_use": True,
    "content_redaction_controls_verified": True,
    "separate_process_reopen_verified": True,
    "expected_native_requests": len(expected_keys),
    "duplicate_delivery_attempts_before_restart": 2 * len(retained),
    "distinct_after_duplicate_delivery_and_reopen": len(after_reopen),
    "missing_after_one_dropped_event": len(expected_keys - partial.keys()),
    "missing_is_coverage_gap_not_zero_usage": True,
    "distinct_after_late_replay": len(complete),
    "duplicate_did_not_change_counters": True,
    "conflicting_duplicate_refused": True,
    "child": dict(zip(fields, totals["child"])),
    "parent": dict(zip(fields, totals["parent"])),
    "live_provider_retransmission_proven": False,
    "original_ownership_proven": False,
}
(target / "replay.json").write_text(json.dumps(report, indent=2) + "\n")
database.unlink()
print(json.dumps(report, indent=2))
