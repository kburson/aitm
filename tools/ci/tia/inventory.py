"""Project a complete pytest collection into execution obligations."""

import json
import math
import re
from dataclasses import dataclass
from hashlib import sha256

Inventory = bytes

_PRODUCT_TARGET = "packages/aitm-usage/tests/"
_CLI = "tools/ci/tests/test_cli_evidence.py::test_usage_console_help"
_WORKLOAD_PROFILES = {
    "full": {"product-cli", "ci-helpers"},
    "compare-product-base": {"product-base"},
    "compare-product-cli": {"product-cli"},
    "compare-ci-helpers": {"ci-helpers"},
}
_REFERENCE_ROLES = {
    "ci103_historical_replay": {
        "pr_base": "product-base",
        "pr_candidate": "product-cli",
        "trunk_push": "product-cli",
    },
    "ci103_current_replay": {"trunk_push": "product-cli"},
    "local_collect_only": {"helper_collection": "ci-helpers"},
}
_SUITES = {"unit", "integration", "system"}
_SCOPE_IDENTITY = (
    "profile",
    "platform_scope",
    "runner",
    "capabilities",
    "observer",
    "controls",
    "receipt_sha256",
)


@dataclass(frozen=True)
class SuitePolicy:
    """Reviewed policy bytes and the workload selected independently of collection."""

    suites: bytes
    ci103: bytes
    workload: str


@dataclass(frozen=True)
class _Rules:
    workloads: dict
    profiles: dict
    runners: dict
    modules: dict
    overrides: dict
    mandatory: dict
    optional_skips: dict


def _require(condition, error):
    if not condition:
        raise ValueError(error)


def _canonical(value):
    return json.dumps(
        value,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        _require(key not in result, "malformed input: duplicate JSON key")
        result[key] = value
    return result


def _finite(number):
    value = float(number)
    _require(math.isfinite(value), "malformed input: non-finite JSON number")
    return value


def _read(raw, schema):
    _require(isinstance(raw, bytes), "malformed input: expected UTF-8 JSON bytes")
    try:
        document = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=_unique_object,
            parse_float=_finite,
            parse_constant=_finite,
        )
        # Reject escaped lone surrogates that cannot appear in canonical UTF-8.
        json.dumps(document, ensure_ascii=False).encode("utf-8")
    except (ValueError, RecursionError) as error:
        if str(error).startswith("malformed input:"):
            raise
        raise ValueError("malformed input: invalid UTF-8 JSON") from error
    _require(
        isinstance(document, dict) and document.get("schema") == schema,
        f"malformed input: expected {schema}",
    )
    return document


def _shape(value, fields, error, *, optional=()):
    _require(
        isinstance(value, dict) and fields <= value.keys() <= fields | set(optional),
        error,
    )


def _text(value):
    return isinstance(value, str) and bool(value.strip()) and "\0" not in value


def _names(values, error):
    _require(isinstance(values, list) and all(map(_text, values)), error)
    names = set(values)
    _require(len(names) == len(values), error)
    return names


def _digest(value, *lengths):
    return (
        isinstance(value, str)
        and len(value) in lengths
        and re.fullmatch(r"[0-9a-f]+", value) is not None
    )


def _path(value):
    return (
        _text(value)
        and "\\" not in value
        and re.match(r"^[A-Za-z]:", value) is None
        and all(
            part.lower() not in {"", ".", "..", ".git"} for part in value.split("/")
        )
        and all(ord(char) >= 32 and ord(char) != 127 for char in value)
    )


def _node(nodeid, error):
    _require(_text(nodeid), error)
    source, _, remainder = nodeid.partition("::")
    qualified, _, _ = remainder.partition("[")
    _require(
        _path(source) and all(_text(part) for part in qualified.split("::")), error
    )
    return source, source + "::" + qualified


def _targets_node(targets, source, nodeid):
    return (
        source in targets
        or nodeid in targets
        or any(target.endswith("/") and source.startswith(target) for target in targets)
    )


def _named_records(records, error):
    _require(isinstance(records, dict) and records and all(map(_text, records)), error)
    return records


def _profiles(records, ci103):
    helper_sources = _names(ci103["helpers"], "policy: invalid #103 helper sources")
    _require(
        helper_sources
        and all(re.fullmatch(r"tools/ci/[A-Za-z0-9_]+\.py", p) for p in helper_sources),
        "policy: invalid #103 helper sources",
    )
    helper_targets = {
        "tools/ci/tests/test_" + path.removeprefix("tools/ci/")
        for path in helper_sources
    }
    expected = {
        "product-base": ("aitm-usage", {_PRODUCT_TARGET}),
        "product-cli": ("aitm-usage", {_PRODUCT_TARGET, _CLI}),
        "ci-helpers": ("ci-tools", helper_targets),
    }
    _require(
        isinstance(records, dict) and records.keys() == expected.keys(),
        "policy: invalid profile names",
    )
    for name, row in records.items():
        error = "policy: invalid profile"
        _shape(row, {"owner", "targets", "required_capabilities"}, error)
        owner, targets = expected[name]
        _require(
            row["owner"] == owner and _names(row["targets"], error) == targets, error
        )
        _require(_names(row["required_capabilities"], error), error)
    return records


def _runners(records):
    error = "policy: invalid runner profile"
    for row in _named_records(records, error).values():
        _shape(
            row,
            {"platform_scope", "identity", "capabilities", "required_capabilities"},
            error,
        )
        identity = _named_records(row["identity"], error)
        required = _names(row["required_capabilities"], error)
        _require(
            _text(row["platform_scope"])
            and not identity.keys() & {"profile", "name"}
            and all(map(_text, identity.values()))
            and bool(required)
            and required <= _names(row["capabilities"], error),
            error,
        )
    return records


def _workloads(records, profiles, runners):
    error = "policy: invalid workload"
    _require(
        isinstance(records, dict) and records.keys() == _WORKLOAD_PROFILES.keys(), error
    )
    for name, row in records.items():
        _shape(row, {"scope_status", "required_pairs"}, error)
        status = "complete_workload" if name == "full" else "comparison_component"
        pairs = row["required_pairs"]
        _require(
            row["scope_status"] == status and isinstance(pairs, list) and pairs, error
        )
        seen = set()
        for pair in pairs:
            _require(
                isinstance(pair, list) and len(pair) == 2 and all(map(_text, pair)),
                error,
            )
            profile, scope = pair
            _require(
                profile in _WORKLOAD_PROFILES[name] and (profile, scope) not in seen,
                error,
            )
            required = set(profiles[profile]["required_capabilities"])
            _require(
                any(
                    runner["platform_scope"] == scope
                    and required <= set(runner["capabilities"])
                    for runner in runners.values()
                ),
                "policy: workload pair has no compatible runner",
            )
            seen.add((profile, scope))
        _require({profile for profile, _ in seen} == _WORKLOAD_PROFILES[name], error)
    return records


def _modules(records, profiles):
    error = "policy: invalid module rule"
    for source, row in _named_records(records, error).items():
        _shape(row, {"owner", "suite", "isolation_group"}, error)
        _require(
            _path(source)
            and source.endswith(".py")
            and isinstance(row["suite"], str)
            and row["suite"] in _SUITES
            and _text(row["isolation_group"])
            and any(
                row["owner"] == profile["owner"]
                and _targets_node(
                    [target.partition("::")[0] for target in profile["targets"]],
                    source,
                    source,
                )
                for profile in profiles.values()
            ),
            error,
        )
    targets = {*profiles["ci-helpers"]["targets"], _CLI.partition("::")[0]}
    _require(targets <= records.keys(), "policy: missing required target module rule")
    return records


def _overrides(records, modules, runners):
    error = "policy: invalid or overlapping override"
    _require(isinstance(records, list), error)
    available = {cap for runner in runners.values() for cap in runner["capabilities"]}
    result = {}
    for row in records:
        _shape(
            row,
            {"selector"},
            error,
            optional={
                "suite",
                "isolation_group",
                "required_capabilities",
                "mandatory",
                "required_children",
            },
        )
        source, selector = _node(row["selector"], error)
        _require(
            source in modules
            and selector == row["selector"]
            and selector not in result,
            error,
        )
        suite = row.get("suite", modules[source]["suite"])
        _require(
            len(row) > 1
            and isinstance(suite, str)
            and suite in _SUITES
            and _text(row.get("isolation_group", modules[source]["isolation_group"]))
            and ("mandatory" not in row or row["mandatory"] is True)
            and _names(row.get("required_capabilities", []), error) <= available,
            error,
        )
        _names(row.get("required_children", []), error)
        result[selector] = row
    return result


def _policy(suite_policy):
    suites = _read(suite_policy.suites, "aitm.tia-suite-policy/v1")
    _shape(
        suites,
        {"schema", "workloads", "profiles", "runners", "modules", "overrides"},
        "policy: invalid suite policy",
    )
    ci103 = _read(suite_policy.ci103, "aitm.ci-policy/v1")
    _require(
        {"helpers", "required_tests", "optional_skips", "required_children"}
        <= ci103.keys()
        and ci103.get("package") == "aitm-usage",
        "policy: invalid #103 policy",
    )
    profiles = _profiles(suites["profiles"], ci103)
    runners = _runners(suites["runners"])
    workloads = _workloads(suites["workloads"], profiles, runners)
    modules = _modules(suites["modules"], profiles)
    overrides = _overrides(suites["overrides"], modules, runners)

    error = "policy: invalid #103 obligation mapping"
    required = _names(ci103["required_tests"], error)
    labels = _names(ci103["required_children"], error)
    optional = ci103["optional_skips"]
    _require(
        required
        and labels
        and isinstance(optional, dict)
        and not required & optional.keys(),
        error,
    )
    for nodeid in required | optional.keys():
        source, _ = _node(nodeid, error)
        _require(
            source.startswith(_PRODUCT_TARGET)
            and source in modules
            and modules[source]["owner"] == "aitm-usage"
            and (nodeid not in optional or _text(optional[nodeid])),
            error,
        )

    mandatory = {
        "product-base": set(required),
        "product-cli": set(required),
        "ci-helpers": set(),
    }
    child_labels = set()
    for selector, row in overrides.items():
        source, _, _ = selector.partition("::")
        applicable = {
            name
            for name, profile in profiles.items()
            if modules[source]["owner"] == profile["owner"]
            and _targets_node(profile["targets"], source, selector)
        }
        _require(applicable, "policy: override has no applicable profile")
        if row.get("mandatory"):
            for name in applicable:
                mandatory[name].add(selector)
        for label in row.get("required_children", []):
            _require(
                label not in child_labels
                and "product-cli" in applicable
                and (row.get("mandatory") or selector in required),
                error,
            )
            child_labels.add(label)
    _require(
        _CLI in mandatory["product-cli"]
        and child_labels == labels
        and all(not nodes & optional.keys() for nodes in mandatory.values()),
        error,
    )
    return _Rules(workloads, profiles, runners, modules, overrides, mandatory, optional)


def _run_identity(record):
    return all(
        type(record[key]) is int and record[key] > 0
        for key in ("run_id", "run_attempt")
    )


def _binding(record):
    error = "malformed input: invalid collection binding"
    _shape(record, {"kind", "repository", "snapshot"}, error)
    repository = record["repository"]
    _require(
        _path(repository)
        and re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository) is not None,
        error,
    )
    snapshot = record["snapshot"]
    if record["kind"] == "local_advisory":
        _shape(snapshot, {"content_digest"}, error)
        _require(_digest(snapshot["content_digest"], 64), error)
    elif record["kind"] == "hosted_collection_proof":
        _shape(snapshot, {"commit", "tree", "ref", "run_id", "run_attempt"}, error)
        _require(
            _digest(snapshot["commit"], 40, 64)
            and _digest(snapshot["tree"], len(snapshot["commit"]))
            and _path(snapshot["ref"])
            and snapshot["ref"].startswith("refs/")
            and _run_identity(snapshot),
            error,
        )
    else:
        raise ValueError(error)


def _source_reference(reference, profile):
    error = "scope: invalid comparison source reference"
    _shape(
        reference,
        {"kind", "tree", "receipt_sha256"},
        error,
        optional={"run_id", "run_attempt", "role"},
    )
    kind = reference["kind"]
    _require(
        _text(kind)
        and kind in _REFERENCE_ROLES
        and _digest(reference["tree"], 40, 64)
        and _digest(reference["receipt_sha256"], 64),
        error,
    )
    roles = _REFERENCE_ROLES[kind]
    _require(profile in roles.values(), error)
    if "role" in reference:
        _require(
            _text(reference["role"]) and roles.get(reference["role"]) == profile, error
        )
    run_fields = {"run_id", "run_attempt"} & reference.keys()
    _require(not run_fields or len(run_fields) == 2 and _run_identity(reference), error)


def _scopes(scopes, binding, workload):
    _require(isinstance(scopes, list), "malformed input: expected scope array")
    result = {}
    for scope in scopes:
        _shape(
            scope,
            {
                *_SCOPE_IDENTITY,
                "binding",
                "exit_code",
                "complete",
                "deselected",
                "items",
            },
            "malformed input: invalid scope record",
            optional={"source_reference"},
        )
        pair = (scope["profile"], scope["platform_scope"])
        _require(
            all(map(_text, pair)) and pair not in result,
            "scope: invalid or repeated pair",
        )
        _binding(scope["binding"])
        _require(scope["binding"] == binding, "scope: component binding differs")
        if "source_reference" in scope:
            _require(
                workload["scope_status"] == "comparison_component"
                and binding["kind"] == "local_advisory",
                "scope: comparison source cannot qualify this component",
            )
            _source_reference(scope["source_reference"], scope["profile"])
        result[pair] = scope
    _require(
        result.keys() == {tuple(pair) for pair in workload["required_pairs"]},
        "scope: observed pairs differ from workload policy",
    )
    return result


def _scope_identity(scope, profile, runners):
    error = "capability: incompatible runner or missing scope capabilities"
    runner = _named_records(scope["runner"], error)
    _require(
        all(map(_text, runner.values())) and {"profile", "name"} <= runner.keys(), error
    )
    rule = runners.get(runner["profile"])
    capabilities = _names(scope["capabilities"], error)
    _require(
        rule is not None
        and rule["platform_scope"] == scope["platform_scope"]
        and all(runner.get(key) == value for key, value in rule["identity"].items())
        and set(rule["required_capabilities"]) | set(profile["required_capabilities"])
        <= capabilities
        <= set(rule["capabilities"]),
        error,
    )
    error = "malformed input: invalid scope provenance"
    controls = _named_records(scope["controls"], error)
    _require(
        _digest(scope["observer"], 64)
        and _digest(scope["receipt_sha256"], 64)
        and all(_digest(identity, 40, 64) for identity in controls.values()),
        error,
    )
    identity = {key: scope[key] for key in _SCOPE_IDENTITY}
    identity["capabilities"] = sorted(capabilities)
    if "source_reference" in scope:
        identity["source_reference"] = scope["source_reference"]
    return identity


def _obligations(scope, profile, capabilities, rules):
    _require(
        type(scope["exit_code"]) is int
        and scope["exit_code"] == 0
        and scope["complete"] is True
        and scope["deselected"] == []
        and isinstance(scope["items"], list)
        and bool(scope["items"]),
        "collection: unsuccessful, incomplete, empty or deselected",
    )
    name = scope["profile"]
    mandatory = rules.mandatory[name]
    observed = set()
    sources = set()
    for item in scope["items"]:
        _shape(
            item,
            {"nodeid", "disposition"},
            "collection: invalid item record",
            optional={"reason"},
        )
        nodeid = item["nodeid"]
        source, selector = _node(nodeid, "collection: invalid node ID")
        module = rules.modules.get(source)
        _require(
            module is not None
            and module["owner"] == profile["owner"]
            and _targets_node(profile["targets"], source, nodeid),
            "collection: unclassified or out-of-profile node ID",
        )
        _require(nodeid not in observed, "collection: duplicate node ID")
        observed.add(nodeid)
        sources.add(source)
        override = rules.overrides.get(selector, {})
        required = set(override.get("required_capabilities", []))
        _require(required <= capabilities, "capability: node requirements unavailable")
        optional = rules.optional_skips.get(nodeid)
        disposition = item["disposition"]
        _require(
            (disposition == "collected" and "reason" not in item)
            or (
                disposition == "allowed_skip"
                and optional is not None
                and item.get("reason") == optional
            ),
            "collection: unexpected skip, xfail or disposition",
        )
        yield {
            "provider": "pytest",
            "owner": module["owner"],
            "profile": name,
            "platform_scope": scope["platform_scope"],
            "nodeid": nodeid,
            "suite": override.get("suite", module["suite"]),
            "isolation_group": override.get(
                "isolation_group", module["isolation_group"]
            ),
            "required_capabilities": sorted(required),
            "mandatory": nodeid in mandatory,
            "optional_skip_reason": optional,
            "required_children": sorted(override.get("required_children", []))
            if name == "product-cli" and nodeid == selector
            else [],
            "disposition": disposition,
        }
    _require(mandatory <= observed, "collection: missing mandatory node ID")
    if name == "ci-helpers":
        _require(
            sources == set(profile["targets"]), "collection: missing helper target"
        )


def classify(collection: bytes, suite_policy: SuitePolicy) -> Inventory:
    """Classify a normalized collection supplied by a trusted caller.

    The projection preserves hosted proof identity without qualifying the proof.
    """
    _require(isinstance(suite_policy, SuitePolicy), "policy: expected SuitePolicy")
    rules = _policy(suite_policy)
    name = suite_policy.workload
    _require(_text(name) and name in rules.workloads, "policy: unknown workload")
    workload = rules.workloads[name]
    document = _read(collection, "aitm.tia-collection/v1")
    _shape(
        document, {"schema", "binding", "scopes"}, "malformed input: invalid collection"
    )
    binding = document["binding"]
    _binding(binding)
    scopes = _scopes(document["scopes"], binding, workload)
    identities = []
    obligations = {}
    for pair in sorted(scopes):
        scope = scopes[pair]
        profile = rules.profiles[scope["profile"]]
        identity = _scope_identity(scope, profile, rules.runners)
        identities.append(identity)
        for row in _obligations(scope, profile, set(identity["capabilities"]), rules):
            key = (row["provider"], row["owner"], row["platform_scope"], row["nodeid"])
            _require(key not in obligations, "collection: duplicate obligation")
            obligations[key] = row
    return _canonical(
        {
            "schema": "aitm.tia-inventory/v1",
            "binding": binding,
            "workload": name,
            "scope_status": workload["scope_status"],
            "suite_policy_sha256": sha256(suite_policy.suites).hexdigest(),
            "ci103_policy_sha256": sha256(suite_policy.ci103).hexdigest(),
            "scopes": identities,
            "obligations": [obligations[key] for key in sorted(obligations)],
        }
    )
