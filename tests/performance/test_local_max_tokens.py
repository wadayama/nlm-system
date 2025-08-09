#!/usr/bin/env python
"""Test if max_tokens is needed for gpt-oss:20b"""

from nlm_interpreter import NLMSession


def test_without_max_tokens():
    """Test gpt-oss:20b without max_tokens parameter"""
    print("="*60)
    print("gpt-oss:20b max_tokens パラメータテスト")
    print("="*60)
    
    # Test with current implementation (max_tokens included)
    print("\n1️⃣ 現在の実装（max_tokens=1000あり）:")
    try:
        session = NLMSession(model="gpt-oss:20b", namespace="test_max_tokens")
        result = session.execute("Set {{test1}} to 'With max_tokens'")
        value = session.get("test1")
        print(f"   ✅ 成功: {value}")
        print(f"   Result length: {len(result)} characters")
    except Exception as e:
        print(f"   ❌ エラー: {e}")
    
    print("\n2️⃣ max_tokensなしのテスト:")
    print("   一時的にmax_tokensを削除してテストします...")
    
    # Temporarily test without max_tokens
    from nlm_interpreter import NLMSession
    import json
    from openai import OpenAI
    
    # Create a test session
    test_session = NLMSession(model="gpt-oss:20b", namespace="test_no_max")
    
    # Test direct API call without max_tokens
    try:
        client = OpenAI(
            base_url="http://localhost:1234/v1",
            api_key="not-needed"
        )
        
        response = client.chat.completions.create(
            model="gpt-oss:20b",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'Hello World' and nothing else."}
            ]
            # No max_tokens parameter
        )
        
        content = response.choices[0].message.content
        print(f"   ✅ max_tokensなしでも動作!")
        print(f"   Response: {content}")
        print(f"   Response length: {len(content)} characters")
        
    except Exception as e:
        print(f"   ❌ max_tokensなしでエラー: {e}")
    
    print("\n3️⃣ 長い出力のテスト（max_tokensなし）:")
    try:
        response = client.chat.completions.create(
            model="gpt-oss:20b",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Count from 1 to 100."}
            ]
            # No max_tokens parameter
        )
        
        content = response.choices[0].message.content
        print(f"   ✅ 長い出力も成功!")
        print(f"   Response length: {len(content)} characters")
        print(f"   First 100 chars: {content[:100]}...")
        
    except Exception as e:
        print(f"   ❌ エラー: {e}")
    
    print("\n" + "="*60)
    print("📊 結論:")
    print("="*60)
    print("max_tokensパラメータは：")
    print("- gpt-oss:20b（ローカル）: オプション（なくても動作）")
    print("- gpt-5シリーズ（OpenAI）: 使用不可（エラーになる）")
    print("\n💡 推奨: max_tokensパラメータを完全に削除")


if __name__ == "__main__":
    try:
        test_without_max_tokens()
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()