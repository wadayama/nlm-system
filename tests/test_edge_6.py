#!/usr/bin/env python
"""Test 6: Malformed syntax recovery - No LLM needed"""

from nlm_interpreter import NLMSession
from variable_db import VariableDB

print("="*60)
print("6. 不正構文の回復テスト（LLM不要）")
print("="*60)

# NLMSessionを使うことでデータベースが適切に初期化される
session = NLMSession(namespace="edge_test")
db = session.db  # 初期化済みのデータベースを使用

# Case 1: 特殊文字を含む変数名
print("\nCase 1: 特殊文字を含む変数名（DBレベル）")
try:
    db.save_variable("test-with-dashes", "value1")
    value = db.get_variable("test-with-dashes")
    print(f"✅ ダッシュ付き変数名: {value}")
except Exception as e:
    print(f"❌ エラー: {e}")

try:
    db.save_variable("test.with.dots", "value2")
    value = db.get_variable("test.with.dots")
    print(f"✅ ドット付き変数名: {value}")
except Exception as e:
    print(f"❌ エラー: {e}")

# Case 2: 非常に長い変数名
print("\nCase 2: 長い変数名")
long_name = "very_" * 50 + "long_name"
try:
    db.save_variable(long_name, "value3")
    value = db.get_variable(long_name)
    print(f"✅ {len(long_name)}文字の変数名: OK")
except Exception as e:
    print(f"❌ エラー: {e}")

# Case 3: Unicode文字
print("\nCase 3: Unicode変数名")
unicode_names = ["😀emoji", "日本語", "العربية", "🔥fire🔥"]
for name in unicode_names:
    try:
        db.save_variable(name, f"value_{name}")
        value = db.get_variable(name)
        print(f"✅ {name}: {value}")
    except Exception as e:
        print(f"❌ {name}: {e}")

# Case 4: 空文字列や特殊値
print("\nCase 4: 特殊値")
special_values = [
    ("empty", ""),
    ("spaces", "   "),
    ("newline", "line1\nline2"),
    ("tab", "tab\ttab"),
    ("json", '{"key": "value"}'),
    ("sql", "'; DROP TABLE variables; --")
]

for name, value in special_values:
    try:
        db.save_variable(f"special_{name}", value)
        retrieved = db.get_variable(f"special_{name}")
        if retrieved == value:
            print(f"✅ {name}: 正しく保存・取得")
        else:
            print(f"🤔 {name}: 値が変わった")
    except Exception as e:
        print(f"❌ {name}: {e}")

print("\n" + "="*60)
print("テスト6完了（LLM不要）")