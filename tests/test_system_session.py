#!/usr/bin/env python3
"""Test SystemSession class functionality

Tests the SystemSession class for unified global variable access,
including @ prefix handling, inheritance features, and compatibility.
"""

import sys
from pathlib import Path
import logging

# Add parent directory to path

from system_session import SystemSession
from nlm_interpreter import NLMSession


def test_basic_global_operations():
    """Test basic global variable operations"""
    print("\n1️⃣ Testing basic global operations...")
    
    system = SystemSession()
    
    # Set and get with auto @ prefix
    system.set_global("status", "active")
    value = system.get_global("status")
    assert value == "active"
    
    # Set and get with explicit @ prefix
    system.set_global("@config", "production")
    value = system.get_global("@config")
    assert value == "production"
    
    # Mixed prefix usage should work the same
    system.set_global("test_var", "value1")
    value1 = system.get_global("test_var")      # No @
    value2 = system.get_global("@test_var")     # With @
    assert value1 == value2 == "value1"
    
    print("   ✅ Basic global operations work")


def test_auto_prefix_handling():
    """Test automatic @ prefix handling"""
    print("\n2️⃣ Testing auto @ prefix handling...")
    
    system = SystemSession()
    
    # Test various combinations
    test_cases = [
        ("var1", "value1"),      # No @ in set
        ("@var2", "value2"),     # @ in set
        ("var3", "value3"),      # No @ in set
    ]
    
    for key, value in test_cases:
        system.set_global(key, value)
    
    # All should be accessible both ways
    assert system.get_global("var1") == "value1"
    assert system.get_global("@var1") == "value1"
    assert system.get_global("var2") == "value2" 
    assert system.get_global("@var2") == "value2"
    assert system.get_global("var3") == "value3"
    assert system.get_global("@var3") == "value3"
    
    print("   ✅ Auto @ prefix handling works")


def test_list_globals():
    """Test listing global variables"""
    print("\n3️⃣ Testing list_globals...")
    
    system = SystemSession()
    
    # Clear any existing globals for clean test
    system.clear_globals()
    
    # Add test variables
    system.set_global("app_status", "running")
    system.set_global("@version", "1.0.0")
    system.set_global("debug_mode", "false")
    
    # List globals - should return clean keys (no @ prefix)
    globals_dict = system.list_globals()
    
    expected_keys = {"app_status", "version", "debug_mode"}
    actual_keys = set(globals_dict.keys())
    
    assert expected_keys == actual_keys
    assert globals_dict["app_status"] == "running"
    assert globals_dict["version"] == "1.0.0"
    assert globals_dict["debug_mode"] == "false"
    
    print("   ✅ list_globals works correctly")


def test_delete_operations():
    """Test global variable deletion"""
    print("\n4️⃣ Testing delete operations...")
    
    system = SystemSession()
    
    # Set some variables
    system.set_global("temp1", "value1")
    system.set_global("@temp2", "value2")
    
    # Verify they exist
    assert system.get_global("temp1") == "value1"
    assert system.get_global("temp2") == "value2"
    
    # Delete with different prefix styles
    success1 = system.delete_global("temp1")      # No @
    success2 = system.delete_global("@temp2")     # With @
    
    assert success1 == True
    assert success2 == True
    
    # Verify they're gone (VariableDB returns "" for deleted variables)
    assert system.get_global("temp1") == ""
    assert system.get_global("temp2") == ""
    
    # Delete non-existent should return False
    success3 = system.delete_global("nonexistent")
    assert success3 == False
    
    print("   ✅ Delete operations work correctly")


def test_context_manager():
    """Test context manager functionality"""
    print("\n5️⃣ Testing context manager...")
    
    # Test with statement
    with SystemSession() as system:
        system.set_global("context_test", "inside_context")
        value = system.get_global("context_test")
        assert value == "inside_context"
        
        # Test inherited functionality
        settings = system.get_settings()
        assert "namespace" in settings
        assert settings["namespace"] == "system_session"
    
    # Context should exit cleanly
    print("   ✅ Context manager works")


def test_inheritance_compatibility():
    """Test that SystemSession inherits all NLMSession functionality"""
    print("\n6️⃣ Testing inheritance compatibility...")
    
    system = SystemSession()
    
    # Test inherited settings functionality
    assert hasattr(system, 'set_reasoning_effort')
    assert hasattr(system, 'set_verbosity')
    assert hasattr(system, 'get_settings')
    
    # Test settings work
    system.set_reasoning_effort("medium")
    system.set_verbosity("high")
    
    settings = system.get_settings()
    assert settings["reasoning_effort"] == "medium"
    assert settings["verbosity"] == "high"
    assert settings["namespace"] == "system_session"
    
    # Test conversation history methods exist
    assert hasattr(system, 'reset_context')
    assert hasattr(system, 'trim_context')
    assert hasattr(system, 'get_context_info')
    
    # Test original variable methods still work (backward compatibility)
    assert hasattr(system, 'save')
    assert hasattr(system, 'get')
    assert hasattr(system, 'delete')
    
    system.save("@legacy_var", "legacy_value")
    legacy_value = system.get("@legacy_var")
    assert legacy_value == "legacy_value"
    
    print("   ✅ Inheritance compatibility works")


def test_compatibility_with_nlmsession():
    """Test compatibility between SystemSession and NLMSession global access"""
    print("\n7️⃣ Testing compatibility with NLMSession...")
    
    # Create both session types
    system = SystemSession()
    regular_session = NLMSession("test_compat")
    
    # Set global variable from SystemSession
    system.set_global("shared_var", "from_system")
    
    # Access from regular NLMSession
    value_from_regular = regular_session.get("@shared_var")
    assert value_from_regular == "from_system"
    
    # Set from regular session
    regular_session.save("@another_shared", "from_regular")
    
    # Access from SystemSession
    value_from_system = system.get_global("another_shared")
    assert value_from_system == "from_regular"
    
    print("   ✅ Compatibility with NLMSession works")


def test_clear_globals():
    """Test clearing all global variables"""
    print("\n8️⃣ Testing clear_globals...")
    
    system = SystemSession()
    
    # Add several global variables
    system.set_global("clear_test1", "value1")
    system.set_global("clear_test2", "value2")
    system.set_global("clear_test3", "value3")
    
    # Verify they exist
    globals_before = system.list_globals()
    assert len(globals_before) >= 3
    
    # Clear all globals
    cleared_count = system.clear_globals()
    assert cleared_count >= 3
    
    # Verify they're gone
    globals_after = system.list_globals()
    for key in ["clear_test1", "clear_test2", "clear_test3"]:
        assert key not in globals_after
    
    print("   ✅ clear_globals works correctly")


def test_system_info():
    """Test system info functionality"""
    print("\n9️⃣ Testing system info...")
    
    system = SystemSession()
    system.set_global("info_test", "test_value")
    
    info = system.get_system_info()
    
    # Check required fields
    assert "session_type" in info
    assert info["session_type"] == "SystemSession"
    assert "global_variables_count" in info
    assert info["global_variables_count"] >= 1
    assert "primary_purpose" in info
    assert "namespace" in info
    assert info["namespace"] == "system_session"
    
    # Test repr
    repr_str = repr(system)
    assert "SystemSession" in repr_str
    assert "globals=" in repr_str
    
    print("   ✅ System info works correctly")


def test_interface_consistency():
    """Test interface consistency between natural language and Python"""
    print("\n🔟 Testing interface consistency...")
    
    system = SystemSession()
    
    # This simulates the consistency we want:
    # Natural language: {{@status}} 
    # Python: system.get_global("@status") or system.get_global("status")
    
    # Set via Python API
    system.set_global("@interface_test", "consistent")
    
    # Should be accessible both ways
    value1 = system.get_global("interface_test")       # No @
    value2 = system.get_global("@interface_test")      # With @
    
    assert value1 == value2 == "consistent"
    
    # In real usage, natural language macro would be:
    # "Save 'ready' to {{@system_status}}"
    # And Python would be:
    # system.get_global("system_status") or system.get_global("@system_status")
    
    system.set_global("system_status", "ready")
    status_value = system.get_global("@system_status")
    assert status_value == "ready"
    
    print("   ✅ Interface consistency achieved")


def run_all_tests():
    """Run all SystemSession tests"""
    print("🧪 Running SystemSession Tests")
    print("=" * 50)
    
    # Reduce logging noise
    logging.basicConfig(
        level=logging.WARNING,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        test_basic_global_operations()
        test_auto_prefix_handling()
        test_list_globals()
        test_delete_operations()
        test_context_manager()
        test_inheritance_compatibility()
        test_compatibility_with_nlmsession()
        test_clear_globals()
        test_system_info()
        test_interface_consistency()
        
        print("\n" + "=" * 50)
        print("✅ All SystemSession tests passed!")
        print("\n📊 Test Summary:")
        print("  • Basic global operations ✓")
        print("  • Auto @ prefix handling ✓")
        print("  • List globals functionality ✓")
        print("  • Delete operations ✓")
        print("  • Context manager support ✓")
        print("  • Inheritance compatibility ✓")
        print("  • NLMSession compatibility ✓")
        print("  • Clear globals functionality ✓")
        print("  • System info methods ✓")
        print("  • Interface consistency ✓")
        print("\n🎯 SystemSession provides unified @-prefixed global variable access")
        print("   while maintaining full NLMSession compatibility!")
        
        return True
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)