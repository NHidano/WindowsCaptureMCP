"""Tests for window module."""

import pytest

from windows_capture_mcp.window import (
    focus_window,
    list_windows,
    maximize_window,
    move_window,
    resize_window,
)


class TestListWindows:
    """Tests for list_windows function."""

    def test_returns_non_empty_list(self):
        windows = list_windows()
        assert isinstance(windows, list)
        assert len(windows) > 0

    def test_each_window_has_required_keys(self):
        windows = list_windows()
        required_keys = {"hwnd", "title", "process_name", "x", "y", "width", "height"}
        for window in windows:
            assert required_keys.issubset(window.keys()), (
                f"Missing keys: {required_keys - window.keys()}"
            )

    def test_filter_partial_match(self):
        """Filter should match by partial, case-insensitive title."""
        all_windows = list_windows()
        assert len(all_windows) > 0
        # Use a substring of the first window's title for filtering
        sample_title = all_windows[0]["title"]
        # Take the first 3 characters as filter substring
        substring = sample_title[:3]
        filtered = list_windows(filter=substring)
        assert len(filtered) > 0
        for w in filtered:
            assert substring.lower() in w["title"].lower()

    def test_include_hidden_increases_results(self):
        visible = list_windows(include_hidden=False)
        with_hidden = list_windows(include_hidden=True)
        assert len(with_hidden) >= len(visible)


class TestFocusWindow:
    """Tests for focus_window function."""

    def test_invalid_hwnd_raises_error(self):
        with pytest.raises(ValueError, match="Invalid window handle"):
            focus_window(0)


class TestMaximizeWindow:
    """Tests for maximize_window function."""

    def test_invalid_hwnd_raises_error(self):
        with pytest.raises(ValueError, match="Invalid window handle"):
            maximize_window(0)


class TestResizeWindow:
    """Tests for resize_window function."""

    def test_invalid_hwnd_raises_error(self):
        with pytest.raises(ValueError, match="Invalid window handle"):
            resize_window(0, 800, 600)


class TestMoveWindow:
    """Tests for move_window function."""

    def test_invalid_hwnd_raises_error(self):
        with pytest.raises(ValueError, match="Invalid window handle"):
            move_window(0, 100, 100)
