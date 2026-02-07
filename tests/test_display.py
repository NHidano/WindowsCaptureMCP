"""Tests for display module."""

import pytest

from windows_capture_mcp.display import get_display_rect, get_displays

REQUIRED_KEYS = {
    "display_number",
    "name",
    "width",
    "height",
    "x",
    "y",
    "scale_factor",
    "is_primary",
}


def test_get_displays_returns_non_empty_list():
    displays = get_displays()
    assert isinstance(displays, list)
    assert len(displays) > 0


def test_get_displays_contains_required_keys():
    displays = get_displays()
    for display in displays:
        assert REQUIRED_KEYS.issubset(display.keys()), (
            f"Missing keys: {REQUIRED_KEYS - display.keys()}"
        )


def test_get_displays_primary_exists():
    displays = get_displays()
    primary_displays = [d for d in displays if d["is_primary"]]
    assert len(primary_displays) == 1


def test_get_displays_display_numbers_start_at_one():
    displays = get_displays()
    numbers = [d["display_number"] for d in displays]
    assert numbers == list(range(1, len(displays) + 1))


def test_get_displays_positive_dimensions():
    displays = get_displays()
    for display in displays:
        assert display["width"] > 0
        assert display["height"] > 0


def test_get_display_rect_returns_tuple():
    rect = get_display_rect(1)
    assert isinstance(rect, tuple)
    assert len(rect) == 4


def test_get_display_rect_values():
    rect = get_display_rect(1)
    x, y, width, height = rect
    assert isinstance(x, int)
    assert isinstance(y, int)
    assert isinstance(width, int)
    assert isinstance(height, int)
    assert width > 0
    assert height > 0


def test_get_display_rect_invalid_number_raises_error():
    with pytest.raises(ValueError):
        get_display_rect(9999)
