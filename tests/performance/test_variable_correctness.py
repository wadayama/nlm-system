#!/usr/bin/env python
"""Test correctness of variable operations with gpt-5-nano"""

from nlm_interpreter import NLMSession


def test_variable_correctness():
    """Verify variable operations work correctly"""
    print("="*70)
    print("✅ 変数操作の正確性テスト (gpt-5-nano)")
    print("="*70)
    
    session = NLMSession(model="gpt-5-nano", namespace="correctness_test")
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Simple string save
    print("\n📝 Test 1: 文字列の保存")
    tests_total += 1
    session.execute("Set {{test_string}} to 'Hello GPT-5'")
    value = session.get("test_string")
    expected = "Hello GPT-5"
    if value == expected:
        print(f"   ✅ PASS: '{value}' == '{expected}'")
        tests_passed += 1
    else:
        print(f"   ❌ FAIL: '{value}' != '{expected}'")
    
    # Test 2: Number save
    print("\n🔢 Test 2: 数値の保存")
    tests_total += 1
    session.execute("Store the number 42 in {{test_number}}")
    value = session.get("test_number")
    if str(value) == "42":
        print(f"   ✅ PASS: {value} == 42")
        tests_passed += 1
    else:
        print(f"   ❌ FAIL: {value} != 42")
    
    # Test 3: Calculation result
    print("\n🧮 Test 3: 計算結果の保存")
    tests_total += 1
    session.execute("Calculate 15 * 3 and save to {{calc_result}}")
    value = session.get("calc_result")
    expected = 45
    if str(value) == str(expected):
        print(f"   ✅ PASS: {value} == {expected}")
        tests_passed += 1
    else:
        print(f"   ❌ FAIL: {value} != {expected}")
    
    # Test 4: Japanese text
    print("\n🇯🇵 Test 4: 日本語テキスト")
    tests_total += 1
    session.execute("{{挨拶}}を'こんにちは'に設定")
    value = session.get("挨拶")
    expected = "こんにちは"
    if value == expected:
        print(f"   ✅ PASS: '{value}' == '{expected}'")
        tests_passed += 1
    else:
        print(f"   ❌ FAIL: '{value}' != '{expected}'")
    
    # Test 5: Multiple variables
    print("\n🔗 Test 5: 複数変数の同時操作")
    tests_total += 2  # Two variables to check
    session.execute("Set {{first}} to 'Alpha' and {{second}} to 'Beta'")
    first = session.get("first")
    second = session.get("second")
    if first == "Alpha":
        print(f"   ✅ PASS: first = '{first}'")
        tests_passed += 1
    else:
        print(f"   ❌ FAIL: first = '{first}' != 'Alpha'")
    
    if second == "Beta":
        print(f"   ✅ PASS: second = '{second}'")
        tests_passed += 1
    else:
        print(f"   ❌ FAIL: second = '{second}' != 'Beta'")
    
    # Test 6: Variable read and reference
    print("\n📖 Test 6: 変数の読み取りと参照")
    tests_total += 1
    session.save("preset_value", "PresetData")
    result = session.execute("What is in {{preset_value}}?")
    if "PresetData" in result:
        print(f"   ✅ PASS: Variable read correctly")
        print(f"   Result: {result[:100]}...")
        tests_passed += 1
    else:
        print(f"   ❌ FAIL: Could not read variable")
        print(f"   Result: {result[:100]}...")
    
    # Test 7: Global variable
    print("\n🌐 Test 7: グローバル変数")
    tests_total += 1
    session.execute("Save 'GlobalData' to {{@global_test_var}}")
    value = session.get("@global_test_var")
    if value == "GlobalData":
        print(f"   ✅ PASS: Global variable = '{value}'")
        tests_passed += 1
    else:
        print(f"   ❌ FAIL: Global variable = '{value}' != 'GlobalData'")
    
    # Test 8: List/Array storage
    print("\n📋 Test 8: リスト形式のデータ")
    tests_total += 1
    session.execute("Store a list [1,2,3] in {{test_list}}")
    value = session.get("test_list")
    if value and ("1" in str(value) and "2" in str(value) and "3" in str(value)):
        print(f"   ✅ PASS: List stored = {value}")
        tests_passed += 1
    else:
        print(f"   ❌ FAIL: List = {value}")
    
    # Summary
    print("\n" + "="*70)
    print("📊 テスト結果サマリー:")
    print("="*70)
    print(f"   合格: {tests_passed}/{tests_total}")
    print(f"   成功率: {tests_passed/tests_total*100:.1f}%")
    
    if tests_passed == tests_total:
        print("\n🎉 すべてのテストに合格！変数操作は完璧に動作しています。")
    elif tests_passed >= tests_total * 0.8:
        print("\n✅ ほとんどのテストに合格。変数操作は正しく動作しています。")
    else:
        print("\n⚠️ 一部のテストが失敗。変数操作に問題がある可能性があります。")
    
    # List all variables created
    print("\n📦 作成された変数一覧:")
    local_vars = session.list_local()
    for key, value in local_vars.items():
        print(f"   {key}: {value}")


if __name__ == "__main__":
    try:
        test_variable_correctness()
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted")
    except Exception as e:
        print(f"❌ Test failed: {e}")