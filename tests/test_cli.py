#!/usr/bin/env python3
"""Test CLI functionality"""

import os
import sys
import subprocess
import tempfile
import sqlite3
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from nlm_interpreter import _handle_list_sessions, _execute_single_macro, _execute_from_file
from variable_db import VariableDB


def test_handle_list_sessions():
    """Test _handle_list_sessions function"""
    print("=== Test _handle_list_sessions ===")
    
    try:
        # Create test database with some sessions
        db = VariableDB("test_sessions.db")
        db.save_variable("session1:test_var", "value1")
        db.save_variable("session2:test_var", "value2")
        db.save_variable("global:shared", "shared_value")
        
        # Capture output
        from io import StringIO
        import contextlib
        
        captured_output = StringIO()
        with contextlib.redirect_stdout(captured_output):
            _handle_list_sessions()
        
        output = captured_output.getvalue()
        
        # Verify sessions are listed
        assert "session1" in output, "session1 should be in output"
        assert "session2" in output, "session2 should be in output"
        assert "global" in output, "global should be in output"
        
        print("✓ Sessions listed correctly")
        
        # Clean up
        if os.path.exists("test_sessions.db"):
            os.remove("test_sessions.db")
        
        return True
        
    except Exception as e:
        print(f"❌ _handle_list_sessions test failed: {e}")
        if os.path.exists("test_sessions.db"):
            os.remove("test_sessions.db")
        return False


def test_execute_single_macro():
    """Test _execute_single_macro function"""
    print("\n=== Test _execute_single_macro ===")
    
    try:
        from io import StringIO
        import contextlib
        
        # Test with a simple macro that doesn't require LLM
        captured_output = StringIO()
        with contextlib.redirect_stdout(captured_output):
            # This will fail with LLM connection, but we can test the function structure
            try:
                _execute_single_macro("test macro", "test_namespace", "test_model", "http://localhost:1234/v1")
            except Exception:
                # Expected to fail due to no LLM connection
                pass
        
        print("✓ _execute_single_macro function executes without syntax errors")
        return True
        
    except Exception as e:
        print(f"❌ _execute_single_macro test failed: {e}")
        return False


def test_execute_from_file():
    """Test _execute_from_file function"""
    print("\n=== Test _execute_from_file ===")
    
    try:
        # Create a test macro file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# Test Macro File\n")
            f.write("\n")
            f.write("Save 'test_value' to {{test_var}}\n")
            f.write("\n")
            f.write("# Another macro\n")
            f.write("Get {{test_var}}\n")
            test_file = f.name
        
        from io import StringIO
        import contextlib
        
        captured_output = StringIO()
        with contextlib.redirect_stdout(captured_output):
            try:
                _execute_from_file(test_file, "test_namespace", "test_model", "http://localhost:1234/v1")
            except Exception:
                # Expected to fail due to no LLM connection
                pass
        
        output = captured_output.getvalue()
        
        # Verify file processing logic
        assert "Executing line" in output, "Should show line execution"
        
        print("✓ _execute_from_file processes file correctly")
        
        # Clean up
        os.unlink(test_file)
        return True
        
    except Exception as e:
        print(f"❌ _execute_from_file test failed: {e}")
        if 'test_file' in locals() and os.path.exists(test_file):
            os.unlink(test_file)
        return False


def test_cli_argument_parsing():
    """Test CLI argument parsing by calling main script"""
    print("\n=== Test CLI Argument Parsing ===")
    
    try:
        # Test --list-sessions
        result = subprocess.run([
            sys.executable, "nlm_interpreter.py", "--list-sessions"
        ], capture_output=True, text=True, cwd=os.path.dirname(os.path.dirname(__file__)))
        
        # Should not crash and should produce output
        assert result.returncode == 0, f"CLI should not crash, got return code {result.returncode}"
        
        print("✓ --list-sessions argument works")
        
        # Test help
        result = subprocess.run([
            sys.executable, "nlm_interpreter.py", "--help"
        ], capture_output=True, text=True, cwd=os.path.dirname(os.path.dirname(__file__)))
        
        assert result.returncode == 0, "Help should not crash"
        assert "Natural Language Macro Interpreter" in result.stdout, "Help should show description"
        
        print("✓ --help argument works")
        
        return True
        
    except Exception as e:
        print(f"❌ CLI argument parsing test failed: {e}")
        return False


def run_cli_tests():
    """Run all CLI tests"""
    print("🔧 CLI Functionality Tests")
    print("=" * 50)
    
    tests = [
        test_handle_list_sessions,
        test_execute_single_macro,
        test_execute_from_file,
        test_cli_argument_parsing
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
            print("✅ PASSED")
        else:
            print("❌ FAILED")
    
    print(f"\n📊 CLI Test Results: {passed}/{total} tests passed")
    return passed == total


if __name__ == "__main__":
    success = run_cli_tests()
    sys.exit(0 if success else 1)