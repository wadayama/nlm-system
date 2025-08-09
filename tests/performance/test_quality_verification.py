#!/usr/bin/env python
"""Verify that reasoning_effort='minimal' doesn't degrade quality"""

from nlm_interpreter import NLMSession
import time


def test_quality_verification():
    """Test quality of responses with reasoning_effort='minimal'"""
    print("="*70)
    print("🧪 品質検証テスト: reasoning_effort='minimal' の影響")
    print("="*70)
    
    session = NLMSession(model="gpt-5-nano", namespace="quality_test")
    
    # Comprehensive test cases to verify quality
    test_cases = [
        {
            "name": "Basic Variable Assignment",
            "command": "Set {{name}} to 'Alice'",
            "expected_var": "name",
            "expected_value": "Alice",
            "description": "Simple string assignment"
        },
        {
            "name": "Math Calculation",
            "command": "Calculate 15 * 23 and save to {{result}}",
            "expected_var": "result",
            "expected_value": "345",
            "description": "Arithmetic calculation"
        },
        {
            "name": "Multi-variable Operation",
            "command": "Set {{first}} to 'John' and {{last}} to 'Doe'",
            "expected_vars": ["first", "last"],
            "expected_values": ["John", "Doe"],
            "description": "Multiple variable assignment"
        },
        {
            "name": "Japanese Processing",
            "command": "{{都市}}を'東京'に、{{国}}を'日本'に設定してください",
            "expected_vars": ["都市", "国"],
            "expected_values": ["東京", "日本"],
            "description": "Japanese language handling"
        },
        {
            "name": "Complex Calculation",
            "command": "Calculate (10 + 5) * 2 - 3 and store in {{complex_result}}",
            "expected_var": "complex_result",
            "expected_value": "27",
            "description": "Order of operations"
        },
        {
            "name": "String Processing",
            "command": "Take the text 'Hello World' and save it to {{greeting}}",
            "expected_var": "greeting",
            "expected_value": "Hello World",
            "description": "String extraction and storage"
        },
        {
            "name": "Global Variable",
            "command": "Store 'shared data' in the global variable {{@global_test}}",
            "expected_var": "@global_test",
            "expected_value": "shared data",
            "description": "Global variable handling"
        },
        {
            "name": "Conditional Logic",
            "command": "If 5 > 3, set {{condition}} to 'true', otherwise 'false'",
            "expected_var": "condition",
            "expected_value": "true",
            "description": "Basic conditional reasoning"
        }
    ]
    
    results = []
    total_tests = len(test_cases)
    passed_tests = 0
    
    print(f"\n実行中: {total_tests}個のテストケース...")
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
    print("📊 品質検証結果:")
    print("="*70)
    
    success_rate = (passed_tests / total_tests) * 100
    print(f"\n合格率: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    
    if success_rate == 100:
        print("🎉 すべてのテストに合格！品質に問題なし")
    elif success_rate >= 90:
        print("✅ ほぼすべてのテストに合格。品質は良好")
    elif success_rate >= 75:
        print("⚠️ 一部テストが失敗。軽微な品質低下あり")
    else:
        print("🔴 多くのテストが失敗。品質低下が懸念される")
    
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
            print("  🚀 高速な実行時間を維持")
        elif avg_time < 5.0:
            print("  ✅ 良好な実行時間")
        else:
            print("  🐢 実行時間が長め")
    
    print(f"\n💡 結論:")
    if success_rate >= 95 and successful_times and sum(successful_times)/len(successful_times) < 3:
        print("  reasoning_effort='minimal'は高い品質と速度を両立")
        print("  本番環境での使用を推奨")
    elif success_rate >= 90:
        print("  軽微な品質トレードオフはあるが、速度向上のメリット大")
        print("  用途に応じて使用を検討")
    else:
        print("  品質低下が顕著。設定の見直しを推奨")


if __name__ == "__main__":
    try:
        test_quality_verification()
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()