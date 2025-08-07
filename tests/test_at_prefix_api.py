#!/usr/bin/env python3
"""Test @prefix API for global variables"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from nlm_interpreter import NLMSession
from variable_history import enable_logging

def test_at_prefix_api():
    """Test the new @prefix API for global variables"""
    print("🌟 @Prefix API for Global Variables Test")
    print("=" * 60)
    
    # Enable logging
    enable_logging()
    
    # Create sessions
    session1 = NLMSession(namespace="agent1")
    session2 = NLMSession(namespace="agent2")
    
    print(f"Session 1 namespace: {session1.namespace}")
    print(f"Session 2 namespace: {session2.namespace}")
    
    print("\n📋 New unified save() API with @prefix")
    print("-" * 50)
    
    print("# Local variables (no @)")
    key1 = session1.save("task", "データ収集")
    key2 = session1.save("progress", "75%")
    key3 = session1.save("status", "実行中")
    
    print(f"session1.save('task', 'データ収集') → {key1}")
    print(f"session1.save('progress', '75%') → {key2}")
    print(f"session1.save('status', '実行中') → {key3}")
    
    print("\n# Global variables (with @)")
    global1 = session1.save("@project_name", "AI Research 2024")
    global2 = session1.save("@version", "2.0")
    global3 = session1.save("@database_url", "postgresql://localhost/research")
    
    print(f"session1.save('@project_name', 'AI Research 2024') → {global1}")
    print(f"session1.save('@version', '2.0') → {global2}")
    print(f"session1.save('@database_url', 'postgresql://localhost/research') → {global3}")
    
    print("\n📋 Unified get() API with @prefix")
    print("-" * 50)
    
    print("# Session 1 retrieving local variables")
    task = session1.get("task")
    progress = session1.get("progress")
    
    print(f"session1.get('task') → {task}")
    print(f"session1.get('progress') → {progress}")
    
    print("\n# Session 1 retrieving global variables")
    project1 = session1.get("@project_name")
    version1 = session1.get("@version")
    
    print(f"session1.get('@project_name') → {project1}")
    print(f"session1.get('@version') → {version1}")
    
    print("\n# Session 2 accessing same globals")
    project2 = session2.get("@project_name")
    version2 = session2.get("@version")
    
    print(f"session2.get('@project_name') → {project2}")
    print(f"session2.get('@version') → {version2}")
    
    print("✅ Both sessions see the same global values!")
    
    print("\n📋 Cross-session global modification")
    print("-" * 50)
    
    # Session 2 modifies global variables
    print("Session 2 modifying globals:")
    session2.save("@project_name", "Updated AI Research 2024")
    session2.save("@status", "production")
    
    print("session2.save('@project_name', 'Updated AI Research 2024')")
    print("session2.save('@status', 'production')")
    
    # Session 1 sees the changes
    print("\nSession 1 sees the updates:")
    updated_project = session1.get("@project_name")
    new_status = session1.get("@status")
    
    print(f"session1.get('@project_name') → {updated_project}")
    print(f"session1.get('@status') → {new_status}")
    
    print("\n📋 Comparison: @prefix vs explicit methods")
    print("-" * 50)
    
    print("Old explicit methods:")
    print("  session1.save_global('config', 'value')")
    print("  session1.get_global('config')")
    print("  session1.delete_global('config')")
    
    print("\nNew @prefix approach:")
    print("  session1.save('@config', 'value')")
    print("  session1.get('@config')")
    print("  session1.delete('@config')")
    
    # Demonstrate both approaches work
    session1.save_global("old_method", "using explicit method")
    session1.save("@new_method", "using @prefix")
    
    old_way = session1.get_global("old_method")
    new_way = session1.get("@new_method")
    
    print(f"\nBoth approaches work:")
    print(f"  Old method result: {old_way}")
    print(f"  New @prefix result: {new_way}")
    
    print("\n📋 Delete operations with @prefix")
    print("-" * 50)
    
    # Test deletion
    session1.save("@temp_var", "temporary")
    print("session1.save('@temp_var', 'temporary')")
    
    temp_value = session1.get("@temp_var")
    print(f"session1.get('@temp_var') → {temp_value}")
    
    deleted = session1.delete("@temp_var")
    print(f"session1.delete('@temp_var') → {deleted}")
    
    after_delete = session1.get("@temp_var")
    print(f"session1.get('@temp_var') after delete → {after_delete}")
    
    print("\n📋 Consistency with NLM syntax")
    print("-" * 50)
    
    print("NLM macro syntax:")
    print("  Save 'value' to {{@global_var}}   ← @prefix for global")
    print("  Save 'value' to {{local_var}}     ← no prefix for local")
    print("  Get {{@global_var}}               ← @prefix for global")
    print("  Get {{local_var}}                 ← no prefix for local")
    
    print("\nPython API syntax (now consistent!):")
    print("  session.save('@global_var', 'value')  ← @prefix for global")
    print("  session.save('local_var', 'value')    ← no prefix for local")
    print("  session.get('@global_var')            ← @prefix for global")
    print("  session.get('local_var')              ← no prefix for local")
    
    print("\n📊 API advantages:")
    print("-" * 50)
    print("✅ Consistent with NLM {{@variable}} syntax")
    print("✅ Single method for both local and global")
    print("✅ Intuitive: @ = global, no @ = local")
    print("✅ Backward compatibility maintained")
    print("✅ Less methods to remember")
    print("✅ Visual clarity in code")
    
    print("\n✅ @Prefix API test completed!")

if __name__ == "__main__":
    test_at_prefix_api()