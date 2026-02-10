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


def focus_window(hwnd: int) -> dict:
    """Bring a window to the foreground.

    Uses AttachThreadInput and Alt key simulation to bypass the
    foreground lock restriction when called from a background process.

    Args:
        hwnd: Window handle.

    Returns:
        Dict with status information.

    Raises:
        ValueError: If the hwnd is invalid.
    """
    if not win32gui.IsWindow(hwnd):
        raise ValueError(f"Invalid window handle: {hwnd}")

    # If the window is minimized, restore it first
    if win32gui.IsIconic(hwnd):
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)

    VK_MENU = 0x12
    KEYEVENTF_KEYUP = 0x0002

    target_thread_id, _ = win32process.GetWindowThreadProcessId(hwnd)
    current_thread_id = ctypes.windll.kernel32.GetCurrentThreadId()
    threads_attached = False

    # Simulate Alt key press to bypass foreground lock timeout
    ctypes.windll.user32.keybd_event(VK_MENU, 0, 0, 0)
    try:
        # Attach input threads if they differ
        if current_thread_id != target_thread_id:
            try:
                win32process.AttachThreadInput(current_thread_id, target_thread_id, True)
                threads_attached = True
            except Exception:
                pass

        try:
            win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
            win32gui.SetForegroundWindow(hwnd)
            win32gui.BringWindowToTop(hwnd)
        except Exception:
            # Fallback: temporarily disable foreground lock timeout
            SPI_SETFOREGROUNDLOCKTIMEOUT = 0x2001
            SPIF_SENDCHANGE = 0x0002
            old_timeout = ctypes.wintypes.DWORD()
            ctypes.windll.user32.SystemParametersInfoW(
                0x2000, 0, ctypes.byref(old_timeout), 0  # SPI_GETFOREGROUNDLOCKTIMEOUT
            )
            ctypes.windll.user32.SystemParametersInfoW(
                SPI_SETFOREGROUNDLOCKTIMEOUT, 0, 0, SPIF_SENDCHANGE
            )
            try:
                win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
                win32gui.SetForegroundWindow(hwnd)
                win32gui.BringWindowToTop(hwnd)
            finally:
                ctypes.windll.user32.SystemParametersInfoW(
                    SPI_SETFOREGROUNDLOCKTIMEOUT,
                    0,
                    old_timeout.value,
                    SPIF_SENDCHANGE,
                )
    finally:
        # Release Alt key
        ctypes.windll.user32.keybd_event(VK_MENU, 0, KEYEVENTF_KEYUP, 0)
        # Detach threads
        if threads_attached:
            try:
                win32process.AttachThreadInput(
                    current_thread_id, target_thread_id, False
                )
            except Exception:
                pass

    title = win32gui.GetWindowText(hwnd)
    return {"hwnd": hwnd, "title": title, "status": "focused"}


def maximize_window(hwnd: int) -> dict:
    """Maximize a window.

    Args:
        hwnd: Window handle.

    Returns:
        Dict with status information.

    Raises:
        ValueError: If the hwnd is invalid.
    """
    if not win32gui.IsWindow(hwnd):
        raise ValueError(f"Invalid window handle: {hwnd}")

    win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)

    title = win32gui.GetWindowText(hwnd)
    return {"hwnd": hwnd, "title": title, "status": "maximized"}


def resize_window(hwnd: int, width: int, height: int) -> dict:
    """Resize a window while keeping its position.

    Args:
        hwnd: Window handle.
        width: New width in pixels.
        height: New height in pixels.

    Returns:
        Dict with status information.

    Raises:
        ValueError: If the hwnd is invalid or dimensions are not positive.
    """
    if not win32gui.IsWindow(hwnd):
        raise ValueError(f"Invalid window handle: {hwnd}")
    if width <= 0 or height <= 0:
        raise ValueError(f"Width and height must be positive, got {width}x{height}")

    rect = win32gui.GetWindowRect(hwnd)
    x, y = rect[0], rect[1]

    win32gui.SetWindowPos(
        hwnd, 0, x, y, width, height, win32con.SWP_NOZORDER | win32con.SWP_NOACTIVATE
    )

    title = win32gui.GetWindowText(hwnd)
    return {"hwnd": hwnd, "title": title, "width": width, "height": height, "status": "resized"}


def move_window(hwnd: int, x: int, y: int) -> dict:
    """Move a window while keeping its size.

    Args:
        hwnd: Window handle.
        x: New x position in pixels.
        y: New y position in pixels.

    Returns:
        Dict with status information.

    Raises:
        ValueError: If the hwnd is invalid.
    """
    if not win32gui.IsWindow(hwnd):
        raise ValueError(f"Invalid window handle: {hwnd}")

    rect = win32gui.GetWindowRect(hwnd)
    width = rect[2] - rect[0]
    height = rect[3] - rect[1]

    win32gui.SetWindowPos(
        hwnd, 0, x, y, width, height, win32con.SWP_NOZORDER | win32con.SWP_NOACTIVATE
    )

    title = win32gui.GetWindowText(hwnd)
    return {"hwnd": hwnd, "title": title, "x": x, "y": y, "status": "moved"}
