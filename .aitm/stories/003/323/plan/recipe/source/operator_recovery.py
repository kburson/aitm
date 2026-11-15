"""Disposable GitHub workflow preflight and public signed-admission verifier."""

import argparse
from base64 import b64decode
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import subprocess
from tempfile import TemporaryDirectory


ROOT = Path(__file__).resolve().parent
NAMESPACE = "aitm-323-missed-slot"
WORKFLOW = ".github/workflows/operator-recovery.yml"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def instant(value):
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    need(result.tzinfo is not None, "UTC timestamps required")
    return result.astimezone(timezone.utc)


def hex_id(value, length):
    return isinstance(value, str) and re.fullmatch(rf"[0-9a-f]{{{length}}}", value) is not None


def signed(admission_raw, signature_raw, allowed_signers):
    with TemporaryDirectory(prefix="aitm-recovery-signature-") as work:
        sig = Path(work) / "authorization.sig"
        sig.write_bytes(signature_raw)
        result = subprocess.run(
            ["ssh-keygen", "-Y", "verify", "-f", str(allowed_signers), "-I",
             "rehearsal-operator", "-n", NAMESPACE, "-s", str(sig)],
            input=admission_raw, capture_output=True,
        )
    need(result.returncode == 0, "operator authorization signature refused")
    admission = json.loads(admission_raw)
    need(admission_raw == (json.dumps(admission, sort_keys=True, separators=(",", ":")) + "\n").encode(),
         "operator authorization is not canonical")
    return admission


def validate_admission(payload, scenario, binding, when):
    need(set(payload) == {
        "schema", "issue", "id", "operator", "slot", "deadline", "miss_record_sha256",
        "producer", "production", "action", "issued_at", "expires_at",
    }, "operator authorization schema disagrees")
    need(payload["schema"] == "aitm.rehearsal-operator-authorization/v1" and payload["issue"] == 323
         and payload["action"] == "recover-full-suite-after-missed-slot"
         and hex_id(payload["id"], 32) and hex_id(payload["miss_record_sha256"], 64),
         "operator recovery intent disagrees")
    need(payload["slot"] == scenario["slot"] and payload["deadline"] == scenario["deadline"]
         and payload["production"] == scenario["production"]
         and payload["producer"] == {
             "repository": binding["repository"], "repository_id": binding["repository_id"],
             "ref": binding["ref"], "sha": binding["sha"], "workflow": WORKFLOW,
         }
         and payload["operator"] == {"id": binding["actor_id"], "login": binding["actor"]},
         "operator authorization target or actor disagrees")
    need(instant(payload["slot"]) < instant(payload["deadline"])
         <= instant(payload["issued_at"]) < instant(payload["expires_at"])
         and instant(payload["issued_at"]) <= when <= instant(payload["expires_at"]),
         "operator authorization is premature or expired")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    env = os.environ
    event = json.loads(Path(env["GITHUB_EVENT_PATH"]).read_bytes())
    scenario = json.loads((ROOT / "scenario.json").read_bytes())
    binding = {
        "repository": env["GITHUB_REPOSITORY"],
        "repository_id": int(env["GITHUB_REPOSITORY_ID"]),
        "sha": env["GITHUB_SHA"],
        "ref": env["GITHUB_REF"],
        "workflow_ref": env["GITHUB_WORKFLOW_REF"],
        "workflow_sha": env["GITHUB_WORKFLOW_SHA"],
        "event": env["GITHUB_EVENT_NAME"],
        "run_id": int(env["GITHUB_RUN_ID"]),
        "attempt": int(env["GITHUB_RUN_ATTEMPT"]),
        "actor": env["GITHUB_ACTOR"],
        "actor_id": int(env["GITHUB_ACTOR_ID"]),
        "triggering_actor": env["GITHUB_TRIGGERING_ACTOR"],
    }
    need(binding["event"] == "workflow_dispatch" and binding["attempt"] == 1
         and binding["actor"] == binding["triggering_actor"], "wrong event or replayed attempt")
    repo = event["repository"]
    sender = event["sender"]
    need(repo["id"] == scenario["lab"]["id"] == binding["repository_id"]
         and repo["full_name"] == scenario["lab"]["repository"] == binding["repository"]
         and "refs/heads/" + repo["default_branch"] == scenario["lab"]["ref"] == binding["ref"]
         and sender["id"] == binding["actor_id"] and sender["login"] == binding["actor"]
         and binding["workflow_ref"] == f"{binding['repository']}/{WORKFLOW}@{binding['ref']}"
         and binding["workflow_sha"] == binding["sha"]
         and subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip() == binding["sha"],
         "provider producer identity disagrees")
    raw = b64decode(event["inputs"]["authorization"], validate=True)
    signature = b64decode(event["inputs"]["signature"], validate=True)
    payload = signed(raw, signature, ROOT / "operator.allowed_signers")
    need(event["inputs"]["admission_id"] == payload["id"], "dispatch admission ID disagrees")
    now = datetime.now(timezone.utc)
    validate_admission(payload, scenario, binding, now)
    args.output.mkdir()
    (args.output / "authorization.json").write_bytes(raw)
    (args.output / "authorization.sig").write_bytes(signature)
    doc = {"schema": "aitm.rehearsal-operator-preflight/v1", "producer": binding,
           "authorization_sha256": sha256(raw).hexdigest(), "authorized_at": now.isoformat(),
           "admission_id": payload["id"], "production": scenario["production"]}
    (args.output / "preflight.json").write_text(json.dumps(doc, sort_keys=True, indent=2) + "\n")
    print(json.dumps(doc, sort_keys=True))


if __name__ == "__main__":
    main()
