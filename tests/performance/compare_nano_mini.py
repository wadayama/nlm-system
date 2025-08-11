#!/usr/bin/env python
"""Compare gpt-5-nano and gpt-5-mini performance"""

import time
import statistics
import subprocess
import sys
import re


def run_speed_test(model_name):
    """Run speed test for specified model and extract results"""
    print(f"\n🚀 Running {model_name} speed test...")
    print("="*60)
    
    if model_name == "nano":
        script = "tests/performance/test_gpt5_nano_speed.py"
    else:
        script = "tests/performance/test_gpt5_mini_speed.py"
    
    try:
        # Run the test script and capture output
        result = subprocess.run(
            ["uv", "run", script],
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes timeout
        )
        
        if result.returncode == 0:
            output = result.stdout
            print(output)
            
            # Extract timing information
            times = []
            lines = output.split('\n')
            
            for line in lines:
                if "Time:" in line:
                    # Extract time value from "Time: X.XXXs"
                    time_match = re.search(r'Time: (\d+\.\d+)s', line)
                    if time_match:
                        times.append(float(time_match.group(1)))
            
            if times:
                return {
                    'times': times,
                    'average': statistics.mean(times),
                    'fastest': min(times),
                    'slowest': max(times),
                    'median': statistics.median(times),
                    'count': len(times)
                }
        else:
            print(f"❌ Error running {model_name} test:")
            print(result.stderr)
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {model_name} test timed out")
    except Exception as e:
        print(f"❌ Error running {model_name} test: {e}")
    
    return None


def compare_results(nano_results, mini_results):
    """Compare and analyze results from both models"""
    print("\n" + "="*80)
    print("📊 NANO vs MINI Performance Comparison")
    print("="*80)
    
    if not nano_results or not mini_results:
        print("❌ Cannot compare - missing results")
        return
    
    print(f"\n📋 Results Summary:")
    print("-" * 50)
    print(f"{'Metric':<20} {'GPT-5-NANO':<15} {'GPT-5-MINI':<15} {'Difference':<15}")
    print("-" * 65)
    
    # Average time comparison
    avg_diff = mini_results['average'] - nano_results['average']
    avg_pct = (avg_diff / nano_results['average']) * 100
    print(f"{'Average Time':<20} {nano_results['average']:.3f}s{'':<7} {mini_results['average']:.3f}s{'':<7} {avg_pct:+.1f}%")
    
    # Fastest time comparison
    fast_diff = mini_results['fastest'] - nano_results['fastest']
    fast_pct = (fast_diff / nano_results['fastest']) * 100
    print(f"{'Fastest Time':<20} {nano_results['fastest']:.3f}s{'':<7} {mini_results['fastest']:.3f}s{'':<7} {fast_pct:+.1f}%")
    
    # Slowest time comparison
    slow_diff = mini_results['slowest'] - nano_results['slowest']
    slow_pct = (slow_diff / nano_results['slowest']) * 100
    print(f"{'Slowest Time':<20} {nano_results['slowest']:.3f}s{'':<7} {mini_results['slowest']:.3f}s{'':<7} {slow_pct:+.1f}%")
    
    # Median time comparison
    med_diff = mini_results['median'] - nano_results['median']
    med_pct = (med_diff / nano_results['median']) * 100
    print(f"{'Median Time':<20} {nano_results['median']:.3f}s{'':<7} {mini_results['median']:.3f}s{'':<7} {med_pct:+.1f}%")
    
    # Analysis
    print(f"\n📈 Performance Analysis:")
    print("-" * 50)
    
    if avg_pct < -10:
        print("🚀 GPT-5-MINI is significantly faster than GPT-5-NANO")
    elif avg_pct < -5:
        print("⚡ GPT-5-MINI is moderately faster than GPT-5-NANO")
    elif avg_pct < 5:
        print("⚖️  GPT-5-MINI and GPT-5-NANO have similar performance")
    elif avg_pct < 10:
        print("🐌 GPT-5-MINI is moderately slower than GPT-5-NANO")
    else:
        print("🐢 GPT-5-MINI is significantly slower than GPT-5-NANO")
    
    print(f"\n🎯 Key Insights:")
    print(f"   • Average speed difference: {abs(avg_pct):.1f}% ({'faster' if avg_pct < 0 else 'slower'} for MINI)")
    print(f"   • Consistency: NANO range = {nano_results['slowest']-nano_results['fastest']:.3f}s, MINI range = {mini_results['slowest']-mini_results['fastest']:.3f}s")
    
    # Cost considerations (approximate)
    print(f"\n💰 Cost Considerations:")
    print(f"   • GPT-5-NANO: Economy tier (lowest cost)")
    print(f"   • GPT-5-MINI: Standard tier (moderate cost)")
    print(f"   • For similar tasks, consider cost vs speed trade-off")


def main():
    """Main comparison function"""
    print("🔍 GPT-5 Model Performance Comparison")
    print("="*60)
    print("Comparing gpt-5-nano (Economy) vs gpt-5-mini (Standard)")
    
    # Run tests for both models
    nano_results = run_speed_test("nano")
    mini_results = run_speed_test("mini")
    
    # Compare results
    if nano_results and mini_results:
        compare_results(nano_results, mini_results)
    else:
        print("❌ Could not complete comparison - one or both tests failed")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️ Comparison interrupted")
    except Exception as e:
        print(f"\n❌ Comparison failed: {e}")