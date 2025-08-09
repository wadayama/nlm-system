#!/usr/bin/env python
"""Test reasoning_effort parameter to improve latency"""

import time
from openai import OpenAI
import statistics


def test_reasoning_effort():
    """Compare response times with different reasoning_effort settings"""
    print("="*70)
    print("🚀 Testing reasoning_effort parameter for latency improvement")
    print("="*70)
    
    # Load API key
    try:
        with open('.openai_key', 'r') as f:
            api_key = f.read().strip()
    except FileNotFoundError:
        print("❌ .openai_key not found")
        return
    
    client = OpenAI(api_key=api_key)
    
    # Test prompt
    test_prompt = "Say 'Hello World' and nothing else"
    
    # Test different reasoning efforts
    reasoning_modes = [
        ("default", None),
        ("minimal", "minimal"),
        ("low", "low"),
        ("medium", "medium"),
        ("high", "high")
    ]
    
    models_to_test = ["gpt-5", "gpt-5-mini", "gpt-5-nano"]
    
    for model in models_to_test:
        print(f"\n📊 Testing {model}:")
        print("-" * 50)
        
        results = {}
        
        for mode_name, reasoning_value in reasoning_modes:
            times = []
            errors = 0
            
            # Run 3 tests for each mode
            for i in range(3):
                try:
                    # Build request parameters
                    params = {
                        "model": model,
                        "messages": [{"role": "user", "content": test_prompt}]
                    }
                    
                    # Add reasoning_effort if specified
                    if reasoning_value:
                        # Try as a direct parameter
                        params["reasoning_effort"] = reasoning_value
                    
                    start = time.time()
                    response = client.chat.completions.create(**params)
                    elapsed = time.time() - start
                    times.append(elapsed)
                    
                except Exception as e:
                    error_msg = str(e)
                    if "reasoning_effort" in error_msg or "parameter" in error_msg:
                        # Try alternative approach
                        try:
                            # Try as extra_body parameter
                            params = {
                                "model": model,
                                "messages": [{"role": "user", "content": test_prompt}]
                            }
                            if reasoning_value:
                                params["extra_body"] = {"reasoning_effort": reasoning_value}
                            
                            start = time.time()
                            response = client.chat.completions.create(**params)
                            elapsed = time.time() - start
                            times.append(elapsed)
                        except Exception as e2:
                            errors += 1
                            if i == 0:  # Only print error once
                                print(f"  {mode_name}: ❌ Error - {str(e2)[:60]}")
                    else:
                        errors += 1
                        if i == 0:
                            print(f"  {mode_name}: ❌ Error - {error_msg[:60]}")
            
            if times and errors < 3:
                avg_time = statistics.mean(times)
                results[mode_name] = avg_time
                print(f"  {mode_name}: {avg_time:.3f}s (avg of {len(times)} runs)")
        
        # Compare results
        if len(results) > 1 and "default" in results:
            print(f"\n  ⚡ Performance comparison for {model}:")
            baseline = results["default"]
            for mode, time_val in results.items():
                if mode != "default":
                    improvement = (baseline - time_val) / baseline * 100
                    if improvement > 0:
                        print(f"    {mode}: {improvement:.1f}% faster")
                    elif improvement < 0:
                        print(f"    {mode}: {abs(improvement):.1f}% slower")
                    else:
                        print(f"    {mode}: same speed")
    
    # Test with NLM system
    print("\n\n🔧 Testing with NLM system (gpt-5-nano):")
    print("-" * 50)
    from nlm_interpreter import NLMSession
    
    # Standard session
    print("\nStandard NLM session:")
    session1 = NLMSession(model="gpt-5-nano", namespace="test_standard")
    start = time.time()
    result1 = session1.execute("Say hello")
    time1 = time.time() - start
    print(f"  Time: {time1:.3f}s")
    
    # Try to modify the session to use reasoning_effort
    print("\nAttempting to use reasoning_effort in NLM...")
    print("  Note: This would require modifying nlm_interpreter.py")
    print("  to pass reasoning_effort parameter to OpenAI API calls")
    
    print("\n" + "="*70)
    print("💡 Summary:")
    print("="*70)
    print("If reasoning_effort parameter works:")
    print("  - 'minimal' should provide fastest response")
    print("  - Trade-off: Less sophisticated reasoning for speed")
    print("  - Best for simple, straightforward tasks")
    print("\nIf not supported:")
    print("  - Parameter might be model-specific")
    print("  - May require API version update")


if __name__ == "__main__":
    test_reasoning_effort()