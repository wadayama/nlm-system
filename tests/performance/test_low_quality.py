#!/usr/bin/env python
"""Test quality with reasoning_effort='low'"""

from nlm_interpreter import NLMSession
import time


def test_low_quality():
    """Test quality of responses with reasoning_effort='low'"""
    print("="*70)
    print("🧪 品質検証テスト: reasoning_effort='low'")
    print("="*70)
    
    session = NLMSession(model="gpt-5-nano", namespace="low_quality_test")
    
    # Comprehensive test cases to verify quality
    test_cases = [
        {
            "name": "Basic Variable Assignment",
            "command": "Set {{user_name}} to 'Alice'",
            "expected_var": "user_name",
            "expected_value": "Alice",
            "description": "Simple string assignment"
        },
        {
            "name": "Math Calculation",
            "command": "Calculate 25 * 16 and save to {{math_result}}",
            "expected_var": "math_result",
            "expected_value": "400",
            "description": "Arithmetic calculation"
        },
        {
            "name": "Multi-variable Operation",
            "command": "Set {{first_name}} to 'John' and {{last_name}} to 'Smith'",
            "expected_vars": ["first_name", "last_name"],
            "expected_values": ["John", "Smith"],
            "description": "Multiple variable assignment"
        },
        {
            "name": "Japanese Processing",
            "command": "{{県名}}を'神奈川'に、{{市名}}を'横浜'に設定してください",
            "expected_vars": ["県名", "市名"],
            "expected_values": ["神奈川", "横浜"],
            "description": "Japanese language handling"
        },
        {
            "name": "Complex Calculation",
            "command": "Calculate (8 + 12) * 3 - 5 and store in {{complex_calc}}",
            "expected_var": "complex_calc",
            "expected_value": "55",
            "description": "Order of operations"
        },
        {
            "name": "String Processing",
            "command": "Take the phrase 'Good Morning' and save it to {{greeting_msg}}",
            "expected_var": "greeting_msg",
            "expected_value": "Good Morning",
            "description": "String extraction and storage"
        },
        {
            "name": "Global Variable",
            "command": "Store 'system config' in the global variable {{@config_data}}",
            "expected_var": "@config_data",
            "expected_value": "system config",
            "description": "Global variable handling"
        },
        {
            "name": "Conditional Logic",
            "command": "If 10 > 5, set {{logic_result}} to 'correct', otherwise 'incorrect'",
            "expected_var": "logic_result",
            "expected_value": "correct",
            "description": "Basic conditional reasoning"
        },
        {
            "name": "Number Processing",
            "command": "Set {{age}} to 25 and {{score}} to 95",
            "expected_vars": ["age", "score"],
            "expected_values": ["25", "95"],
            "description": "Number handling"
        },
        {
            "name": "List Creation",
            "command": "Create a list [red, green, blue] and save to {{colors}}",
            "expected_var": "colors",
            "expected_contains": ["red", "green", "blue"],
            "description": "List/array handling"
        }
    ]
    
    results = []
    total_tests = len(test_cases)
    passed_tests = 0
    
    print(f"\n実行中: {total_tests}個の品質テスト...")
    print("-" * 70)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{i}. {test['name']}:")
        print(f"   Command: {test['command']}")
        
        start = time.time()
        try:
            # Execute command
            result = session.execute(test['command'])
            elapsed = time.time() - start
            
            # Check results
            test_passed = True
            error_msg = ""
            
            if "expected_var" in test:
                # Single variable test
                value = session.get(test['expected_var'])
                if "expected_contains" in test:
                    # Check if all expected elements are in the value
                    value_str = str(value).lower()
                    all_present = all(item.lower() in value_str for item in test['expected_contains'])
                    if all_present:
                        print(f"   ✅ PASS: {test['expected_var']} contains expected items")
                        print(f"        Value: {value}")
                    else:
                        missing = [item for item in test['expected_contains'] if item.lower() not in value_str]
                        print(f"   ❌ FAIL: Missing items: {missing}")
                        print(f"        Got: {value}")
                        test_passed = False
                        error_msg = f"Missing: {missing}"
                else:
                    # Exact value check
                    if str(value) == str(test['expected_value']):
                        print(f"   ✅ PASS: {test['expected_var']} = '{value}'")
                    else:
                        print(f"   ❌ FAIL: Expected '{test['expected_value']}', got '{value}'")
                        test_passed = False
                        error_msg = f"Wrong value: {value}"
            
            elif "expected_vars" in test:
                # Multiple variables test
                all_correct = True
                for var, expected in zip(test['expected_vars'], test['expected_values']):
                    value = session.get(var)
                    if str(value) == str(expected):
                        print(f"   ✅ {var} = '{value}'")
                    else:
                        print(f"   ❌ {var}: Expected '{expected}', got '{value}'")
                        all_correct = False
                        error_msg += f"{var}:{value} "
                
                if all_correct:
                    print(f"   ✅ PASS: All variables correct")
                else:
                    print(f"   ❌ FAIL: Some variables incorrect")
                    test_passed = False
            
            if test_passed:
                passed_tests += 1
            
            # Record result
            results.append({
                'name': test['name'],
                'passed': test_passed,
                'time': elapsed,
                'error': error_msg if not test_passed else None,
                'description': test['description']
            })
            
            print(f"   ⏱️  Time: {elapsed:.3f}s")
            
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)[:100]}")
            results.append({
                'name': test['name'],
                'passed': False,
                'time': None,
                'error': str(e),
                'description': test['description']
            })
    
    # Summary
    print("\n" + "="*70)
    print("📊 reasoning_effort='low' 品質検証結果:")
    print("="*70)
    
    success_rate = (passed_tests / total_tests) * 100
    print(f"\n合格率: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    
    if success_rate == 100:
        print("🎉 すべてのテストに合格！品質に問題なし")
        quality_rating = "優秀"
    elif success_rate >= 90:
        print("✅ ほぼすべてのテストに合格。品質は良好")
        quality_rating = "良好"
    elif success_rate >= 75:
        print("⚠️ 一部テストが失敗。軽微な品質低下あり")
        quality_rating = "許容可能"
    elif success_rate >= 50:
        print("🟡 半数のテストが失敗。品質低下が目立つ")
        quality_rating = "要改善"
    else:
        print("🔴 多くのテストが失敗。品質低下が深刻")
        quality_rating = "不適切"
    
    # Detailed results
    print(f"\n📋 詳細結果:")
    for result in results:
        status = "✅ PASS" if result['passed'] else "❌ FAIL"
        time_str = f"{result['time']:.3f}s" if result['time'] else "N/A"
        print(f"  {status} {result['name']} ({time_str})")
        if not result['passed'] and result['error']:
            print(f"      Error: {result['error']}")
    
    # Performance analysis
    successful_times = [r['time'] for r in results if r['time'] and r['passed']]
    if successful_times:
        avg_time = sum(successful_times) / len(successful_times)
        print(f"\n⚡ パフォーマンス:")
        print(f"  平均実行時間: {avg_time:.3f}s")
        print(f"  最速: {min(successful_times):.3f}s")
        print(f"  最遅: {max(successful_times):.3f}s")
        
        if avg_time < 3.0:
            perf_rating = "高速"
        elif avg_time < 5.0:
            perf_rating = "良好"
        elif avg_time < 8.0:
            perf_rating = "許容可能"
        else:
            perf_rating = "遅い"
    else:
        perf_rating = "測定不可"
        avg_time = 0
    
    # Final recommendation
    print(f"\n" + "="*70)
    print(f"💡 reasoning_effort='low' 総合評価:")
    print("="*70)
    print(f"  品質: {quality_rating} ({success_rate:.1f}%)")
    if successful_times:
        print(f"  速度: {perf_rating} ({avg_time:.1f}秒)")
    
    # Compare with settings
    print(f"\n📊 設定比較サマリー:")
    print(f"  Default (なし):     品質=100% 速度=11.3秒")
    print(f"  Minimal:           品質=12%   速度=2.0秒")
    print(f"  Low (現在):         品質={success_rate:.0f}%   速度={avg_time:.1f}秒")
    
    if success_rate >= 85 and avg_time < 6:
        print(f"\n🎯 推奨: reasoning_effort='low'は最適なバランス")
        print(f"   品質と速度の良いトレードオフを実現")
    elif success_rate >= 75:
        print(f"\n✅ 推奨: reasoning_effort='low'は実用的")
        print(f"   軽微な品質低下はあるが、速度向上のメリット大")
    else:
        print(f"\n⚠️  検討: 品質が低下しすぎている可能性")
        print(f"   デフォルト設定への戻しを検討")


if __name__ == "__main__":
    try:
        test_low_quality()
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()