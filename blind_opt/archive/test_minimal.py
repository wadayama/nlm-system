#!/usr/bin/env python3
"""Minimal test to isolate the issue"""

print("Starting minimal test...")

# Test 1: Import nlm_interpreter
try:
    from nlm_interpreter import NLMSession
    print("✓ Import successful")
except Exception as e:
    print(f"✗ Import failed: {e}")
    exit(1)

# Test 2: Create session with local model
try:
    print("Creating NLMSession with local model...")
    session = NLMSession(namespace="test", model="gpt-oss:20b")
    print("✓ Session created")
except Exception as e:
    print(f"✗ Session creation failed: {e}")
    exit(1)

# Test 3: Simple execution
try:
    print("Executing simple macro...")
    result = session.execute("Save 'test' to {{var}}")
    print(f"✓ Execution successful: {result[:50]}...")
except Exception as e:
    print(f"✗ Execution failed: {e}")
    exit(1)

print("\nAll tests passed!")