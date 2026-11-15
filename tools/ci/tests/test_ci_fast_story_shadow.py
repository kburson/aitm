import pytest
from ci_fast_story_shadow import classify_diff, phase_evidence, reviewed_tuple
from verify_pr import Hold

BASE = "1" * 40
HEAD = "2" * 40
TESTED = "3" * 40
TREE = "4" * 40


def change(status, path, old="100644", new="100644"):
    return f":{old} {new} {BASE} {HEAD} {status}\0{path}\0".encode()


def test_fast_path_only_accepts_regular_markdown_edits_and_additions():
    assert classify_diff(change("M", "docs/ci.md")) == ("docs/ci.md",)
    assert classify_diff(change("A", "docs/guide/quick-start.md", "000000")) == (
        "docs/guide/quick-start.md",
    )
    for raw in (
        b"",
        change("M", "README.md"),
        change("M", "docs/a.md", new="120000"),
        change("M", "docs/run.py"),
        change("M", "packages/aitm-usage/tests/test_service.py"),
        change("D", "docs/ci.md", new="000000"),
        change("M", "docs/../README.md"),
        b"truncated\0",
    ):
        assert classify_diff(raw) == ()


def test_review_binds_all_exact_git_identities_and_digest():
    import hashlib

    review = f"**Verdict: ACCEPTED.** {BASE} {HEAD} {TESTED} {TREE} [PR](https://github.com/kburson/aitm/pull/5)".encode()
    admission = {
        "schema": "aitm.fast-story-admission/v1",
        "pr": 5,
        "base": BASE,
        "head": HEAD,
        "tested": TESTED,
        "tree": TREE,
        "review_sha256": hashlib.sha256(review).hexdigest(),
    }
    assert reviewed_tuple(admission, review)["pr"] == 5
    with pytest.raises(Hold, match="review"):
        reviewed_tuple(admission, review + b"tampered")
    with pytest.raises(Hold, match="review"):
        reviewed_tuple({**admission, "head": "5" * 40}, review)
    with pytest.raises(Hold, match="review"):
        reviewed_tuple({**admission, "pr": 6}, review)
    with pytest.raises(Hold, match="admission"):
        reviewed_tuple({**admission, "pr": True}, review)


def test_exact_outcomes_require_all_phases_and_required_children():
    node = "x.py::test_x"
    document = {
        "collected": [node],
        "schema": "aitm.pytest-evidence/v1",
        "deselected": [],
        "exit_code": 0,
        "reports": [
            {"nodeid": node, "when": phase, "outcome": "passed", "wasxfail": False}
            for phase in ("setup", "call", "teardown")
        ],
        "children": [{"label": "cli-help", "pid": 123, "returncode": 0}],
    }
    assert phase_evidence(document, [node], ["cli-help"]) == {node: "passed"}
    with pytest.raises(Hold, match="outcomes"):
        phase_evidence(
            {**document, "reports": document["reports"][1:]}, [node], ["cli-help"]
        )
    with pytest.raises(Hold, match="children"):
        phase_evidence({**document, "children": []}, [node], ["cli-help"])
    with pytest.raises(Hold, match="inventory"):
        phase_evidence(document, [node, "x.py::test_missing"], ["cli-help"])


def test_signature_must_bind_exact_manifest_and_designated_issuer(
    tmp_path, monkeypatch
):
    import subprocess

    import ci_fast_story_shadow as shadow

    key = tmp_path / "key"
    wrong = tmp_path / "wrong"
    for path in (key, wrong):
        subprocess.run(
            ["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-f", str(path)],
            check=True,
        )
    raw = b'{"review_sha256":"accepted fixture"}\n'
    manifest = tmp_path / "manifest"
    manifest.write_bytes(raw)
    subprocess.run(
        [
            "ssh-keygen",
            "-Y",
            "sign",
            "-f",
            str(key),
            "-n",
            "aitm-fast-story-admission",
            str(manifest),
        ],
        check=True,
        capture_output=True,
    )
    signature = manifest.with_suffix(".sig").read_bytes()
    monkeypatch.setattr(shadow, "SIGNER", key.with_suffix(".pub").read_text())
    shadow.verify_admission_signature(raw, signature)
    with pytest.raises(Hold, match="signature"):
        shadow.verify_admission_signature(raw + b" ", signature)
    monkeypatch.setattr(shadow, "SIGNER", wrong.with_suffix(".pub").read_text())
    with pytest.raises(Hold, match="signature"):
        shadow.verify_admission_signature(raw, signature)


def test_checkout_refuses_case_alias_or_wrong_content(tmp_path):
    from hashlib import sha1

    from ci_fast_story_shadow import verify_checkout

    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "Guide.md").write_bytes(b"old")
    good = sha1(b"blob 3\0old").hexdigest()
    wrong = sha1(b"blob 3\0new").hexdigest()
    verify_checkout(tmp_path, f"100644 blob {good}\tdocs/Guide.md\0".encode())
    with pytest.raises(Hold, match="archive"):
        verify_checkout(tmp_path, f"100644 blob {good}\tdocs/guide.md\0".encode())
    with pytest.raises(Hold, match="archive"):
        verify_checkout(tmp_path, f"100644 blob {wrong}\tdocs/Guide.md\0".encode())
