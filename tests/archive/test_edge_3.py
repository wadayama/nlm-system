#!/usr/bin/env python
"""Test 3: Natural language ambiguity"""

from nlm_interpreter import NLMSession

print("="*60)
print("3. Natural language ambiguity test")
print("="*60)

session = NLMSession(namespace="nlp_ambig")

# Case 1: Homonyms (English example)
print("\nCase 1: Homonym test")
session.save("read", "book")
print(f"Before: read = {session.get('read')}")
# "read" could be a verb or variable name - ambiguous
result = session.execute("I {{read}} the {{read}} yesterday")
print(f"After: read = {session.get('read')}")
print(f"Result: {result[:100]}...")

# Case 2: Partially matching variable names
print("\nCase 2: Partially matching variable names")
session.save("test", "value1")
session.save("testing", "value2")
print(f"Before: test={session.get('test')}, testing={session.get('testing')}")
result = session.execute("Update {{test}} to 'new_value' without changing {{testing}}")
print(f"After: test={session.get('test')}, testing={session.get('testing')}")

if session.get('test') != 'value1' and session.get('testing') == 'value2':
    print("✅ Correctly updated only one variable")
else:
    print("🤔 更新結果が期待と異なる")

print("\n" + "="*60)
print("テスト3完了")