# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

Strands Agents フレームワークの学習リポジトリ。

公式ドキュメント:
- https://strandsagents.com/latest/documentation/docs/
- https://strandsagents.com/latest/documentation/docs/examples/

## 開発コマンド

### パッケージ管理 (UV)

```bash
# 依存関係のインストール・同期
cd app && uv sync

# アプリケーション実行
cd app && uv run main.py

# 依存関係の追加
cd app && uv add <package-name>
```

### リンティング・フォーマット (Ruff)

```bash
cd app && uv run ruff check .          # リントチェック
cd app && uv run ruff check --fix .    # 自動修正
cd app && uv run ruff format .         # フォーマット
```

### 型チェック (Ty)

```bash
cd app && uv run ty check .
```

## アーキテクチャ

```
learn-strands-agents/
├── app/                    # メインアプリケーション
│   ├── main.py             # エントリーポイント
│   └── pyproject.toml      # Python依存関係 (Python 3.14)
└── .devcontainer/          # 開発コンテナ設定
```

## 開発環境

- **Python**: 3.14
- **パッケージマネージャー**: UV
- **リンター/フォーマッター**: Ruff
- **型チェッカー**: Ty
- **タイムゾーン**: Asia/Tokyo

## 学習サポートの前提条件

このリポジトリはStrands Agentsフレームワークの学習を目的としています。

**サポート方針:**
- ユーザーがStrands Agentsを使って何ができるかを学べるようにする
- AIエージェントとAIアプリケーションの概念を理解できるようにする
- サンプルコードを書き、各コンポーネントがどのように連携してアプリケーション機能を提供するかを説明する
- 効率的な学習を促進するため、段階的かつ実践的なアプローチを取る
