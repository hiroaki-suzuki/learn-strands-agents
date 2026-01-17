"""
Strands Agent + FastMCP 連携サンプル

このサンプルでは、Strands AgentからFastMCPで作成したMCPサーバーの
ツールを利用する方法を学びます。

【アーキテクチャ図】

    ユーザー
       ↓ 質問「東京の天気は？」
    ┌─────────────────────────────────────────────────────────────┐
    │  Strands Agent (MCPクライアント)                            │
    │  ┌─────────────┐                                            │
    │  │     LLM     │ ← 質問を解析                               │
    │  │  (Bedrock)  │                                            │
    │  └──────┬──────┘                                            │
    │         │                                                    │
    │         │ MCPツールを呼び出し                                │
    │         ↓                                                    │
    │  ┌─────────────────────────────────────────────────────┐    │
    │  │  MCPClient                                          │    │
    │  │  - get_weather(city)     ← MCPサーバーから取得した  │    │
    │  │  - get_forecast(city)      ツール一覧               │    │
    │  └──────────────┬──────────────────────────────────────┘    │
    └─────────────────┼───────────────────────────────────────────┘
                      │ stdio通信
                      ↓
    ┌─────────────────────────────────────────────────────────────┐
    │  MCPサーバー (02_mcp_server.py)                             │
    │  FastMCP("weather-server")                                  │
    │  - get_weather(city)                                        │
    │  - get_forecast(city, days)                                 │
    └─────────────────────────────────────────────────────────────┘

【実行方法】
    cd app && uv run python 03_strands_with_mcp.py

【ポイント】
- MCPサーバーは別プロセスとして起動される（stdioモード）
- Strands AgentはMCPClientを通じてツールを取得
- ツールの実装はMCPサーバー側にあるが、Agentから透過的に利用可能
"""

from pathlib import Path

from mcp import StdioServerParameters, stdio_client
from strands import Agent, tool
from strands.tools.mcp import MCPClient

# ============================================================
# MCPサーバーへの接続設定
# ============================================================
# MCPサーバー（02_mcp_server.py）への接続を設定します
# stdio_client: 標準入出力を使ってサーバーと通信

# MCPサーバーのパスを取得
MCP_SERVER_PATH = Path(__file__).parent / "02_mcp_server.py"

# MCPクライアントを作成
# lambda でファクトリ関数を渡すのがポイント
mcp_client = MCPClient(
    lambda: stdio_client(
        StdioServerParameters(
            # uvを使ってPythonスクリプトを実行
            command="uv",
            args=["run", "python", str(MCP_SERVER_PATH)],
            # 環境変数を引き継ぐ（オプション）
            env=None,
        )
    )
)


# ============================================================
# ローカルツールの定義（MCPツールと併用可能）
# ============================================================


@tool
def get_current_time() -> str:
    """現在の日時を取得します。

    Returns:
        現在の日時（日本時間）
    """
    from datetime import datetime, timedelta, timezone

    jst = timezone(timedelta(hours=9))
    now = datetime.now(jst)
    return now.strftime("%Y年%m月%d日 %H時%M分%S秒")


# ============================================================
# メイン処理
# ============================================================
def main():
    print("=" * 60)
    print("Strands Agent + FastMCP 連携デモ")
    print("=" * 60)
    print()

    # MCPクライアントのコンテキスト内でエージェントを使用
    # with文でMCPサーバーへの接続を管理
    with mcp_client:  # type: ignore[invalid-context-manager]
        # MCPサーバーからツール一覧を取得
        mcp_tools = mcp_client.list_tools_sync()

        print("【接続されたMCPツール】")
        for tool_info in mcp_tools:
            description = tool_info.tool_spec.get("description", "")
            short_desc = f"{description[:50]}..." if description else ""
            print(f"  - {tool_info.tool_name}: {short_desc}")
        print()

        # エージェントを作成
        # MCPツール + ローカルツールを組み合わせ
        agent = Agent(
            tools=[*mcp_tools, get_current_time],  # MCPツール + ローカルツール
            system_prompt="""あなたは天気情報を提供するアシスタントです。
ユーザーの質問に対して、適切なツールを使って回答してください。
天気情報はget_weatherやget_forecastツールで取得できます。
現在時刻はget_current_timeツールで取得できます。""",
        )

        # テスト1: 天気の取得（MCPツール）
        print("【質問1】東京の天気を教えてください")
        print("-" * 40)
        response1 = agent("東京の天気を教えてください")
        print(f"\n【回答】\n{response1}")
        print()

        # テスト2: 天気予報の取得（MCPツール）
        print("【質問2】大阪の3日間の天気予報を教えてください")
        print("-" * 40)
        response2 = agent("大阪の3日間の天気予報を教えてください")
        print(f"\n【回答】\n{response2}")
        print()

        # テスト3: ローカルツールとMCPツールの併用
        print("【質問3】今何時ですか？そして札幌の天気も教えてください")
        print("-" * 40)
        response3 = agent("今何時ですか？そして札幌の天気も教えてください")
        print(f"\n【回答】\n{response3}")
        print()

        # テスト4: 複数都市の比較（エージェントの判断力を見る）
        print("【質問4】東京と福岡、どちらが暖かいですか？")
        print("-" * 40)
        response4 = agent("東京と福岡、どちらが暖かいですか？")
        print(f"\n【回答】\n{response4}")


if __name__ == "__main__":
    main()
