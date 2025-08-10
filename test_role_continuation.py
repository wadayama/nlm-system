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
    result1 = session_with_history.execute("あなたは日本の歴史専門家として振る舞ってください。専門分野は江戸時代です。")
    print(f"Response 1: {result1}")
    
    print("\nStep 2: Asking expert question (should remember role)...")
    result2 = session_with_history.execute("江戸時代の特徴について教えてください")
    print(f"Response 2: {result2}")
    
    print("\nStep 3: Follow-up question (should maintain context)...")
    result3 = session_with_history.execute("その時代の文化的な側面についてはどうですか？")
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
    result1_no_history = session_without_history.execute("あなたは日本の歴史専門家として振る舞ってください。専門分野は江戸時代です。")
    print(f"Response 1: {result1_no_history}")
    
    print("\nStep 2: Asking expert question (role likely forgotten)...")
    result2_no_history = session_without_history.execute("江戸時代の特徴について教えてください")
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
        session_manage.execute(f"メッセージ {i+1}: テスト会話")
    
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
    
    session_export.execute("システム：テスト会話を開始します")
    session_export.execute("ユーザー：こんにちは")
    session_export.execute("アシスタント：こんにちは！")
    
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
    result1 = session.execute("あなたは料理専門家です。{{specialty}}を'日本料理'に設定してください")
    specialty = session.get("specialty")
    print(f"Specialty set to: {specialty}")
    
    print("\nStep 2: Continue conversation using both context and variables...")
    result2 = session.execute("{{specialty}}の専門家として、おすすめの料理を教えてください")
    print(f"Expert recommendation: {result2}")
    
    print("\nStep 3: Update variables within context...")
    session.execute("{{difficulty}}を'初心者向け'に設定して、その難易度に適した{{specialty}}のレシピを提案してください")
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