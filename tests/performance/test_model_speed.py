#!/usr/bin/env python
"""Model speed comparison test"""

import time
import statistics
from nlm_interpreter import NLMSession


def test_model_speed(model_name, test_count=3):
    """Test response speed for a specific model
    
    Args:
        model_name: Name of the model to test
        test_count: Number of tests to run for averaging
        
    Returns:
        dict: Test results with timing information
    """
    print(f"\n{'='*60}")
    print(f"Testing Model: {model_name}")
    print('='*60)
    
    results = {
        'model': model_name,
        'times': [],
        'errors': [],
        'success_count': 0,
        'total_tests': test_count
    }
    
    # Simple test tasks
    test_tasks = [
        "Save 'hello' to {{greeting}}",
        "Set {{counter}} to 42", 
        "Store 'test data' in {{data}}"
    ]
    
    for i in range(test_count):
        try:
            print(f"Test {i+1}/{test_count}: ", end="", flush=True)
            
            # Create session for this test
            session = NLMSession(
                model=model_name,
                namespace=f"speed_test_{model_name.replace('-', '_').replace(':', '_')}_{i}"
            )
            
            # Select test task
            task = test_tasks[i % len(test_tasks)]
            
            # Time the execution
            start_time = time.time()
            result = session.execute(task)
            end_time = time.time()
            
            duration = end_time - start_time
            results['times'].append(duration)
            results['success_count'] += 1
            
            print(f"{duration:.2f}s ✅")
            
            # Brief pause between tests
            time.sleep(0.5)
            
        except Exception as e:
            print(f"❌ Error: {str(e)[:50]}...")
            results['errors'].append(str(e))
    
    # Calculate statistics
    if results['times']:
        results['avg_time'] = statistics.mean(results['times'])
        results['min_time'] = min(results['times'])
        results['max_time'] = max(results['times'])
        results['median_time'] = statistics.median(results['times'])
        if len(results['times']) > 1:
            results['std_dev'] = statistics.stdev(results['times'])
        else:
            results['std_dev'] = 0.0
    else:
        results['avg_time'] = None
    
    return results


def format_time(seconds):
    """Format time in a readable way"""
    if seconds is None:
        return "N/A"
    return f"{seconds:.2f}s"


def print_results(results):
    """Print formatted test results"""
    model = results['model']
    success_rate = (results['success_count'] / results['total_tests']) * 100
    
    print(f"\n📊 Results for {model}:")
    print(f"   Success Rate: {success_rate:.1f}% ({results['success_count']}/{results['total_tests']})")
    
    if results['avg_time'] is not None:
        print(f"   Average Time: {format_time(results['avg_time'])}")
        print(f"   Fastest Time: {format_time(results['min_time'])}")
        print(f"   Slowest Time: {format_time(results['max_time'])}")
        print(f"   Median Time:  {format_time(results['median_time'])}")
        print(f"   Std Dev:      {format_time(results['std_dev'])}")
        
        # Performance rating
        avg = results['avg_time']
        if avg < 2.0:
            rating = "🟢 Excellent"
        elif avg < 5.0:
            rating = "🟡 Good"
        elif avg < 10.0:
            rating = "🟠 Acceptable"
        else:
            rating = "🔴 Slow"
        print(f"   Performance:  {rating}")
    
    if results['errors']:
        print(f"   Errors: {len(results['errors'])}")
        for i, error in enumerate(results['errors'][:2]):  # Show first 2 errors
            print(f"     {i+1}. {error[:60]}...")


def run_speed_comparison():
    """Run speed comparison for all supported models"""
    print("🚀 NLM Model Speed Comparison")
    print("=" * 60)
    print("Testing response times for simple variable operations...")
    print("Each model will be tested 3 times for reliability")
    
    # Models to test
    models_to_test = [
        "gpt-oss:20b",    # Local LLM (default)
        "gpt-5-nano",     # OpenAI Economy
        "gpt-5-mini",     # OpenAI Standard  
        "gpt-5"           # OpenAI Premium
    ]
    
    all_results = []
    
    for model in models_to_test:
        try:
            results = test_model_speed(model, test_count=3)
            all_results.append(results)
            print_results(results)
            
        except Exception as e:
            print(f"\n❌ Failed to test {model}: {e}")
    
    # Summary comparison
    print("\n" + "=" * 60)
    print("📈 SPEED COMPARISON SUMMARY")
    print("=" * 60)
    
    # Sort by average time (fastest first)
    successful_results = [r for r in all_results if r['avg_time'] is not None]
    successful_results.sort(key=lambda x: x['avg_time'])
    
    if successful_results:
        print(f"{'Rank':<5} {'Model':<15} {'Avg Time':<10} {'Success Rate':<12} {'Rating'}")
        print("-" * 60)
        
        for i, result in enumerate(successful_results, 1):
            model = result['model']
            avg_time = format_time(result['avg_time'])
            success_rate = f"{(result['success_count']/result['total_tests'])*100:.0f}%"
            
            # Rating emoji
            if result['avg_time'] < 2.0:
                rating = "🟢"
            elif result['avg_time'] < 5.0:
                rating = "🟡"
            elif result['avg_time'] < 10.0:
                rating = "🟠"
            else:
                rating = "🔴"
                
            print(f"{i:<5} {model:<15} {avg_time:<10} {success_rate:<12} {rating}")
        
        fastest = successful_results[0]
        print(f"\n🏆 Fastest Model: {fastest['model']} ({format_time(fastest['avg_time'])})")
        
        # Cost efficiency note
        print("\n💡 Notes:")
        print("   🟢 = Excellent (< 2s)   🟡 = Good (2-5s)")
        print("   🟠 = Acceptable (5-10s)  🔴 = Slow (> 10s)")
        print("   💻 gpt-oss:20b = Local (Free)")
        print("   🌐 gpt-5-* = OpenAI (Paid)")
        
    else:
        print("❌ No successful tests completed")
    
    return all_results


if __name__ == "__main__":
    try:
        results = run_speed_comparison()
        print(f"\n✅ Speed comparison completed!")
    except KeyboardInterrupt:
        print(f"\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")