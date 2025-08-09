#!/usr/bin/env python
"""Simple speed comparison between gpt-5-nano and gpt-oss:20b"""

import time
from nlm_interpreter import NLMSession


def test_single_execution():
    """Compare single execution speed"""
    print("="*60)
    print("⚡ SPEED TEST: gpt-5-nano vs gpt-oss:20b")
    print("="*60)
    
    command = "Set {{benchmark}} to 'Hello Speed Test'"
    
    # Test gpt-5-nano
    print("\n🚀 gpt-5-nano (OpenAI):")
    session_nano = NLMSession(model="gpt-5-nano", namespace="benchmark_nano")
    
    start = time.time()
    result_nano = session_nano.execute(command)
    nano_time = time.time() - start
    value_nano = session_nano.get("benchmark")
    
    print(f"   Time: {nano_time:.3f}s")
    print(f"   Result: {value_nano}")
    
    # Test gpt-oss:20b
    print("\n🖥️  gpt-oss:20b (Local):")
    session_local = NLMSession(model="gpt-oss:20b", namespace="benchmark_local")
    
    start = time.time()
    result_local = session_local.execute(command)
    local_time = time.time() - start
    value_local = session_local.get("benchmark")
    
    print(f"   Time: {local_time:.3f}s")
    print(f"   Result: {value_local}")
    
    # Comparison
    print("\n" + "="*60)
    print("📊 RESULTS:")
    print("="*60)
    speedup = local_time / nano_time
    
    print(f"   gpt-5-nano:  {nano_time:.3f}s")
    print(f"   gpt-oss:20b: {local_time:.3f}s")
    print(f"\n⚡ gpt-5-nano is {speedup:.1f}x faster!")
    
    if speedup > 3:
        print("   🚀 Massive speed advantage for gpt-5-nano")
    elif speedup > 2:
        print("   ✅ Significant speed advantage for gpt-5-nano")
    elif speedup > 1.5:
        print("   👍 Notable speed advantage for gpt-5-nano")
    else:
        print("   🤝 Similar performance")


if __name__ == "__main__":
    try:
        test_single_execution()
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()