#!/usr/bin/env python3
"""Test script for global variable sharing between NLM sessions"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from nlm_interpreter import NLMSession
from variable_history import enable_logging, reset_logging

def test_global_variable_sharing():
    """Test sharing global variables between two sessions"""
    print("🌐 Testing Global Variable Sharing Between Sessions")
    print("=" * 60)
    
    # Enable logging to track the sharing
    enable_logging()
    
    # Create two different sessions
    session1 = NLMSession(namespace="session1")
    session2 = NLMSession(namespace="session2")
    
    print("\n📋 Session 1: Setting global variables")
    print("-" * 40)
    
    # Session 1: Set some global variables using @ syntax
    session1.execute("Save 'Hello from Session 1' to {{@greeting}}")
    session1.execute("Save 42 to {{@magic_number}}")
    session1.execute("Save 'shared data' to {{@shared_info}}")
    
    # Show session1's variables
    session1_vars = session1.variable_db.list_variables()
    session1_local = {k: v for k, v in session1_vars.items() if k.startswith(f"{session1.namespace}:")}
    global_vars = {k: v for k, v in session1_vars.items() if k.startswith("global:")}
    
    print(f"Session 1 local variables: {list(session1_local.keys())}")
    print(f"Global variables after Session 1: {list(global_vars.keys())}")
    
    print("\n📋 Session 2: Accessing global variables")
    print("-" * 40)
    
    # Session 2: Access the global variables using @ syntax
    greeting = session2.execute("Get {{@greeting}}")
    number = session2.execute("Get {{@magic_number}}")
    info = session2.execute("Get {{@shared_info}}")
    
    print(f"Session 2 retrieved greeting: {greeting}")
    print(f"Session 2 retrieved number: {number}")
    print(f"Session 2 retrieved info: {info}")
    
    print("\n📋 Session 2: Modifying global variables")
    print("-" * 40)
    
    # Session 2: Modify global variables using @ syntax
    session2.execute("Save 'Updated by Session 2' to {{@greeting}}")
    session2.execute("Save 100 to {{@magic_number}}")
    
    print("\n📋 Session 1: Seeing the changes")
    print("-" * 40)
    
    # Session 1: Check the updated global variables
    updated_greeting = session1.execute("Get {{@greeting}}")
    updated_number = session1.execute("Get {{@magic_number}}")
    
    print(f"Session 1 sees updated greeting: {updated_greeting}")
    print(f"Session 1 sees updated number: {updated_number}")
    
    print("\n📋 Testing local vs global scope")
    print("-" * 40)
    
    # Test local variables don't interfere
    session1.execute("Save 'Local to Session 1' to {{local_var}}")
    session2.execute("Save 'Local to Session 2' to {{local_var}}")
    
    local1 = session1.execute("Get {{local_var}}")
    local2 = session2.execute("Get {{local_var}}")
    
    print(f"Session 1 local_var: {local1}")
    print(f"Session 2 local_var: {local2}")
    
    # Try to access other session's local variables (should not work)
    print("Attempting to access other session's local variables...")
    try:
        # This should not find the variable as it's in a different namespace
        other_session_var = session1.execute(f"Get {{{session2.namespace}:local_var}}")
        print(f"❌ ERROR: Accessed other session's variable: {other_session_var}")
    except Exception as e:
        print(f"✅ Correctly blocked access to other session's local variables: {str(e)[:50]}...")
    
    print("\n📊 Final state summary:")
    print("-" * 40)
    all_vars = session1.variable_db.list_variables()
    session1_vars = {k: v for k, v in all_vars.items() if k.startswith(f"{session1.namespace}:")}
    session2_vars = {k: v for k, v in all_vars.items() if k.startswith(f"{session2.namespace}:")}
    global_vars = {k: v for k, v in all_vars.items() if k.startswith("global:")}
    
    print(f"Session 1 ({session1.namespace}) variables: {list(session1_vars.keys())}")
    print(f"Session 2 ({session2.namespace}) variables: {list(session2_vars.keys())}")
    print(f"Global variables: {list(global_vars.keys())}")
    
    print("\n✅ Global variable sharing test completed!")
    
if __name__ == "__main__":
    test_global_variable_sharing()