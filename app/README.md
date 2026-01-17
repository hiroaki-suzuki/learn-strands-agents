## 概要

`app/` は Strands Agents の学習用サンプル集です。  
小さな例から、外部API連携やMCP連携まで段階的に試せる構成になっています。

## セットアップ

```bash
cd app
uv sync
```

## 使い方（サンプル実行）

最初は小さな例から順に試すのがおすすめです。

### 1. 最小のエージェント

```bash
cd app
uv run agent.py
```

### 2. カスタムツールを使うエージェント

```bash
cd app
uv run 01_tool_agent.py
```

### 3. 外部APIを呼ぶエージェント（天気）

```bash
cd app
uv run 02_api_agent.py
```

注意:
- Open-Meteo API にアクセスするためネットワークが必要です。
- 対応都市は `list_available_cities` ツールで確認できます。

### 4. MCPサーバー（FastMCP）

サーバー単体の起動:

```bash
cd app
uv run 02_mcp_server.py
```

開発モード（自動再起動）:

```bash
cd app
uv run fastmcp dev 02_mcp_server.py
```

### 5. MCPツールを使うエージェント

```bash
cd app
uv run 03_strands_with_mcp.py
```

## 参考: 最小エントリーポイント

動作確認だけしたい場合は `main.py` を使えます。

```bash
cd app
uv run main.py
```

## 学習ポイント

- `01_tool_agent.py`: `@tool` デコレータでツールを定義し、LLMに使わせる
- `02_api_agent.py`: 外部APIを呼ぶツールを通じて、実データで回答を生成する
- `02_mcp_server.py`: MCPサーバー側のツール/リソースを定義する
- `03_strands_with_mcp.py`: MCPクライアントとしてMCPツールを使う
