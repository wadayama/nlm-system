# Natural Language Macro (NLM) System

## プロジェクト概要

このプロジェクトは自然言語マクロ実行システムです。LLMを使用して自然言語の指示を解釈・実行し、変数の保存・取得・履歴管理を行います。マルチエージェントシステムへの拡張を視野に入れた設計となっています。

## 主要コンポーネント

### コアファイル
- **`nlm_interpreter.py`** - 自然言語マクロの解釈・実行エンジン
- **`variable_db.py`** - SQLiteベースの変数ストレージ管理
- **`variable_history.py`** - 変数変更履歴のトラッキング（デフォルトOFF）
- **`variables.db`** - SQLite データベースファイル

### ツール
- **`history_viewer.py`** - 変数履歴の表示・分析ツール
- **`watch_variables.py`** - リアルタイム変数監視ツール

### 実装計画
- **`AGENT_ARCHITECTURE_IMPLEMENTATION_PLAN.md`** - マルチエージェントシステムの詳細設計書

## 主要機能

### 1. 変数管理システム
- **ローカル変数**: セッション固有の名前空間で管理 (`namespace:key`)
- **グローバル変数**: `@`プレフィックスで全セッション共有 (`@global_key`)
- **履歴管理**: オプトイン方式のロギング機能

### 2. 自然言語マクロ実行
```python
from nlm_interpreter import NLMSession

# セッション作成
session = NLMSession(namespace="agent_1")

# マクロ実行
session.execute("Save 'Hello World' to {{greeting}}")

# 変数アクセス
session.save("config", "value")        # ローカル変数
session.save("@shared", "value")        # グローバル変数
value = session.get("config")
```

### 3. マルチエージェント対応
- セッションベースの名前空間分離
- グローバル変数による協調通信
- 状態外部化による透明性確保

## 開発環境設定

### 必要要件
- Python 3.8+
- LMStudio または Ollama
- SQLite3

### LLMエンドポイント設定
```python
# デフォルト: LMStudio
endpoint = "http://localhost:1234/v1"

# Ollama使用時
endpoint = "http://localhost:11434/v1"
```

## テスト実行

```bash
# 基本テスト
python tests/test_nlm_interpreter.py
python tests/test_variable_db_basic.py

# API機能テスト
python tests/test_at_prefix_api.py
python tests/test_global_sharing.py

# マクロ実行テスト
python tests/test_haiku_generation.py
```

## 次期開発予定

### Agent継承アーキテクチャ実装
2週間後に実装予定の主要機能：

1. **抽象基底クラス設計**
   - `Agent(ABC)` による統一インターフェース
   - 抽象`run()`メソッドによる実装強制

2. **エージェントタイプ**
   - Simple Agent: 1回実行型（80%のユースケース）
   - Complex Agent: 継続実行型（20%の高度なケース）

3. **実装の詳細**
   - 詳細は `AGENT_ARCHITECTURE_IMPLEMENTATION_PLAN.md` を参照

## プロジェクト構成

```
nlm_system/
├── コアファイル
│   ├── nlm_interpreter.py      # マクロ実行エンジン
│   ├── variable_db.py          # 変数ストレージ
│   ├── variable_history.py     # 履歴管理
│   └── variables.db            # SQLiteデータベース
├── ツール
│   ├── history_viewer.py       # 履歴ビューア
│   └── watch_variables.py      # 変数監視ツール
├── テスト
│   └── tests/                  # 重要テストファイル群
├── 設計書
│   ├── README.md               # システム説明
│   ├── CLAUDE.md              # このファイル
│   └── AGENT_ARCHITECTURE_IMPLEMENTATION_PLAN.md
└── その他
    ├── examples/              # 使用例
    └── macros/               # マクロサンプル

```

## LLMへの指示

### このプロジェクトで作業する際は：

1. **状態外部化を維持**: すべての状態はSQLiteデータベースに保存
2. **名前空間を意識**: ローカル変数とグローバル変数の適切な使い分け
3. **履歴管理はオプトイン**: デフォルトでOFF、必要時のみ有効化
4. **Agent設計思想を理解**: 継承ベースアーキテクチャの利点を活かす
5. **テストを重視**: 変更時は必ずテストを実行

### 開発時の注意点：

- **Python 3.8+** の機能を前提とする
- **asyncio** による非同期処理を活用
- **型ヒント** を可能な限り使用
- **エラーハンドリング** を適切に実装
- **ログ出力** で動作を追跡可能にする

### コーディング規約：

- PEP 8準拠
- docstring必須（Google Style）
- 変数名は説明的に
- 関数は単一責任原則に従う

## 連絡先・リポジトリ

- GitHub: `nlm-system` (プライベートリポジトリ)
- 開発者: wadayama

---

*このファイルは新しいセッション開始時の参照ドキュメントです。プロジェクトの全体像を把握し、適切な開発を行うために参照してください。*