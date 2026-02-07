"""T-028: MCP server integration tests.

These tests verify the MCP server tool functions by calling them directly.
This exercises the same code paths as calling through the MCP protocol,
including validation, error handling, and the full capture pipeline.
"""

import json

import pytest

from windows_capture_mcp.server import (
    capture_fullscreen,
    capture_window,
    focus_window,
    list_displays,
    list_windows,
    maximize_window,
    preview_fullscreen,
)


class TestListDisplays:
    """Scenario 1: list_displays returns display information."""

    def test_returns_non_empty_list(self):
        result = list_displays()
        displays = json.loads(result)
        assert len(displays) > 0

    def test_display_has_required_keys(self):
        result = list_displays()
        displays = json.loads(result)
        for d in displays:
            assert "display_number" in d
            assert "name" in d
            assert "width" in d
            assert "height" in d
            assert "x" in d
            assert "y" in d
            assert "scale_factor" in d
            assert "is_primary" in d


class TestListWindows:
    """Scenario 2: list_windows returns window information."""

    def test_returns_non_empty_list(self):
        result = list_windows()
        windows = json.loads(result)
        assert len(windows) > 0

    def test_window_has_required_keys(self):
        result = list_windows()
        windows = json.loads(result)
        for w in windows[:5]:
            assert "hwnd" in w
            assert "title" in w
            assert "process_name" in w
            assert "x" in w
            assert "y" in w
            assert "width" in w
            assert "height" in w


class TestListWindowsFilter:
    """Scenario 3: list_windows with filter narrows results."""

    def test_filter_returns_subset(self):
        all_result = list_windows()
        all_windows = json.loads(all_result)
        assert len(all_windows) > 0

        filter_text = all_windows[0]["title"][:5]
        filtered_result = list_windows(filter=filter_text)
        filtered_windows = json.loads(filtered_result)
        assert len(filtered_windows) >= 1
        assert len(filtered_windows) <= len(all_windows)


class TestCaptureFullscreen:
    """Scenario 4: capture_fullscreen returns an image."""

    def test_returns_image_content(self):
        result = capture_fullscreen(display_number=1, format="jpeg", quality=50)
        assert len(result) == 1
        content = result[0]
        assert content.type == "image"
        assert content.mimeType == "image/jpeg"
        assert len(content.data) > 100


class TestPreviewFullscreen:
    """Scenario 5: preview_fullscreen returns a low-quality JPEG preview."""

    def test_returns_jpeg_preview(self):
        result = preview_fullscreen(display_number=1)
        assert len(result) == 1
        content = result[0]
        assert content.type == "image"
        assert content.mimeType == "image/jpeg"
        assert len(content.data) > 100


class TestCaptureWindow:
    """Scenario 6: capture_window returns an image for a valid hwnd."""

    def test_returns_image_for_valid_hwnd(self):
        windows = json.loads(list_windows())
        assert len(windows) > 0
        hwnd = windows[0]["hwnd"]

        result = capture_window(hwnd=hwnd, format="jpeg", quality=50)
        assert len(result) == 1
        content = result[0]
        assert content.type == "image"
        assert len(content.data) > 100


class TestFocusWindow:
    """Scenario 7: focus_window brings a window to the foreground."""

    def test_focus_returns_focused_status(self):
        windows = json.loads(list_windows())
        assert len(windows) > 0
        hwnd = windows[0]["hwnd"]

        result = focus_window(hwnd=hwnd)
        data = json.loads(result)
        assert data["status"] == "focused"
        assert data["hwnd"] == hwnd


class TestMaximizeWindow:
    """Scenario 8: maximize_window maximizes a window."""

    def test_maximize_returns_maximized_status(self):
        windows = json.loads(list_windows())
        assert len(windows) > 0
        hwnd = windows[0]["hwnd"]

        result = maximize_window(hwnd=hwnd)
        data = json.loads(result)
        assert data["status"] == "maximized"
        assert data["hwnd"] == hwnd
