#!/usr/bin/env python3
"""Test tool execution functionality in detail"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from nlm_interpreter import NLMSession


def test_save_variable_tool():
    """Test _save_variable_tool in detail"""
    print("=== Test Save Variable Tool ===")
    
    try:
        session = NLMSession(namespace="tool_test")
        
        # Test local variable save
        result = session._save_variable_tool("test_var", "test_value")
        assert "Successfully saved" in result, f"Expected success message, got: {result}"
        assert "test_var" in result, "Result should contain variable name"
        
        # Verify the variable was actually saved
        stored_value = session.get("test_var")
        assert stored_value == "test_value", f"Expected 'test_value', got '{stored_value}'"
        
        # Test global variable save
        result = session._save_variable_tool("@global_var", "global_value")
        assert "Successfully saved" in result, f"Expected success message for global, got: {result}"
        
        # Verify global variable was saved
        stored_value = session.get("@global_var")
        assert stored_value == "global_value", f"Expected 'global_value', got '{stored_value}'"
        
        # Test overwriting existing variable
        result = session._save_variable_tool("test_var", "new_value")
        assert "Successfully saved" in result, f"Expected success for overwrite, got: {result}"
        
        stored_value = session.get("test_var")
        assert stored_value == "new_value", f"Expected 'new_value', got '{stored_value}'"
        
        print("✓ Save variable tool works correctly")
        return True
        
    except Exception as e:
        print(f"❌ Save variable tool test failed: {e}")
        return False


def test_get_variable_tool():
    """Test _get_variable_tool in detail"""
    print("\n=== Test Get Variable Tool ===")
    
    try:
        session = NLMSession(namespace="tool_test")
        
        # Set up test variables
        session.save("existing_var", "existing_value")
        session.save("@global_existing", "global_existing_value")
        
        # Test getting existing local variable
        result = session._get_variable_tool("existing_var")
        assert "contains: existing_value" in result, f"Expected value in result, got: {result}"
        
        # Test getting existing global variable
        result = session._get_variable_tool("@global_existing")
        assert "contains: global_existing_value" in result, f"Expected global value, got: {result}"
        
        # Test getting non-existent variable
        result = session._get_variable_tool("non_existent")
        assert "not found" in result, f"Expected 'not found' for non-existent, got: {result}"
        
        # Test getting non-existent global variable
        result = session._get_variable_tool("@non_existent")
        assert "not found" in result, f"Expected 'not found' for non-existent global, got: {result}"
        
        print("✓ Get variable tool works correctly")
        return True
        
    except Exception as e:
        print(f"❌ Get variable tool test failed: {e}")
        return False


def test_list_variables_tool():
    """Test _list_variables_tool in detail"""
    print("\n=== Test List Variables Tool ===")
    
    try:
        session = NLMSession(namespace="tool_test")
        
        # Test with no variables
        session.variable_db.delete_variable(f"{session.namespace}:existing_var")  # Clean up from previous test
        all_vars = session.variable_db.list_variables()
        for key in list(all_vars.keys()):
            if key.startswith(f"{session.namespace}:"):
                session.variable_db.delete_variable(key)
        
        # Set up test variables
        session.save("var1", "value1")
        session.save("var2", "value2")
        session.save("@global1", "global_value1")
        
        # Test listing variables
        result = session._list_variables_tool()
        assert "Variables:" in result, f"Expected 'Variables:' header, got: {result}"
        assert "var1 = value1" in result, f"Expected var1 in list, got: {result}"
        assert "var2 = value2" in result, f"Expected var2 in list, got: {result}"
        assert "global1 = global_value1" in result, f"Expected global1 in list, got: {result}"
        
        # Test with no variables (clean slate)
        session.clear_local()
        session.delete("@global1")
        
        # Check if we get appropriate message for empty list
        remaining_vars = session.variable_db.list_variables()
        if not any(key.startswith(f"{session.namespace}:") or key.startswith("global:global1") for key in remaining_vars.keys()):
            result = session._list_variables_tool()
            # Should either show empty list or "No variables found"
            print(f"  Empty list result: {result}")
        
        print("✓ List variables tool works correctly")
        return True
        
    except Exception as e:
        print(f"❌ List variables tool test failed: {e}")
        return False


def test_delete_variable_tool():
    """Test _delete_variable_tool in detail"""
    print("\n=== Test Delete Variable Tool ===")
    
    try:
        session = NLMSession(namespace="tool_test")
        
        # Set up test variables
        session.save("to_delete", "delete_value")
        session.save("@global_to_delete", "global_delete_value")
        
        # Test deleting existing local variable
        result = session._delete_variable_tool("to_delete")
        assert "Successfully deleted" in result, f"Expected success message, got: {result}"
        
        # Verify deletion
        remaining = session.get("to_delete")
        assert remaining is None, f"Variable should be deleted, got: {remaining}"
        
        # Test deleting existing global variable
        result = session._delete_variable_tool("@global_to_delete")
        assert "Successfully deleted" in result, f"Expected success for global delete, got: {result}"
        
        # Verify global deletion
        remaining = session.get("@global_to_delete")
        assert remaining is None, f"Global variable should be deleted, got: {remaining}"
        
        # Test deleting non-existent variable
        result = session._delete_variable_tool("non_existent")
        assert "not found" in result, f"Expected 'not found' for non-existent, got: {result}"
        
        print("✓ Delete variable tool works correctly")
        return True
        
    except Exception as e:
        print(f"❌ Delete variable tool test failed: {e}")
        return False


def test_delete_all_variables_tool():
    """Test _delete_all_variables_tool in detail"""
    print("\n=== Test Delete All Variables Tool ===")
    
    try:
        session = NLMSession(namespace="tool_test")
        
        # Set up multiple test variables
        session.save("var1", "value1")
        session.save("var2", "value2")
        session.save("var3", "value3")
        session.save("@global1", "global1")
        session.save("@global2", "global2")
        
        # Get initial count
        initial_vars = session.variable_db.list_variables()
        initial_count = len(initial_vars)
        
        # Test deleting all variables
        result = session._delete_all_variables_tool()
        assert "Successfully deleted" in result, f"Expected success message, got: {result}"
        assert str(initial_count) in result, f"Expected count {initial_count} in result, got: {result}"
        
        # Verify all variables are deleted
        remaining_vars = session.variable_db.list_variables()
        assert len(remaining_vars) == 0, f"Expected no variables remaining, got: {remaining_vars}"
        
        # Test with no variables to delete
        result = session._delete_all_variables_tool()
        assert "No variables found to delete" in result, f"Expected 'no variables' message, got: {result}"
        
        print("✓ Delete all variables tool works correctly")
        return True
        
    except Exception as e:
        print(f"❌ Delete all variables tool test failed: {e}")
        return False


def test_tool_parameter_validation():
    """Test tool parameter validation"""
    print("\n=== Test Tool Parameter Validation ===")
    
    try:
        session = NLMSession(namespace="tool_test")
        
        # Test save_variable with empty name
        result = session._save_variable_tool("", "value")
        # Should handle empty name gracefully
        print(f"  Empty name result: {result}")
        
        # Test save_variable with empty value
        result = session._save_variable_tool("test_var", "")
        # Should handle empty value
        print(f"  Empty value result: {result}")
        
        # Test get_variable with empty name
        result = session._get_variable_tool("")
        print(f"  Get empty name result: {result}")
        
        # Test delete_variable with empty name
        result = session._delete_variable_tool("")
        print(f"  Delete empty name result: {result}")
        
        # Test with very long variable names
        long_name = "a" * 1000
        result = session._save_variable_tool(long_name, "value")
        print(f"  Long name result: {result[:100]}...")
        
        print("✓ Tool parameter validation handled")
        return True
        
    except Exception as e:
        print(f"❌ Tool parameter validation test failed: {e}")
        return False


def test_tools_definition_completeness():
    """Test that TOOLS_DEFINITION covers all tool functions"""
    print("\n=== Test Tools Definition Completeness ===")
    
    try:
        session = NLMSession(namespace="tool_test")
        
        # Get tool names from TOOLS_DEFINITION
        tool_names = set()
        for tool in session.TOOLS_DEFINITION:
            tool_names.add(tool["function"]["name"])
        
        # Expected tool functions
        expected_tools = {
            "save_variable",
            "get_variable", 
            "list_variables",
            "delete_variable",
            "delete_all_variables"
        }
        
        # Check if all expected tools are defined
        missing_tools = expected_tools - tool_names
        assert len(missing_tools) == 0, f"Missing tools in TOOLS_DEFINITION: {missing_tools}"
        
        # Check if there are any extra tools
        extra_tools = tool_names - expected_tools
        if extra_tools:
            print(f"  Note: Extra tools found: {extra_tools}")
        
        # Verify each tool has required structure
        for tool in session.TOOLS_DEFINITION:
            assert "type" in tool, "Tool should have 'type' field"
            assert tool["type"] == "function", "Tool type should be 'function'"
            assert "function" in tool, "Tool should have 'function' field"
            
            func = tool["function"]
            assert "name" in func, "Function should have 'name'"
            assert "description" in func, "Function should have 'description'"
            assert "parameters" in func, "Function should have 'parameters'"
        
        print("✓ Tools definition is complete and well-structured")
        return True
        
    except Exception as e:
        print(f"❌ Tools definition completeness test failed: {e}")
        return False


def run_tool_execution_tests():
    """Run all tool execution tests"""
    print("🔧 Tool Execution Detailed Tests")
    print("=" * 50)
    
    tests = [
        test_save_variable_tool,
        test_get_variable_tool,
        test_list_variables_tool,
        test_delete_variable_tool,
        test_delete_all_variables_tool,
        test_tool_parameter_validation,
        test_tools_definition_completeness
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
            print("✅ PASSED")
        else:
            print("❌ FAILED")
    
    print(f"\n📊 Tool Execution Test Results: {passed}/{total} tests passed")
    return passed == total


if __name__ == "__main__":
    success = run_tool_execution_tests()
    sys.exit(0 if success else 1)