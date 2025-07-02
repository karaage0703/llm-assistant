# LLM Assistant Bot

Claude Code CLIを活用したブラウザベースのLLMアシスタントbotです。ラズベリーパイ上で動作し、リモートからアクセス可能なWebアプリケーションとして設計されています。

## 機能

- **チャットインターフェース**: ブラウザベースのリアルタイムチャット
- **Claude Code CLI統合**: Claude Code CLIの機能をWebインターフェースで提供
- **MCP (Model Context Protocol) サポート**: `.mcp.json`経由でMCPサーバーと連携
- **WebSocket通信**: リアルタイムメッセージング
- **音声認識機能**: ブラウザ音声入力とリアルタイム音声認識
- **マークダウン対応**: メッセージのマークダウンレンダリング
- **コードハイライト**: シンタックスハイライト機能
- **セッション管理**: 複数の独立したClaude Code CLIセッション
- **ラズパイ対応**: ラズベリーパイでの軽量動作
- **リモートアクセス**: ネットワーク越しでのアクセス可能

## セットアップ

### 1. 環境の準備

```bash
# リポジトリをクローン
git clone <repository-url>
cd llm-assistant

# Python仮想環境の作成（uvを使用）
uv sync

# フロントエンドの依存関係をインストール
cd frontend
npm install
cd ..
```

### 2. Claude Code CLI認証（必須）

```bash
# Claude Code CLIをインストール
npm install -g @anthropic-ai/claude-code

# 認証（Claude Pro/Max契約またはAnthropic Consoleアカウントが必要）
claude auth
```

### 3. 環境変数の設定（オプション）

```bash
# .envファイルを作成
cp .env.example .env

# 必要に応じて設定を編集
# 基本的にはデフォルト設定で動作します
```

### 4. MCP設定（オプション）

MCPサーバーは`.mcp.json`で管理されています。必要に応じて以下を設定してください：

```bash
# .mcp.json.exampleをコピーして設定ファイルを作成
cp .mcp.json.example .mcp.json
```

### 5. アプリケーションの起動

#### バックエンドの起動
```bash
# uvを使用して起動
uv run run_backend.py
```

#### フロントエンドの起動
```bash
# 別のターミナルで
cd frontend
npm start
```

### 6. アクセス

- フロントエンド: http://localhost:3000
- バックエンドAPI: http://localhost:8000
- API ドキュメント: http://localhost:8000/docs

## 現在の状態

現在は基本的な実装が完了しており、以下の機能が動作します：

- ✅ FastAPIバックエンド（基本構造）
- ✅ Reactフロントエンド（チャットUI）
- ✅ WebSocket通信
- ✅ REST API
- ✅ マークダウンレンダリング
- ✅ コードハイライト
- ✅ Claude Code CLI統合（認証対応、セッション管理）
- ✅ MCP対応（`.mcp.json`を通じてClaude Code CLIのMCPサーバーを利用）
- ✅ 音声認識機能（Web Speech API使用、日本語対応）

## 次の開発ステップ

1. **リモートアクセス設定** - Tailscaleによるセキュアなリモートアクセス
2. **音声認識の改善** - 多言語対応、音声品質向上

## テスト

```bash
pytest
```

## 使用方法

### 基本的なチャット
1. ブラウザでhttp://localhost:3000にアクセス
2. チャット欄に質問やコマンドを入力、または🎤ボタンで音声入力
3. Claude Code CLIがMCPサーバーと連携して回答を生成

### 音声認識機能
- **🎤ボタンをクリック**: 音声認識を開始/停止
- **対応ブラウザ**: Chrome、Edge、Safari（最新版）
- **対応言語**: 日本語（デフォルト）、英語
- **注意**: マイクへのアクセス許可が必要です

### MCP機能の活用例
- **論文検索**: 「arxivで面白いLLM論文を探してください」
- **Web検索**: 「最新のAI技術動向を調べて」
- **コード解析**: 「このReactコンポーネントを改善して」
- **ドキュメント参照**: 「Next.jsの最新機能について教えて」

### トラブルシューティング
- **500エラー**: サーバーログを確認し、Claude CLI認証を再実行
- **タイムアウト**: 複雑な処理は最大180秒かかる場合があります
- **MCP接続エラー**: `.mcp.json`の設定とAPIキーを確認

## プロジェクト構造

```
.
├── backend/            # バックエンド（Python/FastAPI）
│   ├── main.py         # FastAPIアプリケーション
│   └── claude_integration.py  # Claude Code CLI統合
├── frontend/           # フロントエンド（React）
│   ├── public/         # 静的ファイル
│   ├── src/            # Reactソースコード
│   │   ├── components/ # コンポーネント
│   │   ├── App.js      # メインアプリ
│   │   └── index.js    # エントリーポイント
│   └── package.json    # npm依存関係
├── docs/               # ドキュメント
│   └── design.md       # プロジェクト設計書
├── papers/             # arxiv論文保存先
├── .devcontainer/      # VS Code開発コンテナ設定
├── .github/workflows/  # GitHub Actions CI/CD
├── .mcp.json.example   # MCP設定テンプレート
├── .mcp.json          # MCP設定ファイル（gitignore）
├── .env.example        # 環境変数テンプレート
├── pyproject.toml      # uv依存関係定義
├── run_backend.py      # バックエンド起動スクリプト
├── CLAUDE.md          # Claude Code設定ガイド
└── README.md          # このファイル
```

## ライセンス

このプロジェクトは[MITライセンス](LICENSE)の下で公開されています。詳細については[LICENSE](LICENSE)ファイルを参照してください。
