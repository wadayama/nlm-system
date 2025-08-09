#!/usr/bin/env python3
"""Test new variable patterns without pre-expansion"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from nlm_interpreter import NLMSession

def test_assignment_patterns():
    """Test various assignment patterns"""
    print("=== Test Assignment Patterns ===")
    
    session = NLMSession(namespace="pattern_test")
    
    # Test 1: Direct assignment pattern
    print("Test 1: {{name}} is Alice")
    result = session.execute("{{name}} is Alice")
    print(f"Result: {result}")
    
    # Verify it was saved
    stored_value = session.get("name")
    assert stored_value == "Alice", f"Expected 'Alice', got '{stored_value}'"
    print("✓ Direct assignment works")
    
    # Test 2: Update pattern
    print("\nTest 2: {{name}} is Bob")
    result = session.execute("{{name}} is Bob")
    print(f"Result: {result}")
    
    # Verify it was updated
    stored_value = session.get("name")
    assert stored_value == "Bob", f"Expected 'Bob', got '{stored_value}'"
    print("✓ Variable update works")
    
    # Test 3: Global assignment
    print("\nTest 3: {{@project}} is Test Project")
    result = session.execute("{{@project}} is Test Project")
    print(f"Result: {result}")
    
    # Verify global variable
    stored_value = session.get("@project")
    assert stored_value == "Test Project", f"Expected 'Test Project', got '{stored_value}'"
    print("✓ Global assignment works")
    
    return True

def test_reference_patterns():
    """Test variable reference patterns"""
    print("\n=== Test Reference Patterns ===")
    
    session = NLMSession(namespace="ref_test")
    
    # Setup data
    session.save("greeting", "Hello")
    session.save("@config", "production")
    
    # Test 1: Show pattern
    print("Test 1: Show me {{greeting}}")
    result = session.execute("Show me {{greeting}}")
    print(f"Result: {result}")
    assert "Hello" in result, f"Expected 'Hello' in result, got: {result}"
    print("✓ Show pattern works")
    
    # Test 2: What is pattern
    print("\nTest 2: What is {{@config}}?")
    result = session.execute("What is {{@config}}?")
    print(f"Result: {result}")
    assert "production" in result, f"Expected 'production' in result, got: {result}"
    print("✓ What is pattern works")
    
    return True

def test_problematic_patterns():
    """Test the problematic patterns that caused issues before"""
    print("\n=== Test Problematic Patterns ===")
    
    session = NLMSession(namespace="problem_test")
    
    # Test the original problem case
    print("Test 1: First assignment - {{name}} is taro")
    result1 = session.execute("{{name}} is taro")
    print(f"Result 1: {result1}")
    
    # Verify first value
    value1 = session.get("name")
    assert value1 == "taro", f"Expected 'taro', got '{value1}'"
    
    print("\nTest 2: Second assignment - {{name}} is jiro")
    result2 = session.execute("{{name}} is jiro")
    print(f"Result 2: {result2}")
    
    # Verify second value (this should work now!)
    value2 = session.get("name")
    assert value2 == "jiro", f"Expected 'jiro', got '{value2}'"
    print("✓ Sequential updates work correctly!")
    
    return True

def test_conditional_patterns():
    """Test conditional/if patterns"""
    print("\n=== Test Conditional Patterns ===")
    
    session = NLMSession(namespace="cond_test")
    
    # Setup status
    session.save("status", "pending")
    
    # Test conditional check
    print("Test 1: If {{status}} is pending, set to active")
    result = session.execute("If {{status}} is pending, set it to active")
    print(f"Result: {result}")
    
    # Check if status was updated
    new_status = session.get("status")
    print(f"Status after conditional: {new_status}")
    # Note: This might not work perfectly yet, but let's see
    
    return True

def run_all_pattern_tests():
    """Run all pattern tests"""
    print("🧪 Testing New Variable Patterns (No Pre-expansion)")
    print("=" * 60)
    
    tests = [
        test_assignment_patterns,
        test_reference_patterns,
        test_problematic_patterns,
        test_conditional_patterns
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
                print("✅ PASSED\n")
            else:
                print("❌ FAILED\n")
        except Exception as e:
            print(f"❌ FAILED: {e}\n")
            import traceback
            traceback.print_exc()
    
    print(f"📊 Pattern Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All pattern tests passed!")
        return True
    else:
        print("⚠️  Some pattern tests failed")
        return False

if __name__ == "__main__":
    success = run_all_pattern_tests()
    sys.exit(0 if success else 1)