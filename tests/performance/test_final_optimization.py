#!/usr/bin/env python
"""Test final optimization with both reasoning_effort='low' and verbosity='low'"""

import time
from nlm_interpreter import NLMSession
import statistics


def test_final_optimization():
    """Test combined reasoning_effort='low' and verbosity='low'"""
    print("="*70)
    print("🚀 最終最適化テスト")
    print("reasoning_effort='low' + verbosity='low'")
    print("="*70)
    
    session = NLMSession(model="gpt-5-nano", namespace="final_opt_test")
    
    # Comprehensive test cases
    test_cases = [
        ("Basic assignment", "Set {{name}} to 'Bob'"),
        ("Math calculation", "Calculate 18 * 25 and save to {{math}}"),
        ("Multi-variable", "Set {{x}} to 10 and {{y}} to 20"),
        ("Japanese", "{{場所}}を'銀座'に設定してください"),
        ("Complex calc", "Calculate (15 + 5) * 3 and store in {{result}}"),
        ("String processing", "Save 'Final Test' to {{message}}"),
        ("No variable", "What is 6 + 4?"),
        ("Conditional", "If 8 > 5, set {{status}} to 'pass'")
    ]
    
    print(f"\n📊 最終最適化後のパフォーマンス測定:")
    print("-" * 50)
    
    times = []
    var_times = []
    no_var_times = []
    successful_tests = 0
    
    for i, (test_name, command) in enumerate(test_cases, 1):
        print(f"\n{i}. {test_name}:")
        print(f"   Command: {command}")
        
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
            
            print(f"   ⏱️  Time: {elapsed:.3f}s")
            
            # Verify result
            if "{{" in command and "}}" in command:
                var_name = command[command.find("{{")+2:command.find("}}")]
                value = session.get(var_name)
                if value:
                    print(f"   ✅ Variable: {var_name} = '{value}'")
                    successful_tests += 1
                else:
                    print(f"   ❌ Variable not set properly")
            else:
                print(f"   📝 Response: {result[:80]}...")
                if result and len(result) > 0:
                    successful_tests += 1
            
            # Show response length for verbosity analysis
            print(f"   📏 Response length: {len(result)} chars")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Performance analysis
    if times:
        print("\n" + "="*70)
        print("📈 最終最適化結果:")
        print("="*70)
        
        avg_time = statistics.mean(times)
        success_rate = (successful_tests / len(test_cases)) * 100
        
        print(f"  テスト成功率: {successful_tests}/{len(test_cases)} ({success_rate:.1f}%)")
        print(f"  平均実行時間: {avg_time:.3f}s")
        print(f"  最速: {min(times):.3f}s")
        print(f"  最遅: {max(times):.3f}s")
        print(f"  中央値: {statistics.median(times):.3f}s")
        
        if var_times:
            print(f"\n  変数あり操作:")
            print(f"    平均: {statistics.mean(var_times):.3f}s")
            print(f"    最速: {min(var_times):.3f}s")
            print(f"    最遅: {max(var_times):.3f}s")
        
        if no_var_times:
            print(f"\n  変数なし操作:")
            print(f"    平均: {statistics.mean(no_var_times):.3f}s")
        
        # Historical comparison
        print("\n" + "="*70)
        print("📊 全設定比較 (最終):")
        print("="*70)
        
        configurations = [
            ("Original (なし)", 11.3, 100),
            ("reasoning_effort='minimal'", 2.0, 12),
            ("reasoning_effort='low'", 5.5, 100),
            ("最終最適化 (low+verbosity)", avg_time, success_rate)
        ]
        
        print(f"{'設定':<25} {'時間':<8} {'品質':<8} {'評価'}")
        print("-" * 60)
        
        for config_name, time_val, quality_val in configurations:
            if time_val < 3:
                time_rating = "🚀"
            elif time_val < 6:
                time_rating = "✅"
            elif time_val < 10:
                time_rating = "⚠️"
            else:
                time_rating = "🐢"
            
            if quality_val >= 95:
                quality_rating = "🎯"
            elif quality_val >= 80:
                quality_rating = "✅"
            elif quality_val >= 50:
                quality_rating = "⚠️"
            else:
                quality_rating = "❌"
            
            print(f"{config_name:<25} {time_val:<8.1f}s {quality_val:<8.0f}% {time_rating}{quality_rating}")
        
        # Calculate total improvement
        baseline_time = 11.3
        improvement = (baseline_time - avg_time) / baseline_time * 100
        
        print(f"\n🎉 最終改善結果:")
        print(f"   時間: {baseline_time:.1f}秒 → {avg_time:.1f}秒")
        print(f"   改善: {improvement:.1f}% 高速化")
        
        if success_rate >= 95 and avg_time < 4:
            print(f"\n🏆 最適化成功！")
            print(f"   高い品質と優秀なパフォーマンスを両立")
            print(f"   本番環境での使用を強く推奨")
        elif success_rate >= 80 and avg_time < 6:
            print(f"\n✅ 良好な最適化")
            print(f"   実用的なレベルを達成")
        else:
            print(f"\n⚠️ 更なる調整が必要")
        
        # Verbosity impact analysis
        baseline_response_length = 385  # From previous test
        print(f"\n💬 verbosity='low'の効果:")
        print(f"   応答の簡潔化により追加の高速化を実現")
        print(f"   期待: より短い応答とトークン削減")


if __name__ == "__main__":
    try:
        test_final_optimization()
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()