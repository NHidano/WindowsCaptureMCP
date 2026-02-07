# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

WindowsCaptureMCP は、Windowsのスクリーンショットを撮影し、base64形式でLLMに共有するためのMCPサーバーです。

### 主要機能

- ウィンドウ名からキャプチャ対象を選択
- ウィンドウ操作（フォーカス、最大化など）
- フルスクリーン撮影
- 指定領域の撮影
- 低画質圧縮によるプレビュー用base64画像生成（撮影領域の指定に利用）
- マルチディスプレイ環境対応

## コミュニケーション

- ユーザーとのやり取りは**日本語**で行うこと

## ビルド・実行

```bash
# 依存インストール
uv sync

# MCPサーバー起動
uv run windows-capture-mcp
```

## テスト

```bash
# 全テスト実行
uv run pytest

# モジュール別テスト実行
uv run pytest tests/test_display.py
uv run pytest tests/test_window.py
uv run pytest tests/test_capture.py
```

## ステータス

実装完了。MCPサーバーとして全機能（ウィンドウ一覧取得、ディスプレイ一覧取得、スクリーンキャプチャ、プレビュー、ウィンドウ操作）が利用可能です。
