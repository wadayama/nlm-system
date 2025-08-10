#!/usr/bin/env python3
"""Test basic functionality of variable_db.py in nlm_system"""

import os
import sys

from variable_db import VariableDB

def test_basic_operations():
    """Test basic variable operations"""
    print("=== Testing Basic Variable Operations ===")
    
    # Create test database
    db = VariableDB("test_variables.db")
    
    try:
        # Test 1: Save variable
        print("Test 1: Save variable")
        db.save_variable("name", "Alice")
        db.save_variable("city", "Tokyo")
        print("✓ Variables saved successfully")
        
        # Test 2: Get variable
        print("Test 2: Get variable")
        name = db.get_variable("name")
        city = db.get_variable("city")
        assert name == "Alice", f"Expected 'Alice', got '{name}'"
        assert city == "Tokyo", f"Expected 'Tokyo', got '{city}'"
        print("✓ Variables retrieved successfully")
        
        # Test 3: List variables
        print("Test 3: List variables")
        variables = db.list_variables()
        assert "name" in variables, "Variable 'name' not found in list"
        assert "city" in variables, "Variable 'city' not found in list"
        assert variables["name"] == "Alice", f"Expected 'Alice', got '{variables['name']}'"
        print("✓ Variables listed successfully")
        
        # Test 4: Delete variable
        print("Test 4: Delete variable")
        success = db.delete_variable("city")
        assert success, "Failed to delete variable 'city'"
        remaining = db.list_variables()
        assert "city" not in remaining, "Variable 'city' still exists after deletion"
        assert "name" in remaining, "Variable 'name' was unexpectedly deleted"
        print("✓ Variable deleted successfully")
        
        # Test 5: Clear all
        print("Test 5: Clear all variables")
        count = db.clear_all()
        assert count >= 1, f"Expected to clear at least 1 variable, cleared {count}"
        remaining = db.list_variables()
        assert len(remaining) == 0, f"Expected empty database, found {remaining}"
        print("✓ All variables cleared successfully")
        
        print("\n🎉 All tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False
        
    finally:
        # Cleanup
        if os.path.exists("test_variables.db"):
            os.remove("test_variables.db")

if __name__ == "__main__":
    success = test_basic_operations()
    sys.exit(0 if success else 1)