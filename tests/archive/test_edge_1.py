#!/usr/bin/env python
"""Test 1: Ambiguous variable references"""

from nlm_interpreter import NLMSession

print("="*60)
print("1. 曖昧な変数参照テスト")
print("="*60)

session = NLMSession(namespace="ambiguous")

# Case 1: 変数名が文章の一部に見えるケース
print("\nCase 1: {{name}} is ... パターン")
session.save("name", "Alice")
before = session.get("name")
print(f"Before: name = {before}")

result = session.execute("{{name}} is a developer and {{name}} is happy")
after = session.get("name")
print(f"After: name = {after}")

if after != "Alice":
    print(f"✅ 変数が更新された: {after}")
else:
    print("🤔 変数が更新されなかった")

# Case 2: リテラル文字列内の変数構文
print("\nCase 2: リテラル変数構文の保存")
result = session.execute("Set {{message}} to 'The value of {{x}} is unknown'")
value = session.get("message")
print(f"Stored message: {value}")

if "{{x}}" in str(value) or "unknown" in str(value):
    print("✅ リテラルとして正しく保存")
else:
    print(f"🤔 予期しない結果: {value}")

# Case 3: 代名詞との衝突
print("\nCase 3: 代名詞との衝突")
session.save("it", "computer")
print(f"Before: it = {session.get('it')}")
result = session.execute("{{it}} is fast but {{it}} needs repair")
print(f"After: it = {session.get('it')}")

print("\n" + "="*60)
print("テスト1完了")