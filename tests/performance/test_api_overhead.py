#!/usr/bin/env python
"""Compare direct API call vs NLM system overhead"""

from time import time
from openai import OpenAI
from nlm_interpreter import NLMSession


def test_api_overhead():
    """Measure overhead of NLM system vs direct API calls"""
    print("="*70)
    print("🔍 API オーバーヘッド分析 (gpt-5-nano)")
    print("="*70)
    
    # Load API key
    try:
        with open('.openai_key', 'r') as f:
            api_key = f.read().strip()
    except FileNotFoundError:
        print("❌ .openai_key not found")
        return
    
    client = OpenAI(api_key=api_key)
    
    # Test 1: Direct API call (simplest possible)
    print("\n1️⃣ 直接API呼び出し（最小構成）:")
    print("-" * 50)
    
    start = time()
    response = client.chat.completions.create(
        model="gpt-5-nano",
        messages=[
            {"role": "user", "content": "Say hello"}
        ]
    )
    direct_simple_time = time() - start
    print(f"  Message: 'Say hello'")
    print(f"  Response: {response.choices[0].message.content}")
    print(f"  ⏱️  Time: {direct_simple_time:.3f}s")
    
    # Test 2: Direct API call with tools (like NLM)
    print("\n2️⃣ 直接API呼び出し（ツール定義付き）:")
    print("-" * 50)
    
    tools_definition = [
        {
            "type": "function",
            "function": {
                "name": "save_variable",
                "description": "Save a value to a variable",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "variable_name": {"type": "string"},
                        "value": {"type": "string"}
                    },
                    "required": ["variable_name", "value"]
                }
            }
        }
    ]
    
    start = time()
    response = client.chat.completions.create(
        model="gpt-5-nano",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that can save variables."},
            {"role": "user", "content": "Say hello"}
        ],
        tools=tools_definition
    )
    direct_tools_time = time() - start
    print(f"  Message: 'Say hello' (with tools)")
    print(f"  Response: {response.choices[0].message.content}")
    print(f"  ⏱️  Time: {direct_tools_time:.3f}s")
    
    # Test 3: NLM system (no variables)
    print("\n3️⃣ NLMシステム経由（変数なし）:")
    print("-" * 50)
    
    session = NLMSession(model="gpt-5-nano", namespace="overhead_test")
    
    start = time()
    result = session.execute("Say hello")
    nlm_no_var_time = time() - start
    print(f"  Command: 'Say hello'")
    print(f"  Result: {result[:100]}...")
    print(f"  ⏱️  Time: {nlm_no_var_time:.3f}s")
    
    # Test 4: NLM system (with variable)
    print("\n4️⃣ NLMシステム経由（変数あり）:")
    print("-" * 50)
    
    start = time()
    result = session.execute("Set {{greeting}} to 'hello'")
    nlm_var_time = time() - start
    value = session.get("greeting")
    print(f"  Command: Set {{{{greeting}}}} to 'hello'")
    print(f"  Variable value: {value}")
    print(f"  ⏱️  Time: {nlm_var_time:.3f}s")
    
    # Analysis
    print("\n\n" + "="*70)
    print("📊 オーバーヘッド分析:")
    print("="*70)
    
    print(f"\n⏱️  レスポンス時間:")
    print(f"  1. 直接API（最小）:        {direct_simple_time:.3f}s")
    print(f"  2. 直接API（ツール付き）:  {direct_tools_time:.3f}s")
    print(f"  3. NLM（変数なし）:        {nlm_no_var_time:.3f}s")
    print(f"  4. NLM（変数あり）:        {nlm_var_time:.3f}s")
    
    print(f"\n📈 オーバーヘッド計算:")
    tools_overhead = direct_tools_time - direct_simple_time
    nlm_overhead = nlm_no_var_time - direct_tools_time
    var_overhead = nlm_var_time - nlm_no_var_time
    
    print(f"  ツール定義の追加:     +{tools_overhead:.3f}s ({tools_overhead/direct_simple_time*100:.0f}%)")
    print(f"  NLMシステム:          +{nlm_overhead:.3f}s ({nlm_overhead/direct_tools_time*100:.0f}%)")
    print(f"  変数操作:             +{var_overhead:.3f}s ({var_overhead/nlm_no_var_time*100:.0f}%)")
    
    print(f"\n💡 分析結果:")
    if nlm_overhead > 1.0:
        print(f"  🔴 NLMシステムのオーバーヘッドが大きい（+{nlm_overhead:.1f}秒）")
        print(f"     原因: システムプロンプト、ツール定義、メッセージ構築")
    elif nlm_overhead > 0.5:
        print(f"  🟡 NLMシステムに中程度のオーバーヘッド（+{nlm_overhead:.1f}秒）")
    else:
        print(f"  🟢 NLMシステムのオーバーヘッドは軽微（+{nlm_overhead:.1f}秒）")
    
    if direct_simple_time > 2.0:
        print(f"  ⚠️  API自体のレスポンスが遅い（{direct_simple_time:.1f}秒）")
        print(f"     これはOpenAI側のレイテンシが主因")


if __name__ == "__main__":
    try:
        test_api_overhead()
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()