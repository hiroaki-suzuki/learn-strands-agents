"""
Strands Agents 学習: カスタムツールを持つエージェント

このサンプルでは、エージェントにカスタムツールを追加する方法を学びます。
ツールとは、エージェントが実行できる「機能」のことです。

【アーキテクチャ図】

    ユーザー
       ↓ 質問「3と5を足して」
    ┌─────────────────────────────────┐
    │          Agent                  │
    │  ┌─────────┐   ┌─────────────┐ │
    │  │  LLM    │ → │ ツール選択   │ │
    │  │(Bedrock)│ ← │ add_numbers │ │
    │  └─────────┘   └─────────────┘ │
    └─────────────────────────────────┘
       ↓ 回答「3と5の合計は8です」
    ユーザー

【処理フロー】
1. ユーザーが質問を入力
2. LLMが質問を解析し、適切なツールを選択
3. ツールが実行され、結果を返す
4. LLMが結果を自然言語で回答にまとめる
"""

from strands import Agent, tool


# ============================================================
# ツールの定義
# ============================================================
# @tool デコレータを使って関数をツールとして定義します
# docstringがツールの説明としてLLMに渡されます


@tool
def add_numbers(a: int, b: int) -> int:
    """2つの数値を足し算します。

    Args:
        a: 1つ目の数値
        b: 2つ目の数値

    Returns:
        2つの数値の合計
    """
    print(f"[ツール実行] add_numbers({a}, {b})")
    return a + b


@tool
def multiply_numbers(a: int, b: int) -> int:
    """2つの数値を掛け算します。

    Args:
        a: 1つ目の数値
        b: 2つ目の数値

    Returns:
        2つの数値の積
    """
    print(f"[ツール実行] multiply_numbers({a}, {b})")
    return a * b


@tool
def get_current_time() -> str:
    """現在の日時を取得します。

    Returns:
        現在の日時（日本時間）
    """
    from datetime import datetime, timezone, timedelta

    jst = timezone(timedelta(hours=9))
    now = datetime.now(jst)
    result = now.strftime("%Y年%m月%d日 %H時%M分%S秒")
    print(f"[ツール実行] get_current_time() -> {result}")
    return result


# ============================================================
# エージェントの作成
# ============================================================
# tools引数でエージェントが使用できるツールを指定します

agent = Agent(
    # エージェントが使用できるツールのリスト
    tools=[add_numbers, multiply_numbers, get_current_time],
    # システムプロンプト: エージェントの役割や振る舞いを定義
    system_prompt="""あなたは親切な計算アシスタントです。
ユーザーの質問に対して、適切なツールを使って回答してください。
計算結果は分かりやすく説明してください。""",
)


# ============================================================
# エージェントの実行
# ============================================================
def main():
    print("=" * 60)
    print("カスタムツールを持つエージェントのデモ")
    print("=" * 60)
    print()

    # テスト1: 足し算
    print("【質問1】3と5を足してください")
    print("-" * 40)
    response1 = agent("3と5を足してください")
    print(f"\n【回答】{response1}")
    print()

    # テスト2: 掛け算
    print("【質問2】7と8を掛けてください")
    print("-" * 40)
    response2 = agent("7と8を掛けてください")
    print(f"\n【回答】{response2}")
    print()

    # テスト3: 現在時刻
    print("【質問3】今何時ですか？")
    print("-" * 40)
    response3 = agent("今何時ですか？")
    print(f"\n【回答】{response3}")
    print()

    # テスト4: 複合的な質問（LLMの判断力を見る）
    print("【質問4】12と3を足した後、その結果に2を掛けてください")
    print("-" * 40)
    response4 = agent("12と3を足した後、その結果に2を掛けてください")
    print(f"\n【回答】{response4}")


if __name__ == "__main__":
    main()
