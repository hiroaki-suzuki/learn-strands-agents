"""
Strands Agents 学習: 外部APIを呼ぶエージェント

このサンプルでは、エージェントが外部APIと連携する方法を学びます。
実際のWebサービスからデータを取得し、それを元に回答を生成します。

【アーキテクチャ図】

    ユーザー
       ↓ 質問「東京の天気は？」
    ┌─────────────────────────────────────────────────────┐
    │                    Agent                            │
    │  ┌─────────┐   ┌─────────────┐   ┌──────────────┐  │
    │  │   LLM   │ → │ ツール選択   │ → │ get_weather  │  │
    │  │(Bedrock)│   │             │   │              │  │
    │  └─────────┘   └─────────────┘   └──────┬───────┘  │
    └─────────────────────────────────────────│───────────┘
                                              ↓
                                    ┌──────────────────┐
                                    │   外部API        │
                                    │ (Open-Meteo API) │
                                    └──────────────────┘
                                              ↓
    ユーザー ← 「東京は晴れ、気温15度です」 ← Agent

【処理フロー】
1. ユーザーが「東京の天気は？」と質問
2. LLMが get_weather ツールを選択
3. ツールが Open-Meteo API を呼び出し
4. APIから天気データを取得
5. LLMがデータを自然言語で回答にまとめる

【使用API】
- Open-Meteo: 無料の天気予報API（APIキー不要）
  https://open-meteo.com/
"""

import httpx
from strands import Agent, tool


# ============================================================
# 都市の座標データ（緯度・経度）
# ============================================================
CITY_COORDINATES = {
    "東京": {"lat": 35.6762, "lon": 139.6503},
    "大阪": {"lat": 34.6937, "lon": 135.5023},
    "名古屋": {"lat": 35.1815, "lon": 136.9066},
    "札幌": {"lat": 43.0618, "lon": 141.3545},
    "福岡": {"lat": 33.5904, "lon": 130.4017},
    "京都": {"lat": 35.0116, "lon": 135.7681},
    "横浜": {"lat": 35.4437, "lon": 139.6380},
    "神戸": {"lat": 34.6901, "lon": 135.1956},
}

# 天気コードの日本語マッピング
WEATHER_CODES = {
    0: "快晴",
    1: "晴れ",
    2: "一部曇り",
    3: "曇り",
    45: "霧",
    48: "着氷性の霧",
    51: "軽い霧雨",
    53: "霧雨",
    55: "濃い霧雨",
    61: "小雨",
    63: "雨",
    65: "大雨",
    71: "小雪",
    73: "雪",
    75: "大雪",
    80: "にわか雨",
    81: "にわか雨（強め）",
    82: "激しいにわか雨",
    95: "雷雨",
    96: "雷雨（雹あり）",
    99: "激しい雷雨（雹あり）",
}


# ============================================================
# ツールの定義
# ============================================================


@tool
def get_weather(city: str) -> str:
    """指定された都市の現在の天気情報を取得します。

    Args:
        city: 天気を取得したい都市名（例: 東京、大阪、名古屋）

    Returns:
        天気情報（気温、天気、湿度、風速を含む）
    """
    print(f"[ツール実行] get_weather({city})")

    # 都市の座標を取得
    if city not in CITY_COORDINATES:
        available = "、".join(CITY_COORDINATES.keys())
        return f"エラー: '{city}'は対応していません。対応都市: {available}"

    coords = CITY_COORDINATES[city]

    # Open-Meteo APIを呼び出し
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": coords["lat"],
        "longitude": coords["lon"],
        "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
        "timezone": "Asia/Tokyo",
    }

    print(f"  → API呼び出し: {url}")

    try:
        response = httpx.get(url, params=params, timeout=10.0)
        response.raise_for_status()
        data = response.json()

        current = data["current"]
        weather_code = current["weather_code"]
        weather_desc = WEATHER_CODES.get(weather_code, f"不明({weather_code})")

        result = f"""
都市: {city}
天気: {weather_desc}
気温: {current['temperature_2m']}°C
湿度: {current['relative_humidity_2m']}%
風速: {current['wind_speed_10m']} km/h
"""
        print(f"  → 取得成功: {weather_desc}, {current['temperature_2m']}°C")
        return result.strip()

    except httpx.HTTPError as e:
        return f"エラー: 天気情報の取得に失敗しました - {e}"


@tool
def get_weather_forecast(city: str, days: int = 3) -> str:
    """指定された都市の天気予報を取得します。

    Args:
        city: 天気予報を取得したい都市名
        days: 予報を取得する日数（1〜7日、デフォルト3日）

    Returns:
        天気予報情報
    """
    print(f"[ツール実行] get_weather_forecast({city}, days={days})")

    if city not in CITY_COORDINATES:
        available = "、".join(CITY_COORDINATES.keys())
        return f"エラー: '{city}'は対応していません。対応都市: {available}"

    coords = CITY_COORDINATES[city]
    days = min(max(days, 1), 7)  # 1〜7日の範囲に制限

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": coords["lat"],
        "longitude": coords["lon"],
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
        "timezone": "Asia/Tokyo",
        "forecast_days": days,
    }

    print(f"  → API呼び出し: {url} ({days}日間の予報)")

    try:
        response = httpx.get(url, params=params, timeout=10.0)
        response.raise_for_status()
        data = response.json()

        daily = data["daily"]
        result_lines = [f"{city}の{days}日間の天気予報:", ""]

        for i in range(days):
            date = daily["time"][i]
            weather_code = daily["weather_code"][i]
            weather_desc = WEATHER_CODES.get(weather_code, f"不明({weather_code})")
            temp_max = daily["temperature_2m_max"][i]
            temp_min = daily["temperature_2m_min"][i]
            precip_prob = daily["precipitation_probability_max"][i]

            result_lines.append(
                f"  {date}: {weather_desc}, {temp_min}°C〜{temp_max}°C, 降水確率{precip_prob}%"
            )

        print(f"  → 取得成功: {days}日分の予報データ")
        return "\n".join(result_lines)

    except httpx.HTTPError as e:
        return f"エラー: 天気予報の取得に失敗しました - {e}"


@tool
def list_available_cities() -> str:
    """天気情報を取得できる都市の一覧を返します。

    Returns:
        対応している都市のリスト
    """
    print("[ツール実行] list_available_cities()")
    cities = "、".join(CITY_COORDINATES.keys())
    return f"対応している都市: {cities}"


# ============================================================
# エージェントの作成
# ============================================================

agent = Agent(
    tools=[get_weather, get_weather_forecast, list_available_cities],
    system_prompt="""あなたは親切な天気予報アシスタントです。
ユーザーの質問に対して、適切なツールを使って天気情報を提供してください。

ガイドライン:
- 現在の天気を聞かれたら get_weather を使用
- 予報を聞かれたら get_weather_forecast を使用
- 対応都市がわからない場合は list_available_cities を使用
- 天気情報は分かりやすく、親しみやすい言葉で伝えてください
- 必要に応じて、服装のアドバイスなども添えてください
""",
)


# ============================================================
# エージェントの実行
# ============================================================
def main():
    """外部API連携エージェントの動作例を順に実行します。"""
    print("=" * 60)
    print("外部APIを呼ぶエージェントのデモ（天気予報）")
    print("=" * 60)
    print()

    # テスト1: 現在の天気
    print("【質問1】東京の天気を教えて")
    print("-" * 40)
    response1 = agent("東京の天気を教えて")
    print(f"\n【回答】{response1}")
    print()

    # テスト2: 天気予報
    print("【質問2】大阪の3日間の天気予報は？")
    print("-" * 40)
    response2 = agent("大阪の3日間の天気予報は？")
    print(f"\n【回答】{response2}")
    print()

    # テスト3: 複数都市の比較（エージェントの判断力を見る）
    print("【質問3】東京と札幌、どっちが今寒い？")
    print("-" * 40)
    response3 = agent("東京と札幌、どっちが今寒い？")
    print(f"\n【回答】{response3}")
    print()

    # テスト4: 対応都市の確認
    print("【質問4】どの都市の天気が調べられますか？")
    print("-" * 40)
    response4 = agent("どの都市の天気が調べられますか？")
    print(f"\n【回答】{response4}")


if __name__ == "__main__":
    main()
