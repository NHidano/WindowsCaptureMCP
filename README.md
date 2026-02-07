# WindowsCaptureMCP

An MCP (Model Context Protocol) server for capturing Windows screenshots and sharing them as base64-encoded images with LLMs.

> **Windows only** — This package requires Windows and uses Win32 APIs for screen capture and window management.

## Features

- List and filter visible windows
- Capture windows, full screen, or custom regions
- Low-quality preview images for quick verification before full capture
- Window management (focus, maximize, resize, move)
- Multi-display support
- PNG / JPEG / WebP output formats

## Requirements

- **Windows**
- **Python >= 3.11**

## Installation

```bash
# Using uvx (recommended)
uvx windows-capture-mcp

# Using pip
pip install windows-capture-mcp
```

## MCP Client Configuration

### Claude Code

```bash
claude mcp add windows-capture-mcp -s user -- uvx windows-capture-mcp
```

### Claude Desktop

Add the following to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "windows-capture-mcp": {
      "command": "uvx",
      "args": ["windows-capture-mcp"]
    }
  }
}
```

## Available Tools

### Information

| Tool | Description |
|------|-------------|
| `list_windows` | List visible windows with optional title filtering (case-insensitive) |
| `list_displays` | List all connected displays with resolution, position, and scale info |

### Screen Capture (Full Quality)

| Tool | Description |
|------|-------------|
| `capture_window` | Capture a specific window by handle |
| `capture_fullscreen` | Capture an entire display |
| `capture_region` | Capture a rectangular region |

All capture tools support `format` (`"png"`, `"jpeg"`, `"webp"`) and `quality` (1-100) parameters.

### Preview (Lightweight)

| Tool | Description |
|------|-------------|
| `preview_window` | Low-quality preview of a window |
| `preview_fullscreen` | Low-quality preview of a display |
| `preview_region` | Low-quality preview of a region |

Preview images are JPEG at quality 30, resized to max 1280px on the longest side. Use these to verify capture targets before taking full-quality screenshots.

### Window Management

| Tool | Description |
|------|-------------|
| `focus_window` | Bring a window to the foreground |
| `maximize_window` | Maximize a window |
| `resize_window` | Resize a window (keeps position) |
| `move_window` | Move a window (keeps size) |

## Usage Example

```
1. list_windows(filter="Chrome")       → Find browser windows
2. preview_window(hwnd=12345)           → Quick preview to verify
3. capture_window(hwnd=12345)           → Full-quality capture
```

## License

MIT
