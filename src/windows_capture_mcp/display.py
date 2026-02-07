"""Display information retrieval."""

import ctypes
import ctypes.wintypes

import win32api
import win32con


def get_displays() -> list[dict]:
    """Get a list of all connected displays with their information.

    Returns a list of dicts with keys:
        display_number, name, width, height, x, y, scale_factor, is_primary
    Display numbers are 1-based.
    """
    displays: list[dict] = []

    monitors = win32api.EnumDisplayMonitors(None, None)
    for i, (hmonitor, _hdc, _rect) in enumerate(monitors, start=1):
        info = win32api.GetMonitorInfo(hmonitor)
        monitor_rect = info["Monitor"]
        x = monitor_rect[0]
        y = monitor_rect[1]
        width = monitor_rect[2] - monitor_rect[0]
        height = monitor_rect[3] - monitor_rect[1]
        is_primary = bool(info["Flags"] & win32con.MONITORINFOF_PRIMARY)
        name = info["Device"]

        # Get scale factor using GetScaleFactorForMonitor
        scale_factor = _get_scale_factor(hmonitor)

        displays.append(
            {
                "display_number": i,
                "name": name,
                "width": width,
                "height": height,
                "x": x,
                "y": y,
                "scale_factor": scale_factor,
                "is_primary": is_primary,
            }
        )

    return displays


def get_display_rect(display_number: int) -> tuple[int, int, int, int]:
    """Get the virtual desktop rectangle for a specific display.

    Args:
        display_number: 1-based display number.

    Returns:
        Tuple of (x, y, width, height) in virtual desktop coordinates.

    Raises:
        ValueError: If the display number does not exist.
    """
    displays = get_displays()
    for d in displays:
        if d["display_number"] == display_number:
            return (d["x"], d["y"], d["width"], d["height"])
    raise ValueError(
        f"Display number {display_number} not found. "
        f"Available displays: {[d['display_number'] for d in displays]}"
    )


def _get_scale_factor(hmonitor: int) -> float:
    """Get the DPI scale factor for a monitor."""
    try:
        # Use GetDpiForMonitor (Windows 8.1+)
        shcore = ctypes.windll.shcore
        dpi_x = ctypes.c_uint()
        dpi_y = ctypes.c_uint()
        # MDT_EFFECTIVE_DPI = 0
        hr = shcore.GetDpiForMonitor(
            int(hmonitor),
            0,
            ctypes.byref(dpi_x),
            ctypes.byref(dpi_y),
        )
        if hr == 0:  # S_OK
            return dpi_x.value / 96.0
    except (OSError, AttributeError):
        pass
    return 1.0
