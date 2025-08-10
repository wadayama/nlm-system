#!/usr/bin/env python
"""Test 2: Recursive patterns"""

from nlm_interpreter import NLMSession

print("="*60)
print("2. Recursive pattern test")
print("="*60)

session = NLMSession(namespace="recursive")

# Case 1: Self-referential update (simple version)
print("\nCase 1: Self-referential update (simple)")
session.save("counter", "5")
print(f"Before: counter = {session.get('counter')}")
result = session.execute("Add 1 to {{counter}}")
print(f"After: counter = {session.get('counter')}")

# Case 2: Literal text containing variables
print("\nCase 2: Meta-variables (text containing variable syntax)")
result = session.execute("Save the literal text '{{another}}' to {{template}}")
value = session.get("template")
print(f"Template value: {value}")
if "{{" in str(value) or "another" in str(value):
    print("✅ Variable syntax saved as literal")
else:
    print(f"🤔 Unexpected result: {value}")

# Case 3: Simple swap
print("\nCase 3: Value swapping (simple version)")
session.save("a", "apple")
session.save("b", "banana")
print(f"Before: a={session.get('a')}, b={session.get('b')}")
# Try with simple assignment
session.save("temp", session.get("a"))
session.save("a", session.get("b"))
session.save("b", session.get("temp"))
print(f"After manual swap: a={session.get('a')}, b={session.get('b')}")

print("\n" + "="*60)
print("テスト2完了")