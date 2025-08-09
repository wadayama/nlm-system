#!/usr/bin/env python
"""Test improved performance with reasoning_effort='minimal'"""

import time
from nlm_interpreter import NLMSession
import statistics


def test_improved_performance():
    """Measure gpt-5-nano performance with reasoning_effort='minimal'"""
    print("="*70)
    print("⚡ GPT-5-NANO 高速化テスト (reasoning_effort='minimal')")
    print("="*70)
    
    session = NLMSession(model="gpt-5-nano", namespace="speed_test_improved")
    
    # Test cases (same as before for comparison)
    test_cases = [
        ("Simple assignment", "Set {{var1}} to 'Speed Test'"),
        ("Math calculation", "Calculate 42 * 10 and save to {{result}}"),
        ("Multi-variable", "Set {{name}} to 'Alice' and {{age}} to 25"),
        ("Japanese", "{{メッセージ}}を'高速'に設定してください"),
        ("No variable", "Tell me what is 2+2")  # Added no-variable test
    ]
    
    times = []
    var_times = []
    no_var_times = []
    
    print("\n📊 改善後の実行時間測定:")
    print("-" * 50)
    
    for test_name, command in test_cases:
        print(f"\n{test_name}:")
        print(f"  Command: {command}")
        
        start = time.time()
        try:
            result = session.execute(command)
            elapsed = time.time() - start
            times.append(elapsed)
            
            # Categorize times
            if "{{" in command:
                var_times.append(elapsed)
            else:
                no_var_times.append(elapsed)
            
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
        print("\n" + "="*70)
        print("📈 改善後の統計サマリー:")
        print("="*70)
        print(f"  実行回数: {len(times)}")
        print(f"  平均時間: {statistics.mean(times):.3f}s")
        print(f"  最速: {min(times):.3f}s")
        print(f"  最遅: {max(times):.3f}s")
        print(f"  中央値: {statistics.median(times):.3f}s")
        
        if var_times:
            print(f"\n  変数あり操作:")
            print(f"    平均: {statistics.mean(var_times):.3f}s")
            print(f"    範囲: {min(var_times):.3f}s - {max(var_times):.3f}s")
        
        if no_var_times:
            print(f"\n  変数なし操作:")
            print(f"    平均: {statistics.mean(no_var_times):.3f}s")
        
        # Compare with previous results
        print("\n" + "="*70)
        print("📊 改善前との比較:")
        print("="*70)
        print("改善前（reasoning_effort なし）:")
        print("  変数なし: 3.3秒")
        print("  変数あり: 10.6秒")
        print("  平均: 11.3秒")
        
        print(f"\n改善後（reasoning_effort='minimal'）:")
        if no_var_times:
            print(f"  変数なし: {statistics.mean(no_var_times):.1f}秒")
        if var_times:
            print(f"  変数あり: {statistics.mean(var_times):.1f}秒")
        print(f"  全体平均: {statistics.mean(times):.1f}秒")
        
        # Calculate improvement
        print("\n⚡ パフォーマンス改善:")
        old_avg = 11.3
        new_avg = statistics.mean(times)
        improvement = (old_avg - new_avg) / old_avg * 100
        
        if improvement > 0:
            print(f"  🎉 {improvement:.1f}% 高速化達成！")
            print(f"  {old_avg:.1f}秒 → {new_avg:.1f}秒")
        else:
            print(f"  ⚠️ 改善なし")
        
        # Performance evaluation
        if new_avg < 5.0:
            print("\n✅ 実用的な応答速度を達成！")
        elif new_avg < 8.0:
            print("\n👍 許容可能な応答速度")
        else:
            print("\n🐢 まだ改善の余地あり")


if __name__ == "__main__":
    try:
        test_improved_performance()
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")