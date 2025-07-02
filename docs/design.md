# 要件・設計書

## 1. 要件定義

### 1.1 基本情報
- ソフトウェア名称: LLM Assistant Bot
- リポジトリ名: llm-assistant

### 1.2 プロジェクト概要

Claude Code CLIを活用したブラウザベースのLLMアシスタントbotを開発します。このシステムは、ラズベリーパイ上で動作し、リモートからアクセス可能なWebアプリケーションとして設計されます。ユーザーはブラウザを通じてLLMと対話でき、Model Context Protocol（MCP）にも対応することで、外部サービスとの連携も可能にします。

主な目的：
- Claude Code CLIの機能をWebインターフェースで提供
- ラズベリーパイでの軽量動作
- リモートアクセスによる柔軟な利用環境
- MCPによる拡張性の確保

### 1.3 機能要件

#### 1.3.1 基本機能
- **チャットインターフェース**
  - リアルタイムメッセージング
  - マークダウン対応
  - コードハイライト
  - 履歴管理
- **Claude Code CLI統合**
  - コマンド実行
  - レスポンス取得・表示
  - エラーハンドリング
- **ファイル管理**
  - ファイルアップロード
  - ファイル表示・編集
  - プロジェクト管理

#### 1.3.2 高度な機能
- **MCP（Model Context Protocol）対応**
  - MCP接続管理
  - プロトコル設定
  - 外部サービス連携
- **設定管理**
  - APIキー管理
  - 接続設定
  - ユーザー設定
- **リモートアクセス**
  - 認証・認可
  - セッション管理
  - セキュリティ設定

### 1.4 非機能要件

#### 1.4.1 性能要件
- レスポンス時間: 2秒以内（通常操作）
- 同時接続数: 10ユーザー（ラズパイ環境）
- メモリ使用量: 512MB以下（ラズパイ4GB想定）
- ストレージ: 4GB以下

#### 1.4.2 セキュリティ要件
- APIキーの暗号化保存
- HTTPS通信の強制
- セッションタイムアウト設定
- 認証機能（トークンベース）
- CORS設定

#### 1.4.3 運用・保守要件
- ログ記録機能
- エラー監視
- 設定ファイルによる管理
- Docker化によるポータビリティ
- 自動起動設定

### 1.5 制約条件
- **技術的制約**
  - ラズベリーパイのCPU・メモリ制限
  - Claude Code CLIの仕様に依存
  - MCP仕様への準拠
- **ビジネス的制約**
  - オープンソース開発
  - 個人利用想定
- **法的制約**
  - APIキーの適切な管理
  - プライバシー保護

### 1.6 開発環境
- 言語：Python 3.11+
- フレームワーク：FastAPI、React/Vue.js
- 外部API：Claude Code CLI、MCP
- 開発ツール：VSCode
- パッケージ管理：uv
- コンテナ：Docker、Docker Compose

### 1.7 成果物
- ソースコード
- 設計書
- テストコード
- README（セットアップ手順含む）
- Docker設定ファイル
- デプロイ手順書

## 2. システム設計

### 2.1 システム概要設計

#### 2.1.1 システムアーキテクチャ
```
[Browser] <---> [Nginx] <---> [React/Vue.js Frontend]
                                        |
                                        | REST API / WebSocket
                                        |
                                        v
                                [FastAPI Backend]
                                        |
                                        |
                        +---------------+---------------+
                        |                               |
                        v                               v
                [Claude Code CLI]                   [MCP Client]
                        |                               |
                        v                               v
                [Claude API]                    [External Services]
```

#### 2.1.2 主要コンポーネント
1. **Webフロントエンド**
   - React/Vue.js ベースのSPA
   - チャットUI、設定画面
   - WebSocketによるリアルタイム通信
2. **APIバックエンド**
   - FastAPI ベース
   - Claude Code CLI ラッパー
   - MCP クライアント機能
3. **Claude Code CLI統合**
   - コマンド実行エンジン
   - レスポンス処理
   - エラーハンドリング
4. **MCP統合**
   - プロトコル実装
   - 外部サービス連携
   - 設定管理
5. **認証・セキュリティ**
   - JWT認証
   - API キー管理
   - セッション管理

#### 2.1.3 設定・パラメータ
- **サーバー設定**
  - host: 0.0.0.0
  - port: 8000
  - reload: false（本番環境）
- **Claude Code CLI設定**
  - api_key: 環境変数から取得
  - model: claude-3-5-sonnet-20241022
  - timeout: 30秒
- **MCP設定**
  - connection_timeout: 10秒
  - max_connections: 5
  - protocols: ["stdio", "sse"]

### 2.2 詳細設計

#### 2.2.1 クラス設計

##### 2.2.1.1 ClaudeCodeManager
```python
class ClaudeCodeManager:
    """Claude Code CLIの実行管理クラス"""

    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022"):
        """初期化メソッド"""
        self.api_key = api_key
        self.model = model
        self.current_session = None

    async def execute_command(self, command: str, context: dict = None) -> dict:
        """Claude Code CLIコマンドを実行"""
        # コマンド実行とレスポンス処理

    async def start_session(self, project_path: str) -> str:
        """新しいセッションを開始"""
        # セッション開始処理

    async def end_session(self, session_id: str) -> bool:
        """セッションを終了"""
        # セッション終了処理
```

##### 2.2.1.2 MCPClient
```python
class MCPClient:
    """MCP（Model Context Protocol）クライアントクラス"""

    def __init__(self, config: MCPConfig):
        """初期化メソッド"""
        self.config = config
        self.connections = {}
        self.available_tools = {}

    async def connect_to_server(self, server_config: dict) -> bool:
        """MCPサーバーに接続"""
        # サーバー接続処理

    async def list_tools(self, server_id: str) -> list:
        """利用可能なツールを取得"""
        # ツール一覧取得

    async def call_tool(self, server_id: str, tool_name: str, args: dict) -> dict:
        """ツールを実行"""
        # ツール実行処理
```

##### 2.2.1.3 ChatManager
```python
class ChatManager:
    """チャット管理クラス"""

    def __init__(self, claude_manager: ClaudeCodeManager, mcp_client: MCPClient):
        """初期化メソッド"""
        self.claude_manager = claude_manager
        self.mcp_client = mcp_client
        self.active_sessions = {}

    async def process_message(self, session_id: str, message: str) -> dict:
        """メッセージを処理してレスポンスを生成"""
        # メッセージ処理ロジック

    async def get_chat_history(self, session_id: str) -> list:
        """チャット履歴を取得"""
        # 履歴取得処理

    async def create_session(self, user_id: str) -> str:
        """新しいチャットセッションを作成"""
        # セッション作成処理
```

##### 2.2.1.4 WebSocketManager
```python
class WebSocketManager:
    """WebSocket接続管理クラス"""

    def __init__(self):
        """初期化メソッド"""
        self.active_connections = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        """WebSocket接続を受け入れ"""
        # 接続処理

    async def disconnect(self, client_id: str):
        """WebSocket接続を切断"""
        # 切断処理

    async def send_message(self, client_id: str, message: dict):
        """特定のクライアントにメッセージを送信"""
        # メッセージ送信処理

    async def broadcast(self, message: dict):
        """全てのクライアントにメッセージをブロードキャスト"""
        # ブロードキャスト処理
```

#### 2.2.2 データフロー
1. **フロントエンドからメッセージ受信**
   - WebSocketまたはREST APIでメッセージを受信
   - 認証・バリデーション
2. **Claude Code CLI実行**
   - メッセージをClaude Code CLIに渡す
   - コマンド実行とレスポンス取得
3. **MCP統合（必要に応じて）**
   - MCPツールの実行
   - 外部サービスとの連携
4. **レスポンス返却**
   - 結果をフロントエンドに送信
   - WebSocketでリアルタイム更新

#### 2.2.3 エラーハンドリング
- **Claude Code CLI実行エラー**
  - タイムアウト処理
  - APIキーエラー
  - コマンド構文エラー
- **MCP接続エラー**
  - サーバー接続失敗
  - プロトコルエラー
  - ツール実行エラー
- **ネットワークエラー**
  - WebSocket切断
  - HTTP通信エラー
  - 認証エラー

### 2.3 インターフェース設計

#### 2.3.1 REST API
- **POST /api/chat/message**
  - メッセージ送信
  - 認証: Bearer Token
  - ボディ: {"message": "string", "session_id": "string"}
- **GET /api/chat/history/{session_id}**
  - チャット履歴取得
  - 認証: Bearer Token
- **POST /api/sessions**
  - 新しいセッション作成
  - 認証: Bearer Token
- **GET /api/mcp/servers**
  - MCPサーバー一覧取得
  - 認証: Bearer Token
- **POST /api/mcp/tools/execute**
  - MCPツール実行
  - 認証: Bearer Token

#### 2.3.2 WebSocket
- **接続エンドポイント**: `/ws/{client_id}`
- **メッセージ形式**:
  ```json
  {
    "type": "message|system|error",
    "data": {
      "content": "string",
      "session_id": "string",
      "timestamp": "ISO8601"
    }
  }
  ```

#### 2.3.3 外部連携
- **Claude Code CLI**
  - コマンドライン実行
  - 標準入出力
  - プロセス管理
- **MCP**
  - JSON-RPC over stdio/SSE
  - プロトコル準拠
  - ツール実行

### 2.4 セキュリティ設計
- **認証・認可**
  - JWT トークンベース認証
  - API キーの暗号化保存
  - セッション管理
- **通信セキュリティ**
  - HTTPS 強制
  - CORS 設定
  - WebSocket セキュリティ
- **データ保護**
  - 機密情報の暗号化
  - ログの適切な管理
  - 入力値バリデーション

### 2.5 テスト設計
- **ユニットテスト**
  - ClaudeCodeManager
    - コマンド実行テスト
    - エラーハンドリング
  - MCPClient
    - 接続テスト
    - ツール実行テスト
  - ChatManager
    - メッセージ処理テスト
    - セッション管理テスト
- **統合テスト**
  - API エンドポイントテスト
  - WebSocket 通信テスト
  - 認証フローテスト
- **エラーケーステスト**
  - 無効な入力値
  - ネットワーク切断
  - 外部サービス障害

### 2.6 開発環境・依存関係
- Python 3.11+
- fastapi
- uvicorn
- websockets
- pydantic
- python-multipart
- python-jose
- bcrypt
- aiofiles
- pytest
- pytest-asyncio
- httpx
- uv（パッケージ管理）

### 2.7 開発工程

#### 2.7.1 開発フェーズ
1. **要件分析・定義フェーズ（完了）**
   - 要件定義書作成
   - 技術調査
   - アーキテクチャ設計
2. **設計フェーズ（1-2日）**
   - 詳細設計書作成
   - API設計
   - データベーススキーマ設計
3. **実装フェーズ（1週間）**
   - バックエンド実装
   - フロントエンド実装
   - Claude Code CLI統合
   - MCP統合
4. **テストフェーズ（2-3日）**
   - ユニットテスト
   - 統合テスト
   - エラーケーステスト
5. **デプロイ・ドキュメント作成フェーズ（1-2日）**
   - Docker設定
   - ラズパイ用設定
   - デプロイメント手順書

#### 2.7.2 マイルストーンとタスク優先順位
- **マイルストーン1: 基本機能実装**（3日後）
  - FastAPI バックエンド構築
  - React フロントエンド構築
  - 基本的なチャット機能
- **マイルストーン2: Claude Code CLI統合**（5日後）
  - CLI実行機能
  - レスポンス処理
  - エラーハンドリング
- **マイルストーン3: MCP対応・デプロイ**（7日後）
  - MCP クライアント実装
  - Docker化
  - ラズパイ対応

#### 2.7.3 リスク管理
- **Claude Code CLI統合の複雑さ**
  - 対応策: 段階的実装、プロトタイプ検証
- **MCP仕様の理解不足**
  - 対応策: 公式ドキュメント精読、サンプル実装
- **ラズパイ性能制限**
  - 対応策: 軽量化設計、最適化実装