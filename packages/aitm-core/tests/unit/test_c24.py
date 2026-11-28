from hashlib import sha256

import pytest

from aitm_core.reviews import portable
from aitm_core.reviews.patches import validate_patch
from aitm_core.reviews.portable import ReviewError, reconstruct_bundle

ARTIFACT = ".aitm/design/fixture.md"
BASE = b"original\r\nkeep\r\n"
FINAL = b"reviewed\r\nkeep"
CREATE = (
    f"diff --git a/{ARTIFACT} b/{ARTIFACT}\n"
    f"new file mode 100644\n--- /dev/null\n+++ b/{ARTIFACT}\n@@ -0,0 +1,2 @@\n"
).encode() + b"+original\r\n+keep\r\n"
EDIT = (
    f"diff --git a/{ARTIFACT} b/{ARTIFACT}\n"
    f"--- a/{ARTIFACT}\n+++ b/{ARTIFACT}\n@@ -1,2 +1,2 @@\n"
).encode() + b"-original\r\n-keep\r\n+reviewed\r\n+keep\n\\ No newline at end of file\n"


def digest(data):
    return "sha256:" + sha256(data).hexdigest()


def write_bundle(root):
    root.mkdir()
    identity = f"level: sar\nstory: 2\nartifact_path: {ARTIFACT}\n"
    manifest = (
        f"---\nschema: aitm.review-manifest/v0\n{identity}"
        f"base_digest: {digest(BASE)}\nfinal_digest: {digest(FINAL)}\n"
        "rounds: 2\noutcome: exhausted\n---\nBody\r\n"
    )
    (root / "review-manifest.md").write_bytes(manifest.encode())
    for round_number, before, after in [(1, BASE, FINAL), (2, FINAL, FINAL)]:
        for role, version in (("reviewer", before), ("author", after)):
            patch = (
                f"patch: patch-{round_number:03d}.diff\n" if role == "author" else ""
            )
            response = (
                f"---\nschema: aitm.review-response/v0\n{identity}"
                f"role: {role}\nround: {round_number}\nartifact_digest: {digest(version)}\n"
                f"{patch}finding_ids: []\nanswered_finding_ids: []\n---\nResponse\n"
            )
            (root / f"{role}-response-{round_number}.md").write_bytes(response.encode())
    for index, patch in enumerate((CREATE, EDIT, b"")):
        (root / f"patch-{index:03d}.diff").write_bytes(patch)
    return root


@pytest.fixture
def bundle(tmp_path, monkeypatch):
    root = write_bundle(tmp_path / "bundle")

    def apply(work, artifact, patch):
        target = work / artifact
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes({CREATE: BASE, EDIT: FINAL}[patch])

    monkeypatch.setattr(portable, "apply_patch", apply)
    return root


def test_reconstructs_and_retains_original_bytes(bundle):
    before = {path.name: path.read_bytes() for path in bundle.iterdir()}
    result = reconstruct_bundle(bundle)
    assert result.base_bytes == BASE
    assert result.final_bytes == FINAL
    assert [(turn.input_bytes, turn.output_bytes) for turn in result.rounds] == [
        (BASE, FINAL),
        (FINAL, FINAL),
    ]
    assert {item.name: item.raw for item in result.originals} == before
    assert all(item.raw_digest == digest(item.raw) for item in result.originals)
    assert {path.name: path.read_bytes() for path in bundle.iterdir()} == before


@pytest.mark.parametrize(
    ("name", "original", "replacement", "error"),
    [
        ("review-manifest.md", "manifest/v0", "manifest/v1", "manifest"),
        ("review-manifest.md", "story: 2", "story: '2'", "manifest"),
        ("review-manifest.md", "story: 2", "story: 2\nstory: 2", "manifest"),
        ("review-manifest.md", "rounds: 2", "rounds: 0", "manifest"),
        ("review-manifest.md", ARTIFACT, "../outside.md", "manifest"),
        ("review-manifest.md", ARTIFACT, "/outside.md", "manifest"),
        ("review-manifest.md", digest(BASE), digest(FINAL), "base digest"),
        (
            "review-manifest.md",
            f"final_digest: {digest(FINAL)}",
            f"final_digest: {digest(BASE)}",
            "final digest",
        ),
        ("reviewer-response-1.md", "response/v0", "response/v1", "response"),
        ("reviewer-response-1.md", "role: reviewer", "role: author", "identity"),
        ("reviewer-response-1.md", "story: 2", "story: 3", "identity"),
        ("reviewer-response-2.md", "round: 2", "round: 1", "identity"),
        (
            "reviewer-response-2.md",
            digest(FINAL),
            digest(BASE),
            "reviewer input digest",
        ),
        ("author-response-1.md", digest(FINAL), digest(BASE), "author output digest"),
        ("author-response-1.md", "patch-001.diff", "../patch-001.diff", "patch"),
    ],
)
def test_rejects_invalid_evidence(bundle, name, original, replacement, error):
    source = bundle / name
    source.write_bytes(
        source.read_bytes().replace(original.encode(), replacement.encode())
    )
    with pytest.raises(ReviewError, match=error):
        reconstruct_bundle(bundle)


@pytest.mark.parametrize("name", ["patch-002.diff", "author-response-2.md"])
def test_requires_originals(bundle, name):
    (bundle / name).unlink()
    with pytest.raises(ReviewError, match=name):
        reconstruct_bundle(bundle)


def test_refuses_symlink_without_reading_target(bundle, tmp_path):
    link = bundle / "patch-000.diff"
    outside = tmp_path / "outside"
    link.rename(outside)
    link.symlink_to(outside)
    with pytest.raises(ReviewError, match="patch-000"):
        reconstruct_bundle(bundle)
    assert outside.read_bytes() == CREATE


def test_refuses_executable_original(bundle):
    patch = bundle / "patch-000.diff"
    patch.chmod(0o755)
    with pytest.raises(ReviewError, match="regular nonexecutable"):
        reconstruct_bundle(bundle)


@pytest.mark.parametrize(
    ("patch", "create"),
    [
        (CREATE.replace(b"100644", b"100755"), True),
        (CREATE.replace(b"100644", b"120000"), True),
        (CREATE.replace(ARTIFACT.encode(), b"../escape.md"), True),
        (CREATE.replace(b"+++ b/" + ARTIFACT.encode(), b"+++ b/other.md"), True),
        (CREATE + EDIT, True),
        (EDIT.replace(b"--- a/", b"rename from elsewhere\n--- a/"), False),
        (EDIT.replace(b"@@ -1,2", b"@@ -1,1"), False),
    ],
)
def test_refuses_patch_outside_single_regular_text_edit(patch, create):
    with pytest.raises(ValueError):
        validate_patch(patch, ARTIFACT, create=create)


def test_empty_base_patch_is_invalid(bundle):
    (bundle / "patch-000.diff").write_bytes(b"")
    with pytest.raises(ReviewError, match="patch-000"):
        reconstruct_bundle(bundle)


@pytest.mark.parametrize("name", ["patch-003.diff", "reviewer-response-3.md"])
def test_refuses_undeclared_round_artifacts(bundle, name):
    (bundle / name).write_bytes(b"")
    with pytest.raises(ReviewError, match="undeclared"):
        reconstruct_bundle(bundle)


def test_refuses_a_symlink_as_bundle_root(bundle, tmp_path):
    alias = tmp_path / "alias"
    alias.symlink_to(bundle, target_is_directory=True)
    with pytest.raises(ReviewError, match="review directory"):
        reconstruct_bundle(f"{alias}/")
