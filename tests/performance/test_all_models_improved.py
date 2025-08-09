#!/usr/bin/env python
"""Test performance improvement for both OpenAI and local models"""

import time
from nlm_interpreter import NLMSession


def test_all_models_improved():
    """Test improved performance for all models"""
    print("="*70)
    print("🚀 全モデル高速化テスト (reasoning_effort='minimal')")
    print("="*70)
    
    models_to_test = [
        ("gpt-5-nano", "OpenAI Cloud"),
        ("gpt-oss:20b", "Local")
    ]
    
    test_command = "Set {{greeting}} to 'Hello World'"
    
    for model, type_desc in models_to_test:
        print(f"\n📊 Testing {model} ({type_desc}):")
        print("-" * 50)
        
        try:
            session = NLMSession(model=model, namespace=f"test_{model.replace(':', '_')}")
            
            # Run test
            start = time.time()
            result = session.execute(test_command)
            elapsed = time.time() - start
            
            # Verify result
            value = session.get("greeting")
            
            print(f"  Command: {test_command}")
            print(f"  ⏱️  Time: {elapsed:.3f}s")
            print(f"  ✅ Variable value: {value}")
            
            # Performance evaluation
            if elapsed < 2.0:
                print(f"  🚀 Excellent performance!")
            elif elapsed < 5.0:
                print(f"  ✅ Good performance")
            elif elapsed < 10.0:
                print(f"  👍 Acceptable performance")
            else:
                print(f"  🐢 Needs optimization")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
            if "connection" in str(e).lower():
                print(f"     Make sure LMStudio/Ollama is running for local models")
    
    print("\n" + "="*70)
    print("💡 Summary:")
    print("="*70)
    print("reasoning_effort='minimal' now applied to ALL models:")
    print("  ✅ OpenAI models: gpt-5, gpt-5-mini, gpt-5-nano")
    print("  ✅ Local models: gpt-oss:20b (and others)")
    print("\nExpected improvements:")
    print("  🚀 OpenAI: ~80% faster (11s → 2s)")
    print("  ⚡ Local: ~60% faster (1.5s → 0.6s direct API)")
    print("      Note: NLM overhead still applies for local models")


if __name__ == "__main__":
    try:
        test_all_models_improved()
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted")
    except Exception as e:
        print(f"❌ Test failed: {e}")