"""Cover literal pre-push routing and stable ignore proposals in isolation."""

import pytest

from aitm_core.setup.hooks import ignore_proposal, push_updates

TARGET = "refs/heads/team/records"


@pytest.mark.parametrize(
    ("original", "expected"),
    [
        (b"", b"/.aitm/\n"),
        (b"keep", b"keep\n/.aitm/\n"),
        (b"keep\n", b"keep\n/.aitm/\n"),
        (b"keep\r\n", b"keep\r\n/.aitm/\r\n"),
        (b".aitm/\n", b".aitm/\n/.aitm/\n"),
        (b"keep\n/.aitm/\n", b"keep\n/.aitm/\n"),
        (b"# /.aitm/\n", b"# /.aitm/\n/.aitm/\n"),
    ],
)
def test_ignore_proposal(original, expected):
    assert ignore_proposal(original) == expected
    assert ignore_proposal(expected) == expected


@pytest.mark.parametrize("length", [40, 64])
def test_updates_use_actual_object_format(length):
    first, second = "a" * length, "b" * length
    records = (
        f"local {first} {TARGET} {second}\nlocal {second} {TARGET}-review {first}\n"
    )
    assert push_updates(records.encode(), TARGET, length) == ((first, second),)


@pytest.mark.parametrize(
    "row",
    [
        b"one two three",
        b"one two three four five",
        f"local invalid {TARGET} {'0' * 40}".encode(),
        f"local {'0' * 40} {TARGET} {'B' * 40}".encode(),
        f"local {'a' * 39} {TARGET} {'0' * 40}".encode(),
    ],
)
def test_malformed_planning_updates_fail_closed(row):
    with pytest.raises(ValueError, match="pre-push"):
        push_updates(row, TARGET, 40)
