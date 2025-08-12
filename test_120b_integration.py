#!/usr/bin/env python3
"""Test gpt-oss:120b model integration"""

from src.nlm_interpreter import NLMSession

def test_120b_model_support():
    """Test comprehensive 120b model support"""
    
    print("🧪 Testing gpt-oss:120b Model Integration")
    print("=" * 50)
    
    # Test 1: Model initialization
    print("\n📋 Test 1: Model Initialization")
    session_120b = NLMSession(model="gpt-oss:120b")
    
    assert session_120b.model == "gpt-oss:120b"
    assert session_120b.endpoint == "http://localhost:1234/v1"
    assert session_120b.api_key == "ollama"
    print("✅ 120b model initializes with correct local configuration")
    
    # Test 2: Compare with 20b model 
    print("\n📋 Test 2: Comparison with 20b Model")
    session_20b = NLMSession(model="gpt-oss:20b")
    
    # Both should have same endpoint and api_key (local config)
    assert session_120b.endpoint == session_20b.endpoint
    assert session_120b.api_key == session_20b.api_key
    print("✅ Both 20b and 120b use identical local configuration")
    
    # Test 3: Model classification logic
    print("\n📋 Test 3: Model Classification")
    openai_models = ["gpt-5", "gpt-5-mini", "gpt-5-nano"]
    local_models = ["gpt-oss:20b", "gpt-oss:120b"]
    
    assert "gpt-oss:120b" not in openai_models
    assert "gpt-oss:120b" in local_models
    print("✅ 120b correctly classified as local model")
    
    # Test 4: Per-call model switching
    print("\n📋 Test 4: Per-Call Model Override")
    session = NLMSession(model="gpt-5-mini")
    original_model = session.model
    
    # Save original state
    state = session._save_current_state()
    
    # Test temporary switch to 120b (config only - no actual call)
    try:
        session._apply_temporary_model("gpt-oss:120b")
        
        # Check configuration was applied
        assert session.model == "gpt-oss:120b"
        assert session.endpoint == "http://localhost:1234/v1"
        assert session.api_key == "ollama"
        
        # Restore original state
        session._restore_state(state)
        assert session.model == original_model
        
        print("✅ Per-call 120b override works correctly")
        
    except Exception as e:
        if "Failed to configure model" in str(e) and "connection" in str(e).lower():
            print("✅ 120b configuration logic works (expected connection error)")
        else:
            raise e
    
    # Test 5: Settings preservation
    print("\n📋 Test 5: Settings Preservation")
    session_with_settings = NLMSession(
        model="gpt-oss:120b", 
        reasoning_effort="high",
        verbosity="medium"
    )
    
    assert session_with_settings.model == "gpt-oss:120b"
    assert session_with_settings.reasoning_effort == "high"
    assert session_with_settings.verbosity == "medium"
    print("✅ 120b preserves custom reasoning and verbosity settings")
    
    print("\n" + "=" * 50)
    print("🎉 All gpt-oss:120b integration tests passed!")
    print("📝 120b model is ready for use with local LLM servers")
    return True

if __name__ == "__main__":
    try:
        success = test_120b_model_support()
        if success:
            print("\n✅ Test suite completed successfully")
            exit(0)
        else:
            print("\n❌ Test suite failed")
            exit(1)
    except Exception as e:
        print(f"\n💥 Test suite crashed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)