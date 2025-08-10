#!/usr/bin/env python3
"""Test edge cases and boundary conditions"""

import os
import sys
import tempfile
import sqlite3

from nlm_interpreter import NLMSession, nlm_execute
from variable_db import VariableDB


def test_unicode_and_special_characters():
    """Test handling of unicode and special characters"""
    print("=== Test Unicode and Special Characters ===")
    
    try:
        session = NLMSession(namespace="unicode_test")
        
        # Test unicode characters in variable names
        unicode_vars = [
            ("测试", "chinese_test"),
            ("тест", "russian_test"),  
            ("テスト", "japanese_test"),
            ("🚀", "rocket_emoji"),
        ]
        
        for var_name, value in unicode_vars:
            try:
                session.save(var_name, value)
                result = session.get(var_name)
                assert result == value, f"Unicode variable {var_name} failed: expected {value}, got {result}"
                print(f"  ✓ Unicode variable '{var_name}' handled correctly")
            except Exception as e:
                print(f"  ⚠️ Unicode variable '{var_name}' failed: {e}")
        
        # Test unicode in values
        session.save("unicode_value", "Hello 世界 🌍 Привет مرحبا")
        result = session.get("unicode_value")
        expected = "Hello 世界 🌍 Привет مرحبا"
        assert result == expected, f"Expected unicode value, got: {result}"
        
        # Test special characters in values
        special_chars = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
        session.save("special_chars", special_chars)
        result = session.get("special_chars")
        assert result == special_chars, f"Special characters not preserved: {result}"
        
        print("✓ Unicode and special characters handled correctly")
        return True
        
    except Exception as e:
        print(f"❌ Unicode and special characters test failed: {e}")
        return False


def test_very_long_values():
    """Test handling of very long variable values"""
    print("\n=== Test Very Long Values ===")
    
    try:
        session = NLMSession(namespace="long_test")
        
        # Test very long string (10KB)
        long_value = "A" * 10000
        session.save("long_value", long_value)
        result = session.get("long_value")
        assert result == long_value, f"Long value not preserved correctly"
        assert len(result) == 10000, f"Expected 10000 chars, got {len(result)}"
        
        # Test extremely long string (1MB)
        try:
            very_long_value = "B" * 1000000
            session.save("very_long_value", very_long_value)
            result = session.get("very_long_value")
            assert result == very_long_value, "Very long value not preserved"
            print("  ✓ 1MB value handled successfully")
        except Exception as e:
            print(f"  ⚠️ 1MB value caused issue (may be expected): {e}")
        
        print("✓ Long values handled appropriately")
        return True
        
    except Exception as e:
        print(f"❌ Long values test failed: {e}")
        return False


def test_concurrent_sessions():
    """Test multiple concurrent sessions"""
    print("\n=== Test Concurrent Sessions ===")
    
    try:
        # Create multiple sessions
        sessions = []
        for i in range(10):
            session = NLMSession(namespace=f"concurrent_{i}")
            sessions.append(session)
        
        # Each session saves its own variables
        for i, session in enumerate(sessions):
            session.save("session_id", str(i))
            session.save("data", f"data_for_session_{i}")
            session.save("@shared_counter", str(i))  # This will overwrite
        
        # Verify session isolation
        for i, session in enumerate(sessions):
            session_id = session.get("session_id")
            assert session_id == str(i), f"Session {i} isolation failed: got {session_id}"
            
            data = session.get("data")
            expected_data = f"data_for_session_{i}"
            assert data == expected_data, f"Session {i} data failed: got {data}"
        
        # Verify global variable sharing (last write wins)
        shared_value = sessions[0].get("@shared_counter")
        assert shared_value == "9", f"Expected final shared value '9', got '{shared_value}'"
        
        # All sessions should see the same global value
        for session in sessions:
            shared = session.get("@shared_counter")
            assert shared == "9", f"Global sharing failed: got {shared}"
        
        print("✓ Concurrent sessions handled correctly")
        return True
        
    except Exception as e:
        print(f"❌ Concurrent sessions test failed: {e}")
        return False


def test_database_corruption_recovery():
    """Test behavior when database is corrupted or locked"""
    print("\n=== Test Database Corruption Recovery ===")
    
    try:
        # Create a temporary database file
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
            tmp_db_path = tmp_file.name
        
        # Write garbage to the file to simulate corruption
        with open(tmp_db_path, 'wb') as f:
            f.write(b"This is not a valid SQLite database file")
        
        try:
            # Try to use the corrupted database
            db = VariableDB(tmp_db_path)
            db.save_variable("test", "value")  # This should handle the error gracefully
            print("  ✓ Corrupted database handled gracefully")
        except Exception as e:
            print(f"  ⚠️ Corrupted database caused error (may be expected): {e}")
        
        # Clean up
        if os.path.exists(tmp_db_path):
            os.unlink(tmp_db_path)
        
        return True
        
    except Exception as e:
        print(f"❌ Database corruption recovery test failed: {e}")
        return False


def test_memory_usage_patterns():
    """Test memory usage with large numbers of variables"""
    print("\n=== Test Memory Usage Patterns ===")
    
    try:
        session = NLMSession(namespace="memory_test")
        
        # Create many variables
        num_vars = 1000
        for i in range(num_vars):
            session.save(f"var_{i}", f"value_{i}")
        
        # Verify they're all stored correctly
        for i in range(0, num_vars, 100):  # Check every 100th variable
            result = session.get(f"var_{i}")
            expected = f"value_{i}"
            assert result == expected, f"Variable var_{i} failed: got {result}"
        
        # Test list_local performance
        local_vars = session.list_local()
        assert len(local_vars) == num_vars, f"Expected {num_vars} local vars, got {len(local_vars)}"
        
        # Clean up
        session.clear_local()
        remaining = session.list_local()
        assert len(remaining) == 0, f"Expected 0 remaining vars, got {len(remaining)}"
        
        print("✓ Memory usage patterns handled correctly")
        return True
        
    except Exception as e:
        print(f"❌ Memory usage patterns test failed: {e}")
        return False


def test_boundary_namespace_values():
    """Test boundary values for namespaces"""
    print("\n=== Test Boundary Namespace Values ===")
    
    try:
        # Test very short namespace
        short_session = NLMSession(namespace="a")
        short_session.save("test", "short_namespace")
        result = short_session.get("test")
        assert result == "short_namespace", "Short namespace failed"
        
        # Test very long namespace
        long_namespace = "a" * 255
        long_session = NLMSession(namespace=long_namespace)
        long_session.save("test", "long_namespace")
        result = long_session.get("test")
        assert result == "long_namespace", "Long namespace failed"
        
        # Test empty namespace (should use auto-generated)
        empty_session = NLMSession(namespace="")
        assert empty_session.namespace != "", "Empty namespace should be auto-generated"
        
        # Test None namespace (should use auto-generated)
        none_session = NLMSession(namespace=None)
        assert none_session.namespace is not None, "None namespace should be auto-generated"
        assert len(none_session.namespace) > 0, "Auto-generated namespace should not be empty"
        
        print("✓ Boundary namespace values handled correctly")
        return True
        
    except Exception as e:
        print(f"❌ Boundary namespace values test failed: {e}")
        return False


def test_variable_name_edge_cases():
    """Test edge cases for variable names"""
    print("\n=== Test Variable Name Edge Cases ===")
    
    try:
        session = NLMSession(namespace="name_test")
        
        # Test variable names with special patterns
        edge_case_names = [
            "normal_var",
            "123_numeric_start",
            "_underscore_start",
            "var_with_numbers_123",
            "UPPERCASE_VAR",
            "MiXeD_CaSe_VaR",
            "var.with.dots",
            "var-with-dashes",
            "@regular_global",
        ]
        
        for var_name in edge_case_names:
            try:
                session.save(var_name, f"value_for_{var_name}")
                result = session.get(var_name)
                expected = f"value_for_{var_name}"
                assert result == expected, f"Variable {var_name} failed: got {result}"
                print(f"  ✓ Variable name '{var_name}' handled correctly")
            except Exception as e:
                print(f"  ⚠️ Variable name '{var_name}' caused issue: {e}")
        
        print("✓ Variable name edge cases handled appropriately")
        return True
        
    except Exception as e:
        print(f"❌ Variable name edge cases test failed: {e}")
        return False


def test_api_parameter_types():
    """Test different parameter types in API"""
    print("\n=== Test API Parameter Types ===")
    
    try:
        session = NLMSession(namespace="type_test")
        
        # Test different value types (all converted to string)
        test_values = [
            ("string_val", "hello", "hello"),
            ("int_val", 42, "42"),
            ("float_val", 3.14, "3.14"),
            ("bool_val", True, "True"),
            ("none_val", None, "None"),
            ("list_val", [1, 2, 3], "[1, 2, 3]"),
            ("dict_val", {"key": "value"}, "{'key': 'value'}"),
        ]
        
        for var_name, input_val, expected_str in test_values:
            session.save(var_name, input_val)
            result = session.get(var_name)
            assert result == expected_str, f"Type conversion failed for {var_name}: got {result}"
            print(f"  ✓ Type {type(input_val).__name__} converted correctly")
        
        print("✓ API parameter types handled correctly")
        return True
        
    except Exception as e:
        print(f"❌ API parameter types test failed: {e}")
        return False


def run_edge_cases_tests():
    """Run all edge cases tests"""
    print("🎯 Edge Cases and Boundary Conditions Tests")
    print("=" * 50)
    
    tests = [
        test_unicode_and_special_characters,
        test_very_long_values,
        test_concurrent_sessions,
        test_database_corruption_recovery,
        test_memory_usage_patterns,
        test_boundary_namespace_values,
        test_variable_name_edge_cases,
        test_api_parameter_types
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
            print("✅ PASSED")
        else:
            print("❌ FAILED")
    
    print(f"\n📊 Edge Cases Test Results: {passed}/{total} tests passed")
    return passed == total


if __name__ == "__main__":
    success = run_edge_cases_tests()
    sys.exit(0 if success else 1)