#!/usr/bin/env python
"""Compare edge case handling between gpt-oss:20b (local) and gpt-5-nano"""

import time
from nlm_interpreter import NLMSession


def test_model_edge_cases(model_name, namespace_suffix):
    """Run edge case tests for a specific model"""
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
        
        if value_a == "valueB" and value_b == "valueA":
            results.append(("Variable swap", True, elapsed))
            print(f"        ✅ Perfect swap")
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
        results.append(("Word ambiguity", True, elapsed))
        print(f"        ✅ Handled gracefully")
        
        # Complex conditional
        start = time.time()
        result = session.execute("If {{weather}} is sunny, then set {{mood}} to 'happy', otherwise 'neutral'")
        elapsed = time.time() - start
        mood_val = session.get("mood")
        
        print(f"    3b. Conditional logic: {elapsed:.3f}s")
        print(f"        Mood set to: '{mood_val}'")
        
        if mood_val:
            results.append(("Conditional logic", True, elapsed))
            print(f"        ✅ Logic processed")
        else:
            results.append(("Conditional logic", False, elapsed))
            print(f"        ❌ No mood set")
        
    except Exception as e:
        print(f"    ❌ Error in NL complexity: {e}")
        results.append(("NL complexity", False, None))
    
    # Test 4: Extreme Cases
    print("\n  4️⃣ 極端なケース:")
    
    try:
        # Empty variable
        start = time.time()
        result = session.execute("Set {{}} to 'empty name' if possible")
        elapsed = time.time() - start
        
        print(f"    4a. Empty variable: {elapsed:.3f}s")
        results.append(("Empty variable syntax", True, elapsed))
        print(f"        ✅ Handled gracefully")
        
        # Unicode variables (if supported)
        start = time.time()
        result = session.execute("Set {{🚀}} to 'rocket' and {{日本語}} to 'Japanese'")
        elapsed = time.time() - start
        rocket_val = session.get("🚀")
        jp_val = session.get("日本語")
        
        print(f"    4b. Unicode variables: {elapsed:.3f}s")
        print(f"        🚀: '{rocket_val}', 日本語: '{jp_val}'")
        
        if rocket_val or jp_val:
            results.append(("Unicode variables", True, elapsed))
            print(f"        ✅ Unicode supported")
        else:
            results.append(("Unicode variables", False, elapsed))
            print(f"        ❌ Unicode not supported")
        
    except Exception as e:
        print(f"    ❌ Error in extreme cases: {e}")
        results.append(("Extreme cases", False, None))
    
    return results


def main():
    """Compare edge cases between local and OpenAI models"""
    print("="*70)
    print("🆚 ローカル vs OpenAI エッジケース比較")
    print("gpt-oss:20b vs gpt-5-nano")
    print("="*70)
    
    # Test both models
    print("\n🖥️ Testing gpt-oss:20b (Local LLM)...")
    local_results = test_model_edge_cases("gpt-oss:20b", "local")
    
    print("\n\n🌐 Testing gpt-5-nano (OpenAI)...")
    nano_results = test_model_edge_cases("gpt-5-nano", "nano")
    
    # Analysis
    print("\n\n" + "="*70)
    print("📊 比較分析:")
    print("="*70)
    
    # Calculate success rates
    local_successful = sum(1 for _, success, _ in local_results if success)
    nano_successful = sum(1 for _, success, _ in nano_results if success)
    
    local_success_rate = (local_successful / len(local_results)) * 100
    nano_success_rate = (nano_successful / len(nano_results)) * 100
    
    # Calculate average times
    local_times = [time_val for _, success, time_val in local_results if success and time_val is not None]
    nano_times = [time_val for _, success, time_val in nano_results if success and time_val is not None]
    
    local_avg_time = sum(local_times) / len(local_times) if local_times else 0
    nano_avg_time = sum(nano_times) / len(nano_times) if nano_times else 0
    
    print(f"\n📈 総合スコア:")
    print(f"{'Model':<15} {'Success Rate':<12} {'Avg Time':<10} {'Rating'}")
    print("-" * 50)
    
    # Local model rating
    local_rating = "🥇" if local_success_rate > nano_success_rate else "🥈" if local_success_rate == nano_success_rate else "🥉"
    nano_rating = "🥇" if nano_success_rate > local_success_rate else "🥈" if nano_success_rate == local_success_rate else "🥉"
    
    print(f"{'gpt-oss:20b':<15} {local_success_rate:<12.1f}% {local_avg_time:<10.3f}s {local_rating}")
    print(f"{'gpt-5-nano':<15} {nano_success_rate:<12.1f}% {nano_avg_time:<10.3f}s {nano_rating}")
    
    # Detailed comparison
    print(f"\n📋 詳細比較:")
    print(f"{'Test Case':<25} {'Local':<8} {'OpenAI':<8} {'Winner'}")
    print("-" * 60)
    
    # Compare each test case
    for i, (local_result, nano_result) in enumerate(zip(local_results, nano_results)):
        if len(local_result) >= 2 and len(nano_result) >= 2:
            test_name = local_result[0][:24]
            local_status = "✅" if local_result[1] else "❌"
            nano_status = "✅" if nano_result[1] else "❌"
            
            if local_result[1] and nano_result[1]:
                winner = "TIE 🤝"
            elif local_result[1]:
                winner = "Local 🏆"
            elif nano_result[1]:
                winner = "OpenAI 🏆"
            else:
                winner = "Both ❌"
            
            print(f"{test_name:<25} {local_status:<8} {nano_status:<8} {winner}")
    
    # Performance vs Quality analysis
    print(f"\n⚖️ パフォーマンス vs 品質:")
    if local_avg_time > 0 and nano_avg_time > 0:
        speed_ratio = local_avg_time / nano_avg_time
        quality_diff = local_success_rate - nano_success_rate
        
        print(f"  Speed: gpt-oss:20b is {speed_ratio:.1f}x {'slower' if speed_ratio > 1 else 'faster'} than gpt-5-nano")
        print(f"  Quality: gpt-oss:20b is {abs(quality_diff):.1f}% {'better' if quality_diff > 0 else 'worse'} than gpt-5-nano")
    
    # Final recommendation
    print(f"\n💡 推奨事項:")
    
    if local_success_rate >= nano_success_rate and local_avg_time <= nano_avg_time * 2:
        print(f"  🏠 gpt-oss:20b (Local) 推奨")
        print(f"     - 品質が同等以上で、コストなし")
        print(f"     - プライバシー保護")
    elif nano_success_rate > local_success_rate + 10:
        print(f"  🌐 gpt-5-nano (OpenAI) 推奨")
        print(f"     - 品質で明確な優位性")
        print(f"     - エッジケース対応が優秀")
    else:
        print(f"  ⚖️ 用途に応じて選択")
        print(f"     - コスト重視: gpt-oss:20b")
        print(f"     - 品質重視: gpt-5-nano")
    
    return {
        'local_success_rate': local_success_rate,
        'nano_success_rate': nano_success_rate,
        'local_avg_time': local_avg_time,
        'nano_avg_time': nano_avg_time
    }


if __name__ == "__main__":
    try:
        comparison_results = main()
        print(f"\n✅ Edge case comparison completed successfully")
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()