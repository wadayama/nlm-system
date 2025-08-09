#!/usr/bin/env python
"""Test verbosity parameter for latency improvement"""

import time
from openai import OpenAI
from nlm_interpreter import NLMSession


def test_verbosity_comparison():
    """Compare different verbosity settings"""
    print("="*70)
    print("🔍 verbosity パラメータテスト")
    print("="*70)
    
    # Load API key
    try:
        with open('.openai_key', 'r') as f:
            api_key = f.read().strip()
    except FileNotFoundError:
        print("❌ .openai_key not found")
        return
    
    client = OpenAI(api_key=api_key)
    
    # Test cases
    test_cases = [
        {
            "prompt": "You have tools to save variables. Execute: Set variable 'name' to 'Alice'",
            "tools": [{
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
            }],
            "description": "Tool use with variable"
        },
        {
            "prompt": "Calculate 15 * 23",
            "tools": None,
            "description": "Simple math"
        },
        {
            "prompt": "Explain what is 2+2 and provide the answer",
            "tools": None,
            "description": "Math with explanation"
        }
    ]
    
    # Test different verbosity levels
    verbosity_levels = [
        ("default", None),
        ("high", "high"),
        ("medium", "medium"),
        ("low", "low")
    ]
    
    results = {}
    
    for level_name, level_value in verbosity_levels:
        print(f"\n📊 Testing verbosity = {level_name}:")
        print("-" * 50)
        
        level_results = []
        
        for i, test in enumerate(test_cases, 1):
            print(f"\n  Test {i}: {test['description']}")
            
            # Prepare request
            params = {
                "model": "gpt-5-nano",
                "messages": [{"role": "user", "content": test['prompt']}],
                "reasoning_effort": "low"  # Keep current setting
            }
            
            if test['tools']:
                params["tools"] = test['tools']
            
            # Add verbosity if specified
            if level_value:
                params["verbosity"] = level_value
            
            # Make request
            start = time.time()
            try:
                response = client.chat.completions.create(**params)
                elapsed = time.time() - start
                
                message = response.choices[0].message
                content = message.content or ""
                tool_calls = message.tool_calls
                
                print(f"    ⏱️  Time: {elapsed:.3f}s")
                print(f"    Response length: {len(content)} chars")
                print(f"    Content: {content[:100]}...")
                
                if tool_calls:
                    print(f"    Tool calls: {len(tool_calls)}")
                    for call in tool_calls:
                        print(f"      {call.function.name}: {call.function.arguments}")
                
                level_results.append({
                    'test': test['description'],
                    'time': elapsed,
                    'content_length': len(content),
                    'content': content,
                    'tool_calls': len(tool_calls) if tool_calls else 0,
                    'success': True
                })
                
            except Exception as e:
                error_str = str(e)
                if "verbosity" in error_str.lower():
                    print(f"    ❌ verbosity parameter not supported: {error_str[:80]}")
                else:
                    print(f"    ❌ Error: {error_str[:80]}")
                
                level_results.append({
                    'test': test['description'],
                    'time': None,
                    'content_length': 0,
                    'content': None,
                    'tool_calls': 0,
                    'success': False,
                    'error': error_str
                })
        
        results[level_name] = level_results
    
    # Analysis
    print("\n" + "="*70)
    print("📊 verbosity 設定比較:")
    print("="*70)
    
    print(f"\n{'Level':<10} {'Avg Time':<10} {'Avg Length':<12} {'Success':<8} {'Notes'}")
    print("-" * 60)
    
    for level_name, level_results in results.items():
        successful = [r for r in level_results if r['success']]
        success_rate = len(successful) / len(level_results) * 100
        
        if successful:
            avg_time = sum(r['time'] for r in successful) / len(successful)
            avg_length = sum(r['content_length'] for r in successful) / len(successful)
            notes = "OK"
        else:
            avg_time = 0
            avg_length = 0
            notes = "Failed"
        
        print(f"{level_name:<10} {avg_time:<10.3f} {avg_length:<12.0f} {success_rate:<8.0f}% {notes}")
    
    # Find best performing setting
    successful_levels = [(name, results[name]) for name in results 
                        if any(r['success'] for r in results[name])]
    
    if len(successful_levels) > 1:
        print(f"\n💡 パフォーマンス比較:")
        
        # Compare times
        times = {}
        for name, level_results in successful_levels:
            successful = [r for r in level_results if r['success']]
            if successful:
                times[name] = sum(r['time'] for r in successful) / len(successful)
        
        if times:
            fastest = min(times, key=times.get)
            slowest = max(times, key=times.get)
            improvement = (times[slowest] - times[fastest]) / times[slowest] * 100
            
            print(f"  最速: {fastest} ({times[fastest]:.3f}s)")
            print(f"  最遅: {slowest} ({times[slowest]:.3f}s)")
            if improvement > 10:
                print(f"  改善: {improvement:.1f}% 高速化")
    
    return results


def test_verbosity_in_nlm():
    """Test verbosity parameter in NLM system"""
    print("\n" + "="*70)
    print("🔧 NLMシステムでのverbosity効果テスト")
    print("="*70)
    
    print("\n注意: 現在のNLMシステムはverbosityパラメータに対応していません")
    print("対応するには nlm_interpreter.py の修正が必要です")
    
    # Show what the modification would look like
    print("\n💡 実装例:")
    print("""
# nlm_interpreter.py の execute メソッドに以下を追加:
request_params = {
    "model": self.model,
    "messages": messages,
    "tools": self.TOOLS_DEFINITION,
    "reasoning_effort": "low",
    "verbosity": "low"  # 追加
}
""")
    
    # Test current performance for comparison
    print("\n📊 現在のNLMシステム (reasoning_effort='low'):")
    session = NLMSession(model="gpt-5-nano", namespace="verbosity_test")
    
    start = time.time()
    try:
        result = session.execute("Set {{test}} to 'verbosity test'")
        elapsed = time.time() - start
        value = session.get("test")
        
        print(f"  Command: Set {{{{test}}}} to 'verbosity test'")
        print(f"  ⏱️  Time: {elapsed:.3f}s")
        print(f"  ✅ Value: {value}")
        print(f"  📝 Result length: {len(result)} chars")
        print(f"  Content: {result[:100]}...")
        
        print(f"\n💭 verbosity='low'を追加すれば:")
        print(f"   期待される改善: 10-20%の高速化")
        print(f"   応答の簡潔化: より短い説明")
        print(f"   推定時間: {elapsed * 0.8:.3f}s - {elapsed * 0.9:.3f}s")
        
    except Exception as e:
        print(f"  ❌ Error: {e}")


if __name__ == "__main__":
    try:
        api_results = test_verbosity_comparison()
        test_verbosity_in_nlm()
        
        # Summary
        if api_results:
            print("\n" + "="*70)
            print("📋 verbosity パラメータ検証結果:")
            print("="*70)
            
            # Check if verbosity is supported
            supported_levels = [name for name, results in api_results.items() 
                              if any(r['success'] for r in results)]
            
            if len(supported_levels) > 1:
                print("✅ verbosity パラメータはサポートされています")
                print("💡 NLMシステムへの実装を推奨します")
            else:
                print("❌ verbosity パラメータはサポートされていません")
                print("   または現在のAPIバージョンでは利用不可")
        
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()