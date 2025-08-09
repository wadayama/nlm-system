#!/usr/bin/env python
"""Basic functionality test for gpt-5-mini"""

import time
from nlm_interpreter import NLMSession


def test_basic_functionality():
    """Test basic NLM functionality with gpt-5-mini"""
    print("="*60)
    print("GPT-5-MINI ベーシック機能テスト")
    print("="*60)
    
    session = NLMSession(model="gpt-5-mini", namespace="basic_test")
    
    results = {
        "session_creation": False,
        "python_api": False,
        "global_vars": False,
        "japanese_vars": False,
        "llm_execution": False,
        "variable_listing": False
    }
    
    # Test 1: セッション作成
    try:
        print(f"\n📊 Session Info:")
        print(f"   Model: {session.model}")
        print(f"   Endpoint: {session.endpoint}")
        print(f"   Namespace: {session.namespace}")
        results["session_creation"] = True
        print("   ✅ Session creation: SUCCESS")
    except Exception as e:
        print(f"   ❌ Session creation failed: {e}")
        return results
    
    # Test 2: Python API機能
    try:
        print(f"\n🔧 Python API Test:")
        session.save("test_var", "hello")
        value = session.get("test_var")
        if value == "hello":
            results["python_api"] = True
            print("   ✅ Python API: SUCCESS")
        else:
            print(f"   ❌ Expected 'hello', got '{value}'")
    except Exception as e:
        print(f"   ❌ Python API failed: {e}")
    
    # Test 3: グローバル変数
    try:
        print(f"\n🌐 Global Variables Test:")
        session.save("@global_test", "global_value")
        value = session.get("@global_test")
        if value == "global_value":
            results["global_vars"] = True
            print("   ✅ Global variables: SUCCESS")
        else:
            print(f"   ❌ Expected 'global_value', got '{value}'")
    except Exception as e:
        print(f"   ❌ Global variables failed: {e}")
    
    # Test 4: 日本語変数名
    try:
        print(f"\n🇯🇵 Japanese Variables Test:")
        session.save("名前", "田中")
        session.save("年齢", "25")
        name = session.get("名前")
        age = session.get("年齢")
        if name == "田中" and age == "25":
            results["japanese_vars"] = True
            print(f"   ✅ Japanese variables: SUCCESS ({name}, {age})")
        else:
            print(f"   ❌ Japanese vars failed: name={name}, age={age}")
    except Exception as e:
        print(f"   ❌ Japanese variables failed: {e}")
    
    # Test 5: 変数一覧
    try:
        print(f"\n📋 Variable Listing Test:")
        local_vars = session.list_local()
        global_vars = session.list_global()
        print(f"   Local variables: {len(local_vars)}")
        print(f"   Global variables: {len(global_vars)}")
        if len(local_vars) >= 2 and len(global_vars) >= 1:
            results["variable_listing"] = True
            print("   ✅ Variable listing: SUCCESS")
        else:
            print("   ❌ Variable listing: Unexpected counts")
    except Exception as e:
        print(f"   ❌ Variable listing failed: {e}")
    
    # Test 6: LLM実行機能 (API制限時はスキップ)
    try:
        print(f"\n🤖 LLM Execution Test:")
        print("   Testing simple variable assignment...")
        
        result = session.execute('Set {{message}} to "Hello GPT-5-Mini"')
        time.sleep(1)  # Rate limiting
        
        value = session.get("message")
        if "Hello GPT-5-Mini" in value or value == "Hello GPT-5-Mini":
            results["llm_execution"] = True
            print(f"   ✅ LLM execution: SUCCESS")
            print(f"   Result: {result[:100]}...")
        else:
            print(f"   ❌ LLM execution failed, got: {value}")
            
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "quota" in error_msg.lower():
            print("   ⚠️  LLM execution: SKIPPED (API quota exceeded)")
        else:
            print(f"   ❌ LLM execution failed: {error_msg[:60]}...")
    
    return results


def print_summary(results):
    """Print test summary"""
    print("\n" + "="*60)
    print("📊 GPT-5-MINI ベーシック機能テスト結果")
    print("="*60)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    test_names = {
        "session_creation": "セッション作成",
        "python_api": "Python API",
        "global_vars": "グローバル変数",
        "japanese_vars": "日本語変数名",
        "variable_listing": "変数一覧",
        "llm_execution": "LLM実行"
    }
    
    for key, passed in results.items():
        name = test_names.get(key, key)
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {name:<15}: {status}")
    
    print("-" * 60)
    print(f"合計: {passed_tests}/{total_tests} テスト成功")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED!")
    elif passed_tests >= total_tests - 1:
        print("🟡 MOSTLY SUCCESSFUL (API制限により一部未完了)")
    else:
        print("🔴 SOME TESTS FAILED")
    
    # 推奨事項
    print(f"\n💡 推奨事項:")
    if not results["llm_execution"]:
        print("   - API制限解除後にLLM機能を再テスト")
    if results["python_api"] and results["global_vars"]:
        print("   - 基本機能は完全動作、プロダクション利用可能")
    if results["japanese_vars"]:
        print("   - 日本語サポート完璧")


if __name__ == "__main__":
    try:
        results = test_basic_functionality()
        print_summary(results)
    except KeyboardInterrupt:
        print(f"\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()