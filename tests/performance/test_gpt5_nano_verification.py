#!/usr/bin/env python
"""Verification test for gpt-5-nano after payment"""

from nlm_interpreter import NLMSession


def test_gpt5_nano():
    """Test gpt-5-nano functionality after OpenAI payment"""
    print("="*60)
    print("GPT-5-NANO 動作確認テスト (支払い後)")
    print("="*60)
    
    # Create session with gpt-5-nano
    session = NLMSession(model="gpt-5-nano", namespace="payment_test")
    print(f"✅ セッション作成成功")
    print(f"   Model: {session.model}")
    print(f"   Endpoint: {session.endpoint}")
    print(f"   Namespace: {session.namespace}")
    
    # Test 1: Simple variable assignment
    print(f"\n📝 Test 1: Simple variable assignment")
    print(f"   Command: Set {{greeting}} to 'Hello from GPT-5-Nano'")
    try:
        result = session.execute("Set {{greeting}} to 'Hello from GPT-5-Nano'")
        value = session.get("greeting")
        print(f"   ✅ LLM実行成功!")
        print(f"   Result: {result[:100]}...")
        print(f"   Variable value: {value}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False
    
    # Test 2: Math calculation
    print(f"\n🔢 Test 2: Math calculation")
    print(f"   Command: Calculate 15 * 23 and save it to {{calculation}}")
    try:
        result = session.execute("Calculate 15 * 23 and save it to {{calculation}}")
        value = session.get("calculation")
        print(f"   ✅ LLM実行成功!")
        print(f"   Result: {result[:100]}...")
        print(f"   Variable value: {value}")
        expected = 15 * 23
        if str(expected) in str(value):
            print(f"   ✅ Correct calculation: {expected}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False
    
    # Test 3: Japanese processing
    print(f"\n🇯🇵 Test 3: Japanese processing")
    print(f"   Command: {{都市}}を'東京'に設定してください")
    try:
        result = session.execute("{{都市}}を'東京'に設定してください")
        value = session.get("都市")
        print(f"   ✅ LLM実行成功!")
        print(f"   Result: {result[:100]}...")
        print(f"   Variable value: {value}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False
    
    # Test 4: Multi-variable operation
    print(f"\n🔗 Test 4: Multi-variable operation")
    print(f"   Command: Set {{name}} to 'Alice' and {{age}} to 25")
    try:
        result = session.execute("Set {{name}} to 'Alice' and {{age}} to 25")
        name = session.get("name")
        age = session.get("age")
        print(f"   ✅ LLM実行成功!")
        print(f"   Result: {result[:100]}...")
        print(f"   Name: {name}, Age: {age}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False
    
    # Summary
    print(f"\n" + "="*60)
    print(f"✅ GPT-5-NANO 動作確認完了!")
    print(f"="*60)
    print(f"すべてのテストが正常に実行されました。")
    print(f"OpenAI APIが正常に機能しています。")
    
    # List all variables created
    print(f"\n📊 作成された変数:")
    local_vars = session.list_local()
    for var, value in local_vars.items():
        print(f"   {var}: {value}")
    
    return True


if __name__ == "__main__":
    try:
        success = test_gpt5_nano()
        if not success:
            print("\n⚠️ Some tests failed")
    except KeyboardInterrupt:
        print(f"\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()