"""Window management and enumeration."""

import ctypes
import ctypes.wintypes

import win32api
import win32con
import win32gui
import win32process


def _get_process_name(hwnd: int) -> str:
    """Get the process name for a window handle."""
    try:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        handle = ctypes.windll.kernel32.OpenProcess(
            win32con.PROCESS_QUERY_LIMITED_INFORMATION, False, pid
        )
        if not handle:
            return ""
        try:
            buf = ctypes.create_unicode_buffer(260)
            size = ctypes.wintypes.DWORD(260)
            if ctypes.windll.kernel32.QueryFullProcessImageNameW(
                handle, 0, buf, ctypes.byref(size)
            ):
                # Return only the filename portion
                full_path = buf.value
                return full_path.rsplit("\\", 1)[-1]
            return ""
        finally:
            ctypes.windll.kernel32.CloseHandle(handle)
    except Exception:
        return ""


def list_windows(
    filter: str | None = None, include_hidden: bool = False
) -> list[dict]:
    """List windows with optional filtering.

    Args:
        filter: Optional title substring filter (case-insensitive).
        include_hidden: If True, include invisible windows. Default is False.

    Returns:
        List of dicts with keys: hwnd, title, process_name, x, y, width, height.
    """
    results: list[dict] = []

    def _enum_callback(hwnd: int, _: object) -> bool:
        if not include_hidden and not win32gui.IsWindowVisible(hwnd):
            return True

        title = win32gui.GetWindowText(hwnd)
        if not title:
            return True

        if filter is not None and filter.lower() not in title.lower():
            return True

        rect = win32gui.GetWindowRect(hwnd)
        x, y, right, bottom = rect
        width = right - x
        height = bottom - y

        process_name = _get_process_name(hwnd)

        results.append(
            {
                "hwnd": hwnd,
                "title": title,
                "process_name": process_name,
                "x": x,
                "y": y,
                "width": width,
                "height": height,
            }
        )
        return True

    win32gui.EnumWindows(_enum_callback, None)
    return results
