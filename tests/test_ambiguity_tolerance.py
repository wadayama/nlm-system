#!/usr/bin/env python3
"""Test ambiguity tolerance capabilities of NLM system

This test suite evaluates how well the system handles
different levels of ambiguity in user requests,
based on the pattern from macro.md documentation.
"""

from nlm_interpreter import NLMSession
import time

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
CYAN = '\033[96m'
BLUE = '\033[94m'
RESET = '\033[0m'


def test_ambiguity_handler(session, request, expected_level):
    """Execute ambiguity handling macro and check results"""
    
    # Clear previous state
    session.clear_local()
    
    # Save the user request
    session.save("user_request", request)
    
    # Execute the ambiguity handling macro
    result = session.execute("""
Analyze the ambiguity level of {{user_request}} and execute the following:

For clear requests:
→ Execute definitively and save result to {{definitive_result}}
→ Record "clear" in {{ambiguity_level}}

For partially ambiguous requests:
→ Execute with "Processing based on context inference" and save to {{inferred_result}}
→ Record "Contains partial inference" in {{uncertainty_note}}
→ Record "partial" in {{ambiguity_level}}

For highly ambiguous requests:
→ Execute with "Processing with most likely interpretation" and save to {{speculative_result}}
→ Record "High uncertainty interpretation" in {{speculation_note}}
→ Record "high" in {{ambiguity_level}}

For uninterpretable requests:
→ Provide general framework and save to {{fallback_framework}}
→ Record "Recommend specific request re-input" in {{clarification_request}}
→ Record "uninterpretable" in {{ambiguity_level}}
""")
    
    # Get the detected ambiguity level
    detected_level = session.get("ambiguity_level")
    
    # Check which result variable was set
    results = {
        "definitive_result": session.get("definitive_result"),
        "inferred_result": session.get("inferred_result"),
        "speculative_result": session.get("speculative_result"),
        "fallback_framework": session.get("fallback_framework"),
        "uncertainty_note": session.get("uncertainty_note"),
        "speculation_note": session.get("speculation_note"),
        "clarification_request": session.get("clarification_request")
    }
    
    return detected_level, results


def run_ambiguity_tests(model="gpt-5-mini", reasoning="low"):
    """Run ambiguity tolerance test suite"""
    
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}🌫️  Ambiguity Tolerance Test Suite{RESET}")
    print(f"{BLUE}Model: {model}{RESET}")
    print(f"{BLUE}Reasoning: {reasoning}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    # Initialize session
    session = NLMSession(
        namespace=f"ambiguity_test_{model}",
        model=model,
        reasoning_effort=reasoning
    )
    
    # Test cases with different ambiguity levels
    test_cases = [
        {
            "request": "Please tell me the weather forecast for Tokyo on January 15, 2024",
            "expected": "clear",
            "description": "Specific date and location"
        },
        {
            "request": "Write Python code to find all prime numbers up to 100",
            "expected": "clear",
            "description": "Clear programming task"
        },
        {
            "request": "Tell me about recent weather",
            "expected": "partial",
            "description": "Unclear timeframe and location"
        },
        {
            "request": "Recommend good restaurants",
            "expected": "partial",
            "description": "Missing location and cuisine type"
        },
        {
            "request": "Make that better",
            "expected": "high",
            "description": "No context for 'that'"
        },
        {
            "request": "Do the thing",
            "expected": "high",
            "description": "Completely vague reference"
        },
        {
            "request": "🎨🚀💡",
            "expected": "uninterpretable",
            "description": "Only emojis, no text"
        },
        {
            "request": "ksdjfh askdjh asdkjh",
            "expected": "uninterpretable",
            "description": "Random characters"
        }
    ]
    
    results = []
    print(f"{CYAN}Testing {len(test_cases)} ambiguity cases:{RESET}\n")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"{CYAN}Test {i}/{len(test_cases)}: {test_case['description']}{RESET}")
        print(f"  Request: \"{test_case['request'][:50]}...\"" if len(test_case['request']) > 50 else f"  Request: \"{test_case['request']}\"")
        print(f"  Expected: {test_case['expected']}")
        
        start_time = time.time()
        detected_level, result_vars = test_ambiguity_handler(
            session,
            test_case['request'],
            test_case['expected']
        )
        elapsed = time.time() - start_time
        
        print(f"  Detected: {detected_level if detected_level else 'None'}")
        
        # Determine which result was produced
        if result_vars['definitive_result']:
            print(f"  → Definitive result produced")
        elif result_vars['inferred_result']:
            print(f"  → Inferred result with note: {result_vars['uncertainty_note']}")
        elif result_vars['speculative_result']:
            print(f"  → Speculative result with note: {result_vars['speculation_note']}")
        elif result_vars['fallback_framework']:
            print(f"  → Fallback framework with: {result_vars['clarification_request']}")
        
        # Check if correct (direct comparison since both are in English now)
        success = (test_case['expected'] == detected_level)
        
        if success:
            print(f"  {GREEN}✅ CORRECT{RESET}")
        else:
            print(f"  {RED}❌ INCORRECT{RESET}")
        
        print(f"  Time: {elapsed:.2f}s\n")
        
        results.append({
            "request": test_case['request'],
            "expected": test_case['expected'],
            "detected": detected_level,
            "success": success,
            "time": elapsed
        })
    
    # Summary
    print(f"{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}📊 Summary{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    # Count by ambiguity level
    level_counts = {"clear": 0, "partial": 0, "high": 0, "uninterpretable": 0}
    level_correct = {"clear": 0, "partial": 0, "high": 0, "uninterpretable": 0}
    
    for r in results:
        if r['expected'] in level_counts:
            level_counts[r['expected']] += 1
            if r['success']:
                level_correct[r['expected']] += 1
    
    print("Accuracy by ambiguity level:")
    for level in ["clear", "partial", "high", "uninterpretable"]:
        if level_counts[level] > 0:
            accuracy = (level_correct[level] / level_counts[level]) * 100
            print(f"  {level}: {level_correct[level]}/{level_counts[level]} ({accuracy:.0f}%)")
    
    # Overall accuracy
    total_correct = sum(1 for r in results if r['success'])
    total = len(results)
    overall_accuracy = (total_correct / total * 100) if total > 0 else 0
    
    print(f"\nOverall Accuracy: {total_correct}/{total} ({overall_accuracy:.0f}%)")
    
    # Average time
    avg_time = sum(r['time'] for r in results) / len(results) if results else 0
    print(f"Average Time: {avg_time:.2f}s per test")
    
    # Confusion matrix
    print(f"\n{CYAN}Confusion Matrix:{RESET}")
    print("(Expected → Detected)")
    for r in results:
        if not r['success']:
            print(f"  {r['expected']} → {r['detected'] if r['detected'] else 'None'}: \"{r['request'][:30]}...\"")
    
    return results, overall_accuracy


def compare_reasoning_levels(model="gpt-5-mini"):
    """Compare ambiguity handling across reasoning levels"""
    
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}🔬 Reasoning Level Comparison for Ambiguity Tolerance{RESET}")
    print(f"{BLUE}Model: {model}{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    levels = ["low", "medium", "high"]
    comparison_results = {}
    
    for level in levels:
        print(f"\n{CYAN}━━━ Testing with reasoning={level} ━━━{RESET}")
        results, accuracy = run_ambiguity_tests(model, level)
        comparison_results[level] = {
            "results": results,
            "accuracy": accuracy
        }
    
    # Comparison summary
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}📈 Reasoning Level Comparison Summary{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    print("Overall Accuracy by Reasoning Level:")
    for level in levels:
        acc = comparison_results[level]["accuracy"]
        print(f"  {level}: {acc:.0f}%")
    
    # Check which ambiguity levels benefit most from higher reasoning
    print(f"\n{CYAN}Impact of Reasoning on Each Ambiguity Level:{RESET}")
    
    for ambig_level in ["clear", "partial", "high", "uninterpretable"]:
        print(f"\n{ambig_level}:")
        for reasoning in levels:
            results = comparison_results[reasoning]["results"]
            relevant = [r for r in results if r['expected'] == ambig_level]
            if relevant:
                correct = sum(1 for r in relevant if r['success'])
                total = len(relevant)
                acc = (correct / total * 100)
                print(f"  {reasoning}: {correct}/{total} ({acc:.0f}%)")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test ambiguity tolerance in NLM system")
    parser.add_argument("-m", "--model", default="gpt-5-mini",
                       help="Model to test")
    parser.add_argument("-r", "--reasoning", default="low",
                       choices=["low", "medium", "high"],
                       help="Reasoning effort level")
    parser.add_argument("--compare", action="store_true",
                       help="Compare across reasoning levels")
    
    args = parser.parse_args()
    
    if args.compare:
        compare_reasoning_levels(args.model)
    else:
        run_ambiguity_tests(args.model, args.reasoning)


if __name__ == "__main__":
    main()