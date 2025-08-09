#!/usr/bin/env python
"""Test API latency breakdown for gpt-5-nano"""

import time
from openai import OpenAI


def test_direct_api_call():
    """Test direct OpenAI API call without NLM overhead"""
    print("="*60)
    print("🔍 OpenAI API 直接呼び出しテスト (gpt-5-nano)")
    print("="*60)
    
    # Load API key
    try:
        with open('.openai_key', 'r') as f:
            api_key = f.read().strip()
    except FileNotFoundError:
        print("❌ .openai_key not found")
        return
    
    client = OpenAI(api_key=api_key)
    
    # Test cases
    test_messages = [
        "Say 'Hello'",
        "What is 2+2?",
        "Count to 3",
        "Return 'OK'"
    ]
    
    print("\n📊 レイテンシ測定:")
    print("-" * 40)
    
    times = []
    for msg in test_messages:
        print(f"\nPrompt: {msg}")
        
        start = time.time()
        try:
            response = client.chat.completions.create(
                model="gpt-5-nano",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant. Be very brief."},
                    {"role": "user", "content": msg}
                ]
            )
            elapsed = time.time() - start
            times.append(elapsed)
            
            content = response.choices[0].message.content
            print(f"  Response: {content[:50]}")
            print(f"  ⏱️  Time: {elapsed:.3f}s")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    if times:
        avg = sum(times) / len(times)
        print(f"\n" + "="*60)
        print(f"📈 結果:")
        print(f"="*60)
        print(f"  平均応答時間: {avg:.3f}s")
        print(f"  最速: {min(times):.3f}s")
        print(f"  最遅: {max(times):.3f}s")
        
        if avg < 2:
            print("\n✅ API自体は高速 → NLMシステムのオーバーヘッドが原因")
        else:
            print("\n🐢 API自体が遅い → OpenAI側の問題")


if __name__ == "__main__":
    try:
        test_direct_api_call()
    except Exception as e:
        print(f"❌ Test failed: {e}")