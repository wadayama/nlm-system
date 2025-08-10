#!/usr/bin/env python
"""Speed comparison between gpt-5-nano and gpt-oss:20b"""

import time
from nlm_interpreter import NLMSession
import statistics


def measure_execution_time(session, command, runs=3):
    """Measure average execution time over multiple runs"""
    times = []
    
    for i in range(runs):
        start = time.time()
        try:
            result = session.execute(command)
            elapsed = time.time() - start
            times.append(elapsed)
            print(f"      Run {i+1}: {elapsed:.3f}s")
        except Exception as e:
            print(f"      Run {i+1}: Failed - {e}")
            continue
    
    if times:
        return {
            "avg": statistics.mean(times),
            "min": min(times),
            "max": max(times),
            "median": statistics.median(times),
            "runs": len(times)
        }
    return None


def run_speed_comparison():
    """Compare speed between gpt-5-nano and gpt-oss:20b"""
    print("="*70)
    print("🏁 SPEED COMPARISON: gpt-5-nano vs gpt-oss:20b")
    print("="*70)
    
    # Test cases
    test_cases = [
        ("Simple assignment", "Set {{test_var}} to 'Speed Test'"),
        ("Math calculation", "Calculate 123 * 456 and save to {{result}}"),
        ("Multi-variable", "Set {{name}} to 'Test' and {{value}} to 100"),
        ("Japanese processing", "{{メッセージ}}を'高速テスト'に設定してください")
    ]
    
    results = {}
    
    # Test gpt-5-nano
    print("\n🚀 Testing gpt-5-nano (OpenAI Cloud)")
    print("-" * 50)
    session_nano = NLMSession(model="gpt-5-nano", namespace="speed_test_nano")
    nano_times = []
    
    for test_name, command in test_cases:
        print(f"\n   📝 {test_name}:")
        print(f"      Command: {command[:50]}...")
        result = measure_execution_time(session_nano, command, runs=3)
        if result:
            nano_times.append(result['avg'])
            print(f"      Average: {result['avg']:.3f}s (min: {result['min']:.3f}s, max: {result['max']:.3f}s)")
    
    # Test gpt-oss:20b
    print("\n\n🖥️  Testing gpt-oss:20b (Local)")
    print("-" * 50)
    session_local = NLMSession(model="gpt-oss:20b", namespace="speed_test_local")
    local_times = []
    
    for test_name, command in test_cases:
        print(f"\n   📝 {test_name}:")
        print(f"      Command: {command[:50]}...")
        result = measure_execution_time(session_local, command, runs=3)
        if result:
            local_times.append(result['avg'])
            print(f"      Average: {result['avg']:.3f}s (min: {result['min']:.3f}s, max: {result['max']:.3f}s)")
    
    # Summary
    print("\n\n" + "="*70)
    print("📊 PERFORMANCE SUMMARY")
    print("="*70)
    
    if nano_times and local_times:
        nano_avg = statistics.mean(nano_times)
        local_avg = statistics.mean(local_times)
        
        print(f"\n🚀 gpt-5-nano (OpenAI):")
        print(f"   Average response time: {nano_avg:.3f}s")
        print(f"   Min: {min(nano_times):.3f}s")
        print(f"   Max: {max(nano_times):.3f}s")
        
        print(f"\n🖥️  gpt-oss:20b (Local):")
        print(f"   Average response time: {local_avg:.3f}s")
        print(f"   Min: {min(local_times):.3f}s")
        print(f"   Max: {max(local_times):.3f}s")
        
        # Speed comparison
        speedup = local_avg / nano_avg
        print(f"\n⚡ SPEED COMPARISON:")
        print(f"   gpt-5-nano is {speedup:.1f}x faster than gpt-oss:20b")
        
        if speedup > 3:
            print(f"   🎯 Significant performance advantage!")
            print(f"   💡 Recommendation: Use gpt-5-nano for time-critical tasks")
        elif speedup > 1.5:
            print(f"   ✅ Notable performance improvement")
            print(f"   💡 Recommendation: Consider gpt-5-nano for better responsiveness")
        else:
            print(f"   🤝 Comparable performance")
            print(f"   💡 Recommendation: Choose based on cost and privacy requirements")
        
        # Detailed comparison table
        print(f"\n📈 DETAILED COMPARISON:")
        print(f"   {'Task':<25} {'gpt-5-nano':<12} {'gpt-oss:20b':<12} {'Speedup':<10}")
        print(f"   {'-'*25} {'-'*12} {'-'*12} {'-'*10}")
        
        for i, (test_name, _) in enumerate(test_cases):
            if i < len(nano_times) and i < len(local_times):
                speedup_task = local_times[i] / nano_times[i]
                print(f"   {test_name:<25} {nano_times[i]:<12.3f} {local_times[i]:<12.3f} {speedup_task:<10.1f}x")
        
        # Cost-benefit analysis
        print(f"\n💰 COST-BENEFIT ANALYSIS:")
        print(f"   gpt-5-nano:")
        print(f"      ✅ {speedup:.1f}x faster response")
        print(f"      ❌ API costs apply")
        print(f"      ❌ Requires internet connection")
        print(f"      ✅ No local GPU/CPU load")
        
        print(f"\n   gpt-oss:20b:")
        print(f"      ✅ Free (no API costs)")
        print(f"      ✅ Works offline")
        print(f"      ✅ Complete privacy")
        print(f"      ❌ {speedup:.1f}x slower")
        print(f"      ❌ Uses local resources")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    try:
        run_speed_comparison()
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()