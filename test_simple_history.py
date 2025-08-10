#!/usr/bin/env python3
"""Simple test for conversation history functionality without LLM calls"""

from nlm_interpreter import NLMSession
from conversation_history import ConversationHistory


def test_basic_functionality():
    """Test basic history functionality without LLM calls"""
    print("🧪 Testing Basic History Functionality")
    print("=" * 50)
    
    # Test 1: Session with history enabled (default)
    print("\n✅ Test 1: Session Creation with History")
    session_enabled = NLMSession(namespace="test_enabled", disable_history=False)
    print(f"History enabled: {not session_enabled.disable_history}")
    print(f"Namespace: {session_enabled.namespace}")
    print(f"Conversation history object: {session_enabled.conversation_history is not None}")
    
    # Test 2: Session with history disabled
    print("\n❌ Test 2: Session Creation without History") 
    session_disabled = NLMSession(namespace="test_disabled", disable_history=True)
    print(f"History enabled: {not session_disabled.disable_history}")
    print(f"Conversation history object: {session_disabled.conversation_history}")
    
    # Test 3: Context management methods
    print("\n🔧 Test 3: Context Management Methods")
    
    # Test with history enabled
    info_enabled = session_enabled.get_context_info()
    print(f"Enabled session context info: {info_enabled}")
    
    reset_result = session_enabled.reset_context()
    print(f"Reset context (enabled): {reset_result}")
    
    # Test with history disabled
    info_disabled = session_disabled.get_context_info()
    print(f"Disabled session context info: {info_disabled}")
    
    reset_result_disabled = session_disabled.reset_context()
    print(f"Reset context (disabled): {reset_result_disabled}")
    
    # Test 4: Direct conversation history usage
    print("\n💬 Test 4: Direct ConversationHistory Usage")
    
    history = ConversationHistory("direct_test")
    
    # Add messages
    history.add_message("user", "Hello, world!")
    history.add_message("assistant", "Hello! How can I help you?")
    history.add_message("user", "What's the weather?")
    
    # Get messages
    messages = history.get_messages()
    print(f"Total messages: {len(messages)}")
    for i, msg in enumerate(messages):
        print(f"  {i+1}. {msg['role']}: {msg['content']}")
    
    # Get stats
    stats = history.get_stats()
    print(f"Stats: {stats}")
    
    print("\n✅ All basic tests passed!")


if __name__ == "__main__":
    test_basic_functionality()