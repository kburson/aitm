"""Check advisory recovery and record an explicit local operator acknowledgment."""

import argparse
import json
import re
import sqlite3
import sys
from datetime import datetime, timezone
from hashlib import sha256

import ci_advisory as intake
from ci_incident import OWNER, Store, encode, identity, order
from verify_pr import (
    GitHub,
    blob,
    commit,
    decode_json,
    digest,
    positive,
    regular_blob,
    require,
    timestamp,
    tree_entries,
)

ACCEPTED = re.compile(rb"\*\*Verdict: ACCEPTED\.\*\*")
PR_RECEIPT = re.compile(r"\.aitm/stories/([0-9]{3})/([1-9][0-9]*)/plan/delivery\.json")
TUPLE = (
    "pr",
    "base",
    "head",
    "tested",
    "tree",
    "run_id",
    "run_attempt",
    "artifact_id",
    "archive_digest",
    "subject_digest",
    "workflow_id",
    "repository_id",
)


def operator(value):
    require(isinstance(value, str) and OWNER.fullmatch(value), "invalid operator")


def verify_repair(github, plan_commit, receipt_path, receipt_digest, review_digest):
    """Authenticate delivery and independent review against protected planning."""
    match = PR_RECEIPT.fullmatch(receipt_path)
    require(
        match
        and int(match[1]) == int(match[2]) // 100
        and digest(plan_commit)
        and digest(receipt_digest, 64)
        and digest(review_digest, 64),
        "invalid exact repair evidence identifiers",
    )
    planning = github.document("branches/planning")
    current = planning["commit"]["sha"]
    require(
        planning["name"] == "planning"
        and planning["protected"] is True
        and digest(current),
        "protected planning provenance unavailable",
    )
    if current != plan_commit:
        compared = github.document(f"compare/{plan_commit}...{current}")
        require(
            compared["status"] == "ahead"
            and compared["merge_base_commit"]["sha"] == plan_commit,
            "repair receipt revision is absent from protected planning",
        )
    tree = commit(github, plan_commit)["tree"]["sha"]
    entries = tree_entries(github, tree)
    raw = blob(github, regular_blob(entries, receipt_path))
    require(
        sha256(raw).hexdigest() == receipt_digest, "repair delivery digest disagrees"
    )
    delivery = decode_json(raw)
    require(
        delivery["status"] == "accepted"
        and delivery["target"] == intake.TARGET
        and delivery["repository"] == intake.REPO
        and delivery["repository_id"] == intake.REPOSITORY_ID
        and delivery["workflow_id"] == intake.WORKFLOW_ID
        and delivery["issue"] == int(match[2])
        and delivery["review_sha256"] == review_digest
        and delivery["review"] == "plan/reviews/formal-review.md"
        and delivery["tree"] == delivery["reviewed_tree"]
        and all(
            positive(delivery[key])
            for key in ("pr", "run_id", "run_attempt", "artifact_id")
        )
        and all(
            digest(delivery[key]) for key in ("base", "head", "tested", "tree", "merge")
        ),
        "repair delivery evidence is incomplete or disagrees",
    )
    plan_dir = receipt_path.rsplit("/", 1)[0]
    review_path = f"{plan_dir}/reviews/formal-review.md"
    review = blob(github, regular_blob(entries, review_path))
    require(
        sha256(review).hexdigest() == review_digest and ACCEPTED.search(review),
        "repair's independent review is missing or unaccepted",
    )
    require(
        all(
            delivery[key].encode() in review
            for key in ("base", "head", "tested", "tree")
        )
        and f"/pull/{delivery['pr']})".encode() in review
        and f"/actions/runs/{delivery['run_id']}/attempts/{delivery['run_attempt']})".encode()
        in review,
        "independent review does not bind the repair's exact PR and attempt",
    )
    verifier = decode_json(
        blob(github, regular_blob(entries, f"{plan_dir}/premerge-verifier.json"))
    )
    require(
        verifier["status"] == "pass"
        and all(verifier[key] == delivery[key] for key in TUPLE),
        "trusted #103 premerge evidence disagrees with delivery",
    )
    pull = github.document(f"pulls/{delivery['pr']}")
    require(
        pull["number"] == delivery["pr"]
        and pull["merged"] is True
        and pull["state"] == "closed"
        and pull["base"]["ref"] == intake.TARGET
        and pull["base"]["repo"]["id"]
        == pull["head"]["repo"]["id"]
        == intake.REPOSITORY_ID
        and pull["head"]["sha"] == delivery["head"]
        and pull["merge_commit_sha"] == delivery["merge"],
        "nominated repair PR was not delivered at the reviewed identity",
    )
    for sha in (delivery["tested"], delivery["merge"]):
        row = commit(github, sha)
        require(
            [parent["sha"] for parent in row["parents"]]
            == [delivery["base"], delivery["head"]]
            and row["tree"]["sha"] == delivery["tree"],
            "repair tested or landed commit differs from reviewed tree and parents",
        )
    timestamp(pull["merged_at"])
    return {
        "pr": delivery["pr"],
        "sha": delivery["merge"],
        "landed_at": pull["merged_at"],
        "receipt": receipt_digest,
        "review": review_digest,
        "planning": plan_commit,
        "head": delivery["head"],
        "tree": delivery["tree"],
    }


def confirm_infrastructure(store, version, actor, reason, *, now=None, live=False):
    operator(actor)
    require(
        isinstance(reason, str) and 0 < len(reason.strip()) <= 500,
        "invalid infrastructure reason",
    )
    now = now or datetime.now(timezone.utc)
    held = False
    with store.transaction() as db:
        outcome = (
            store._observe(db, intake.observe(GitHub(intake.REPO))) if live else None
        )
        state = store._load(db)
        active = state["incident"]
        confirmed = bool(
            active
            and active["active"]
            and active["version"] == version
            and active["status"] == "incomplete"
            and not active["failures"]
            and active["nomination"] is None
            and state["pending_sha"] is None
            and state["latest"]["key"] == active["key"]
            and state["latest"]["status"] == "incomplete"
            and now > timestamp(active["started_at"])
            and (not live or outcome in {"warning", "updated", "duplicate"})
        )
        if confirmed:
            confirmation = {
                "operator": actor,
                "reason": reason.strip(),
                "time": now.isoformat(),
            }
            prior = active.get("infrastructure")
            if prior is None:
                active["infrastructure"] = confirmation
                active["recovery"] = None
                store._save(db, state)
            else:
                held = any(
                    confirmation[key] != prior[key] for key in ("operator", "reason")
                )
        else:
            held = True
    require(
        not held,
        "infrastructure confirmation requires an incomplete current incident with no authenticated failures and matching operator confirmation",
    )


def proposed_recovery(store, state, version, observation, repair):
    active = state["incident"]
    if not active or not active["active"] or active["version"] != version:
        return None
    if not observation or observation.get("status") != "green":
        return None
    key = identity(observation, store.provenance)
    latest = state["latest"]
    if (
        state["pending_sha"] is not None
        or latest["key"] != key
        or latest["status"] != "green"
        or order(key) <= order(active["key"])
    ):
        return None
    artifact = observation.get("artifact") or {}
    if not (
        positive(artifact.get("id"))
        and isinstance(artifact.get("digest"), str)
        and artifact["digest"].startswith("sha256:")
        and digest(artifact["digest"][7:], 64)
        and artifact.get("policy_result", {}).get("passed") is True
    ):
        return None
    token_data = {"version": version, "green": key, "artifact": artifact["digest"]}
    started = timestamp(observation["started_at"])
    if repair is not None:
        nomination = active["nomination"]
        if (
            not nomination
            or nomination["pr"] != repair["pr"]
            or key["sha"] != repair["sha"]
            or active["key"]["sha"] == repair["sha"]
            or timestamp(active["started_at"]) >= timestamp(repair["landed_at"])
            or started < timestamp(repair["landed_at"])
        ):
            return None
        token_data["repair"] = repair
    else:
        infrastructure = active.get("infrastructure")
        if (
            not infrastructure
            or active["failures"]
            or active["nomination"]
            or key["sha"] != active["key"]["sha"]
            or started <= timestamp(infrastructure["time"])
        ):
            return None
        token_data["infrastructure"] = infrastructure
    return {**token_data, "token": sha256(encode(token_data).encode()).hexdigest()}


def _reconcile(
    store, db, version, observation, repair, actor=None, token=None, *, evidence_ok=True
):
    outcome = store._observe(db, observation) if observation else "unavailable"
    state = store._load(db)
    active = state["incident"]
    if not active or not active["active"] or active["version"] != version:
        return None
    prior = active["recovery"]
    checked = (
        proposed_recovery(store, state, version, observation, repair)
        if outcome == "green" and evidence_ok
        else None
    )
    active["recovery"] = checked
    result = checked["token"] if checked and actor is None else None
    if actor and checked and prior == checked and checked["token"] == token:
        active["active"] = False
        active["acknowledgment"] = {
            "operator": actor,
            "time": datetime.now(timezone.utc).isoformat(),
            **checked,
        }
        db.execute(
            "CREATE TABLE IF NOT EXISTS acknowledgments (version INTEGER PRIMARY KEY, body TEXT NOT NULL)"
        )
        db.execute(
            "INSERT INTO acknowledgments VALUES (?,?)",
            (version, encode(active["acknowledgment"])),
        )
        result = token
    store._save(db, state)
    return result


def reconcile(store, version, observation, *, repair=None):
    require(
        store.provenance == "shadow", "supplied recovery observations require shadow"
    )
    with store.transaction() as db:
        return _reconcile(store, db, version, observation, repair)


def acknowledge(store, version, actor, token, observation, *, repair=None):
    operator(actor)
    require(
        store.provenance == "shadow", "supplied recovery observations require shadow"
    )
    with store.transaction() as db:
        return _reconcile(store, db, version, observation, repair, actor, token)


def live_reconcile(store, version, evidence, *, actor=None, token=None):
    """Read provider evidence within the same serialized transaction as the decision."""
    require(store.provenance == "live", "live recovery requires a live incident store")
    if actor:
        operator(actor)
    github = GitHub(intake.REPO)
    with store.transaction() as db:
        observation = repair = None
        problem = None
        if evidence:
            try:
                repair = verify_repair(github, *evidence)
            except (ValueError, KeyError, TypeError, OSError) as exc:
                problem = str(exc)
        try:
            observation = intake.observe(github)
        except (ValueError, KeyError, TypeError, OSError) as exc:
            problem = str(exc)
        result = _reconcile(
            store,
            db,
            version,
            observation,
            repair,
            actor,
            token,
            evidence_ok=problem is None,
        )
    return result, problem


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", required=True)
    commands = parser.add_subparsers(dest="command", required=True)
    infra = commands.add_parser("confirm-infrastructure")
    infra.add_argument("version", type=int)
    infra.add_argument("operator")
    infra.add_argument("reason")
    for command in ("check", "acknowledge"):
        action = commands.add_parser(command)
        action.add_argument("version", type=int)
        action.add_argument(
            "--repair-evidence",
            nargs=4,
            metavar=(
                "PLANNING_COMMIT",
                "RECEIPT_PATH",
                "RECEIPT_SHA256",
                "REVIEW_SHA256",
            ),
        )
        if command == "acknowledge":
            action.add_argument("operator")
            action.add_argument("token")
    args = parser.parse_args(argv)
    try:
        require(positive(args.version), "invalid incident version")
        store = Store(args.database, "live")
        if args.command == "confirm-infrastructure":
            confirm_infrastructure(
                store, args.version, args.operator, args.reason, live=True
            )
            result = {"status": "confirmed"}
        else:
            ack = args.command == "acknowledge"
            if ack:
                require(digest(args.token, 64), "invalid recovery token")
            result_token, problem = live_reconcile(
                store,
                args.version,
                args.repair_evidence,
                actor=args.operator if ack else None,
                token=args.token if ack else None,
            )
            result = {
                "status": ("acknowledged" if ack else "ready")
                if result_token
                else "held",
                "token": result_token,
                "problem": problem,
            }
    except (ValueError, TypeError, KeyError, OSError, sqlite3.Error) as exc:
        print(f"advisory recovery: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] != "held" else 2


if __name__ == "__main__":
    raise SystemExit(main())
