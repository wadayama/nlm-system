#!/usr/bin/env python
"""Test 3: Natural language ambiguity"""

from nlm_interpreter import NLMSession

print("="*60)
print("3. 自然言語の曖昧性テスト")
print("="*60)

session = NLMSession(namespace="nlp_ambig")

# Case 1: 同音異義語（英語の例）
print("\nCase 1: 同音異義語テスト")
session.save("read", "book")
print(f"Before: read = {session.get('read')}")
# "read"が動詞か変数名か曖昧
result = session.execute("I {{read}} the {{read}} yesterday")
print(f"After: read = {session.get('read')}")
print(f"Result: {result[:100]}...")

# Case 2: 部分一致する変数名
print("\nCase 2: 部分一致する変数名")
session.save("test", "value1")
session.save("testing", "value2")
print(f"Before: test={session.get('test')}, testing={session.get('testing')}")
result = session.execute("Update {{test}} to 'new_value' without changing {{testing}}")
print(f"After: test={session.get('test')}, testing={session.get('testing')}")

if session.get('test') != 'value1' and session.get('testing') == 'value2':
    print("✅ 正しく片方だけ更新された")
else:
    print("🤔 更新結果が期待と異なる")

print("\n" + "="*60)
print("テスト3完了")