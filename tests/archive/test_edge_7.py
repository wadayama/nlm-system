#!/usr/bin/env python
"""Test 7: Performance tests (without LLM)"""

from nlm_interpreter import NLMSession
import time

print("="*60)
print("7. Performance test (No LLM needed)")
print("="*60)

session = NLMSession(namespace="performance")

# Case 1: Very long variable values
print("\nCase 1: Processing huge values")
long_value = "x" * 10000
session.save("huge", long_value)
retrieved = session.get("huge")
if len(retrieved) == 10000:
    print(f"✅ Successfully saved and retrieved 10,000 character value")
else:
    print(f"❌ Value length mismatch: {len(retrieved)}")

# Case 2: Many variables
print("\nCase 2: Creating many variables")
start = time.time()
for i in range(100):
    session.save(f"var{i}", f"value{i}")
elapsed = time.time() - start
print(f"✅ Created 100 variables in {elapsed:.3f} seconds")

# Case 3: Fast reading
print("\nCase 3: Fast reading")
start = time.time()
for i in range(100):
    value = session.get(f"var{i}")
elapsed = time.time() - start
print(f"✅ Read 100 variables in {elapsed:.3f} seconds")

# Case 4: Memory efficiency (multiple huge values)
print("\nCase 4: Memory efficiency test")
huge_val = "y" * 100000
for i in range(10):
    session.save(f"huge{i}", huge_val)
print(f"✅ Saved 10 variables of 100KB each")

# Case 5: Namespace separation performance
print("\nCase 5: Namespace separation overhead")
sessions = []
start = time.time()
for i in range(10):
    s = NLMSession(namespace=f"ns{i}")
    s.save("test", f"value{i}")
    sessions.append(s)
elapsed = time.time() - start
print(f"✅ Created 10 sessions in {elapsed:.3f} seconds")

# Case 6: Global variable performance
print("\nCase 6: Global variable access")
start = time.time()
for i in range(50):
    session.save(f"@global{i}", f"gvalue{i}")
for i in range(50):
    value = session.get(f"@global{i}")
elapsed = time.time() - start
print(f"✅ Saved and retrieved 50 global variables in {elapsed:.3f} seconds")

print("\n" + "="*60)
print("Test 7 complete")