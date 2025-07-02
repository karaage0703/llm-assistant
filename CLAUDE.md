# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

このプロジェクトは、Claude Code CLIを活用したブラウザベースのLLMアシスタントbotです。ラズベリーパイ上で動作し、リモートからアクセス可能なWebアプリケーションとして設計されています。主要コンポーネントはFastAPIバックエンドとReactフロントエンドで構成されており、WebSocketによるリアルタイム通信とClaude Code CLIとの統合を特徴としています。

## 開発コマンド

### 環境セットアップ
```bash
# Python環境の準備
uv venv
uv pip install -r requirements.txt

# フロントエンド依存関係のインストール
cd frontend && npm install && cd ..
```

### 開発サーバーの起動
```bash
# バックエンド起動（Port 8000）
source .venv/bin/activate
python run_backend.py

# フロントエンド起動（Port 3000）- 別ターミナル
cd frontend && npm start
```

### テスト実行
```bash
# Python テスト
pytest

# フロントエンドテスト（利用可能な場合）
cd frontend && npm test
```

### リンティング
**重要**: 必ず`.github/workflows/ruff.yml`の設定に従ってLintを実行してください

```bash
# Python - GitHub Actions設定に従った正しいコマンド
ruff check --line-length=127
ruff format --check --diff --line-length=127

# フォーマット適用
ruff format --line-length=127

# JavaScript（React Scripts経由）
cd frontend && npm run build  # 警告とエラーをチェック
```

### Claude Code CLI要件
```bash
# Claude Code CLIのインストールと認証
npm install -g @anthropic-ai/claude-code
claude auth  # Claude Pro/Max契約またはAnthropic Console認証が必要
```

## アーキテクチャ

### 全体構成
- **バックエンド**: FastAPI (Python) - `/backend/main.py`
- **フロントエンド**: React SPA - `/frontend/src/`
- **Claude統合**: カスタムマネージャー - `/backend/claude_integration.py`
- **通信**: WebSocket + REST API

### 主要クラスとコンポーネント

#### バックエンド
- `AdvancedClaudeCodeManager`: Claude Code CLI統合の中核。セッション管理、認証チェック、コマンド実行を担当
- `ChatSession`: セッション状態を管理するデータクラス。作業ディレクトリ、履歴、タイムスタンプを保持
- `ConnectionManager`: WebSocket接続の管理
- FastAPIエンドポイント: `/api/chat`, `/api/sessions`, `/health`

#### フロントエンド
- `ChatInterface`: メインのチャットUI。WebSocketとREST APIの両方をサポート
- マークダウンレンダリング: `marked`ライブラリでコードハイライト付き
- リアルタイム接続状態表示

### Claude Code CLI統合
- 複数のコマンド名を試行: `claude`, `npx @anthropic-ai/claude-code`, `claude-code`
- 認証状態の自動チェック
- セッション毎の独立した作業ディレクトリ
- フォールバック: CLI未インストール時はシミュレーションモード

### セッション管理
- セッション毎に一時ディレクトリを作成
- チャット履歴をメモリに保持
- 自動クリーンアップ機能

## 重要な設計決定

1. **APIキー不要**: Claude Code CLIは認証済みセッション（Max/Pro契約）を使用し、直接的なAPIキー管理を回避
2. **デュアル通信**: WebSocketとREST APIの両方をサポートし、接続状況に応じて自動切り替え
3. **セッション分離**: ユーザーセッション毎に独立した作業環境を提供
4. **フォールバック機能**: Claude CLI未設定時でもUIとして機能

## 環境変数
```bash
# オプション設定（.env.exampleを参照）
HOST=0.0.0.0
PORT=8000
DEBUG=true
FRONTEND_URL=http://localhost:3000
LOG_LEVEL=INFO
```

## MCP（Model Context Protocol）対応
このプロジェクトは`.mcp.json`を通じてClaude Code CLIのMCP機能を利用します。MCPサーバーの設定は`.mcp.json`で管理され、以下のサーバーが利用可能です：
- gemini-google-search: Google検索
- arxiv-mcp-server: 論文検索・ダウンロード
- markitdown: マークダウン変換
- voicevox/aivisspeech: 音声合成
- youtube: YouTube字幕取得
- playwright: ブラウザ自動化
- context7: ライブラリドキュメント検索

MCPサーバー用の環境変数：
```bash
export BRAVE_API_KEY="your-brave-api-key"
export GITHUB_PERSONAL_ACCESS_TOKEN="your-github-token"
export GEMINI_API_KEY="your-gemini-api-key"
```

## 今後の実装予定
- 認証・セキュリティ機能
- ファイルアップロード機能
- ラズパイ用Docker設定