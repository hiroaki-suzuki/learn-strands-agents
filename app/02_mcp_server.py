"""
FastMCP サーバー: 天気情報を提供するMCPサーバー

このサンプルでは、FastMCPを使ってMCPサーバーを作成します。
このサーバーは、Strands AgentやClaude Desktop等のMCPクライアントから
利用できます。

【アーキテクチャ図】

    ┌─────────────────────────────────────────────────────────┐
    │                    MCPサーバー                          │
    │                  (このファイル)                         │
    │  ┌─────────────────────────────────────────────────┐   │
    │  │  FastMCP("weather-server")                      │   │
    │  │                                                  │   │
    │  │  ツール:                                         │   │
    │  │  - get_weather(city) : 天気情報を取得            │   │
    │  │  - get_forecast(city, days) : 天気予報を取得     │   │
    │  │                                                  │   │
    │  │  リソース:                                       │   │
    │  │  - weather://cities : 対応都市一覧               │   │
    │  └─────────────────────────────────────────────────┘   │
    │                         ↑                               │
    │                    MCP プロトコル                       │
    │                    (stdio/SSE)                         │
    └─────────────────────────────────────────────────────────┘
                              ↑
                    MCPクライアントから接続
                    (Strands Agent, Claude Desktop等)

【実行方法】
    # サーバー単体テスト (開発モード)
    cd app && uv run fastmcp dev 02_mcp_server.py

    # サーバー起動 (stdioモード - Strands Agentから利用)
    cd app && uv run python 02_mcp_server.py
"""

from fastmcp import FastMCP

# MCPサーバーのインスタンスを作成
# この名前はクライアントから識別するために使用されます
mcp = FastMCP(
    name="weather-server",
    instructions="天気情報を提供するサーバーです。都市名を指定して天気を取得できます。",
)

# ============================================================
# ダミーの天気データ（実際のアプリではAPIから取得）
# ============================================================
WEATHER_DATA = {
    "東京": {"temp": 22, "condition": "晴れ", "humidity": 45},
    "大阪": {"temp": 24, "condition": "曇り", "humidity": 55},
    "名古屋": {"temp": 23, "condition": "晴れ", "humidity": 50},
    "札幌": {"temp": 15, "condition": "雨", "humidity": 70},
    "福岡": {"temp": 25, "condition": "晴れ", "humidity": 60},
}

FORECAST_DATA = {
    "東京": ["晴れ", "晴れ", "曇り", "雨", "晴れ"],
    "大阪": ["曇り", "雨", "雨", "晴れ", "晴れ"],
    "名古屋": ["晴れ", "晴れ", "晴れ", "曇り", "曇り"],
    "札幌": ["雨", "曇り", "晴れ", "晴れ", "雪"],
    "福岡": ["晴れ", "晴れ", "曇り", "曇り", "晴れ"],
}


# ============================================================
# MCPツールの定義
# ============================================================
# @mcp.tool() デコレータでツールを定義します
# これらのツールはMCPクライアントから呼び出し可能になります


@mcp.tool()
def get_weather(city: str) -> str:
    """指定された都市の現在の天気情報を取得します。

    Args:
        city: 天気を取得したい都市名（例: 東京、大阪）

    Returns:
        天気情報の文字列
    """
    if city not in WEATHER_DATA:
        available = ", ".join(WEATHER_DATA.keys())
        return f"エラー: '{city}'の天気データはありません。利用可能な都市: {available}"

    data = WEATHER_DATA[city]
    return (
        f"{city}の天気:\n"
        f"  気温: {data['temp']}°C\n"
        f"  天候: {data['condition']}\n"
        f"  湿度: {data['humidity']}%"
    )


@mcp.tool()
def get_forecast(city: str, days: int = 3) -> str:
    """指定された都市の天気予報を取得します。

    Args:
        city: 天気予報を取得したい都市名
        days: 予報日数（1-5日、デフォルト3日）

    Returns:
        天気予報の文字列
    """
    if city not in FORECAST_DATA:
        available = ", ".join(FORECAST_DATA.keys())
        return f"エラー: '{city}'の予報データはありません。利用可能な都市: {available}"

    days = min(max(days, 1), 5)  # 1-5日の範囲に制限
    forecast = FORECAST_DATA[city][:days]

    lines = [f"{city}の{days}日間の天気予報:"]
    for i, weather in enumerate(forecast, 1):
        lines.append(f"  {i}日目: {weather}")

    return "\n".join(lines)


# ============================================================
# MCPリソースの定義（オプション）
# ============================================================
# リソースはクライアントが読み取れる静的/動的なデータです


@mcp.resource("weather://cities")
def list_cities() -> str:
    """利用可能な都市の一覧を返します。"""
    return "利用可能な都市:\n" + "\n".join(f"  - {city}" for city in WEATHER_DATA.keys())


# ============================================================
# サーバー起動
# ============================================================
if __name__ == "__main__":
    # stdioモードでサーバーを起動
    # Strands AgentはこのモードでMCPサーバーと通信します
    mcp.run()
