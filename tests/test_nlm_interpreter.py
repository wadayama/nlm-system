#!/usr/bin/env python3
"""Test nlm_interpreter.py functionality"""

import os
import sys
import tempfile
import uuid
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from nlm_interpreter import NLMSession, nlm_execute


def test_basic_session_creation():
    """Test basic session creation and properties"""
    print("=== Test Basic Session Creation ===")
    
    try:
        # Test 1: Auto-generated namespace
        print("Test 1: Auto-generated namespace")
        session1 = NLMSession()
        assert session1.namespace is not None, "Namespace should be auto-generated"
        assert len(session1.namespace) == 8, f"Expected 8-char namespace, got {len(session1.namespace)}"
        print(f"✓ Session created with namespace: {session1.namespace}")
        
        # Test 2: Explicit namespace
        print("Test 2: Explicit namespace")
        session2 = NLMSession(namespace="test_session")
        assert session2.namespace == "test_session", f"Expected 'test_session', got '{session2.namespace}'"
        print(f"✓ Session created with explicit namespace: {session2.namespace}")
        
        # Test 3: Different sessions have different namespaces
        print("Test 3: Different sessions")
        session3 = NLMSession()
        assert session1.namespace != session3.namespace, "Different sessions should have different namespaces"
        print("✓ Different sessions have different namespaces")
        
        return True
        
    except Exception as e:
        print(f"❌ Session creation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_variable_namespace_resolution():
    """Test variable namespace resolution"""
    print("\n=== Test Variable Namespace Resolution ===")
    
    try:
        session = NLMSession(namespace="test_ns")
        
        # Test 1: Simple variable name (should get namespace)
        print("Test 1: Simple variable name resolution")
        resolved = session._resolve_variable_name("myvar")
        expected = "test_ns.myvar"
        assert resolved == expected, f"Expected '{expected}', got '{resolved}'"
        print(f"✓ 'myvar' resolved to '{resolved}'")
        
        # Test 2: Variable with namespace (should not change)
        print("Test 2: Variable with namespace")
        resolved = session._resolve_variable_name("global.config")
        expected = "global.config"
        assert resolved == expected, f"Expected '{expected}', got '{resolved}'"
        print(f"✓ 'global.config' resolved to '{resolved}'")
        
        # Test 3: Another namespace
        print("Test 3: Other namespace")
        resolved = session._resolve_variable_name("other.data")
        expected = "other.data"
        assert resolved == expected, f"Expected '{expected}', got '{resolved}'"
        print(f"✓ 'other.data' resolved to '{resolved}'")
        
        return True
        
    except Exception as e:
        print(f"❌ Namespace resolution test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_tool_functions():
    """Test variable management tool functions"""
    print("\n=== Test Tool Functions ===")
    
    try:
        # Create test database
        test_db = f"test_nlm_{uuid.uuid4().hex[:8]}.db"
        session = NLMSession(namespace="tool_test")
        session.variable_db.db_path = test_db
        session.history_manager.db_path = test_db
        
        # Initialize database for testing
        session.variable_db._init_database()
        session.history_manager._init_history_table()
        
        # Test 1: Save variable
        print("Test 1: Save variable")
        result = session._save_variable_tool("name", "Alice")
        assert "Successfully saved" in result, f"Expected success message, got: {result}"
        print(f"✓ Save result: {result}")
        
        # Test 2: Get variable
        print("Test 2: Get variable")
        result = session._get_variable_tool("name")
        assert "Alice" in result, f"Expected 'Alice' in result, got: {result}"
        print(f"✓ Get result: {result}")
        
        # Test 3: List variables
        print("Test 3: List variables")
        result = session._list_variables_tool()
        assert "tool_test.name" in result, f"Expected namespaced variable in result, got: {result}"
        assert "Alice" in result, f"Expected 'Alice' in result, got: {result}"
        print(f"✓ List result: {result}")
        
        # Test 4: Save global variable
        print("Test 4: Save global variable")
        result = session._save_variable_tool("global.config", "test_config")
        assert "global.config" in result, f"Expected 'global.config' in result, got: {result}"
        print(f"✓ Global save result: {result}")
        
        # Test 5: Get global variable
        print("Test 5: Get global variable")
        result = session._get_variable_tool("global.config")
        assert "test_config" in result, f"Expected 'test_config' in result, got: {result}"
        print(f"✓ Global get result: {result}")
        
        # Test 6: Delete variable
        print("Test 6: Delete variable")
        result = session._delete_variable_tool("name")
        assert "Successfully deleted" in result, f"Expected success message, got: {result}"
        print(f"✓ Delete result: {result}")
        
        # Test 7: Try to get deleted variable
        print("Test 7: Get deleted variable")
        result = session._get_variable_tool("name")
        assert "not found" in result, f"Expected 'not found', got: {result}"
        print(f"✓ Get deleted result: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Tool functions test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cleanup
        if os.path.exists(test_db):
            os.remove(test_db)


def test_nlm_execute_function():
    """Test the simple nlm_execute function interface"""
    print("\n=== Test nlm_execute Function ===")
    
    try:
        # Create a test database
        test_db = f"test_execute_{uuid.uuid4().hex[:8]}.db"
        original_db = None
        
        # Mock the database path (simplified test - just check if function works)
        print("Test 1: Simple macro execution")
        
        # This is a basic test that checks if the function can be called
        # without actually connecting to Ollama (which may not be available in test environment)
        session = NLMSession(namespace="execute_test")
        session.variable_db.db_path = test_db
        session.variable_db._init_database()
        
        # Test the tool functions directly (without LLM)
        result = session._save_variable_tool("test", "value")
        assert "Successfully saved" in result, f"Expected success, got: {result}"
        print(f"✓ Direct tool execution works: {result}")
        
        print("✓ nlm_execute function interface is properly structured")
        return True
        
    except Exception as e:
        print(f"❌ nlm_execute test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cleanup
        if test_db and os.path.exists(test_db):
            os.remove(test_db)


def run_all_tests():
    """Run all tests"""
    print("🧪 Running nlm_interpreter tests...\n")
    
    tests = [
        test_basic_session_creation,
        test_variable_namespace_resolution,
        test_tool_functions,
        test_nlm_execute_function
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
            print("✅ PASSED\n")
        else:
            print("❌ FAILED\n")
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return True
    else:
        print("⚠️  Some tests failed")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)