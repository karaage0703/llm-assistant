# LLM Assistant Bot

Claude Code CLIを活用したブラウザベースのLLMアシスタントbotです。ラズベリーパイ上で動作し、リモートからアクセス可能なWebアプリケーションとして設計されています。

## 機能

- **チャットインターフェース**: ブラウザベースのリアルタイムチャット
- **Claude Code CLI統合**: Claude Code CLIの機能をWebインターフェースで提供
- **WebSocket通信**: リアルタイムメッセージング
- **マークダウン対応**: メッセージのマークダウンレンダリング
- **コードハイライト**: シンタックスハイライト機能
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

### 4. アプリケーションの起動

#### バックエンドの起動
```bash
# 仮想環境をアクティベート
source .venv/bin/activate  # Linux/Mac
# または .venv\Scripts\activate  # Windows

# バックエンドサーバー起動
python run_backend.py
```

#### フロントエンドの起動
```bash
# 別のターミナルで
cd frontend
npm start
```

### 5. アクセス

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
- ❌ MCP対応（未実装）
- ❌ 認証機能（未実装）

## 次の開発ステップ

1. **MCP（Model Context Protocol）対応** - 外部サービス連携
2. **認証・セキュリティ機能** - ユーザー認証とアクセス制御
3. **ファイルアップロード機能** - コード解析とプロジェクト管理
4. **ラズパイ用Docker設定** - コンテナ化デプロイ
5. **リモートアクセス設定** - Nginx、SSL設定

## テスト

```bash
pytest
```

## 設計書テンプレート

`docs/design.md.sample`には、プロジェクトの要件定義から設計、開発工程までを体系的に記述するためのテンプレートが含まれています。このテンプレートは以下の特徴を持っています：

- 要件定義セクション（基本情報、プロジェクト概要、機能要件、非機能要件など）
- システム設計セクション（アーキテクチャ、クラス設計、データフロー、エラーハンドリングなど）
- 開発工程セクション（フェーズ、マイルストーン、リスク管理など）

LLMはこのテンプレートを参照し、ユーザーから提供された要件に基づいて具体的な設計書を自動生成します。ユーザーは生成された設計書を確認し、必要に応じて調整を依頼できます。

## プロジェクト構造

```
.
├── docs/               # ドキュメント
│   ├── design.md       # プロジェクト設計書
│   └── design.md.sample  # 設計書テンプレート
├── backend/            # バックエンド（Python/FastAPI）
│   ├── __init__.py
│   └── main.py         # FastAPIアプリケーション
├── frontend/           # フロントエンド（React）
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatInterface.js
│   │   │   └── ChatInterface.css
│   │   ├── App.js
│   │   ├── App.css
│   │   ├── index.js
│   │   └── index.css
│   └── package.json
├── src/                # 既存のPythonソース
├── tests/              # テストコード
├── .env.example        # 環境変数テンプレート
├── run_backend.py      # バックエンド起動スクリプト
├── requirements.txt    # Python依存関係
└── README.md          # このファイル
```

## ライセンス

このプロジェクトは[MITライセンス](LICENSE)の下で公開されています。詳細については[LICENSE](LICENSE)ファイルを参照してください。
