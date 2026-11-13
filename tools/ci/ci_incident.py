"""Persist #277 advisory observations and expose a durable local warning."""

import argparse
import json
import os
import re
import sqlite3
import sys
from contextlib import contextmanager
from hashlib import sha256
from pathlib import Path
from tempfile import NamedTemporaryFile

import ci_advisory
from verify_pr import GitHub, Hold, digest, positive, require, timestamp

SCHEMA = 1
INITIAL = {"version": 0, "incident": None, "latest": None}
OWNER = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,79}")
LANE = re.compile(
    r"(python|quality|file-checks|collect-evidence):(failure|timed_out|action_required)"
)


def encode(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def order(key):
    return key["run_number"], key["attempt"]


def identity(decision, provenance):
    require(
        decision.get("schema") == "aitm.ci-advisory/v1"
        and decision.get("provenance") == provenance
        and decision.get("repository_id") == ci_advisory.REPOSITORY_ID
        and decision.get("workflow_id") == ci_advisory.WORKFLOW_ID
        and decision.get("target") == ci_advisory.TARGET,
        "decision identity or provenance disagrees with incident store",
    )
    status = decision.get("status")
    require(
        status in {"stale", "pending", "incomplete", "red", "green"}, "invalid status"
    )
    if status == "stale" or (status == "pending" and "run_id" not in decision):
        return None
    key = {
        name: decision.get(name) for name in ("run_number", "attempt", "run_id", "sha")
    }
    require(
        all(positive(key[name]) for name in ("run_number", "attempt", "run_id"))
        and digest(key["sha"])
        and type(decision.get("current_verified")) is bool,
        "invalid advisory attempt",
    )
    timestamp(decision["started_at"])
    failures = decision["failures"]
    require(
        isinstance(failures, list)
        and all(isinstance(item, str) and LANE.fullmatch(item) for item in failures)
        and (status != "red" or failures)
        and (status != "green" or decision["current_verified"] and not failures),
        "invalid advisory failures or freshness",
    )
    return key


def filename(key):
    return f"trunk-{key['run_id']}-a{key['attempt']}.md"


def warning(key, failures, provenance):
    detail = ", ".join(failures) if failures else "Required CI evidence is incomplete."
    return (
        f"# Trunk CI warning ({provenance})\n\n"
        f"Run {key['run_id']}, attempt {key['attempt']}, commit `{key['sha']}`.\n\n"
        f"{detail}\n\n"
        "Pause ordinary trunk work and nominate one repair owner. "
        "Continue through the existing #103 merge gate.\n"
    ).encode()


class DirectorySink:
    """Publish one warning per attempt and acknowledge the persisted content."""

    def __init__(self, directory):
        self.directory = Path(directory)

    def __call__(self, name, content):
        self.directory.mkdir(mode=0o700, parents=True, exist_ok=True)
        target = self.directory / name
        require(
            isinstance(name, str)
            and re.fullmatch(r"trunk-[1-9][0-9]*-a[1-9][0-9]*\.md", name),
            "invalid warning filename",
        )
        if (
            target.is_symlink()
            or not target.is_file()
            or target.read_bytes() != content
        ):
            with NamedTemporaryFile(
                dir=self.directory, prefix=".warning-", delete=False
            ) as stream:
                pending = Path(stream.name)
                try:
                    stream.write(content)
                    stream.flush()
                    os.fsync(stream.fileno())
                    os.replace(pending, target)
                finally:
                    pending.unlink(missing_ok=True)
        fd = os.open(self.directory, os.O_RDONLY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
        return sha256(target.read_bytes()).hexdigest()


class Store:
    def __init__(self, database, provenance):
        require(provenance in {"live", "shadow"}, "invalid incident provenance")
        self.database = Path(database)
        self.provenance = provenance
        with self.transaction() as db:
            db.execute(
                "CREATE TABLE IF NOT EXISTS state "
                "(singleton INTEGER PRIMARY KEY CHECK(singleton=1), "
                "schema INTEGER NOT NULL, provenance TEXT NOT NULL, body TEXT NOT NULL)"
            )
            db.execute(
                "INSERT OR IGNORE INTO state VALUES (1,?,?,?)",
                (SCHEMA, provenance, encode(INITIAL)),
            )
            require(
                db.execute("SELECT schema, provenance FROM state").fetchone()
                == (SCHEMA, provenance),
                "incident database schema or provenance disagrees",
            )
            db.execute(
                "CREATE TABLE IF NOT EXISTS attempts "
                "(run_number INTEGER, attempt INTEGER, identity TEXT NOT NULL, "
                "body TEXT NOT NULL, PRIMARY KEY (run_number, attempt))"
            )
            db.execute(
                "CREATE TABLE IF NOT EXISTS warning "
                "(name TEXT PRIMARY KEY, body BLOB NOT NULL, delivered TEXT)"
            )

    @contextmanager
    def transaction(self):
        db = sqlite3.connect(self.database, timeout=15, isolation_level=None)
        try:
            db.execute("PRAGMA synchronous = FULL")
            db.execute("BEGIN IMMEDIATE")
            yield db
            db.commit()
        except BaseException:
            db.rollback()
            raise
        finally:
            db.close()

    @staticmethod
    def _load(db):
        return json.loads(db.execute("SELECT body FROM state").fetchone()[0])

    @staticmethod
    def _save(db, state):
        db.execute("UPDATE state SET body = ? WHERE singleton=1", (encode(state),))

    def status(self):
        with self.transaction() as db:
            state = self._load(db)
            state["warnings"] = [
                {
                    "name": name,
                    "desired": sha256(body).hexdigest(),
                    "delivered": delivered,
                }
                for name, body, delivered in db.execute(
                    "SELECT name, body, delivered FROM warning ORDER BY name"
                )
            ]
            return state

    def observe(self, decision):
        key = identity(decision, self.provenance)
        if key is None:
            return decision["status"]
        with self.transaction() as db:
            state = self._load(db)
            latest = state["latest"]
            previous = db.execute(
                "SELECT identity, body FROM attempts WHERE run_number=? AND attempt=?",
                order(key),
            ).fetchone()
            if previous:
                require(json.loads(previous[0]) == key, "attempt identity collision")
            if latest and order(key) < order(latest["key"]):
                return "stale"
            if latest and key["run_number"] == latest["key"]["run_number"]:
                require(
                    all(key[name] == latest["key"][name] for name in ("sha", "run_id")),
                    "run identity collision",
                )
            failures = set(decision["failures"])
            if previous:
                failures.update(json.loads(previous[1])["failures"])
            record = {**decision, "failures": sorted(failures)}
            db.execute(
                "INSERT INTO attempts VALUES (?,?,?,?) ON CONFLICT(run_number,attempt) "
                "DO UPDATE SET body=excluded.body",
                (*order(key), encode(key), encode(record)),
            )
            if not decision["current_verified"]:
                return "unverified"
            status = "red" if failures else decision["status"]
            return self._apply(db, state, key, status, record)

    def _apply(self, db, state, key, status, record):
        latest = state["latest"]
        active = state["incident"]
        same_attempt = latest is not None and latest["key"] == key
        if same_attempt and status == "pending":
            return "duplicate" if latest["status"] == "pending" else "stale"
        state["latest"] = {
            "key": key,
            "status": status,
            "started_at": record["started_at"],
        }
        if status in {"red", "incomplete"}:
            failures = sorted(
                set(record["failures"]) | set(active["failures"] if active else [])
            )
            current_failure = active and active["key"] == key
            if (
                current_failure
                and failures == active["failures"]
                and status == active["status"]
            ):
                self._save(db, state)
                return "duplicate"
            state["version"] += 1
            state["incident"] = {
                "active": True,
                "key": key,
                "status": status,
                "started_at": record["started_at"],
                "version": state["version"],
                "failures": failures,
                "nomination": None,
                "recovery": None,
            }
            content = warning(key, failures, self.provenance)
            db.execute(
                "INSERT INTO warning VALUES (?,?,NULL) ON CONFLICT(name) "
                "DO UPDATE SET body=excluded.body",
                (filename(key), content),
            )
            result = "updated" if current_failure else "warning"
        else:
            if active and (
                status == "pending" or active["recovery"] and not same_attempt
            ):
                state["version"] += 1
                active.update(
                    version=state["version"],
                    nomination=None if status == "pending" else active["nomination"],
                    recovery=None,
                )
            result = status
        self._save(db, state)
        return result

    def nominate(self, version, owner, pr=None):
        require(
            positive(version) and isinstance(owner, str) and OWNER.fullmatch(owner),
            "invalid incident version or repair owner",
        )
        require(pr is None or positive(pr), "invalid repair PR")
        with self.transaction() as db:
            state = self._load(db)
            active = state["incident"]
            require(
                active
                and active["active"]
                and active["version"] == version
                and state["latest"]["status"] != "pending",
                "active incident version changed or awaits completion",
            )
            nomination = {"owner": owner, "pr": pr}
            existing = active["nomination"]
            if existing == nomination:
                return
            require(
                existing is None
                or existing["owner"] == owner
                and existing["pr"] is None,
                "incident already has a repair nomination",
            )
            active["nomination"] = nomination
            self._save(db, state)

    def deliver(self, sink):
        delivered = 0
        while True:
            with self.transaction() as db:
                row = db.execute(
                    "SELECT name, body, delivered FROM warning ORDER BY name"
                ).fetchall()
                pending = next(
                    (
                        (name, body, sha256(body).hexdigest())
                        for name, body, receipt in row
                        if receipt != sha256(body).hexdigest()
                    ),
                    None,
                )
                if pending is None:
                    return delivered
                name, body, desired = pending
                require(
                    sink(name, body) == desired,
                    "operator warning receipt digest disagrees",
                )
                db.execute(
                    "UPDATE warning SET delivered=? WHERE name=?", (desired, name)
                )
            delivered += 1


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", required=True, type=Path)
    parser.add_argument("--shadow", action="store_true")
    commands = parser.add_subparsers(dest="command", required=True)
    observe = commands.add_parser("observe")
    observe.add_argument("--replay", type=Path)
    commands.add_parser("status")
    flush = commands.add_parser("deliver")
    flush.add_argument("directory", type=Path)
    nominate = commands.add_parser("nominate")
    nominate.add_argument("version", type=int)
    nominate.add_argument("owner")
    nominate.add_argument("--pr", type=int)
    args = parser.parse_args(argv)
    if args.command == "observe" and args.shadow != bool(args.replay):
        parser.error(
            "shadow observations require --replay and live observations use GitHub"
        )
    try:
        store = Store(args.database, "shadow" if args.shadow else "live")
        if args.command == "observe":
            decision = (
                ci_advisory.decode_json(args.replay.read_bytes())
                if args.shadow
                else ci_advisory.observe(GitHub(ci_advisory.REPO))
            )
            result = {"decision": store.observe(decision)}
        elif args.command == "nominate":
            store.nominate(args.version, args.owner, args.pr)
            result = store.status()
        elif args.command == "deliver":
            result = {"delivered": store.deliver(DirectorySink(args.directory))}
        else:
            result = store.status()
    except (Hold, ValueError, OSError, sqlite3.Error) as exc:
        print(f"advisory incident: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
