#!/usr/bin/env python
"""Compare quality between different reasoning_effort settings"""

from openai import OpenAI
import time


def test_reasoning_comparison():
    """Compare quality and speed of different reasoning effort levels"""
    print("="*70)
    print("🔬 reasoning_effort 設定比較テスト")
    print("="*70)
    
    # Load API key
    try:
        with open('.openai_key', 'r') as f:
            api_key = f.read().strip()
    except FileNotFoundError:
        print("❌ .openai_key not found")
        return
    
    client = OpenAI(api_key=api_key)
    
    # Test cases to evaluate quality
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
            "description": "Simple tool use"
        },
        {
            "prompt": "Calculate 15 * 23 and respond with just the number",
            "tools": None,
            "description": "Math calculation"
        },
        {
            "prompt": "If 5 > 3, respond 'true', otherwise 'false'",
            "tools": None,
            "description": "Logic reasoning"
        }
    ]
    
    reasoning_levels = [
        ("default", None),
        ("minimal", "minimal"),
        ("low", "low"),
        ("medium", "medium")
    ]
    
    results = {}
    
    for level_name, level_value in reasoning_levels:
        print(f"\n📊 Testing reasoning_effort = {level_name}:")
        print("-" * 50)
        
        level_results = []
        
        for i, test in enumerate(test_cases, 1):
            print(f"\n  Test {i}: {test['description']}")
            print(f"  Prompt: {test['prompt'][:60]}...")
            
            # Prepare request
            params = {
                "model": "gpt-5-nano",
                "messages": [{"role": "user", "content": test['prompt']}]
            }
            
            if test['tools']:
                params["tools"] = test['tools']
            
            if level_value:
                params["reasoning_effort"] = level_value
            
            # Make request
            start = time.time()
            try:
                response = client.chat.completions.create(**params)
                elapsed = time.time() - start
                
                message = response.choices[0].message
                content = message.content or ""
                tool_calls = message.tool_calls
                
                print(f"    ⏱️  Time: {elapsed:.3f}s")
                print(f"    Response: {content[:80]}...")
                
                if tool_calls:
                    print(f"    Tool calls: {len(tool_calls)}")
                    for call in tool_calls:
                        print(f"      {call.function.name}: {call.function.arguments}")
                
                level_results.append({
                    'test': test['description'],
                    'time': elapsed,
                    'content': content,
                    'tool_calls': len(tool_calls) if tool_calls else 0,
                    'success': True
                })
                
            except Exception as e:
                print(f"    ❌ Error: {e}")
                level_results.append({
                    'test': test['description'],
                    'time': None,
                    'content': None,
                    'tool_calls': 0,
                    'success': False,
                    'error': str(e)
                })
        
        results[level_name] = level_results
    
    # Analysis
    print("\n" + "="*70)
    print("📊 比較分析:")
    print("="*70)
    
    print(f"\n{'Level':<10} {'Avg Time':<10} {'Success Rate':<12} {'Quality Notes'}")
    print("-" * 60)
    
    for level_name, level_results in results.items():
        successful = [r for r in level_results if r['success']]
        success_rate = len(successful) / len(level_results) * 100
        avg_time = sum(r['time'] for r in successful) / len(successful) if successful else 0
        
        quality_notes = []
        if level_name == "minimal":
            # Check if tools were used properly
            tool_use_results = [r for r in successful if 'Simple tool use' in r['test']]
            if tool_use_results and tool_use_results[0]['tool_calls'] == 0:
                quality_notes.append("Tools not used")
            
            # Check math accuracy
            math_results = [r for r in successful if 'Math' in r['test']]
            if math_results and '345' not in math_results[0]['content']:
                quality_notes.append("Math incorrect")
        
        quality_str = ", ".join(quality_notes) if quality_notes else "OK"
        
        print(f"{level_name:<10} {avg_time:<10.3f} {success_rate:<12.1f}% {quality_str}")
    
    print(f"\n💡 推奨設定:")
    
    # Find best balance
    minimal_results = results.get('minimal', [])
    default_results = results.get('default', [])
    
    if minimal_results and default_results:
        minimal_success = len([r for r in minimal_results if r['success']])
        default_success = len([r for r in default_results if r['success']])
        
        if minimal_success >= default_success * 0.8:  # 80% success rate threshold
            print("  ✅ reasoning_effort='minimal' は許容可能")
            print("     速度向上のメリットが品質低下を上回る")
        else:
            print("  ⚠️ reasoning_effort='minimal' は品質が低下")
            print("     'low' または 'default' の使用を推奨")


if __name__ == "__main__":
    try:
        test_reasoning_comparison()
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted")
    except Exception as e:
        print(f"❌ Test failed: {e}")