#!/usr/bin/env python
"""Speed measurement for gpt-5-mini only"""

import time
from nlm_interpreter import NLMSession
import statistics


def test_gpt5_mini_speed():
    """Measure gpt-5-mini execution speed"""
    print("="*60)
    print("⚡ GPT-5-MINI Speed Measurement")
    print("="*60)
    
    session = NLMSession(model="gpt-5-mini", namespace="speed_test")
    
    # Test cases (same as nano version for comparison)
    test_cases = [
        ("Simple assignment", "Set {{var1}} to 'Speed Test'"),
        ("Math calculation", "Calculate 42 * 10 and save to {{result}}"),
        ("Multi-variable", "Set {{name}} to 'Alice' and {{age}} to 25"),
        ("Japanese text", "Set {{メッセージ}} to '高速' please"),
        ("Complex", "Create a greeting {{greeting}} with 'Hello World'")
    ]
    
    times = []
    
    print("\n📊 Execution Time Measurement:")
    print("-" * 40)
    
    for test_name, command in test_cases:
        print(f"\n{test_name}:")
        print(f"  Command: {command}")
        
        start = time.time()
        try:
            result = session.execute(command)
            elapsed = time.time() - start
            times.append(elapsed)
            print(f"  ⏱️  Time: {elapsed:.3f}s")
            
            # Show variable value for verification
            if "{{" in command and "}}" in command:
                var_name = command[command.find("{{")+2:command.find("}}")]
                value = session.get(var_name)
                if value:
                    print(f"  ✅ Value: {value}")
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    # Statistics
    if times:
        print("\n" + "="*60)
        print("📈 Statistics Summary:")
        print("="*60)
        print(f"  Executions: {len(times)}")
        print(f"  Average time: {statistics.mean(times):.3f}s")
        print(f"  Fastest: {min(times):.3f}s")
        print(f"  Slowest: {max(times):.3f}s")
        print(f"  Median: {statistics.median(times):.3f}s")
        
        if statistics.mean(times) < 1.0:
            print("\n⚡ Extremely fast! Average response time under 1 second")
        elif statistics.mean(times) < 2.0:
            print("\n✅ Fast! Practical response time")
        elif statistics.mean(times) < 3.0:
            print("\n👍 Good response time")
        else:
            print("\n🐢 Slower response time")


if __name__ == "__main__":
    try:
        test_gpt5_mini_speed()
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")