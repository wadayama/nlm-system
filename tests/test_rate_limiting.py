#!/usr/bin/env python
"""Test rate limiting functionality"""

import time
from nlm_interpreter import NLMSession


def test_rate_limiting():
    """Test rate limiting for different models"""
    print("="*60)
    print("レート制限機能テスト")
    print("="*60)
    
    models_to_test = [
        ("gpt-oss:20b", "ローカル"),
        ("gpt-5-mini", "OpenAI")
    ]
    
    for model, model_type in models_to_test:
        print(f"\n{'='*40}")
        print(f"Testing {model} ({model_type})")
        print('='*40)
        
        try:
            start_time = time.time()
            session = NLMSession(model=model, namespace=f"rate_test_{model.replace(':', '_').replace('-', '_')}")
            
            # Test multiple operations
            operations = [
                "Save 'test1' to {{var1}}",
                "Save 'test2' to {{var2}}", 
                "Get {{var1}} and display it"
            ]
            
            print(f"\n🧪 Testing {len(operations)} operations...")
            
            for i, operation in enumerate(operations, 1):
                print(f"\nOperation {i}: {operation}")
                op_start = time.time()
                
                try:
                    result = session.execute(operation)
                    op_end = time.time()
                    op_duration = op_end - op_start
                    
                    print(f"✅ Completed in {op_duration:.1f}s")
                    if len(result) > 100:
                        print(f"Result: {result[:100]}...")
                    else:
                        print(f"Result: {result}")
                        
                except Exception as e:
                    op_end = time.time() 
                    op_duration = op_end - op_start
                    error_msg = str(e)
                    if "429" in error_msg:
                        print(f"❌ Rate limit hit after {op_duration:.1f}s")
                    else:
                        print(f"❌ Error after {op_duration:.1f}s: {error_msg[:60]}...")
                    break
            
            total_time = time.time() - start_time
            print(f"\n📊 Total test time: {total_time:.1f}s")
            
            # Expected behavior
            if model.startswith("gpt-5"):
                expected_min_time = len(operations) * 2.0  # 2s delay per operation
                print(f"   Expected minimum time (with delays): {expected_min_time:.1f}s")
                if total_time >= expected_min_time * 0.8:  # Allow some tolerance
                    print("   ✅ Rate limiting appears to be working")
                else:
                    print("   ⚠️  Rate limiting may not be applied")
            else:
                print("   💻 Local model - no rate limiting expected")
                
        except Exception as e:
            print(f"❌ Model setup failed: {e}")


def test_rate_limiting_detailed():
    """Detailed rate limiting test"""
    print("\n" + "="*60)
    print("詳細レート制限テスト")
    print("="*60)
    
    try:
        # Test OpenAI model
        session = NLMSession(model="gpt-5-mini", namespace="detailed_rate_test")
        
        print("\n🔍 Testing _apply_rate_limiting() method directly...")
        
        # Test the rate limiting method directly
        times = []
        for i in range(3):
            print(f"\nTest {i+1}/3:")
            start = time.time()
            session._apply_rate_limiting()  # Direct method call
            end = time.time()
            duration = end - start
            times.append(duration)
            print(f"Rate limiting took: {duration:.1f}s")
        
        avg_time = sum(times) / len(times)
        print(f"\n📊 Average rate limiting delay: {avg_time:.1f}s")
        
        if avg_time >= 1.8:  # Should be ~2.0s
            print("✅ Rate limiting working correctly")
        else:
            print("❌ Rate limiting not working as expected")
            
    except Exception as e:
        print(f"❌ Detailed test failed: {e}")


if __name__ == "__main__":
    test_rate_limiting()
    test_rate_limiting_detailed()