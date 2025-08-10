#!/usr/bin/env python
"""Test 6: Malformed syntax recovery - No LLM needed"""

from nlm_interpreter import NLMSession
from variable_db import VariableDB

print("="*60)
print("6. Malformed syntax recovery test (No LLM needed)")
print("="*60)

# Using NLMSession ensures proper database initialization
session = NLMSession(namespace="edge_test")
db = session.db  # Use initialized database

# Case 1: Variable names with special characters
print("\nCase 1: Variable names with special characters (DB level)")
try:
    db.save_variable("test-with-dashes", "value1")
    value = db.get_variable("test-with-dashes")
    print(f"✅ Variable name with dashes: {value}")
except Exception as e:
    print(f"❌ Error: {e}")

try:
    db.save_variable("test.with.dots", "value2")
    value = db.get_variable("test.with.dots")
    print(f"✅ Variable name with dots: {value}")
except Exception as e:
    print(f"❌ Error: {e}")

# Case 2: Very long variable names
print("\nCase 2: Long variable names")
long_name = "very_" * 50 + "long_name"
try:
    db.save_variable(long_name, "value3")
    value = db.get_variable(long_name)
    print(f"✅ Variable name with {len(long_name)} characters: OK")
except Exception as e:
    print(f"❌ Error: {e}")

# Case 3: Unicode characters
print("\nCase 3: Unicode variable names")
unicode_names = ["😀emoji", "日本語", "العربية", "🔥fire🔥"]
for name in unicode_names:
    try:
        db.save_variable(name, f"value_{name}")
        value = db.get_variable(name)
        print(f"✅ {name}: {value}")
    except Exception as e:
        print(f"❌ {name}: {e}")

# Case 4: Empty strings and special values
print("\nCase 4: Special values")
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
            print(f"✅ {name}: Correctly saved and retrieved")
        else:
            print(f"🤔 {name}: Value changed")
    except Exception as e:
        print(f"❌ {name}: {e}")

print("\n" + "="*60)
print("テスト6完了（LLM不要）")