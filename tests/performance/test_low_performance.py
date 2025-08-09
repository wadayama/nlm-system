#!/usr/bin/env python
"""Test performance with reasoning_effort='low'"""

import time
from nlm_interpreter import NLMSession
import statistics


def test_low_performance():
    """Test gpt-5-nano performance with reasoning_effort='low'"""
    print("="*70)
    print("⚡ GPT-5-NANO パフォーマンステスト (reasoning_effort='low')")
    print("="*70)
    
    session = NLMSession(model="gpt-5-nano", namespace="low_perf_test")
    
    # Test cases for comprehensive evaluation
    test_cases = [
        ("Simple assignment", "Set {{name}} to 'Alice'"),
        ("Math calculation", "Calculate 42 * 15 and save to {{result}}"),
        ("Multi-variable", "Set {{first}} to 'John' and {{last}} to 'Doe'"),
        ("Japanese", "{{都市}}を'大阪'に設定してください"),
        ("Complex calc", "Calculate (20 + 5) * 2 and store in {{calc}}"),
        ("No variable", "Tell me what is 3+7")
    ]
    
    times = []
    var_times = []
    no_var_times = []
    
    print("\n📊 reasoning_effort='low' 実行時間測定:")
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
                print(f"  ✅ Value: {value}")
            else:
                print(f"  📝 Result: {result[:60]}...")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    # Statistics
    if times:
        print("\n" + "="*70)
        print("📈 reasoning_effort='low' 統計サマリー:")
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
        print("📊 設定比較:")
        print("="*70)
        print("改善前（reasoning_effort なし）:")
        print("  変数なし: 3.3秒")
        print("  変数あり: 10.6秒")
        print("  平均: 11.3秒")
        
        print(f"\nreasoning_effort='minimal':")
        print("  変数なし: 1.2秒")
        print("  変数あり: 2.2秒 (品質問題あり)")
        print("  平均: 2.0秒")
        
        print(f"\nreasoning_effort='low' (現在):")
        if no_var_times:
            print(f"  変数なし: {statistics.mean(no_var_times):.1f}秒")
        if var_times:
            print(f"  変数あり: {statistics.mean(var_times):.1f}秒")
        print(f"  全体平均: {statistics.mean(times):.1f}秒")
        
        # Calculate improvement from baseline
        baseline_avg = 11.3
        current_avg = statistics.mean(times)
        improvement = (baseline_avg - current_avg) / baseline_avg * 100
        
        print(f"\n⚡ ベースラインからの改善:")
        if improvement > 0:
            print(f"  🎉 {improvement:.1f}% 高速化達成！")
            print(f"  {baseline_avg:.1f}秒 → {current_avg:.1f}秒")
        
        # Performance evaluation
        if current_avg < 3.0:
            print(f"\n✅ 優秀な応答速度！")
            print(f"   実用的なレベルを達成")
        elif current_avg < 5.0:
            print(f"\n👍 良好な応答速度")
            print(f"   日常使用に適している")
        elif current_avg < 8.0:
            print(f"\n⚠️ 許容可能な応答速度")
            print(f"   さらなる最適化の余地あり")
        else:
            print(f"\n🐢 改善が必要")
            print(f"   設定の見直しを検討")
        
        # Compare with minimal setting
        print(f"\n💡 'minimal' vs 'low' 比較:")
        minimal_avg = 2.0  # From previous test
        if current_avg > minimal_avg:
            slowdown = (current_avg - minimal_avg) / minimal_avg * 100
            print(f"  'low'は'minimal'より {slowdown:.1f}% 遅い")
            print(f"  しかし品質の安定性を重視")
        else:
            print(f"  'low'は'minimal'と同等またはより高速")


if __name__ == "__main__":
    try:
        test_low_performance()
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")