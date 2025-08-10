#!/usr/bin/env python3
"""Test variable expansion functionality in detail"""

import os
import sys

from nlm_interpreter import NLMSession


def test_basic_variable_expansion():
    """Test basic variable expansion patterns"""
    print("=== Test Basic Variable Expansion ===")
    
    try:
        session = NLMSession(namespace="expansion_test")
        
        # Test the actual behavior of _expand_variables
        # It should handle variables that exist in the current format
        
        # Save in the correct format for testing expansion
        session.variable_db.save_variable("expansion_test:name", "Alice")
        session.variable_db.save_variable("expansion_test:age", "25") 
        session.variable_db.save_variable("global:project", "AI Research")
        
        # Test simple expansion
        result = session._expand_variables("Hello {{name}}")
        assert result == "Hello Alice", f"Expected 'Hello Alice', got '{result}'"
        
        # Test global variable expansion
        result = session._expand_variables("Project: {{@project}}")
        assert result == "Project: AI Research", f"Expected 'Project: AI Research', got '{result}'"
        
        # Test multiple variables
        result = session._expand_variables("{{name}} is {{age}} years old")
        assert result == "Alice is 25 years old", f"Expected 'Alice is 25 years old', got '{result}'"
        
        print("✓ Basic variable expansion works correctly")
        return True
        
    except Exception as e:
        print(f"❌ Basic variable expansion test failed: {e}")
        return False


def test_non_existent_variable_expansion():
    """Test expansion of non-existent variables"""
    print("\n=== Test Non-existent Variable Expansion ===")
    
    try:
        session = NLMSession(namespace="expansion_test")
        
        # Test non-existent local variable
        result = session._expand_variables("Value: {{non_existent}}")
        assert result == "Value: {{non_existent}}", f"Non-existent variable should remain unchanged, got '{result}'"
        
        # Test non-existent global variable
        result = session._expand_variables("Global: {{@non_existent}}")
        assert result == "Global: {{@non_existent}}", f"Non-existent global should remain unchanged, got '{result}'"
        
        print("✓ Non-existent variables handled correctly")
        return True
        
    except Exception as e:
        print(f"❌ Non-existent variable expansion test failed: {e}")
        return False


def test_empty_variable_expansion():
    """Test expansion of empty variables"""
    print("\n=== Test Empty Variable Expansion ===")
    
    try:
        session = NLMSession(namespace="expansion_test")
        
        # Set empty variables
        session.save("empty_local", "")
        session.save("@empty_global", "")
        
        # Test empty variable expansion
        result = session._expand_variables("Value: {{empty_local}}")
        assert result == "Value: {{empty_local}}", f"Empty variable should remain as placeholder, got '{result}'"
        
        result = session._expand_variables("Global: {{@empty_global}}")
        assert result == "Global: {{@empty_global}}", f"Empty global should remain as placeholder, got '{result}'"
        
        print("✓ Empty variables handled correctly")
        return True
        
    except Exception as e:
        print(f"❌ Empty variable expansion test failed: {e}")
        return False


def test_complex_expansion_patterns():
    """Test complex variable expansion patterns"""
    print("\n=== Test Complex Expansion Patterns ===")
    
    try:
        session = NLMSession(namespace="expansion_test")
        
        # Set up variables with special characters
        session.save("path", "/data/file.txt")
        session.save("command", "uv run script.py")
        session.save("@config_file", "config.json")
        session.save("json_data", '{"key": "value"}')
        
        # Test with special characters
        result = session._expand_variables("Execute {{command}} with {{path}}")
        expected = "Execute uv run script.py with /data/file.txt"
        assert result == expected, f"Expected '{expected}', got '{result}'"
        
        # Test with JSON-like content
        result = session._expand_variables("Data: {{json_data}}")
        expected = 'Data: {"key": "value"}'
        assert result == expected, f"Expected '{expected}', got '{result}'"
        
        # Test with mixed local and global
        result = session._expand_variables("Run {{command}} using config {{@config_file}}")
        expected = "Run uv run script.py using config config.json"
        assert result == expected, f"Expected '{expected}', got '{result}'"
        
        print("✓ Complex expansion patterns work correctly")
        return True
        
    except Exception as e:
        print(f"❌ Complex expansion patterns test failed: {e}")
        return False


def test_namespace_variable_expansion():
    """Test expansion of variables from different namespaces"""
    print("\n=== Test Namespace Variable Expansion ===")
    
    try:
        session1 = NLMSession(namespace="session1")
        session2 = NLMSession(namespace="session2")
        
        # Set variables in different sessions
        session1.save("local_var", "session1_value")
        session2.save("local_var", "session2_value")
        session1.save("@global_var", "shared_value")
        
        # Test local variable expansion (should remain as is if from different session)
        result = session1._expand_variables("Value: {{local_var}}")
        assert result == "Value: session1_value", f"Expected session1 local value, got '{result}'"
        
        result = session2._expand_variables("Value: {{local_var}}")
        assert result == "Value: session2_value", f"Expected session2 local value, got '{result}'"
        
        # Test global variable expansion (should work from both sessions)
        result = session1._expand_variables("Global: {{@global_var}}")
        assert result == "Global: shared_value", f"Expected shared global value from session1, got '{result}'"
        
        result = session2._expand_variables("Global: {{@global_var}}")
        assert result == "Global: shared_value", f"Expected shared global value from session2, got '{result}'"
        
        print("✓ Namespace variable expansion works correctly")
        return True
        
    except Exception as e:
        print(f"❌ Namespace variable expansion test failed: {e}")
        return False


def test_edge_case_expansion():
    """Test edge cases in variable expansion"""
    print("\n=== Test Edge Case Expansion ===")
    
    try:
        session = NLMSession(namespace="expansion_test")
        
        # Variables with edge case names
        session.save("_underscore", "underscore_value")
        session.save("123numeric", "numeric_value")
        session.save("@_global", "global_underscore")
        
        # Test underscore variables
        result = session._expand_variables("Value: {{_underscore}}")
        assert result == "Value: underscore_value", f"Expected underscore expansion, got '{result}'"
        
        # Test numeric prefix variables  
        result = session._expand_variables("Value: {{123numeric}}")
        assert result == "Value: numeric_value", f"Expected numeric expansion, got '{result}'"
        
        # Test global with underscore
        result = session._expand_variables("Global: {{@_global}}")
        assert result == "Global: global_underscore", f"Expected global underscore expansion, got '{result}'"
        
        # Test variables with values containing braces
        session.save("braces_value", "{{not_a_variable}}")
        result = session._expand_variables("Value: {{braces_value}}")
        assert result == "Value: {{not_a_variable}}", f"Expected literal braces in value, got '{result}'"
        
        print("✓ Edge case expansion works correctly")
        return True
        
    except Exception as e:
        print(f"❌ Edge case expansion test failed: {e}")
        return False


def test_recursive_expansion_prevention():
    """Test that recursive expansion is handled safely"""
    print("\n=== Test Recursive Expansion Prevention ===")
    
    try:
        session = NLMSession(namespace="expansion_test")
        
        # Set up potentially recursive variables
        session.save("recursive1", "{{recursive2}}")
        session.save("recursive2", "{{recursive1}}")
        
        # Test recursive expansion (should not cause infinite loop)
        result = session._expand_variables("Value: {{recursive1}}")
        # Should either remain unexpanded or handle recursion gracefully
        print(f"  Recursive expansion result: '{result}'")
        
        # Test self-referencing variable
        session.save("self_ref", "{{self_ref}}")
        result = session._expand_variables("Value: {{self_ref}}")
        print(f"  Self-reference result: '{result}'")
        
        print("✓ Recursive expansion handled safely")
        return True
        
    except Exception as e:
        print(f"❌ Recursive expansion test failed: {e}")
        return False


def test_whitespace_in_expansion():
    """Test handling of whitespace in variable expansion"""
    print("\n=== Test Whitespace in Expansion ===")
    
    try:
        session = NLMSession(namespace="expansion_test")
        
        # Variables with whitespace in values
        session.save("spaced_value", "  value with spaces  ")
        session.save("@multi_line", "line1\nline2\nline3")
        
        # Test whitespace preservation
        result = session._expand_variables("Value: {{spaced_value}}")
        assert result == "Value:   value with spaces  ", f"Expected whitespace preservation, got '{result}'"
        
        # Test multiline values
        result = session._expand_variables("Data: {{@multi_line}}")
        expected = "Data: line1\nline2\nline3"
        assert result == expected, f"Expected multiline preservation, got '{result}'"
        
        print("✓ Whitespace in expansion handled correctly")
        return True
        
    except Exception as e:
        print(f"❌ Whitespace expansion test failed: {e}")
        return False


def run_variable_expansion_tests():
    """Run all variable expansion tests"""
    print("🔄 Variable Expansion Detailed Tests")
    print("=" * 50)
    
    tests = [
        test_basic_variable_expansion,
        test_non_existent_variable_expansion,
        test_empty_variable_expansion,
        test_complex_expansion_patterns,
        test_namespace_variable_expansion,
        test_edge_case_expansion,
        test_recursive_expansion_prevention,
        test_whitespace_in_expansion
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
            print("✅ PASSED")
        else:
            print("❌ FAILED")
    
    print(f"\n📊 Variable Expansion Test Results: {passed}/{total} tests passed")
    return passed == total


if __name__ == "__main__":
    success = run_variable_expansion_tests()
    sys.exit(0 if success else 1)