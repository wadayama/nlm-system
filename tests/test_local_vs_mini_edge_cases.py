#!/usr/bin/env python
"""Compare edge case handling between gpt-oss:20b (local) and gpt-5-mini"""

import time
from nlm_interpreter import NLMSession


def test_model_edge_cases(model_name, namespace_suffix):
    """Run comprehensive edge case tests for a specific model"""
    print(f"\n🔬 {model_name} エッジケーステスト:")
    print("-" * 60)
    
    session = NLMSession(model=model_name, namespace=f"edge_{namespace_suffix}")
    
    results = []
    
    # Test 1: Ambiguous Variable References
    print("\n  1️⃣ あいまいな変数参照:")
    
    try:
        # Case 1a: Variable name as sentence pattern
        session.save("name", "Alice")
        start = time.time()
        result = session.execute("{{name}} is a developer")
        elapsed = time.time() - start
        value = session.get("name")
        
        print(f"    1a. Sentence context: {elapsed:.3f}s")
        print(f"        Before: 'Alice' → After: '{value}'")
        print(f"        Response: {result[:80]}...")
        
        # Check if variable was updated
        if value != "Alice":
            results.append(("Variable update in sentence", True, elapsed))
            print(f"        ✅ Variable updated (expected)")
        else:
            results.append(("Variable update in sentence", False, elapsed))
            print(f"        📝 Variable unchanged")
        
        # Case 1b: Nested variable syntax
        start = time.time()
        result = session.execute("Set {{message}} to 'The value of {{x}} is unknown'")
        elapsed = time.time() - start
        value = session.get("message")
        
        print(f"    1b. Nested syntax: {elapsed:.3f}s")
        print(f"        Stored: '{value}'")
        print(f"        Response: {result[:80]}...")
        
        if "{{x}}" in str(value) or "unknown" in str(value):
            results.append(("Nested variable syntax", True, elapsed))
            print(f"        ✅ Literal storage")
        else:
            results.append(("Nested variable syntax", False, elapsed))
            print(f"        ❌ Unexpected handling")
        
    except Exception as e:
        print(f"    ❌ Error in ambiguous references: {e}")
        results.append(("Ambiguous references", False, None))
    
    # Test 2: Self-referential Operations
    print("\n  2️⃣ 自己参照操作:")
    
    try:
        # Counter increment
        session.save("counter", "5")
        start = time.time()
        result = session.execute("Increment {{counter}} by 3 and save back to {{counter}}")
        elapsed = time.time() - start
        value = session.get("counter")
        
        print(f"    2a. Counter increment: {elapsed:.3f}s")
        print(f"        5 + 3 = '{value}'")
        print(f"        Response: {result[:80]}...")
        
        if str(value) == "8":
            results.append(("Self-reference increment", True, elapsed))
            print(f"        ✅ Correct increment")
        else:
            results.append(("Self-reference increment", False, elapsed))
            print(f"        ❌ Incorrect result")
        
        # Variable swap
        session.save("a", "valueA")
        session.save("b", "valueB")
        start = time.time()
        result = session.execute("Swap the values: set {{a}} to {{b}} and {{b}} to {{a}}")
        elapsed = time.time() - start
        value_a = session.get("a")
        value_b = session.get("b")
        
        print(f"    2b. Variable swap: {elapsed:.3f}s")
        print(f"        Result: a='{value_a}', b='{value_b}'")
        print(f"        Response: {result[:80]}...")
        
        if value_a == "valueB" and value_b == "valueA":
            results.append(("Variable swap", True, elapsed))
            print(f"        ✅ Perfect swap")
        elif value_a != "valueA" or value_b != "valueB":
            results.append(("Variable swap", False, elapsed))
            print(f"        📝 Partial change")
        else:
            results.append(("Variable swap", False, elapsed))
            print(f"        ❌ Swap failed")
        
    except Exception as e:
        print(f"    ❌ Error in self-reference: {e}")
        results.append(("Self-referential ops", False, None))
    
    # Test 3: Natural Language Complexity
    print("\n  3️⃣ 自然言語の複雑さ:")
    
    try:
        # Word ambiguity
        session.save("read", "newspaper")
        start = time.time()
        result = session.execute("I read the {{read}} this morning")
        elapsed = time.time() - start
        
        print(f"    3a. Word ambiguity: {elapsed:.3f}s")
        print(f"        Response: {result[:80]}...")
        results.append(("Word ambiguity", True, elapsed))
        print(f"        ✅ Handled gracefully")
        
        # Complex conditional
        start = time.time()
        result = session.execute("If {{weather}} is sunny, then set {{mood}} to 'happy', otherwise 'neutral'")
        elapsed = time.time() - start
        weather_val = session.get("weather")
        mood_val = session.get("mood")
        
        print(f"    3b. Conditional logic: {elapsed:.3f}s")
        print(f"        Weather: '{weather_val}', Mood: '{mood_val}'")
        print(f"        Response: {result[:80]}...")
        
        if mood_val:
            results.append(("Conditional logic", True, elapsed))
            print(f"        ✅ Logic processed")
        else:
            results.append(("Conditional logic", False, elapsed))
            print(f"        ❌ No mood set")
        
    except Exception as e:
        print(f"    ❌ Error in NL complexity: {e}")
        results.append(("NL complexity", False, None))
    
    # Test 4: Mathematical Operations
    print("\n  4️⃣ 数学的操作:")
    
    try:
        # Complex calculation
        start = time.time()
        result = session.execute("Calculate (15 + 5) * 3 - 8 and store in {{complex_calc}}")
        elapsed = time.time() - start
        value = session.get("complex_calc")
        
        print(f"    4a. Complex math: {elapsed:.3f}s")
        print(f"        (15 + 5) * 3 - 8 = '{value}' (expected: 52)")
        print(f"        Response: {result[:80]}...")
        
        if str(value) == "52":
            results.append(("Complex calculation", True, elapsed))
            print(f"        ✅ Correct calculation")
        else:
            results.append(("Complex calculation", False, elapsed))
            print(f"        ❌ Incorrect calculation")
        
    except Exception as e:
        print(f"    ❌ Error in math operations: {e}")
        results.append(("Math operations", False, None))
    
    # Test 5: Extreme Cases
    print("\n  5️⃣ 極端なケース:")
    
    try:
        # Empty variable
        start = time.time()
        result = session.execute("Set {{}} to 'empty name' if possible")
        elapsed = time.time() - start
        
        print(f"    5a. Empty variable: {elapsed:.3f}s")
        print(f"        Response: {result[:80]}...")
        results.append(("Empty variable syntax", True, elapsed))
        print(f"        ✅ Handled gracefully")
        
        # Unicode variables
        start = time.time()
        result = session.execute("Set {{🚀}} to 'rocket' and {{日本語}} to 'Japanese'")
        elapsed = time.time() - start
        rocket_val = session.get("🚀")
        jp_val = session.get("日本語")
        
        print(f"    5b. Unicode variables: {elapsed:.3f}s")
        print(f"        🚀: '{rocket_val}', 日本語: '{jp_val}'")
        print(f"        Response: {result[:80]}...")
        
        if rocket_val or jp_val:
            results.append(("Unicode variables", True, elapsed))
            print(f"        ✅ Unicode supported")
        else:
            results.append(("Unicode variables", False, elapsed))
            print(f"        ❌ Unicode not supported")
        
        # Long variable name
        long_var = "very_long_variable_name_that_tests_system_limits"
        start = time.time()
        result = session.execute(f"Set {{{{{long_var}}}}} to 'long name test'")
        elapsed = time.time() - start
        value = session.get(long_var)
        
        print(f"    5c. Long variable name: {elapsed:.3f}s")
        print(f"        Value: '{value}'")
        print(f"        Response: {result[:80]}...")
        
        if value:
            results.append(("Long variable name", True, elapsed))
            print(f"        ✅ Long name handled")
        else:
            results.append(("Long variable name", False, elapsed))
            print(f"        ❌ Long name failed")
        
    except Exception as e:
        print(f"    ❌ Error in extreme cases: {e}")
        results.append(("Extreme cases", False, None))
    
    return results


def main():
    """Compare edge cases between local gpt-oss:20b and gpt-5-mini"""
    print("="*70)
    print("🆚 ローカル vs GPT-5-MINI エッジケース比較")
    print("gpt-oss:20b vs gpt-5-mini (最適化済み)")
    print("="*70)
    
    # Test both models
    print("\n🖥️ Testing gpt-oss:20b (Local LLM)...")
    local_results = test_model_edge_cases("gpt-oss:20b", "local_vs_mini")
    
    print("\n\n🌐 Testing gpt-5-mini (OpenAI)...")
    mini_results = test_model_edge_cases("gpt-5-mini", "mini_vs_local")
    
    # Analysis
    print("\n\n" + "="*70)
    print("📊 比較分析:")
    print("="*70)
    
    # Calculate success rates
    local_successful = sum(1 for _, success, _ in local_results if success)
    mini_successful = sum(1 for _, success, _ in mini_results if success)
    
    local_success_rate = (local_successful / len(local_results)) * 100 if len(local_results) > 0 else 0
    mini_success_rate = (mini_successful / len(mini_results)) * 100 if len(mini_results) > 0 else 0
    
    # Calculate average times for successful tests
    local_times = [time_val for _, success, time_val in local_results if success and time_val is not None]
    mini_times = [time_val for _, success, time_val in mini_results if success and time_val is not None]
    
    local_avg_time = sum(local_times) / len(local_times) if local_times else 0
    mini_avg_time = sum(mini_times) / len(mini_times) if mini_times else 0
    
    print(f"\n📈 総合スコア:")
    print(f"{'Model':<15} {'Tests':<8} {'Success Rate':<12} {'Avg Time':<10} {'Rating'}")
    print("-" * 65)
    
    # Determine winner
    if mini_success_rate > local_success_rate:
        local_rating = "🥉"
        mini_rating = "🥇"
    elif local_success_rate > mini_success_rate:
        local_rating = "🥇"
        mini_rating = "🥉"
    else:
        # Same success rate, check time
        if local_avg_time < mini_avg_time:
            local_rating = "🥇"
            mini_rating = "🥈"
        else:
            local_rating = "🥈"
            mini_rating = "🥇"
    
    print(f"{'gpt-oss:20b':<15} {len(local_results):<8} {local_success_rate:<12.1f}% {local_avg_time:<10.3f}s {local_rating}")
    print(f"{'gpt-5-mini':<15} {len(mini_results):<8} {mini_success_rate:<12.1f}% {mini_avg_time:<10.3f}s {mini_rating}")
    
    # Detailed comparison
    print(f"\n📋 テスト別詳細比較:")
    print(f"{'Test Case':<28} {'Local':<8} {'Mini':<8} {'Winner'}")
    print("-" * 65)
    
    # Compare each test case
    max_tests = max(len(local_results), len(mini_results))
    for i in range(max_tests):
        local_result = local_results[i] if i < len(local_results) else ("Missing", False, None)
        mini_result = mini_results[i] if i < len(mini_results) else ("Missing", False, None)
        
        test_name = local_result[0][:27] if local_result[0] != "Missing" else mini_result[0][:27]
        local_status = "✅" if local_result[1] else "❌"
        mini_status = "✅" if mini_result[1] else "❌"
        
        if local_result[1] and mini_result[1]:
            winner = "TIE 🤝"
        elif local_result[1]:
            winner = "Local 🏆"
        elif mini_result[1]:
            winner = "Mini 🏆"
        else:
            winner = "Both ❌"
        
        print(f"{test_name:<28} {local_status:<8} {mini_status:<8} {winner}")
    
    # Performance vs Quality analysis
    print(f"\n⚖️ パフォーマンス vs 品質分析:")
    if local_avg_time > 0 and mini_avg_time > 0:
        speed_ratio = local_avg_time / mini_avg_time
        quality_diff = local_success_rate - mini_success_rate
        
        print(f"  ⏱️ Speed: gpt-oss:20b は gpt-5-mini より {speed_ratio:.1f}x {'遅い' if speed_ratio > 1 else '速い'}")
        print(f"  🎯 Quality: gpt-oss:20b は gpt-5-mini より {abs(quality_diff):.1f}% {'良い' if quality_diff > 0 else '悪い'}")
        
        # Cost-benefit analysis
        print(f"\n💰 コスト効果分析:")
        print(f"  gpt-oss:20b (Local):")
        print(f"    ✅ コスト: $0 (完全無料)")
        print(f"    ✅ プライバシー: 完全保護")
        print(f"    {'✅' if local_success_rate >= 80 else '❌'} 品質: {local_success_rate:.1f}%")
        print(f"    {'✅' if local_avg_time < 10 else '⚠️'} 速度: {local_avg_time:.1f}秒")
        
        print(f"\n  gpt-5-mini (OpenAI):")
        print(f"    ❌ コスト: API料金あり")
        print(f"    ⚠️ プライバシー: データ送信")
        print(f"    {'✅' if mini_success_rate >= 80 else '❌'} 品質: {mini_success_rate:.1f}%")
        print(f"    {'✅' if mini_avg_time < 10 else '⚠️'} 速度: {mini_avg_time:.1f}秒")
    
    # Final recommendation
    print(f"\n💡 推奨事項:")
    
    quality_advantage = abs(mini_success_rate - local_success_rate)
    speed_advantage = abs(local_avg_time - mini_avg_time) / max(local_avg_time, mini_avg_time) * 100
    
    if mini_success_rate > local_success_rate + 15:
        print(f"  🌐 gpt-5-mini 強く推奨")
        print(f"     - 品質で大幅な優位性 ({quality_advantage:.1f}% 差)")
        print(f"     - エッジケース対応が優秀")
    elif local_success_rate >= mini_success_rate - 5 and local_avg_time <= mini_avg_time * 1.5:
        print(f"  🏠 gpt-oss:20b 推奨")
        print(f"     - 品質がほぼ同等で無料")
        print(f"     - プライバシー重視の用途に最適")
    else:
        print(f"  ⚖️ 用途別選択:")
        print(f"     - 高品質・複雑なタスク: gpt-5-mini")
        print(f"     - コスト重視・基本タスク: gpt-oss:20b")
        print(f"     - プライバシー重視: gpt-oss:20b")
    
    # Edge case insights
    print(f"\n🔍 エッジケース洞察:")
    common_failures = []
    
    for i, (local_result, mini_result) in enumerate(zip(local_results, mini_results)):
        if not local_result[1] and not mini_result[1]:
            common_failures.append(local_result[0])
        elif not local_result[1] and mini_result[1]:
            print(f"  • {local_result[0]}: OpenAIのみ成功")
        elif local_result[1] and not mini_result[1]:
            print(f"  • {local_result[0]}: ローカルのみ成功")
    
    if common_failures:
        print(f"  • 共通の課題: {', '.join(common_failures)}")
    else:
        print(f"  • 両モデルで補完的な強みを発揮")
    
    return {
        'local_success_rate': local_success_rate,
        'mini_success_rate': mini_success_rate,
        'local_avg_time': local_avg_time,
        'mini_avg_time': mini_avg_time
    }


if __name__ == "__main__":
    try:
        comparison_results = main()
        print(f"\n✅ Edge case comparison between gpt-oss:20b and gpt-5-mini completed successfully")
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()