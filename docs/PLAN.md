# WindowsCaptureMCP 実装仕様書

## 1. プロジェクト概要

Windowsのスクリーンショットを撮影し、base64形式でLLMに共有するためのMCPサーバー。

## 2. 技術スタック

| 項目 | 選択 |
|------|------|
| 言語 | Python 3.11+ |
| パッケージ管理 | uv (pyproject.toml) |
| MCPトランスポート | stdio |
| キャプチャAPI | Win32 GDI (BitBlt) |
| Win32ライブラリ | pywin32 |
| 画像処理 | Pillow |
| MCP SDK | mcp (Python SDK) |
| テスト | pytest |
| 設定管理 | ハードコード定数 |

## 3. ディレクトリ構成

```
WindowsCaptureMCP/
├── pyproject.toml
├── README.md
├── CLAUDE.md
├── PLAN.md
├── src/
│   └── windows_capture_mcp/
│       ├── __init__.py
│       ├── server.py       # MCPサーバー定義・ツール登録
│       ├── capture.py      # スクリーンキャプチャロジック
│       ├── window.py       # ウィンドウ操作・一覧取得
│       └── display.py      # ディスプレイ情報取得
└── tests/
    ├── __init__.py
    ├── test_capture.py
    ├── test_window.py
    └── test_display.py
```

## 4. MCPツール一覧（12ツール）

### 4.1 情報取得ツール

#### `list_windows`
- **説明**: 可視ウィンドウの一覧を取得
- **パラメータ**:
  - `filter` (string, optional): ウィンドウタイトルのフィルタ文字列（部分一致）
  - `include_hidden` (boolean, optional, default=false): 不可視ウィンドウも含めるか
- **返却情報**: 各ウィンドウについて以下を返す
  - `hwnd` (int): ウィンドウハンドル
  - `title` (string): ウィンドウタイトル
  - `process_name` (string): プロセス名（例: chrome.exe）
  - `x`, `y`, `width`, `height` (int): ウィンドウの位置とサイズ

#### `list_displays`
- **説明**: 接続されたディスプレイの一覧を取得
- **パラメータ**: なし
- **返却情報**: 各ディスプレイについて以下を返す
  - `display_number` (int): ディスプレイ番号（1始まり）
  - `name` (string): デバイス名
  - `width`, `height` (int): 解像度（ピクセル）
  - `x`, `y` (int): 仮想デスクトップ上の位置
  - `scale_factor` (float): スケーリング倍率
  - `is_primary` (boolean): プライマリディスプレイか

### 4.2 キャプチャツール（本番画質）

#### `capture_window`
- **説明**: 指定ウィンドウをキャプチャ
- **パラメータ**:
  - `hwnd` (int, required): ウィンドウハンドル
  - `format` (string, optional, default="png"): 画像フォーマット（"png" | "jpeg" | "webp"）
  - `quality` (int, optional, default=90): JPEG/WebP画質（1-100）
- **返却**: MCP image content (base64埋め込み)

#### `capture_fullscreen`
- **説明**: 指定ディスプレイのフルスクリーンをキャプチャ
- **パラメータ**:
  - `display_number` (int, optional, default=1): ディスプレイ番号
  - `format` (string, optional, default="png"): 画像フォーマット（"png" | "jpeg" | "webp"）
  - `quality` (int, optional, default=90): JPEG/WebP画質（1-100）
- **返却**: MCP image content (base64埋め込み)

#### `capture_region`
- **説明**: 指定領域をキャプチャ
- **パラメータ**:
  - `x` (int, required): 左上X座標
  - `y` (int, required): 左上Y座標
  - `width` (int, required): 幅
  - `height` (int, required): 高さ
  - `display_number` (int, optional, default=1): ディスプレイ番号（座標基準）
  - `format` (string, optional, default="png"): 画像フォーマット
  - `quality` (int, optional, default=90): JPEG/WebP画質
- **返却**: MCP image content (base64埋め込み)

### 4.3 プレビューツール（低画質・軽量）

共通仕様:
- JPEG低画質（quality=30）
- 長辺1280pxにリサイズ
- 撮影領域の確認用途

#### `preview_window`
- **パラメータ**: `hwnd` (int, required)
- **返却**: MCP image content (base64 JPEG)

#### `preview_fullscreen`
- **パラメータ**: `display_number` (int, optional, default=1)
- **返却**: MCP image content (base64 JPEG)

#### `preview_region`
- **パラメータ**: `x`, `y`, `width`, `height` (int, required), `display_number` (int, optional, default=1)
- **返却**: MCP image content (base64 JPEG)

### 4.4 ウィンドウ操作ツール

#### `focus_window`
- **説明**: ウィンドウを前面にフォーカス
- **パラメータ**: `hwnd` (int, required)

#### `maximize_window`
- **説明**: ウィンドウを最大化
- **パラメータ**: `hwnd` (int, required)

#### `resize_window`
- **説明**: ウィンドウのサイズを変更
- **パラメータ**: `hwnd` (int, required), `width` (int, required), `height` (int, required)

#### `move_window`
- **説明**: ウィンドウを移動
- **パラメータ**: `hwnd` (int, required), `x` (int, required), `y` (int, required)

## 5. 画像処理仕様

### 5.1 本番キャプチャ
- フォーマット: PNG（デフォルト）/ JPEG / WebP（パラメータ指定）
- 画質: JPEG/WebPの場合 quality パラメータで指定（デフォルト90）
- リサイズ: なし（原寸）

### 5.2 プレビュー
- フォーマット: JPEG固定
- 画質: quality=30
- リサイズ: 長辺1280px（アスペクト比維持）

## 6. ウィンドウ検索仕様

- 検索方式: 部分一致（タイトルに指定文字列が含まれるか）
- 大文字小文字: 区別しない（case-insensitive）
- デフォルト: 可視ウィンドウのみ
- オプション: `include_hidden=true` で不可視ウィンドウも含める

## 7. マルチディスプレイ対応

- `list_displays` でディスプレイ一覧を取得
- `capture_fullscreen` / `preview_fullscreen` で `display_number` を指定してキャプチャ
- `capture_region` / `preview_region` で `display_number` を基準にした座標指定
- ディスプレイ番号は1始まり

## 8. 定数（ハードコード）

```python
# プレビュー設定
PREVIEW_QUALITY = 30
PREVIEW_MAX_LONG_SIDE = 1280
PREVIEW_FORMAT = "jpeg"

# 本番キャプチャデフォルト
DEFAULT_FORMAT = "png"
DEFAULT_QUALITY = 90
```

## 9. 依存ライブラリ

```
mcp           # MCP Python SDK
pywin32       # Win32 API アクセス
Pillow        # 画像処理（リサイズ、フォーマット変換、base64エンコード）
```

### 開発依存
```
pytest        # テストフレームワーク
```

## 10. 実装順序

1. **プロジェクト初期化**: pyproject.toml、ディレクトリ構成、uv環境構築
2. **display.py**: ディスプレイ情報取得
3. **window.py**: ウィンドウ一覧取得、ウィンドウ操作
4. **capture.py**: スクリーンキャプチャ、画像処理（本番・プレビュー）
5. **server.py**: MCPサーバー定義、12ツール登録
6. **テスト**: 各モジュールのユニットテスト
7. **統合テスト・動作確認**
