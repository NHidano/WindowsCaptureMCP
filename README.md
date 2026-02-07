# WindowsCaptureMCP

Windows のスクリーンショットを撮影し、base64 形式で LLM に共有するための MCP サーバーです。

## 主な機能

- ウィンドウ一覧の取得・フィルタリング
- ウィンドウ単位 / フルスクリーン / 指定領域のスクリーンキャプチャ
- 低画質プレビュー画像の生成（撮影領域の確認用）
- ウィンドウ操作（フォーカス、最大化、リサイズ、移動）
- マルチディスプレイ対応
- PNG / JPEG / WebP 形式対応

## 必要環境

- Windows
- Python 3.11 以上
- [uv](https://docs.astral.sh/uv/)

## インストール

```bash
git clone <repository-url>
cd WindowsCaptureMCP
uv sync
```

## MCP クライアントへの設定

### Claude Desktop

`claude_desktop_config.json` に以下を追加してください。

```json
{
  "mcpServers": {
    "windows-capture-mcp": {
      "command": "uv",
      "args": ["run", "--directory", "C:/path/to/WindowsCaptureMCP", "windows-capture-mcp"]
    }
  }
}
```

### Claude Code

`settings.json` または `.mcp.json` に以下を追加してください。

```json
{
  "mcpServers": {
    "windows-capture-mcp": {
      "command": "uv",
      "args": ["run", "--directory", "C:/path/to/WindowsCaptureMCP", "windows-capture-mcp"]
    }
  }
}
```

> `C:/path/to/WindowsCaptureMCP` はリポジトリの実際のパスに置き換えてください。

## 提供ツール一覧

### 情報取得

| ツール名 | 説明 |
|---|---|
| `list_windows` | 表示中のウィンドウ一覧を取得（タイトルでのフィルタリング可） |
| `list_displays` | 接続中のディスプレイ一覧を取得 |

### スクリーンキャプチャ（フル画質）

| ツール名 | 説明 |
|---|---|
| `capture_window` | ウィンドウハンドルを指定してキャプチャ |
| `capture_fullscreen` | ディスプレイ全体をキャプチャ |
| `capture_region` | 指定した矩形領域をキャプチャ |

### プレビュー（低画質・軽量）

| ツール名 | 説明 |
|---|---|
| `preview_window` | ウィンドウの低画質プレビューを取得 |
| `preview_fullscreen` | ディスプレイ全体の低画質プレビューを取得 |
| `preview_region` | 指定領域の低画質プレビューを取得 |

プレビューは JPEG 品質 30、長辺最大 1280px にリサイズされます。キャプチャ対象の確認に使用してください。

### ウィンドウ操作

| ツール名 | 説明 |
|---|---|
| `focus_window` | ウィンドウを前面に表示 |
| `maximize_window` | ウィンドウを最大化 |
| `resize_window` | ウィンドウのサイズを変更 |
| `move_window` | ウィンドウの位置を変更 |

## ツール詳細

### list_windows

表示中のウィンドウ一覧を取得します。

**パラメータ:**

| 名前 | 型 | 必須 | デフォルト | 説明 |
|---|---|---|---|---|
| `filter` | string | - | なし | タイトルの部分一致フィルタ（大文字小文字を区別しない） |
| `include_hidden` | bool | - | false | 非表示ウィンドウも含める |

**戻り値の例:**

```json
[
  {
    "hwnd": 12345,
    "title": "README.md - Visual Studio Code",
    "process_name": "Code.exe",
    "x": 0,
    "y": 0,
    "width": 1920,
    "height": 1080
  }
]
```

### list_displays

接続中のディスプレイ一覧を取得します。

**パラメータ:** なし

**戻り値の例:**

```json
[
  {
    "display_number": 1,
    "name": "\\\\.\\DISPLAY1",
    "width": 1920,
    "height": 1080,
    "x": 0,
    "y": 0,
    "scale_factor": 1.0,
    "is_primary": true
  }
]
```

### capture_window / capture_fullscreen / capture_region

スクリーンキャプチャを撮影し、base64 エンコードされた画像を返します。

**共通パラメータ:**

| 名前 | 型 | 必須 | デフォルト | 説明 |
|---|---|---|---|---|
| `format` | string | - | "png" | 画像形式（"png" / "jpeg" / "webp"） |
| `quality` | int | - | 90 | JPEG / WebP の品質（1〜100） |

**capture_window 固有パラメータ:**

| 名前 | 型 | 必須 | 説明 |
|---|---|---|---|
| `hwnd` | int | 必須 | ウィンドウハンドル（`list_windows` で取得） |

**capture_fullscreen 固有パラメータ:**

| 名前 | 型 | 必須 | デフォルト | 説明 |
|---|---|---|---|---|
| `display_number` | int | - | 1 | ディスプレイ番号（1始まり） |

**capture_region 固有パラメータ:**

| 名前 | 型 | 必須 | デフォルト | 説明 |
|---|---|---|---|---|
| `x` | int | 必須 | - | 左端の X 座標（ディスプレイ相対） |
| `y` | int | 必須 | - | 上端の Y 座標（ディスプレイ相対） |
| `width` | int | 必須 | - | 幅（ピクセル） |
| `height` | int | 必須 | - | 高さ（ピクセル） |
| `display_number` | int | - | 1 | ディスプレイ番号（1始まり） |

### preview_window / preview_fullscreen / preview_region

低画質のプレビュー画像を返します。パラメータはキャプチャ系ツールの固有パラメータと同じです（`format` / `quality` は指定不可）。

### focus_window / maximize_window

**パラメータ:**

| 名前 | 型 | 必須 | 説明 |
|---|---|---|---|
| `hwnd` | int | 必須 | ウィンドウハンドル |

### resize_window

**パラメータ:**

| 名前 | 型 | 必須 | 説明 |
|---|---|---|---|
| `hwnd` | int | 必須 | ウィンドウハンドル |
| `width` | int | 必須 | 新しい幅（ピクセル） |
| `height` | int | 必須 | 新しい高さ（ピクセル） |

### move_window

**パラメータ:**

| 名前 | 型 | 必須 | 説明 |
|---|---|---|---|
| `hwnd` | int | 必須 | ウィンドウハンドル |
| `x` | int | 必須 | 新しい X 座標（ピクセル） |
| `y` | int | 必須 | 新しい Y 座標（ピクセル） |

## 使い方の例

### 1. ウィンドウを探してキャプチャする

```
1. list_windows(filter="Chrome") でブラウザのウィンドウを検索
2. 取得した hwnd を使って capture_window(hwnd=12345) でキャプチャ
```

### 2. プレビューで位置を確認してから領域キャプチャ

```
1. preview_fullscreen() で画面全体のプレビューを確認
2. キャプチャしたい領域の座標を特定
3. capture_region(x=100, y=200, width=800, height=600) で領域をキャプチャ
```

### 3. ウィンドウを操作してからキャプチャ

```
1. list_windows(filter="メモ帳") でウィンドウを検索
2. focus_window(hwnd=12345) でウィンドウを前面に表示
3. resize_window(hwnd=12345, width=1280, height=720) でサイズを調整
4. capture_window(hwnd=12345) でキャプチャ
```

## 開発

### テストの実行

```bash
# 全テスト
uv run pytest

# モジュール別
uv run pytest tests/test_display.py
uv run pytest tests/test_window.py
uv run pytest tests/test_capture.py
```

## ライセンス

MIT
