#!/usr/bin/env python
"""Test final optimization with gpt-5-mini: reasoning_effort='low' + verbosity='low'"""

import time
from nlm_interpreter import NLMSession
import statistics


def test_gpt5_mini_final():
    """Test combined reasoning_effort='low' and verbosity='low' with gpt-5-mini"""
    print("="*70)
    print("🚀 GPT-5-MINI 最終最適化テスト")
    print("reasoning_effort='low' + verbosity='low'")
    print("="*70)
    
    session = NLMSession(model="gpt-5-mini", namespace="mini_final_test")
    
    # Same test cases as gpt-5-nano for comparison
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
    
    print(f"\n📊 GPT-5-MINI 最適化後のパフォーマンス測定:")
    print("-" * 50)
    
    times = []
    var_times = []
    no_var_times = []
    successful_tests = 0
    response_lengths = []
    
    for i, (test_name, command) in enumerate(test_cases, 1):
        print(f"\n{i}. {test_name}:")
        print(f"   Command: {command}")
        
        start = time.time()
        try:
            result = session.execute(command)
            elapsed = time.time() - start
            times.append(elapsed)
            response_lengths.append(len(result))
            
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
        print("📈 GPT-5-MINI 最終最適化結果:")
        print("="*70)
        
        avg_time = statistics.mean(times)
        success_rate = (successful_tests / len(test_cases)) * 100
        avg_response_length = statistics.mean(response_lengths) if response_lengths else 0
        
        print(f"  テスト成功率: {successful_tests}/{len(test_cases)} ({success_rate:.1f}%)")
        print(f"  平均実行時間: {avg_time:.3f}s")
        print(f"  最速: {min(times):.3f}s")
        print(f"  最遅: {max(times):.3f}s")
        print(f"  中央値: {statistics.median(times):.3f}s")
        print(f"  平均応答長: {avg_response_length:.0f} chars")
        
        if var_times:
            print(f"\n  変数あり操作:")
            print(f"    平均: {statistics.mean(var_times):.3f}s")
            print(f"    最速: {min(var_times):.3f}s")
            print(f"    最遅: {max(var_times):.3f}s")
        
        if no_var_times:
            print(f"\n  変数なし操作:")
            print(f"    平均: {statistics.mean(no_var_times):.3f}s")
        
        # Model comparison
        print("\n" + "="*70)
        print("🆚 GPT-5-NANO vs GPT-5-MINI 比較:")
        print("="*70)
        
        # gpt-5-nano results from previous test
        nano_results = {
            "avg_time": 4.085,
            "success_rate": 100.0,
            "var_avg": 4.462,
            "no_var_avg": 1.444
        }
        
        print(f"{'Metric':<20} {'GPT-5-NANO':<15} {'GPT-5-MINI':<15} {'Winner'}")
        print("-" * 65)
        
        # Overall time
        nano_faster = nano_results["avg_time"] < avg_time
        time_winner = "NANO 🏆" if nano_faster else "MINI 🏆"
        print(f"{'Average Time':<20} {nano_results['avg_time']:<15.3f}s {avg_time:<15.3f}s {time_winner}")
        
        # Success rate
        success_winner = "NANO 🏆" if nano_results["success_rate"] > success_rate else "MINI 🏆" if success_rate > nano_results["success_rate"] else "TIE 🤝"
        print(f"{'Success Rate':<20} {nano_results['success_rate']:<15.1f}% {success_rate:<15.1f}% {success_winner}")
        
        # Variable operations
        if var_times:
            var_avg = statistics.mean(var_times)
            var_winner = "NANO 🏆" if nano_results["var_avg"] < var_avg else "MINI 🏆"
            print(f"{'Variable Ops':<20} {nano_results['var_avg']:<15.3f}s {var_avg:<15.3f}s {var_winner}")
        
        # No variable operations
        if no_var_times:
            no_var_avg = statistics.mean(no_var_times)
            no_var_winner = "NANO 🏆" if nano_results["no_var_avg"] < no_var_avg else "MINI 🏆"
            print(f"{'No Variable Ops':<20} {nano_results['no_var_avg']:<15.3f}s {no_var_avg:<15.3f}s {no_var_winner}")
        
        # Overall performance rating
        print(f"\n🏆 総合評価:")
        if success_rate >= 95 and avg_time < 3:
            mini_rating = "🚀 Excellent"
        elif success_rate >= 90 and avg_time < 5:
            mini_rating = "✅ Very Good"
        elif success_rate >= 80 and avg_time < 8:
            mini_rating = "👍 Good"
        else:
            mini_rating = "⚠️ Needs Improvement"
        
        print(f"  GPT-5-MINI: {mini_rating}")
        print(f"  GPT-5-NANO: ✅ Very Good (参考)")
        
        # Recommendation
        print(f"\n💡 推奨事項:")
        if avg_time < nano_results["avg_time"] and success_rate >= nano_results["success_rate"]:
            print(f"  🎯 GPT-5-MINI が総合的に優秀")
            print(f"     速度と品質の両方で優位性を示す")
        elif success_rate >= 95:
            print(f"  ✅ 両モデルとも実用レベル")
            print(f"     用途に応じて選択可能")
            if avg_time < nano_results["avg_time"]:
                print(f"     速度重視: GPT-5-MINI")
            else:
                print(f"     バランス重視: 両方とも良好")
        else:
            print(f"  ⚠️ 品質の確認が必要")
        
        # Historical comparison for GPT-5-MINI
        print("\n" + "="*70)
        print("📊 GPT-5-MINI 設定別比較:")
        print("="*70)
        
        # Previous gpt-5-mini results (if available from earlier tests)
        configurations = [
            ("Original (なし)", 11.3, 100),  # Estimated
            ("reasoning_effort='low'", 5.5, 100),  # From previous test
            ("最終最適化 (low+verbosity)", avg_time, success_rate)
        ]
        
        print(f"{'設定':<30} {'時間':<8} {'品質':<8} {'評価'}")
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
            
            print(f"{config_name:<30} {time_val:<8.1f}s {quality_val:<8.0f}% {time_rating}{quality_rating}")
        
        # Calculate improvement
        baseline_time = 11.3
        improvement = (baseline_time - avg_time) / baseline_time * 100
        
        print(f"\n🎉 GPT-5-MINI 改善結果:")
        print(f"   時間: {baseline_time:.1f}秒 → {avg_time:.1f}秒")
        print(f"   改善: {improvement:.1f}% 高速化")


if __name__ == "__main__":
    try:
        test_gpt5_mini_final()
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()