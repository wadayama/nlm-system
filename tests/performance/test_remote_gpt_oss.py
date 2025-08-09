#!/usr/bin/env python
"""Test if gpt-oss:20b can be used via OpenAI API endpoint"""

from openai import OpenAI
import time


def test_remote_gpt_oss():
    """Test gpt-oss:20b via OpenAI API"""
    print("="*60)
    print("🔍 Testing gpt-oss:20b via OpenAI API")
    print("="*60)
    
    # Load API key
    try:
        with open('.openai_key', 'r') as f:
            api_key = f.read().strip()
    except FileNotFoundError:
        print("❌ .openai_key not found")
        return
    
    # Test with OpenAI endpoint
    print("\n1️⃣ Trying gpt-oss:20b via OpenAI API:")
    print("-" * 40)
    
    client = OpenAI(api_key=api_key)
    
    try:
        start = time.time()
        response = client.chat.completions.create(
            model="gpt-oss:20b",  # Try using local model name
            messages=[
                {"role": "user", "content": "Say hello"}
            ]
        )
        elapsed = time.time() - start
        
        print(f"✅ Success!")
        print(f"Response: {response.choices[0].message.content}")
        print(f"Time: {elapsed:.3f}s")
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        error_str = str(e)
        if "model" in error_str.lower():
            print("\n💡 gpt-oss:20b is not available via OpenAI API")
            print("   This is a local-only model")
    
    # List available models
    print("\n2️⃣ Available OpenAI models:")
    print("-" * 40)
    try:
        # Try to list models (if supported)
        models = client.models.list()
        gpt_models = [m.id for m in models if 'gpt' in m.id.lower()]
        print(f"Found {len(gpt_models)} GPT models:")
        for model in gpt_models[:10]:  # Show first 10
            print(f"  - {model}")
    except Exception as e:
        print(f"Could not list models: {e}")
        print("\nKnown available models:")
        print("  - gpt-5")
        print("  - gpt-5-mini")
        print("  - gpt-5-nano")


if __name__ == "__main__":
    test_remote_gpt_oss()