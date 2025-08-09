#!/usr/bin/env python
"""Test 2: Recursive patterns"""

from nlm_interpreter import NLMSession

print("="*60)
print("2. 再帰的パターンテスト")
print("="*60)

session = NLMSession(namespace="recursive")

# Case 1: 自己参照的な更新（簡単版）
print("\nCase 1: 自己参照更新（簡単）")
session.save("counter", "5")
print(f"Before: counter = {session.get('counter')}")
result = session.execute("Add 1 to {{counter}}")
print(f"After: counter = {session.get('counter')}")

# Case 2: 変数を含むリテラルテキスト
print("\nCase 2: メタ変数（変数構文を含むテキスト）")
result = session.execute("Save the literal text '{{another}}' to {{template}}")
value = session.get("template")
print(f"Template value: {value}")
if "{{" in str(value) or "another" in str(value):
    print("✅ 変数構文をリテラルとして保存")
else:
    print(f"🤔 予期しない結果: {value}")

# Case 3: 簡単な交換
print("\nCase 3: 値の入れ替え（簡単版）")
session.save("a", "apple")
session.save("b", "banana")
print(f"Before: a={session.get('a')}, b={session.get('b')}")
# 単純な代入で試す
session.save("temp", session.get("a"))
session.save("a", session.get("b"))
session.save("b", session.get("temp"))
print(f"After manual swap: a={session.get('a')}, b={session.get('b')}")

print("\n" + "="*60)
print("テスト2完了")