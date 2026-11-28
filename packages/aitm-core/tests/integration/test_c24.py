"""Exercise the real Git apply contract for portable binary-exact text replay."""

from aitm_core.reviews.portable import reconstruct_bundle
from tests.unit.test_c24 import BASE, FINAL, write_bundle


def test_portable_reconstruction(tmp_path, monkeypatch):
    root = write_bundle(tmp_path / "bundle")
    foreign = tmp_path / "foreign"
    foreign.mkdir()
    monkeypatch.setenv("GIT_DIR", str(foreign))
    monkeypatch.setenv("GIT_WORK_TREE", str(foreign))
    before = {path.name: path.read_bytes() for path in root.iterdir()}

    result = reconstruct_bundle(root)

    assert result.base_bytes == BASE
    assert result.final_bytes == FINAL
    assert [(turn.input_bytes, turn.output_bytes) for turn in result.rounds] == [
        (BASE, FINAL),
        (FINAL, FINAL),
    ]
    assert {path.name: path.read_bytes() for path in root.iterdir()} == before
    assert not list(foreign.iterdir())
