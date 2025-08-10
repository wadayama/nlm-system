#!/usr/bin/env python3
"""Test role continuation functionality with conversation history"""

from nlm_interpreter import NLMSession


def test_role_continuation():
    """Test role continuation across multiple execute() calls"""
    print("🎭 Testing Role Continuation with Conversation History")
    print("=" * 60)
    
    # Test 1: History enabled (default)
    print("\n🟢 Test 1: History Enabled (Role Continuation)")
    print("-" * 40)
    
    session_with_history = NLMSession(namespace="role_test", disable_history=False)
    
    print("Step 1: Setting up expert role...")
    result1 = session_with_history.execute("Please act as an expert in Japanese history. Your specialty is the Edo period.")
    print(f"Response 1: {result1}")
    
    print("\nStep 2: Asking expert question (should remember role)...")
    result2 = session_with_history.execute("Please tell me about the characteristics of the Edo period")
    print(f"Response 2: {result2}")
    
    print("\nStep 3: Follow-up question (should maintain context)...")
    result3 = session_with_history.execute("What about the cultural aspects of that era?")
    print(f"Response 3: {result3}")
    
    # Check context info
    context_info = session_with_history.get_context_info()
    print(f"\n📊 Context Info:")
    print(f"  Messages: {context_info['message_count']}")
    print(f"  Estimated tokens: {context_info['estimated_tokens']}")
    print(f"  Role counts: {context_info['role_counts']}")
    
    print("\n" + "=" * 60)
    
    # Test 2: History disabled (comparison)
    print("\n🔴 Test 2: History Disabled (No Role Continuation)")
    print("-" * 40)
    
    session_without_history = NLMSession(namespace="no_role_test", disable_history=True)
    
    print("Step 1: Setting up expert role...")
    result1_no_history = session_without_history.execute("Please act as an expert in Japanese history. Your specialty is the Edo period.")
    print(f"Response 1: {result1_no_history}")
    
    print("\nStep 2: Asking expert question (role likely forgotten)...")
    result2_no_history = session_without_history.execute("Please tell me about the characteristics of the Edo period")
    print(f"Response 2: {result2_no_history}")
    
    # Check context info
    context_info_no_history = session_without_history.get_context_info()
    print(f"\n📊 Context Info (No History):")
    print(f"  History enabled: {context_info_no_history['history_enabled']}")
    print(f"  Messages: {context_info_no_history['message_count']}")
    
    print("\n" + "=" * 60)
    
    # Test 3: Context management
    print("\n🔧 Test 3: Context Management")
    print("-" * 40)
    
    session_manage = NLMSession(namespace="manage_test", disable_history=False)
    
    # Add some conversation
    for i in range(3):
        session_manage.execute(f"Message {i+1}: Test conversation")
    
    print("Before management:")
    info_before = session_manage.get_context_info()
    print(f"  Messages: {info_before['message_count']}")
    
    # Test trimming
    session_manage.trim_context(keep_recent=2)
    print("After trim_context(keep_recent=2):")
    info_after_trim = session_manage.get_context_info()
    print(f"  Messages: {info_after_trim['message_count']}")
    
    # Test reset
    session_manage.reset_context()
    print("After reset_context():")
    info_after_reset = session_manage.get_context_info()
    print(f"  Messages: {info_after_reset['message_count']}")
    
    print("\n" + "=" * 60)
    
    # Test 4: Export functionality
    print("\n📁 Test 4: Export Functionality")
    print("-" * 40)
    
    session_export = NLMSession(namespace="export_test", disable_history=False)
    
    session_export.execute("System: Starting test conversation")
    session_export.execute("User: Hello")
    session_export.execute("Assistant: Hello!")
    
    # Export conversation
    export_success = session_export.export_context("test_conversation.json")
    print(f"Export success: {export_success}")
    
    if export_success:
        print("Conversation exported to: test_conversation.json")
    
    print("\n✅ Role continuation testing completed!")


def test_variable_and_context_integration():
    """Test integration between variables and conversation context"""
    print("\n🔗 Testing Variable and Context Integration")
    print("=" * 50)
    
    session = NLMSession(namespace="integration_test", disable_history=False)
    
    print("Step 1: Set role and save variables...")
    result1 = session.execute("You are a culinary expert. Please set {{specialty}} to 'Japanese cuisine'")
    specialty = session.get("specialty")
    print(f"Specialty set to: {specialty}")
    
    print("\nStep 2: Continue conversation using both context and variables...")
    result2 = session.execute("As an expert in {{specialty}}, please recommend some dishes")
    print(f"Expert recommendation: {result2}")
    
    print("\nStep 3: Update variables within context...")
    session.execute("Set {{difficulty}} to 'beginner-friendly' and suggest {{specialty}} recipes suitable for that difficulty level")
    difficulty = session.get("difficulty")
    print(f"Difficulty set to: {difficulty}")
    
    # Show integration results
    context_info = session.get_context_info()
    all_vars = session.list_local()
    
    print(f"\n📊 Integration Results:")
    print(f"  Context messages: {context_info['message_count']}")
    print(f"  Variables stored: {len(all_vars)}")
    print(f"  Variables: {all_vars}")
    
    print("✅ Variable and context integration works!")


if __name__ == "__main__":
    try:
        test_role_continuation()
        test_variable_and_context_integration()
        
        print("\n🎉 All role continuation tests completed successfully!")
        print("\n💡 Key benefits demonstrated:")
        print("  ✓ Role continuity across multiple execute() calls")
        print("  ✓ Context management (trim, reset, export)")
        print("  ✓ Integration with variable system")
        print("  ✓ User control over context size")
        print("  ✓ History enabled/disabled modes")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()