"""Pure path and handle rules for pre-story intake."""

from datetime import UTC, datetime

import pytest

from aitm_core.paths import intake_location, intake_slug


@pytest.mark.parametrize(
    ("title", "slug"),
    [
        ("  Basement & Kitchen!!  ", "basement-kitchen"),
        ("Café Déjà Vu", "cafe-deja-vu"),
        ("建物", "untitled"),
        ("a" * 39 + " b", "a" * 39),
        ("A_b-3", "a-b-3"),
        ("A" * 90, "a" * 40),
    ],
)
def test_slug_is_bounded_ascii(title, slug):
    assert intake_slug(title) == slug


def test_location_pins_month_and_minute_to_utc():
    with pytest.raises(ValueError, match="timezone"):
        intake_location(datetime(2026, 11, 27, 9, 4), "Budget")
    assert intake_location(datetime(2026, 11, 27, 9, 4, tzinfo=UTC), "Budget") == (
        "2026-11",
        "20261127-0904-budget",
    )


def test_candidate_checks_existing_directory_prefixes():
    from aitm_core.paths import vacant_path

    root = ".aitm/drafts/2026-11"
    occupied = {
        f"{root}/20261127-0904-budget/attachments/kept.txt",
        f"{root}/20261127-0904-budget-2/draft.md",
    }
    assert vacant_path(root, "20261127-0904-budget", "", occupied) == (
        f"{root}/20261127-0904-budget-3"
    )
