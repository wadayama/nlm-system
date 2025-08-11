#!/usr/bin/env python3
"""Test conditional logic capabilities of NLM system

This test suite specifically targets conditional branching,
a known weak point in LLM-based macro processing.
Based on patterns from macro.md documentation.
"""

from nlm_interpreter import NLMSession
import json
from pathlib import Path
import time

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
CYAN = '\033[96m'  # Changed from YELLOW for better readability
BLUE = '\033[94m'
RESET = '\033[0m'


def test_simple_if_then(session):
    """Test simple if-then conditional"""
    test_name = "Simple if-then"
    
    # Clear previous state
    session.clear_local()
    
    # Test 1: Score >= 80 (should be 合格)
    session.save("score", "85")
    result = session.execute(
        "{{score}}が80以上の場合は「合格」、そうでない場合は「不合格」を{{result}}に保存してください"
    )
    actual_result = session.get("result")
    expected = "合格"
    success1 = actual_result == expected
    
    # Test 2: Score < 80 (should be 不合格)
    session.save("score", "75")
    result = session.execute(
        "{{score}}が80以上の場合は「合格」、そうでない場合は「不合格」を{{result}}に保存してください"
    )
    actual_result = session.get("result")
    expected = "不合格"
    success2 = actual_result == expected
    
    return success1 and success2, test_name, f"Test1: {success1}, Test2: {success2}"


def test_multi_level_conditions(session):
    """Test multi-level if-elif-else conditions"""
    test_name = "Multi-level conditions"
    
    session.clear_local()
    
    # Test with score = 85 (should be 優秀)
    session.save("score", "85")
    result = session.execute("""
{{score}}に基づいて評価を決定してください：
- 80点以上の場合は「優秀」
- 60点以上80点未満の場合は「良好」
- 60点未満の場合は「要改善」
結果を{{evaluation}}に保存してください
""")
    
    actual = session.get("evaluation")
    expected = "優秀"
    success1 = actual == expected
    
    # Test with score = 70 (should be 良好)
    session.save("score", "70")
    result = session.execute("""
{{score}}に基づいて評価を決定してください：
- 80点以上の場合は「優秀」
- 60点以上80点未満の場合は「良好」
- 60点未満の場合は「要改善」
結果を{{evaluation}}に保存してください
""")
    
    actual = session.get("evaluation")
    expected = "良好"
    success2 = actual == expected
    
    # Test with score = 50 (should be 要改善)
    session.save("score", "50")
    result = session.execute("""
{{score}}に基づいて評価を決定してください：
- 80点以上の場合は「優秀」
- 60点以上80点未満の場合は「良好」
- 60点未満の場合は「要改善」
結果を{{evaluation}}に保存してください
""")
    
    actual = session.get("evaluation")
    expected = "要改善"
    success3 = actual == expected
    
    return (success1 and success2 and success3), test_name, f"85→優秀:{success1}, 70→良好:{success2}, 50→要改善:{success3}"


def test_compound_conditions(session):
    """Test compound conditions with AND/OR logic"""
    test_name = "Compound conditions"
    
    session.clear_local()
    
    # Test: Cold and Rainy (should be 外出注意)
    session.save("temperature", "15")
    session.save("weather", "雨")
    result = session.execute("""
{{temperature}}が20度未満で{{weather}}が「雨」の場合は「外出注意」、
そうでない場合は「通常外出」を{{advice}}に保存してください
""")
    
    actual = session.get("advice")
    expected = "外出注意"
    success1 = actual == expected
    
    # Test: Warm and Rainy (should be 通常外出)
    session.save("temperature", "25")
    session.save("weather", "雨")
    result = session.execute("""
{{temperature}}が20度未満で{{weather}}が「雨」の場合は「外出注意」、
そうでない場合は「通常外出」を{{advice}}に保存してください
""")
    
    actual = session.get("advice")
    expected = "通常外出"
    success2 = actual == expected
    
    return (success1 and success2), test_name, f"Cold&Rain→外出注意:{success1}, Warm&Rain→通常外出:{success2}"


def test_variable_swap(session):
    """Test variable swapping - a known difficult case"""
    test_name = "Variable swap"
    
    session.clear_local()
    
    # Initialize variables
    session.save("a", "apple")
    session.save("b", "banana")
    
    # Request swap
    result = session.execute("""
{{a}}と{{b}}の値を入れ替えてください。
一時変数{{temp}}を使って、以下の手順で実行：
1. {{a}}の値を{{temp}}に保存
2. {{b}}の値を{{a}}に保存
3. {{temp}}の値を{{b}}に保存
""")
    
    # Check if swap was successful
    new_a = session.get("a")
    new_b = session.get("b")
    
    success = (new_a == "banana" and new_b == "apple")
    
    return success, test_name, f"a={new_a} (expect: banana), b={new_b} (expect: apple)"


def test_string_matching(session):
    """Test string matching conditions"""
    test_name = "String matching"
    
    session.clear_local()
    
    # Test with status = "active"
    session.save("status", "active")
    result = session.execute("""
{{status}}が「active」の場合は「システム稼働中」、
「inactive」の場合は「システム停止中」、
その他の場合は「不明な状態」を{{message}}に保存してください
""")
    
    actual = session.get("message")
    expected = "システム稼働中"
    success1 = actual == expected
    
    # Test with status = "inactive"
    session.save("status", "inactive")
    result = session.execute("""
{{status}}が「active」の場合は「システム稼働中」、
「inactive」の場合は「システム停止中」、
その他の場合は「不明な状態」を{{message}}に保存してください
""")
    
    actual = session.get("message")
    expected = "システム停止中"
    success2 = actual == expected
    
    return (success1 and success2), test_name, f"active→稼働中:{success1}, inactive→停止中:{success2}"


def test_numeric_comparisons(session):
    """Test various numeric comparison operators"""
    test_name = "Numeric comparisons"
    
    session.clear_local()
    results = []
    
    # Test greater than
    session.save("value", "15")
    result = session.execute(
        "{{value}}が10より大きい場合は「大」、そうでない場合は「小」を{{size}}に保存してください"
    )
    actual = session.get("size")
    results.append(actual == "大")
    
    # Test less than or equal
    session.save("value", "10")
    result = session.execute(
        "{{value}}が10以下の場合は「OK」、そうでない場合は「NG」を{{check}}に保存してください"
    )
    actual = session.get("check")
    results.append(actual == "OK")
    
    # Test equality
    session.save("value", "100")
    result = session.execute(
        "{{value}}が100と等しい場合は「一致」、そうでない場合は「不一致」を{{match}}に保存してください"
    )
    actual = session.get("match")
    results.append(actual == "一致")
    
    success = all(results)
    return success, test_name, f"GT:{results[0]}, LE:{results[1]}, EQ:{results[2]}"


def test_ambiguous_conditions(session):
    """Test handling of ambiguous/qualitative conditions"""
    test_name = "Ambiguous conditions"
    
    session.clear_local()
    
    # Test with "十分に高い" (sufficiently high)
    session.save("score", "95")
    result = session.execute(
        "{{score}}が十分に高い場合は「優秀認定」、そうでない場合は「通常」を{{certification}}に保存してください"
    )
    
    actual = session.get("certification")
    # Check if it made a reasonable decision (95 should be considered "high")
    success1 = actual == "優秀認定"
    
    # Test with low score
    session.save("score", "30")
    result = session.execute(
        "{{score}}が十分に高い場合は「優秀認定」、そうでない場合は「通常」を{{certification}}に保存してください"
    )
    
    actual = session.get("certification")
    success2 = actual == "通常"
    
    return (success1 and success2), test_name, f"95→優秀認定:{success1}, 30→通常:{success2}"


def run_test_suite(model="gpt-5-mini", reasoning="low"):
    """Run all conditional logic tests"""
    
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}🧪 Conditional Logic Test Suite{RESET}")
    print(f"{BLUE}Model: {model}{RESET}")
    print(f"{BLUE}Reasoning: {reasoning}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    # Initialize session with reasoning level
    session = NLMSession(namespace=f"cond_test_{model}", model=model, reasoning_effort=reasoning)
    
    # Define all tests
    tests = [
        test_simple_if_then,
        test_multi_level_conditions,
        test_compound_conditions,
        test_variable_swap,
        test_string_matching,
        test_numeric_comparisons,
        test_ambiguous_conditions
    ]
    
    results = []
    total_time = 0
    
    # Run each test
    for i, test_func in enumerate(tests, 1):
        print(f"{CYAN}Test {i}/{len(tests)}: {test_func.__name__}{RESET}")
        
        start_time = time.time()
        try:
            success, test_name, details = test_func(session)
            elapsed = time.time() - start_time
            total_time += elapsed
            
            if success:
                print(f"  {GREEN}✅ PASSED{RESET} - {test_name}")
            else:
                print(f"  {RED}❌ FAILED{RESET} - {test_name}")
            print(f"  Details: {details}")
            print(f"  Time: {elapsed:.2f}s")
            
            results.append({
                "test": test_name,
                "success": success,
                "details": details,
                "time": elapsed
            })
            
        except Exception as e:
            print(f"  {RED}❌ ERROR{RESET} - {str(e)}")
            results.append({
                "test": test_func.__name__,
                "success": False,
                "details": f"Error: {str(e)}",
                "time": 0
            })
        
        print()
    
    # Summary
    successful = sum(1 for r in results if r["success"])
    total = len(results)
    success_rate = (successful / total) * 100 if total > 0 else 0
    
    print(f"{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}📊 Test Summary{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    print(f"Model: {model}")
    print(f"Success Rate: {success_rate:.1f}% ({successful}/{total})")
    print(f"Total Time: {total_time:.2f}s")
    print(f"Average Time per Test: {total_time/total:.2f}s")
    
    # Detailed failure analysis
    failed_tests = [r for r in results if not r["success"]]
    if failed_tests:
        print(f"\n{RED}Failed Tests:{RESET}")
        for r in failed_tests:
            print(f"  - {r['test']}: {r['details']}")
    
    return results, success_rate


def compare_models(reasoning="low"):
    """Compare conditional logic performance across models"""
    
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}🔬 Model Comparison: Conditional Logic{RESET}")
    print(f"{BLUE}Reasoning Level: {reasoning}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    models_to_test = []
    
    # Check if local model is available
    try:
        session_local = NLMSession(namespace="test_local", model="gpt-oss:20b")
        session_local.execute("Test connection")
        models_to_test.append(("gpt-oss:20b", "Local"))
    except:
        print(f"{CYAN}⚠️  Local model not available{RESET}")
    
    # Add OpenAI model
    models_to_test.append(("gpt-5-mini", "OpenAI"))
    
    comparison_results = {}
    
    for model, label in models_to_test:
        print(f"\n{BLUE}Testing {label} Model: {model}{RESET}")
        results, success_rate = run_test_suite(model, reasoning)
        comparison_results[model] = {
            "label": label,
            "results": results,
            "success_rate": success_rate
        }
    
    # Comparison summary
    if len(comparison_results) > 1:
        print(f"\n{BLUE}{'='*60}{RESET}")
        print(f"{BLUE}📈 Comparison Results{RESET}")
        print(f"{BLUE}{'='*60}{RESET}\n")
        
        for model, data in comparison_results.items():
            print(f"{data['label']} ({model}):")
            print(f"  Success Rate: {data['success_rate']:.1f}%")
            
            # Test-by-test comparison
            print(f"  Test Results:")
            for r in data['results']:
                status = "✅" if r['success'] else "❌"
                print(f"    {status} {r['test']}")
        
        # Identify common failures
        print(f"\n{CYAN}Common Challenges:{RESET}")
        all_tests = set()
        failed_by_model = {}
        
        for model, data in comparison_results.items():
            failed_by_model[model] = set()
            for r in data['results']:
                all_tests.add(r['test'])
                if not r['success']:
                    failed_by_model[model].add(r['test'])
        
        # Find tests that all models failed
        common_failures = set.intersection(*failed_by_model.values()) if failed_by_model else set()
        if common_failures:
            print(f"{RED}Tests failed by all models:{RESET}")
            for test in common_failures:
                print(f"  - {test}")
        else:
            print(f"{GREEN}No common failures across models{RESET}")
        
        # Find model-specific strengths
        print(f"\n{GREEN}Model-Specific Strengths:{RESET}")
        for model, data in comparison_results.items():
            passed = set(r['test'] for r in data['results'] if r['success'])
            unique_passes = passed
            for other_model in comparison_results:
                if other_model != model:
                    other_failed = failed_by_model[other_model]
                    unique_passes = unique_passes.intersection(other_failed)
            
            if unique_passes:
                print(f"{data['label']} uniquely passed:")
                for test in unique_passes:
                    print(f"  - {test}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test conditional logic in NLM system")
    parser.add_argument("-m", "--model", default="gpt-5-mini", 
                       help="Model to test (gpt-5-mini, gpt-oss:20b, etc.)")
    parser.add_argument("-c", "--compare", action="store_true",
                       help="Compare performance across models")
    parser.add_argument("-r", "--reasoning", default="low",
                       choices=["low", "medium", "high"],
                       help="Reasoning effort level (low, medium, high)")
    
    args = parser.parse_args()
    
    if args.compare:
        compare_models(args.reasoning)
    else:
        run_test_suite(args.model, args.reasoning)


if __name__ == "__main__":
    main()