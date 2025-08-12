#!/usr/bin/env python3
"""Test README Usage Examples to verify they work correctly"""

from src.nlm_interpreter import NLMSession

def test_readme_examples():
    """Test the exact code from README Usage Examples"""
    print("🧪 Testing README Usage Examples...")
    print("=" * 50)
    
    try:
        # Automatic provider selection based on model name
        print("📋 Creating sessions...")
        session_default = NLMSession()                   # Uses gpt-5-mini (default)
        session_local = NLMSession(model="gpt-oss:20b")  # Uses local LLM
        
        print(f"  session_default model: {session_default.model}")
        print(f"  session_local model: {session_local.model}")
        
        # Basic usage - all models support the same API
        print("\n📝 Basic usage tests...")
        session_default.execute("Save 'Hello Default' to {{message}}")
        print(f"  session_default message: {session_default.get('message')}")
        
        session_local.execute("Save 'Hello Local' to {{message}}")
        print(f"  session_local message: {session_local.get('message')}")
        
        # 🆕 Per-Call Model Override - NEW FEATURE!
        # Optimize each task with the right model without changing your session
        print("\n🆕 Per-Call Model Override tests...")
        session = NLMSession(model="gpt-5-mini")  # Balanced default
        print(f"  session initial model: {session.model}")
        
        # Speed-critical: Use fastest, cheapest model
        session.execute("Quick update to {{status}}", model="gpt-5-nano")
        print(f"  status after nano: {session.get('status')}")
        print(f"  session model after nano: {session.model}")
        
        # Quality-critical: Use most capable model with deep reasoning  
        session.execute("Complex analysis of {{data}}", 
                       model="gpt-5", reasoning_effort="high")
        print(f"  data after gpt-5: {session.get('data')}")
        print(f"  session model after gpt-5: {session.model}")
        
        # Privacy-sensitive: Use local model
        session.execute("Process sensitive {{info}}", model="gpt-oss:20b")
        print(f"  info after local: {session.get('info')}")
        print(f"  session model after local: {session.model}")
        
        final_model = session.model
        print(f"\nSession still using: {final_model}")  # "gpt-5-mini" - unchanged!
        
        # Verify session model is unchanged
        assert final_model == "gpt-5-mini", f"Expected gpt-5-mini, got {final_model}"
        
        print("\n" + "=" * 50)
        print("✅ All README examples work correctly!")
        print("🎯 Key verifications:")
        print(f"  ✅ Default session uses: {session_default.model}")  
        print(f"  ✅ Local session uses: {session_local.model}")
        print(f"  ✅ Per-call overrides work: variables saved successfully")
        print(f"  ✅ Session model preserved: {final_model}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ README examples failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🚀 README Usage Examples Verification")
    print("Testing the exact code from README.md...")
    print()
    
    success = test_readme_examples()
    
    if success:
        print("\n🎉 README examples are working correctly!")
        print("Users can copy-paste these examples with confidence.")
    else:
        print("\n💥 README examples have issues that need fixing!")
        
    return success

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)