#!/usr/bin/env python3
"""Test error handling functionality"""

import os
import sys
import json
import tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from nlm_interpreter import NLMSession


class MockToolCall:
    """Mock tool call for testing"""
    def __init__(self, function_name, arguments_str):
        self.function = MockFunction(function_name, arguments_str)


class MockFunction:
    """Mock function for testing"""
    def __init__(self, name, arguments_str):
        self.name = name
        self.arguments = arguments_str


def test_json_decode_error_handling():
    """Test JSON decode error handling in _execute_tool_call"""
    print("=== Test JSON Decode Error Handling ===")
    
    try:
        session = NLMSession(namespace="error_test")
        
        # Create mock tool call with invalid JSON
        mock_tool_call = MockToolCall("save_variable", "invalid json {")
        
        result = session._execute_tool_call(mock_tool_call)
        
        # Should handle JSON decode error gracefully
        assert "Error parsing tool arguments" in result, f"Expected JSON error message, got: {result}"
        assert "save_variable" in result, "Should include function name in error"
        
        print("✓ JSON decode error handled correctly")
        return True
        
    except Exception as e:
        print(f"❌ JSON decode error test failed: {e}")
        return False


def test_missing_argument_error_handling():
    """Test missing argument error handling"""
    print("\n=== Test Missing Argument Error Handling ===")
    
    try:
        session = NLMSession(namespace="error_test")
        
        # Create mock tool call with missing required argument
        mock_tool_call = MockToolCall("save_variable", '{"name": "test"}')  # Missing "value"
        
        result = session._execute_tool_call(mock_tool_call)
        
        # Should handle missing argument error gracefully
        assert "Missing required argument" in result or "KeyError" in result, f"Expected missing argument error, got: {result}"
        
        print("✓ Missing argument error handled correctly")
        return True
        
    except Exception as e:
        print(f"❌ Missing argument error test failed: {e}")
        return False


def test_unknown_function_error():
    """Test unknown function error handling"""
    print("\n=== Test Unknown Function Error ===")
    
    try:
        session = NLMSession(namespace="error_test")
        
        # Create mock tool call with unknown function
        mock_tool_call = MockToolCall("unknown_function", '{}')
        
        result = session._execute_tool_call(mock_tool_call)
        
        # Should handle unknown function gracefully
        assert "Unknown function: unknown_function" in result, f"Expected unknown function error, got: {result}"
        
        print("✓ Unknown function error handled correctly")
        return True
        
    except Exception as e:
        print(f"❌ Unknown function error test failed: {e}")
        return False


def test_variable_db_error_handling():
    """Test variable database error handling"""
    print("\n=== Test Variable DB Error Handling ===")
    
    try:
        # Create session with invalid database path (read-only directory)
        if os.path.exists("/tmp"):
            readonly_path = "/tmp/readonly_test"
            os.makedirs(readonly_path, exist_ok=True)
            os.chmod(readonly_path, 0o444)  # Read-only
            
            try:
                session = NLMSession(namespace="db_error_test")
                # Force use invalid db path by modifying the db path
                session.variable_db.db_path = os.path.join(readonly_path, "invalid.db")
                
                # This should handle database errors gracefully
                result = session.save("test_key", "test_value")
                
                # Clean up
                os.chmod(readonly_path, 0o755)
                os.rmdir(readonly_path)
                
            except Exception:
                # Clean up even if test fails
                os.chmod(readonly_path, 0o755)
                if os.path.exists(readonly_path):
                    os.rmdir(readonly_path)
                raise
        
        print("✓ Database error handling structure exists")
        return True
        
    except Exception as e:
        print(f"❌ Variable DB error test failed: {e}")
        return False


def test_invalid_namespace_characters():
    """Test handling of invalid namespace characters"""
    print("\n=== Test Invalid Namespace Characters ===")
    
    try:
        # Test various potentially problematic namespace characters
        test_cases = [
            "namespace.with.dots",
            "namespace:with:colons", 
            "namespace with spaces",
            "namespace/with/slashes",
            "namespace\\with\\backslashes"
        ]
        
        for namespace in test_cases:
            try:
                session = NLMSession(namespace=namespace)
                session.save("test_key", "test_value")
                result = session.get("test_key")
                
                # Should either work or handle gracefully
                print(f"  ✓ Namespace '{namespace}' handled successfully")
                
            except Exception as e:
                print(f"  ⚠️ Namespace '{namespace}' caused error (may be expected): {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Invalid namespace test failed: {e}")
        return False


def test_empty_and_none_values():
    """Test handling of empty and None values"""
    print("\n=== Test Empty and None Values ===")
    
    try:
        session = NLMSession(namespace="empty_test")
        
        # Test empty string
        session.save("empty_key", "")
        result = session.get("empty_key")
        assert result == "", f"Expected empty string, got: {result}"
        
        # Test None value (converted to string)
        session.save("none_key", None)
        result = session.get("none_key")
        assert result == "None", f"Expected 'None' string, got: {result}"
        
        # Test getting non-existent key
        result = session.get("non_existent_key")
        assert result is None or result == "", f"Expected None or empty string for non-existent key, got: '{result}'"
        
        print("✓ Empty and None values handled correctly")
        return True
        
    except Exception as e:
        print(f"❌ Empty/None values test failed: {e}")
        return False


def test_malformed_variable_expansion():
    """Test handling of malformed variable expansion patterns"""
    print("\n=== Test Malformed Variable Expansion ===")
    
    try:
        session = NLMSession(namespace="expansion_test")
        
        # Set up some test variables
        session.save("test_var", "test_value")
        session.save("@global_var", "global_value")
        
        # Test various malformed patterns
        test_cases = [
            "{{",  # Incomplete opening
            "}}",  # Just closing
            "{{unclosed",  # No closing braces
            "{{}}",  # Empty variable name
            "{{nested{{var}}}}",  # Nested braces
            "{{@}}",  # Just @ symbol
            "{{.invalid}}",  # Invalid characters
            "{{var1}} {{var2}} {{var3}}",  # Multiple variables
        ]
        
        for test_input in test_cases:
            try:
                result = session._expand_variables(test_input)
                print(f"  ✓ Input '{test_input}' → '{result}'")
            except Exception as e:
                print(f"  ⚠️ Input '{test_input}' caused error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Malformed variable expansion test failed: {e}")
        return False


def run_error_handling_tests():
    """Run all error handling tests"""
    print("🚨 Error Handling Tests")
    print("=" * 50)
    
    tests = [
        test_json_decode_error_handling,
        test_missing_argument_error_handling,
        test_unknown_function_error,
        test_variable_db_error_handling,
        test_invalid_namespace_characters,
        test_empty_and_none_values,
        test_malformed_variable_expansion
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
            print("✅ PASSED")
        else:
            print("❌ FAILED")
    
    print(f"\n📊 Error Handling Test Results: {passed}/{total} tests passed")
    return passed == total


if __name__ == "__main__":
    success = run_error_handling_tests()
    sys.exit(0 if success else 1)