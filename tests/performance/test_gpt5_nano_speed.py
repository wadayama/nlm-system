#!/usr/bin/env python
"""Speed measurement for gpt-5-nano only"""

import time
from nlm_interpreter import NLMSession
import statistics


def test_gpt5_nano_speed():
    """Measure gpt-5-nano execution speed"""
    print("="*60)
    print("⚡ GPT-5-NANO スピード測定")
    print("="*60)
    
    session = NLMSession(model="gpt-5-nano", namespace="speed_test")
    
    # Test cases
    test_cases = [
        ("Simple assignment", "Set {{var1}} to 'Speed Test'"),
        ("Math calculation", "Calculate 42 * 10 and save to {{result}}"),
        ("Multi-variable", "Set {{name}} to 'Alice' and {{age}} to 25"),
        ("Japanese", "{{メッセージ}}を'高速'に設定してください"),
        ("Complex", "Create a greeting {{greeting}} with 'Hello World'")
    ]
    
    times = []
    
    print("\n📊 実行時間測定:")
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
        print("📈 統計サマリー:")
        print("="*60)
        print(f"  実行回数: {len(times)}")
        print(f"  平均時間: {statistics.mean(times):.3f}s")
        print(f"  最速: {min(times):.3f}s")
        print(f"  最遅: {max(times):.3f}s")
        print(f"  中央値: {statistics.median(times):.3f}s")
        
        if statistics.mean(times) < 1.0:
            print("\n⚡ 非常に高速！1秒以下の平均応答時間")
        elif statistics.mean(times) < 2.0:
            print("\n✅ 高速！実用的な応答時間")
        elif statistics.mean(times) < 3.0:
            print("\n👍 良好な応答時間")
        else:
            print("\n🐢 応答時間が長め")


if __name__ == "__main__":
    try:
        test_gpt5_nano_speed()
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")