#!/usr/bin/env python3
"""Test reasoning effort and verbosity settings"""

import sys
from pathlib import Path
import logging

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from nlm_interpreter import NLMSession
from agent_base import BaseAgent


def test_nlm_session_default_settings():
    """Test default settings for NLMSession"""
    print("\n1️⃣ Testing NLMSession default settings...")
    
    session = NLMSession("test_defaults")
    
    # Check defaults
    assert session.reasoning_effort == "low"
    assert session.verbosity == "low"
    
    settings = session.get_settings()
    assert settings["reasoning_effort"] == "low"
    assert settings["verbosity"] == "low"
    assert settings["namespace"] == "test_defaults"
    
    print("   ✅ Default settings work correctly")


def test_nlm_session_custom_settings():
    """Test custom settings for NLMSession"""
    print("\n2️⃣ Testing NLMSession custom settings...")
    
    session = NLMSession("test_custom", reasoning_effort="high", verbosity="medium")
    
    # Check custom settings
    assert session.reasoning_effort == "high"
    assert session.verbosity == "medium"
    
    settings = session.get_settings()
    assert settings["reasoning_effort"] == "high"
    assert settings["verbosity"] == "medium"
    
    print("   ✅ Custom settings initialization works")


def test_nlm_session_setting_changes():
    """Test changing settings after initialization"""
    print("\n3️⃣ Testing NLMSession setting changes...")
    
    session = NLMSession("test_changes")
    
    # Change reasoning effort
    session.set_reasoning_effort("medium")
    assert session.reasoning_effort == "medium"
    
    # Change verbosity
    session.set_verbosity("high")
    assert session.verbosity == "high"
    
    # Change both at once
    session.set_settings(reasoning_effort="high", verbosity="low")
    assert session.reasoning_effort == "high"
    assert session.verbosity == "low"
    
    print("   ✅ Setting changes work correctly")


def test_invalid_settings():
    """Test invalid setting values"""
    print("\n4️⃣ Testing invalid setting values...")
    
    session = NLMSession("test_invalid")
    
    # Test invalid reasoning effort
    try:
        session.set_reasoning_effort("invalid")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Invalid reasoning effort level" in str(e)
    
    # Test invalid verbosity
    try:
        session.set_verbosity("invalid")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Invalid verbosity level" in str(e)
    
    # Original settings should be unchanged
    assert session.reasoning_effort == "low"
    assert session.verbosity == "low"
    
    print("   ✅ Invalid setting validation works")


def test_base_agent_default_settings():
    """Test default settings for BaseAgent"""
    print("\n5️⃣ Testing BaseAgent default settings...")
    
    agent = BaseAgent("test_agent_defaults")
    
    # Check agent session has default settings
    settings = agent.get_settings()
    assert settings["reasoning_effort"] == "low"
    assert settings["verbosity"] == "low"
    assert settings["namespace"] == "test_agent_defaults"
    
    print("   ✅ BaseAgent default settings work")


def test_base_agent_custom_settings():
    """Test custom settings for BaseAgent"""
    print("\n6️⃣ Testing BaseAgent custom settings...")
    
    agent = BaseAgent("test_agent_custom", reasoning_effort="medium", verbosity="high")
    
    # Check custom settings
    settings = agent.get_settings()
    assert settings["reasoning_effort"] == "medium"
    assert settings["verbosity"] == "high"
    
    print("   ✅ BaseAgent custom settings work")


def test_base_agent_setting_changes():
    """Test changing BaseAgent settings"""
    print("\n7️⃣ Testing BaseAgent setting changes...")
    
    agent = BaseAgent("test_agent_changes")
    
    # Change via agent methods
    agent.set_reasoning_effort("high")
    agent.set_verbosity("medium")
    
    settings = agent.get_settings()
    assert settings["reasoning_effort"] == "high" 
    assert settings["verbosity"] == "medium"
    
    # Change multiple at once
    agent.set_settings(reasoning_effort="low", verbosity="high")
    
    settings = agent.get_settings()
    assert settings["reasoning_effort"] == "low"
    assert settings["verbosity"] == "high"
    
    print("   ✅ BaseAgent setting changes work")


def test_settings_isolation():
    """Test that settings are isolated between agents"""
    print("\n8️⃣ Testing settings isolation...")
    
    agent1 = BaseAgent("agent1", reasoning_effort="low", verbosity="low")
    agent2 = BaseAgent("agent2", reasoning_effort="high", verbosity="high")
    
    # Verify initial settings
    settings1 = agent1.get_settings()
    settings2 = agent2.get_settings()
    
    assert settings1["reasoning_effort"] == "low"
    assert settings1["verbosity"] == "low"
    assert settings2["reasoning_effort"] == "high"
    assert settings2["verbosity"] == "high"
    
    # Change agent1 settings
    agent1.set_reasoning_effort("medium")
    
    # Verify agent2 is unchanged
    settings1_updated = agent1.get_settings()
    settings2_check = agent2.get_settings()
    
    assert settings1_updated["reasoning_effort"] == "medium"
    assert settings2_check["reasoning_effort"] == "high"  # Unchanged
    
    print("   ✅ Settings isolation works correctly")


def run_all_tests():
    """Run all settings tests"""
    print("🧪 Running Settings Tests")
    print("=" * 50)
    
    # Reduce logging noise
    logging.basicConfig(
        level=logging.WARNING,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        test_nlm_session_default_settings()
        test_nlm_session_custom_settings()
        test_nlm_session_setting_changes()
        test_invalid_settings()
        test_base_agent_default_settings()
        test_base_agent_custom_settings()
        test_base_agent_setting_changes()
        test_settings_isolation()
        
        print("\n" + "=" * 50)
        print("✅ All settings tests passed!")
        print("\n📊 Test Summary:")
        print("  • NLMSession default settings ✓")
        print("  • NLMSession custom settings ✓")
        print("  • NLMSession setting changes ✓")
        print("  • Invalid setting validation ✓")
        print("  • BaseAgent default settings ✓")
        print("  • BaseAgent custom settings ✓")
        print("  • BaseAgent setting changes ✓")
        print("  • Settings isolation ✓")
        
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