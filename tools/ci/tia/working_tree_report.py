"""Report pinned test obligations for an admitted uncommitted worktree change."""

import argparse
import json
import re
from hashlib import sha1, sha256
from pathlib import Path

from tools.ci import path_map

from .snapshot import LocalRequest, SnapshotUncertain, resolve

_SCHEMA = "aitm.tia-working-tree-report/v1"
_REPOSITORY = "kburson/aitm"
_ANCHOR_COMMIT = "8799c5a445dd4b51d499132e9a314b64796ae918"
_ANCHOR_TREE = "456a155fbe7d10cb7daafd2bf46f134be78366a8"
_FINDING_SHA256 = "887517ab530f9d135c07cab95a17ca01bb8dde344211c0247ec99da2b817621c"
_REVIEW_SHA256 = "7d0dfd66316178aebc0bcad72877cd73e7fc1d2bb4fe08756b142b3bb8abef8d"
_MAP_SHA256 = "a5403981cd9ae6a80eb3f7d8b6d09d34ada0374421bbbb3cc8af534793c272ae"
_SELECTOR_SHA256 = "39bbbe45018fec922a304ae8fcf50bc452f5f28e2c6acc19870adaa0319c03ed"
_INVENTORY_SHA256 = "812bc918dd9da7b413786454906d2ec8f486b5624bc8d1deecf9d546928d48e6"
_INVENTORY_PATH = Path(__file__).with_name("working_tree_obligations.json")
_INVENTORY_SOURCE = (
    "https://github.com/kburson/aitm/actions/runs/43882437964/attempts/2"
)
_PATH = b"packages/aitm-usage/src/aitm_usage/sources/grok_scope_hook.py"
_MODULE = "packages/aitm-usage/tests/test_grok_scope_receipts.py"
_REGULAR = {"100644", "100755"}
_TYPES = dict.fromkeys((*_REGULAR, "120000"), "blob") | {"160000": "commit"}
_DOC = b"docs/ci.md"
_DELIVERY_ADDITIONS = {
    b"tools/ci/tia/working_tree_report.py",
    b"tools/ci/tia/working_tree_obligations.json",
    b"tools/ci/tests/test_tia_working_tree_report.py",
}
_COMMENT_WHITESPACE = re.compile(rb"[ \t\n]*")
_COMMENT_LINE = re.compile(rb"#[\x20-\x7e\t]*")
_COMMIT = re.compile(r"[0-9a-f]{40}")


class _Unavailable(Exception):
    """The report has no admitted obligations for this snapshot."""


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        raise _Unavailable("invalid-arguments")


def _unavailable(reason):
    return {
        "schema": _SCHEMA,
        "mode": "unavailable",
        "reason": reason,
        "node_ids": [],
    }


def _modified(change, path):
    return (
        change.status == "M"
        and change.old is not None
        and change.new is not None
        and change.old.path == change.new.path == path
        and change.old.mode == change.new.mode
        and change.new.mode in _REGULAR
    )


def _delivery_tree(changes):
    additions = set()
    docs = 0
    for change in changes:
        if _modified(change, _DOC):
            docs += 1
        elif (
            change.status == "A"
            and change.old is None
            and change.new is not None
            and change.new.mode == "100644"
        ):
            additions.add(change.new.path)
        else:
            return False
    return (
        docs == 1
        and additions == _DELIVERY_ADDITIONS
        and len(changes) == len(_DELIVERY_ADDITIONS) + 1
    )


def _admitted_change(before, after, base_commit):
    provenance = after.provenance
    head = provenance.observation.head
    committed = provenance.committed_changes
    if (
        before.endpoint_identity.tree != _ANCHOR_TREE
        or head.commit != base_commit
        or (head.commit == _ANCHOR_COMMIT and committed)
        or (head.commit != _ANCHOR_COMMIT and not _delivery_tree(committed))
    ):
        raise _Unavailable("unqualified-base")
    local = provenance.staged_changes + provenance.unstaged_changes
    if not local:
        raise _Unavailable("no-local-change")
    if not all(_modified(change, _PATH) for change in local):
        raise _Unavailable("unsupported-change")

    delivery_paths = _DELIVERY_ADDITIONS | {_DOC} if committed else set()
    effective = [
        change
        for change in after.changes
        if (change.new or change.old).path not in delivery_paths
    ]
    if not effective:
        raise _Unavailable("no-local-change")
    if len(effective) != 1 or not _modified(effective[0], _PATH):
        raise _Unavailable("unsupported-change")
    return effective[0]


def _matches_comment_suffix(content, start):
    if not content.endswith(b"\n") or content.find(b"#", start) == -1:
        return False

    while True:
        start = _COMMENT_WHITESPACE.match(content, start).end()
        if start == len(content):
            return True
        end = content.find(b"\n", start)
        if not _COMMENT_LINE.fullmatch(content, start, end):
            return False
        start = end + 1


def _pinned_ids():
    try:
        raw = _INVENTORY_PATH.read_bytes()
        nodes = json.loads(raw)
    except (OSError, ValueError):
        raise _Unavailable("inventory-unavailable") from None
    if (
        sha256(raw).hexdigest() != _INVENTORY_SHA256
        or not isinstance(nodes, list)
        or len(nodes) != 30
        or not all(
            isinstance(node, str) and node.startswith(_MODULE + "::") for node in nodes
        )
        or len(set(nodes)) != len(nodes)
    ):
        raise _Unavailable("inventory-unavailable")
    return sorted(nodes)


def _consumer_reason(before, change, content):
    try:
        raw_map = before.read_content(path_map.MAP_PATH.encode("ascii"))
        selector = before.read_content(path_map.SELECTOR_PATH.encode("ascii"))
        if (
            sha256(raw_map).hexdigest() != _MAP_SHA256
            or sha256(selector).hexdigest() != _SELECTOR_SHA256
            or Path(path_map.__file__).read_bytes() != selector
        ):
            raise _Unavailable("selector-unavailable")
        entries = {
            entry.path.decode("utf-8"): {
                "mode": entry.mode,
                "type": _TYPES[entry.mode],
                "sha": entry.content_id,
            }
            for entry in before.entries
        }
        path = _PATH.decode("ascii")
        candidate = entries | {
            path: {
                "mode": change.new.mode,
                "type": "blob",
                "sha": sha1(
                    f"blob {len(content)}\0".encode("ascii") + content,
                    usedforsecurity=False,
                ).hexdigest(),
            }
        }
        result = path_map.select(
            [path], json.loads(raw_map), base=entries, candidate=candidate
        )
    except (KeyError, OSError, ValueError, SnapshotUncertain):
        raise _Unavailable("selector-unavailable") from None
    if result["mode"] != "mapped" or result["tests"] != [_MODULE]:
        raise _Unavailable("selector-unavailable")
    return result["paths"][0]["reason"]


def build_report(repo: Path, base_commit: str) -> dict:
    """Return the bounded report or a machine-readable unavailability reason."""
    if not _COMMIT.fullmatch(base_commit):
        return _unavailable("invalid-arguments")
    request = LocalRequest(_REPOSITORY, "local-effective", _ANCHOR_COMMIT)
    try:
        before, after = resolve(repo, request)
        change = _admitted_change(before, after, base_commit)
        prior = before.read_content(_PATH)
        current = after.read_content(_PATH)
        if (
            not prior.endswith(b"\n")
            or not current.startswith(prior)
            or not _matches_comment_suffix(current, len(prior))
        ):
            raise _Unavailable("unsupported-change")
        reason = _consumer_reason(before, change, current)
        nodes = _pinned_ids()
        identity = (before.digest, after.digest)
        try:
            refreshed = resolve(repo, request)
        except (SnapshotUncertain, OSError):
            raise _Unavailable("snapshot-drift") from None
        if tuple(snapshot.digest for snapshot in refreshed) != identity:
            raise _Unavailable("snapshot-drift")
    except _Unavailable as error:
        return _unavailable(str(error))
    except (SnapshotUncertain, OSError):
        return _unavailable("snapshot-unavailable")

    head = after.provenance.observation.head
    return {
        "schema": _SCHEMA,
        "mode": "pinned-mapped-obligations",
        "base_commit": head.commit,
        "base_tree": head.tree,
        "snapshot_sha256": after.digest,
        "path": _PATH.decode("ascii"),
        "file_mode": change.new.mode,
        "content_sha256": change.new.content_id,
        "consumer_reason": reason,
        "module": _MODULE,
        "inventory_sha256": _INVENTORY_SHA256,
        "inventory_source": _INVENTORY_SOURCE,
        "node_ids": nodes,
        "candidate_inventory": "unqualified",
        "impact_completeness": "unqualified",
        "authority": {
            "kind": "reviewed-pinned-obligations",
            "repository": _REPOSITORY,
            "anchor_commit": _ANCHOR_COMMIT,
            "anchor_tree": _ANCHOR_TREE,
            "path": _PATH.decode("ascii"),
            "module": _MODULE,
            "finding_sha256": _FINDING_SHA256,
            "review_sha256": _REVIEW_SHA256,
            "inventory_sha256": _INVENTORY_SHA256,
            "map_sha256": _MAP_SHA256,
            "selector_sha256": _SELECTOR_SHA256,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = _Parser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--repo", required=True, type=Path, metavar="CHECKOUT")
    parser.add_argument("--base", required=True, metavar="COMMIT")
    try:
        args = parser.parse_args(argv)
    except _Unavailable as error:
        result = _unavailable(str(error))
    else:
        result = build_report(args.repo, args.base)
    print(json.dumps(result, sort_keys=True))
    return 2 if result["mode"] == "unavailable" else 0


if __name__ == "__main__":
    raise SystemExit(main())
