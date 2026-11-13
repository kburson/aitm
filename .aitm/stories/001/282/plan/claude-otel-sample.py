from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from uuid import UUID
import json
import re
import sys

from aitm_usage.cli import open_project
from aitm_usage.scopes import resolve_scope, session_reference
from aitm_usage.service import load_registration
from aitm_usage.types import ItemKind, Provider, UsageObservation

root, activation, output = map(Path, sys.argv[1:4])
approved = json.loads(activation.read_text())
ledger = open_project(root)
if str(ledger.identity.project_id) != approved["project_id"]:
    raise ValueError("activation receipt project mismatch")
registration = load_registration(ledger)
snapshot = ledger.as_of()
start, end = map(datetime.fromisoformat, sys.argv[4:6])
if not start < end or start.tzinfo is None or end.tzinfo is None:
    raise ValueError("invalid sample window")
approved_sessions = defaultdict(list)
for revision in snapshot.current:
    row = revision.record
    if not isinstance(row, UsageObservation) or row.boundary.provider is not Provider.CLAUDE:
        continue
    if start <= row.observed_at < end and row.request_ref is not None:
        approved_sessions[row.boundary.session_ref].append(row)

def metadata(path):
    # Bound native inputs. No prompt, message text, or tool input is retained.
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 8_000_000:
        raise ValueError("native input outside sample size")
    for raw in path.open("rb"):
        if not raw.endswith(b"\n"):
            raise ValueError("unsealed trailing row")
        yield json.loads(raw)

def scan(path, session_ref, records):
    native_ids = set()
    prompts = set()
    overlap_prompts = set()
    children = 0
    missing = 0
    for row in metadata(path):
        stamp = row.get("timestamp")
        if not isinstance(stamp, str):
            continue
        timestamp = datetime.fromisoformat(stamp)
        if not start <= timestamp < end:
            continue
        request = row.get("requestId")
        if row.get("type") == "assistant" and isinstance(request, str):
            native_ids.add(ledger.pseudonymize("claude-request", f"{session_ref.value}:{request}"))
        prompt = row.get("promptId")
        if isinstance(prompt, str):
            prompts.add(prompt)
        result = row.get("toolUseResult")
        if not isinstance(result, dict) or not result.get("agentId") or not isinstance(result.get("usage"), dict):
            continue
        agent = result["agentId"]
        if not isinstance(agent, str) or not re.fullmatch(r"[a-zA-Z0-9_-]{1,64}", agent):
            missing += 1
            continue
        sidecar = path.parent / path.stem / "subagents" / f"agent-{agent}.jsonl"
        if sidecar.parent.is_symlink() or sidecar.parent.parent.is_symlink() or not sidecar.is_file():
            missing += 1
            continue
        side_requests = {
            child["requestId"] for child in metadata(sidecar)
            if child.get("type") == "assistant"
            and isinstance(child.get("timestamp"), str)
            and start <= datetime.fromisoformat(child["timestamp"]) < end
            and child.get("agentId") == agent
            and isinstance(child.get("requestId"), str)
        }
        if side_requests:
            if isinstance(prompt, str):
                overlap_prompts.add(prompt)
            children += len(side_requests)
    joined = [item for item in records if item.request_ref in native_ids]
    bound = [scope.marker.item.identifier for item in joined
             if (scope := resolve_scope(item, snapshot).scope) is not None
             and scope.marker.item.kind is ItemKind.ISSUE]
    return len(prompts), len(overlap_prompts), children, missing, len(joined), bound

anchors = list(registration.checkout_anchors)
claude_roots = [path for path in registration.source_roots
                if path.parts[-2:] == (".claude", "projects")]
counts = Counter()
bound_stories = set()
seen = set()
for parent in sorted({root / re.sub(r"[^A-Za-z0-9]", "-", str(anchor))
                      for root in claude_roots for anchor in anchors}):
    if parent.is_symlink() or not parent.is_dir():
        counts["approved_checkout_folders_unavailable"] += 1
        continue
    for path in sorted(parent.glob("*.jsonl")):
        try:
            session = UUID(path.stem)
        except ValueError:
            continue
        reference = session_reference(ledger, Provider.CLAUDE, str(session))
        if reference not in approved_sessions or reference in seen:
            continue
        if len(seen) == 12:
            counts["session_cap_reached"] = 1
            break
        seen.add(reference)
        try:
            prompts, overlap, children, missing, joined, bound = scan(
                path, reference, approved_sessions[reference])
        except (OSError, ValueError, TypeError):
            counts["native_sessions_unavailable_or_oversize"] += 1
            continue
        counts.update({"scanned_sessions": 1, "sessions_with_overlap": bool(overlap or children),
                       "retained_prompt_ids": prompts, "overlap_prompt_ids": overlap,
                       "matched_child_request_rows": children, "missing_child_sidecars": missing,
                       "ledger_requests_joined_to_native": joined,
                       "joined_requests_with_story_scope": len(bound)})
        bound_stories.update(bound)
report = {
    "schema": "aitm.claude-coverage-bounded-sample/v1",
    "start_utc_inclusive": start.isoformat(),
    "end_utc_exclusive": end.isoformat(),
    "sample": "registered #83 AITM Claude sessions with admitted ledger request identity and an exact approved checkout transcript folder, completed foreground Agent detector",
    "eligible_registered_sessions": len(approved_sessions),
    "eligible_registered_requests": sum(map(len, approved_sessions.values())),
    "registered_sessions_without_selected_native_transcript": len(approved_sessions) - len(seen),
    "registered_checkout_anchors_considered": len(anchors),
    "maximum_native_sessions": 12,
    "distinct_joined_stories": len(bound_stories),
    "counts": dict(counts),
    "workload_overlap_prevalence": None,
    "workload_token_or_cost_share": None,
    "zero_window_interpretation": "No admitted Claude request rows; native work may be absent or uncollected." if not approved_sessions else None,
    "reason": "Admitted legacy rows condition the denominator. Unadmitted requests and sessions may be absent. Native sidecars and a trusted telemetry denominator are not complete for this retrospective window. No child usage assigned to a story.",
}
output.write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
