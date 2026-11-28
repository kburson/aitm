"""Replay C24 patches and check native input/output provenance on the real Git path."""

import json
from hashlib import sha1

from aitm_core.reviews.native import validate_bundle
from aitm_core.reviews.policy import ReviewPolicy
from aitm_core.reviews.topology import IdentityBinding, IdentityMapping, Participant
from tests.unit.test_c24 import ARTIFACT, BASE, FINAL, digest, write_bundle

REVIEW = "review-c58"
START = "a" * 40
REVISION = "b" * 40
FINALIZATION = "c" * 40
ACTORS = {
    "author": ("codex", "openai", "author-model", "sha256:" + "a" * 64),
    "reviewer": ("claude-code", "anthropic", "review-model", "sha256:" + "b" * 64),
}


def _blob(raw):
    return sha1(f"blob {len(raw)}\0".encode() + raw, usedforsecurity=False).hexdigest()


def _artifact(raw):
    return {"path": ARTIFACT, "blob": _blob(raw), "digest": digest(raw)}


def _inject(path, extra, body=""):
    head, footer = path.read_text().split("\n---\n", 1)
    path.write_text(
        head.replace("level: sar", "level: xpr")
        + "\n"
        + extra
        + "---\n"
        + (body or footer)
    )


def test_native_mapping(tmp_path):
    root = write_bundle(tmp_path / "bundle")
    native = root / "native"
    native.mkdir()
    manifest_path = native / f"{REVIEW}-review-manifest.md"
    turns = []
    claims = []
    latest = None
    for index in (1, 2):
        refs = {}
        for role in ("reviewer", "author"):
            host, provider, model, fingerprint = ACTORS[role]
            submit = f"2026-11-08T00:{index * 2 + (role == 'author'):02d}:15Z"
            if index == 1:
                claim = f"2026-11-08T00:{index * 2 + (role == 'author'):02d}:12Z"
                claims.append(
                    {
                        "claim_id": f"claim-{role}",
                        "role": role,
                        "host": host,
                        "session_fingerprint": fingerprint,
                        "claimed_at": claim,
                    }
                )
            extra = (
                f"artifact_base_commit: {START}\nsession_identity_kind: native-fingerprint\n"
                f"{role}_session: {fingerprint}\nsubmitted_at: {submit}\n"
                f"agent: {{host: {host}, provider: {provider}, model_id: {model}, effort: high}}\n"
            )
            body = (
                f"## Decision\n\n{'accepted' if index == 2 else 'revisions-requested'}\n"
                if role == "reviewer"
                else ""
            )
            if (index, role) != (2, "author"):
                raw = BASE if index == 1 else FINAL
                native_file = native / f"{REVIEW}-{role}-response-{index}.md"
                native_file.write_text(
                    f"<!-- protected-frontmatter -->\n\n---\nschema: ai-peer-review.response/v1\n"
                    f"review_id: {REVIEW}\nrole: {role}\nturn: {index}\ncommit_mode: normal\n"
                    f"authority_assurance: unavailable\nartifact_path: {ARTIFACT}\n"
                    f"artifact_commit: {START if index == 1 else REVISION}\nartifact_blob: {_blob(raw)}\n"
                    f"artifact_digest: {digest(raw)}\nagent: {{host: {host}, provider: {provider}, "
                    f"model_id: {model}, session_fingerprint: {fingerprint}}}\n"
                    "started_at: 2026-11-08T00:00:00Z\n"
                    f"submitted_at: {submit}\nfinding_ids: []\nanswered_finding_ids: []\n---\n{body}"
                )
                latest = native_file
                native_source = f"native/{native_file.name}"
                refs[f"{role}_response"] = {
                    "path": f".aitm/archive/{native_source}",
                    "digest": digest(native_file.read_bytes()),
                }
                extra += f"native_source: {native_source}\nnative_source_digest: {refs[f'{role}_response']['digest']}\n"
            _inject(root / f"{role}-response-{index}.md", extra, body)
        turns.append(
            {
                "turn": index,
                "decision": "accepted" if index == 2 else "revisions-requested",
                "finding_ids": [],
                "artifact": _artifact(FINAL) if index == 1 else None,
                "commit": REVISION if index == 1 else None,
                "author_response": None,
                **refs,
            }
        )
    manifest = {
        "schema": "ai-peer-review.manifest/v1",
        "review_id": REVIEW,
        "record_id": REVIEW,
        "status": "accepted",
        "commit_mode": "normal",
        "acceptance_basis": "reviewer-consensus",
        "authority_assurance": "unavailable",
        "artifact_path": ARTIFACT,
        "startup_commit": START,
        "final_commit": REVISION,
        "artifact_history": [
            {**_artifact(BASE), "turn": 0, "commit": START},
            {**_artifact(FINAL), "turn": 1, "commit": REVISION},
        ],
        "turns": turns,
        "claims": claims,
        "runtime": {
            "classification": "XPR",
            **{
                role: dict(zip(("host", "provider", "model_id"), data[:3], strict=True))
                | {"effort": "high"}
                for role, data in ACTORS.items()
            },
        },
    }
    manifest_path.write_text(
        "# Review manifest\n\n```json\n" + json.dumps(manifest) + "\n```\n"
    )
    _inject(
        root / "review-manifest.md",
        (
            f"artifact_base_commit: {START}\nnative_review_id: {REVIEW}\nnative_status: accepted\n"
            f"native_revision_commit: {REVISION}\nnative_finalization_commit: {FINALIZATION}\n"
            "session_identity_kind: native-fingerprint\ncommit_mode: normal\nauthority_assurance: unavailable\n"
        ),
    )
    identities = IdentityMapping(
        "fixture public fingerprints",
        tuple(
            IdentityBinding(
                Participant("native-fingerprint", fingerprint, provider), role, provider
            )
            for role, (_, provider, _, fingerprint) in ACTORS.items()
        ),
    )
    policy = ReviewPolicy(("native-consensus-authority-unavailable",), identities)
    originals_before = {
        path: path.read_bytes() for path in root.rglob("*") if path.is_file()
    }

    result = validate_bundle(root, policy)
    assert result.record.final_bytes == FINAL
    facts = result.native
    assert facts.revision_commit == REVISION
    assert facts.finalization_commit == FINALIZATION
    assert facts.turns[0].anchor.basis == "claim"
    assert facts.turns[0].anchor.started_at == claims[0]["claimed_at"]
    assert facts.turns[-1].anchor.basis == "prior-submit"
    assert facts.turns[-1].source_digest == digest(latest.read_bytes())
    assert {path: path.read_bytes() for path in originals_before} == originals_before
