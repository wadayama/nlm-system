#!/usr/bin/env python
"""Simple test of reasoning_effort parameter"""

import time
from openai import OpenAI


def test_reasoning_simple():
    """Simple test of reasoning_effort parameter"""
    print("="*60)
    print("🚀 Testing reasoning_effort='minimal' for gpt-5-nano")
    print("="*60)
    
    # Load API key
    try:
        with open('.openai_key', 'r') as f:
            api_key = f.read().strip()
    except FileNotFoundError:
        print("❌ .openai_key not found")
        return
    
    client = OpenAI(api_key=api_key)
    
    # Test 1: Standard call
    print("\n1️⃣ Standard API call:")
    start = time.time()
    try:
        response = client.chat.completions.create(
            model="gpt-5-nano",
            messages=[{"role": "user", "content": "Say hello"}]
        )
        time1 = time.time() - start
        print(f"  Response: {response.choices[0].message.content}")
        print(f"  ⏱️  Time: {time1:.3f}s")
    except Exception as e:
        print(f"  ❌ Error: {e}")
        time1 = None
    
    # Test 2: With reasoning_effort as parameter
    print("\n2️⃣ With reasoning_effort='minimal' (as parameter):")
    start = time.time()
    try:
        response = client.chat.completions.create(
            model="gpt-5-nano",
            messages=[{"role": "user", "content": "Say hello"}],
            reasoning_effort="minimal"  # Try as direct parameter
        )
        time2 = time.time() - start
        print(f"  Response: {response.choices[0].message.content}")
        print(f"  ⏱️  Time: {time2:.3f}s")
    except Exception as e:
        print(f"  ❌ Not supported as parameter: {str(e)[:80]}")
        time2 = None
    
    # Test 3: With reasoning_effort in extra_body
    print("\n3️⃣ With reasoning_effort='minimal' (in extra_body):")
    start = time.time()
    try:
        response = client.chat.completions.create(
            model="gpt-5-nano",
            messages=[{"role": "user", "content": "Say hello"}],
            extra_body={"reasoning_effort": "minimal"}  # Try in extra_body
        )
        time3 = time.time() - start
        print(f"  Response: {response.choices[0].message.content}")
        print(f"  ⏱️  Time: {time3:.3f}s")
    except Exception as e:
        print(f"  ❌ Not supported in extra_body: {str(e)[:80]}")
        time3 = None
    
    # Test 4: With model-specific options
    print("\n4️⃣ With reasoning_effort in model string (gpt-5-nano:minimal):")
    start = time.time()
    try:
        response = client.chat.completions.create(
            model="gpt-5-nano:minimal",  # Try appending to model name
            messages=[{"role": "user", "content": "Say hello"}]
        )
        time4 = time.time() - start
        print(f"  Response: {response.choices[0].message.content}")
        print(f"  ⏱️  Time: {time4:.3f}s")
    except Exception as e:
        print(f"  ❌ Not supported in model name: {str(e)[:80]}")
        time4 = None
    
    # Summary
    print("\n" + "="*60)
    print("📊 Results:")
    print("="*60)
    
    times = [
        ("Standard", time1),
        ("reasoning_effort param", time2),
        ("extra_body", time3),
        ("model suffix", time4)
    ]
    
    valid_times = [(name, t) for name, t in times if t is not None]
    
    if valid_times:
        print("\nSuccessful methods:")
        for name, t in valid_times:
            print(f"  {name}: {t:.3f}s")
        
        if len(valid_times) > 1:
            fastest = min(valid_times, key=lambda x: x[1])
            slowest = max(valid_times, key=lambda x: x[1])
            improvement = (slowest[1] - fastest[1]) / slowest[1] * 100
            print(f"\n⚡ Fastest: {fastest[0]} ({fastest[1]:.3f}s)")
            if improvement > 5:
                print(f"   {improvement:.1f}% faster than {slowest[0]}")
    else:
        print("\n❌ reasoning_effort parameter not supported")
        print("   This may be a feature for newer models or API versions")


if __name__ == "__main__":
    test_reasoning_simple()