#!/usr/bin/env python
"""Test if reasoning_effort works with local gpt-oss:20b model"""

import time
from openai import OpenAI
from nlm_interpreter import NLMSession


def test_local_reasoning():
    """Test reasoning_effort parameter with local model"""
    print("="*70)
    print("🔍 Testing reasoning_effort with gpt-oss:20b (Local)")
    print("="*70)
    
    # Test with local endpoint
    client = OpenAI(
        base_url="http://localhost:1234/v1",
        api_key="not-needed"
    )
    
    test_prompt = "Say hello and nothing else"
    
    # Test 1: Standard local API call
    print("\n1️⃣ Standard local API call:")
    print("-" * 50)
    start = time.time()
    try:
        response = client.chat.completions.create(
            model="gpt-oss:20b",
            messages=[{"role": "user", "content": test_prompt}]
        )
        time1 = time.time() - start
        print(f"  Response: {response.choices[0].message.content[:100]}")
        print(f"  ⏱️  Time: {time1:.3f}s")
    except Exception as e:
        print(f"  ❌ Error: {e}")
        time1 = None
    
    # Test 2: With reasoning_effort parameter
    print("\n2️⃣ With reasoning_effort='minimal':")
    print("-" * 50)
    start = time.time()
    try:
        response = client.chat.completions.create(
            model="gpt-oss:20b",
            messages=[{"role": "user", "content": test_prompt}],
            reasoning_effort="minimal"
        )
        time2 = time.time() - start
        print(f"  Response: {response.choices[0].message.content[:100]}")
        print(f"  ⏱️  Time: {time2:.3f}s")
        print(f"  ✅ reasoning_effort accepted!")
    except Exception as e:
        error_msg = str(e)
        if "reasoning_effort" in error_msg or "parameter" in error_msg:
            print(f"  ❌ reasoning_effort not supported: {error_msg[:80]}")
        else:
            print(f"  ❌ Other error: {error_msg[:80]}")
        time2 = None
    
    # Test 3: NLM system with local model (current implementation)
    print("\n3️⃣ NLM system with gpt-oss:20b:")
    print("-" * 50)
    print("  Note: Current implementation only adds reasoning_effort for OpenAI models")
    
    session = NLMSession(model="gpt-oss:20b", namespace="local_test")
    start = time.time()
    try:
        result = session.execute("Say hello")
        time3 = time.time() - start
        print(f"  Result: {result[:100]}...")
        print(f"  ⏱️  Time: {time3:.3f}s")
    except Exception as e:
        print(f"  ❌ Error: {e}")
        time3 = None
    
    # Analysis
    print("\n" + "="*70)
    print("📊 Results:")
    print("="*70)
    
    if time1 and time2:
        improvement = (time1 - time2) / time1 * 100
        if improvement > 0:
            print(f"✅ reasoning_effort works with local model!")
            print(f"   {improvement:.1f}% faster with 'minimal' setting")
            print(f"   {time1:.3f}s → {time2:.3f}s")
            
            print("\n💡 Recommendation:")
            print("   Update nlm_interpreter.py to include local models:")
            print("   Remove the OpenAI-only restriction for reasoning_effort")
        else:
            print(f"⚠️  No improvement with reasoning_effort")
            print(f"   Standard: {time1:.3f}s")
            print(f"   With minimal: {time2:.3f}s")
    elif time1 and not time2:
        print("❌ reasoning_effort not supported by local model")
        print("   This is expected - it's likely an OpenAI-specific parameter")
        print(f"   Local model baseline: {time1:.3f}s")
    
    if time3:
        print(f"\n📈 Current NLM performance with local: {time3:.3f}s")
        if time3 > 10:
            print("   🐢 Still slow - local model inherently slower than OpenAI")
        elif time3 < 5:
            print("   ✅ Reasonable performance for local model")


if __name__ == "__main__":
    try:
        test_local_reasoning()
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        print("\n💡 Make sure LMStudio or Ollama is running on localhost:1234")