#!/usr/bin/env python3
"""Test conversation history functionality"""

import os
import sys
import tempfile
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from conversation_history import ConversationHistory
from nlm_interpreter import NLMSession


class TestConversationHistory:
    """Test conversation history basic functionality"""
    
    def setUp(self):
        """Set up test with temporary database"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()
        self.db_path = self.temp_db.name
        self.namespace = "test_session"
        self.history = ConversationHistory(self.namespace, self.db_path)
    
    def tearDown(self):
        """Clean up temporary database"""
        try:
            os.unlink(self.db_path)
        except FileNotFoundError:
            pass
    
    def test_add_and_get_messages(self):
        """Test adding and retrieving messages"""
        print("Testing message addition and retrieval...")
        
        # Add some test messages
        self.history.add_message("user", "Hello, how are you?")
        self.history.add_message("assistant", "I'm doing well, thank you!")
        self.history.add_message("user", "What's the weather like?")
        
        # Get all messages
        messages = self.history.get_messages()
        
        assert len(messages) == 3, f"Expected 3 messages, got {len(messages)}"
        assert messages[0]["role"] == "user"
        assert messages[0]["content"] == "Hello, how are you?"
        assert messages[1]["role"] == "assistant"
        assert messages[2]["role"] == "user"
        
        print("✅ Message addition and retrieval works correctly")
    
    def test_get_recent_messages(self):
        """Test getting recent messages"""
        print("Testing recent message retrieval...")
        
        # Add 5 messages
        for i in range(5):
            self.history.add_message("user", f"Message {i+1}")
        
        # Get 3 most recent messages
        recent = self.history.get_recent_messages(3)
        
        assert len(recent) == 3, f"Expected 3 recent messages, got {len(recent)}"
        assert recent[0]["content"] == "Message 3"  # Should be in chronological order
        assert recent[1]["content"] == "Message 4"
        assert recent[2]["content"] == "Message 5"
        
        print("✅ Recent message retrieval works correctly")
    
    def test_clear_operations(self):
        """Test clearing messages"""
        print("Testing clear operations...")
        
        # Clear any existing messages first
        self.history.clear_all()
        
        # Add test messages
        for i in range(5):
            self.history.add_message("user", f"Message {i+1}")
        
        # Verify we have 5 messages
        initial_messages = self.history.get_messages()
        print(f"Initial messages: {len(initial_messages)}")
        for i, msg in enumerate(initial_messages):
            print(f"  {i+1}: {msg['content']}")
        
        # Test clear recent
        self.history.clear_recent(2)
        remaining = self.history.get_messages()
        print(f"After clear_recent(2): {len(remaining)} messages")
        for i, msg in enumerate(remaining):
            print(f"  {i+1}: {msg['content']}")
        
        assert len(remaining) == 3, f"Expected 3 remaining messages, got {len(remaining)}"
        
        # Test clear all
        self.history.clear_all()
        all_messages = self.history.get_messages()
        assert len(all_messages) == 0, f"Expected 0 messages after clear_all, got {len(all_messages)}"
        
        print("✅ Clear operations work correctly")
    
    def test_stats(self):
        """Test conversation statistics"""
        print("Testing conversation statistics...")
        
        # Add various message types
        self.history.add_message("system", "System prompt")
        self.history.add_message("user", "User question")
        self.history.add_message("assistant", "Assistant response")
        
        stats = self.history.get_stats()
        
        assert stats["total_messages"] == 3
        assert stats["role_counts"]["system"] == 1
        assert stats["role_counts"]["user"] == 1
        assert stats["role_counts"]["assistant"] == 1
        assert stats["estimated_tokens"] > 0
        
        print("✅ Statistics calculation works correctly")
    
    def test_export(self):
        """Test exporting conversation history"""
        print("Testing conversation export...")
        
        # Clear existing messages for clean test
        self.history.clear_all()
        
        # Add test messages
        self.history.add_message("user", "Test message 1")
        self.history.add_message("assistant", "Test response 1")
        
        # Export to temporary file
        export_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=".json")
        export_file.close()
        
        try:
            success = self.history.export_to_file(export_file.name)
            print(f"Export success: {success}")
            assert success, "Export should succeed"
            
            # Verify exported content
            with open(export_file.name, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"Exported data: {data}")
            assert data["namespace"] == self.namespace
            assert len(data["messages"]) == 2
            assert data["messages"][0]["role"] == "user"
            assert data["messages"][1]["role"] == "assistant"
            
            print("✅ Export functionality works correctly")
            
        except Exception as e:
            print(f"Export test error: {e}")
            raise
        finally:
            try:
                os.unlink(export_file.name)
            except FileNotFoundError:
                pass


class TestNLMSessionHistory:
    """Test NLM session conversation history integration"""
    
    def setUp(self):
        """Set up test session"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()
        self.db_path = self.temp_db.name
        
        # Patch the database path for testing
        import nlm_interpreter
        self.original_db = "variables.db"
        # We'll use a test session with disable_history=False
    
    def tearDown(self):
        """Clean up"""
        try:
            os.unlink(self.db_path)
        except FileNotFoundError:
            pass
    
    def test_history_disabled(self):
        """Test session with history disabled"""
        print("Testing session with history disabled...")
        
        # Create session with history disabled
        session = NLMSession(namespace="test_disabled", disable_history=True)
        
        # Check that history is properly disabled
        assert session.disable_history == True
        assert session.conversation_history is None
        
        # Test context methods return appropriate responses
        info = session.get_context_info()
        assert info["history_enabled"] == False
        assert info["message_count"] == 0
        
        success = session.reset_context()
        assert success == False
        
        print("✅ History disabled mode works correctly")
    
    def test_history_enabled(self):
        """Test session with history enabled"""
        print("Testing session with history enabled...")
        
        # Create session with history enabled (default)
        session = NLMSession(namespace="test_enabled", disable_history=False)
        
        # Check that history is properly enabled
        assert session.disable_history == False
        assert session.conversation_history is not None
        
        # Test context info
        info = session.get_context_info()
        assert info["history_enabled"] == True
        assert info["message_count"] >= 0
        
        print("✅ History enabled mode works correctly")
    
    def test_context_management(self):
        """Test context management methods"""
        print("Testing context management methods...")
        
        session = NLMSession(namespace="test_context", disable_history=False)
        
        # Add some mock history
        session.conversation_history.add_message("user", "First message")
        session.conversation_history.add_message("assistant", "First response")
        session.conversation_history.add_message("user", "Second message")
        
        # Test context info
        info = session.get_context_info()
        assert info["message_count"] == 3
        
        # Test trimming
        success = session.trim_context(keep_recent=2)
        assert success == True
        
        info_after_trim = session.get_context_info()
        assert info_after_trim["message_count"] == 2
        
        # Test reset
        success = session.reset_context()
        assert success == True
        
        info_after_reset = session.get_context_info()
        assert info_after_reset["message_count"] == 0
        
        print("✅ Context management methods work correctly")
    
    def test_export_functionality(self):
        """Test export functionality"""
        print("Testing export functionality...")
        
        session = NLMSession(namespace="test_export", disable_history=False)
        
        # Add test conversation
        session.conversation_history.add_message("user", "Export test")
        session.conversation_history.add_message("assistant", "Export response")
        
        # Export to temporary file
        export_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=".json")
        export_file.close()
        
        try:
            success = session.export_context(export_file.name)
            assert success == True
            
            # Verify file exists and has content
            assert os.path.exists(export_file.name)
            assert os.path.getsize(export_file.name) > 0
            
            print("✅ Export functionality works correctly")
            
        finally:
            try:
                os.unlink(export_file.name)
            except FileNotFoundError:
                pass


def run_tests():
    """Run all conversation history tests"""
    print("🧪 Running Conversation History Tests")
    print("=" * 50)
    
    # Test ConversationHistory class
    print("\n📝 Testing ConversationHistory class...")
    test_history = TestConversationHistory()
    
    test_history.setUp()
    try:
        test_history.test_add_and_get_messages()
        test_history.test_get_recent_messages()
        test_history.test_clear_operations()
        test_history.test_stats()
        test_history.test_export()
    finally:
        test_history.tearDown()
    
    # Test NLMSession integration
    print("\n🔄 Testing NLMSession integration...")
    test_session = TestNLMSessionHistory()
    
    test_session.setUp()
    try:
        test_session.test_history_disabled()
        test_session.test_history_enabled()
        test_session.test_context_management()
        test_session.test_export_functionality()
    finally:
        test_session.tearDown()
    
    print("\n" + "=" * 50)
    print("✅ All conversation history tests passed!")
    print("\n💡 Key features tested:")
    print("  • Message storage and retrieval")
    print("  • Recent message filtering") 
    print("  • Clear operations (all/recent)")
    print("  • Statistics and token estimation")
    print("  • Export to JSON")
    print("  • NLMSession integration")
    print("  • Context management methods")
    print("  • History enabled/disabled modes")


if __name__ == "__main__":
    try:
        run_tests()
    except AssertionError as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)