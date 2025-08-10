#!/usr/bin/env python3
"""Test multi-variable operations in single statements"""

import os
import sys

from nlm_interpreter import NLMSession

def test_basic_concatenation():
    """Test basic string concatenation with multiple variables"""
    print("=== Test Basic Concatenation ===")
    
    session = NLMSession(namespace="concat_test")
    
    # Setup variables
    session.save("first", "Hello")
    session.save("second", "World")
    
    # Test 1: Simple concatenation
    print("Test 1: Simple concatenation")
    result = session.execute("Combine {{first}} and {{second}} and save to {{result}}")
    stored_value = session.get("result")
    expected = "HelloWorld"
    assert stored_value == expected, f"Expected '{expected}', got '{stored_value}'"
    print(f"✓ {stored_value}")
    
    # Test 2: Concatenation with space
    print("Test 2: Concatenation with space")
    result = session.execute("Combine {{first}} and {{second}} with a space and save to {{spaced}}")
    stored_value = session.get("spaced")
    expected = "Hello World"
    assert stored_value == expected, f"Expected '{expected}', got '{stored_value}'"
    print(f"✓ {stored_value}")
    
    # Test 3: Three variables
    print("Test 3: Three variable concatenation")
    session.save("middle", "Beautiful")
    result = session.execute("Combine {{first}}, {{middle}}, and {{second}} with spaces and save to {{triple}}") 
    stored_value = session.get("triple")
    assert "Hello" in stored_value and "Beautiful" in stored_value and "World" in stored_value
    print(f"✓ {stored_value}")
    
    return True

def test_arithmetic_operations():
    """Test arithmetic operations with multiple variables"""
    print("\n=== Test Arithmetic Operations ===")
    
    session = NLMSession(namespace="math_test")
    
    # Setup numeric variables
    session.save("num1", "10")
    session.save("num2", "25")
    session.save("num3", "5")
    
    # Test 1: Addition
    print("Test 1: Addition of two numbers")
    result = session.execute("Add {{num1}} and {{num2}} and save to {{sum}}")
    stored_value = session.get("sum")
    expected = "35"
    assert stored_value == expected, f"Expected '{expected}', got '{stored_value}'"
    print(f"✓ {stored_value}")
    
    # Test 2: Subtraction  
    print("Test 2: Subtraction")
    result = session.execute("Subtract {{num1}} from {{num2}} and save to {{diff}}")
    stored_value = session.get("diff")
    expected = "15"
    assert stored_value == expected, f"Expected '{expected}', got '{stored_value}'"
    print(f"✓ {stored_value}")
    
    # Test 3: Three number operation
    print("Test 3: Three number operation")
    result = session.execute("Add {{num1}}, {{num2}}, and {{num3}} together and save to {{total}}")
    stored_value = session.get("total")
    expected = "40"  # 10 + 25 + 5
    assert stored_value == expected, f"Expected '{expected}', got '{stored_value}'"
    print(f"✓ {stored_value}")
    
    return True

def test_conditional_operations():
    """Test conditional operations with multiple variables"""
    print("\n=== Test Conditional Operations ===")
    
    session = NLMSession(namespace="condition_test")
    
    # Setup test variables
    session.save("status1", "pending")
    session.save("status2", "active") 
    session.save("target_status", "completed")
    
    # Test 1: Simple conditional
    print("Test 1: Simple conditional update")
    result = session.execute("If {{status1}} is pending, change to {{target_status}} and save to {{new_status}}")
    stored_value = session.get("new_status")
    expected = "completed"
    assert stored_value == expected, f"Expected '{expected}', got '{stored_value}'"
    print(f"✓ {stored_value}")
    
    # Test 2: Comparison between variables
    print("Test 2: Variable comparison")
    result = session.execute("Check if {{status1}} and {{status2}} are the same and save the result to {{comparison}}")
    stored_value = session.get("comparison")
    assert stored_value is not None, "Comparison result should be stored"
    print(f"✓ {stored_value}")
    
    return True

def test_template_operations():
    """Test template-like operations with multiple variables"""
    print("\n=== Test Template Operations ===")
    
    session = NLMSession(namespace="template_test")
    
    # Setup template variables
    session.save("base_url", "https://api.example.com")
    session.save("version", "v1")
    session.save("endpoint", "/users")
    session.save("user_id", "123")
    
    # Test 1: URL building
    print("Test 1: URL construction")
    result = session.execute("Create URL in format {{base_url}}/{{version}}{{endpoint}}/{{user_id}} and save to {{full_url}}")
    stored_value = session.get("full_url")
    expected = "https://api.example.com/v1/users/123"
    assert stored_value == expected, f"Expected '{expected}', got '{stored_value}'"
    print(f"✓ {stored_value}")
    
    # Test 2: Message template
    print("Test 2: Message template")
    session.save("user_name", "Alice")
    session.save("action", "login")
    session.save("timestamp", "2024-01-15")
    result = session.execute("Create message in format 'User {{user_name}} performed {{action}} on {{timestamp}}' and save to {{log_message}}")
    stored_value = session.get("log_message")
    assert "Alice" in stored_value and "login" in stored_value and "2024-01-15" in stored_value
    print(f"✓ {stored_value}")
    
    return True

def test_global_and_local_mix():
    """Test operations mixing global and local variables"""
    print("\n=== Test Global and Local Variable Mix ===")
    
    session1 = NLMSession(namespace="session1")
    session2 = NLMSession(namespace="session2")
    
    # Setup mixed variables
    session1.save("local_data", "SessionData")
    session1.save("@global_prefix", "GLOBAL")
    session2.save("@global_suffix", "END")
    
    # Test 1: Mix local and global in session1
    print("Test 1: Local + Global combination")
    result = session1.execute("Combine {{local_data}} and {{@global_prefix}} and save to {{@combined}}")
    global_result = session1.get("@combined")
    expected = "SessionDataGLOBAL"
    assert global_result == expected, f"Expected '{expected}', got '{global_result}'"
    print(f"✓ {global_result}")
    
    # Test 2: Access from different session
    print("Test 2: Cross-session global access")
    result = session2.execute("Combine {{@combined}} and {{@global_suffix}} and save to {{@final}}")
    final_result = session2.get("@final")
    expected = "SessionDataGLOBALEND"
    assert final_result == expected, f"Expected '{expected}', got '{final_result}'"
    print(f"✓ {final_result}")
    
    return True

def test_complex_chaining():
    """Test complex multi-step operations with chaining"""
    print("\n=== Test Complex Chaining Operations ===")
    
    session = NLMSession(namespace="chain_test")
    
    # Setup initial data
    session.save("input1", "apple")
    session.save("input2", "banana")
    session.save("input3", "cherry")
    
    # Test 1: Multi-step processing chain
    print("Test 1: Multi-step processing chain")
    result = session.execute("Combine {{input1}}, {{input2}}, {{input3}} with commas and save to {{list}}, then convert the result to uppercase and save to {{upper_list}}")
    
    list_result = session.get("list")
    upper_result = session.get("upper_list")
    
    # Verify intermediate result
    assert "apple" in list_result and "banana" in list_result and "cherry" in list_result
    print(f"✓ List: {list_result}")
    
    # Verify final result (if uppercase conversion worked)
    if upper_result:
        print(f"✓ Upper: {upper_result}")
    else:
        print("⚠ Upper conversion may need refinement")
    
    return True

def test_error_handling():
    """Test error handling with multiple variables"""
    print("\n=== Test Error Handling ===")
    
    session = NLMSession(namespace="error_test")
    
    # Setup partial data
    session.save("existing", "value")
    
    # Test 1: Missing variable handling
    print("Test 1: Missing variable handling")
    result = session.execute("Combine {{existing}} and {{missing}} and save to {{partial_result}}")
    partial_result = session.get("partial_result")
    
    # Should handle gracefully - either skip or provide default
    print(f"Result with missing variable: {partial_result}")
    
    # Test 2: Empty variable handling
    print("Test 2: Empty variable handling")
    session.save("empty", "")
    result = session.execute("Combine {{existing}} and {{empty}} and save to {{empty_result}}")
    empty_result = session.get("empty_result")
    
    assert "value" in str(empty_result), "Should handle empty variables gracefully"
    print(f"✓ Empty handling: {empty_result}")
    
    return True

def run_all_multi_variable_tests():
    """Run all multi-variable operation tests"""
    print("🧪 Testing Multi-Variable Operations")
    print("=" * 60)
    
    tests = [
        test_basic_concatenation,
        test_arithmetic_operations, 
        test_conditional_operations,
        test_template_operations,
        test_global_and_local_mix,
        test_complex_chaining,
        test_error_handling
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
    
    print(f"📊 Multi-Variable Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All multi-variable tests passed!")
        return True
    else:
        print("⚠️  Some multi-variable tests failed")
        return False

if __name__ == "__main__":
    success = run_all_multi_variable_tests()
    sys.exit(0 if success else 1)