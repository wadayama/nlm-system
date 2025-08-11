#!/usr/bin/env python3
"""Test common sense judgment and evaluation capabilities

This test evaluates how well the NLM system can judge 
statements using common sense and assign appropriate 
0-100 scores based on truthfulness and certainty.
"""

from nlm_interpreter import NLMSession
import time

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
CYAN = '\033[96m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
RESET = '\033[0m'


def test_common_sense_judgment(session, statement, expected_range=None):
    """Test common sense evaluation of a statement"""
    
    # Clear previous state
    session.clear_local()
    
    # Save the statement
    session.save("statement", statement)
    
    # Execute common sense evaluation
    result = session.execute("""
Evaluate the statement: "{{statement}}"

Use your common sense to judge this statement and assign a score from 0 to 100:
- 100: Definitely true (commonly accepted fact)
- 80-99: Very likely true (strong evidence, widely accepted)
- 60-79: Probably true (generally accepted, some variation possible)
- 40-59: Uncertain (mixed evidence, depends on context)
- 20-39: Probably false (generally not accepted)
- 1-19: Very likely false (contradicts common knowledge)
- 0: Definitely false (clearly incorrect)

Consider:
- Scientific facts and natural laws
- Social and cultural common knowledge
- Observable phenomena
- General human experience

Provide your reasoning and assign a numerical score.
Save only the numerical score (0-100) to {{common_sense_score}}.
Save your reasoning to {{reasoning}}.
""")
    
    # Get results
    score_str = session.get("common_sense_score")
    reasoning = session.get("reasoning")
    
    # Parse score
    try:
        score = int(score_str) if score_str else None
    except (ValueError, TypeError):
        # Try to extract number from string
        import re
        if score_str:
            numbers = re.findall(r'\d+', score_str)
            score = int(numbers[0]) if numbers else None
        else:
            score = None
    
    return score, reasoning


def run_common_sense_tests(model="gpt-5-mini", reasoning="low"):
    """Run common sense evaluation test suite"""
    
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}🧠 Common Sense Judgment Test Suite{RESET}")
    print(f"{BLUE}Model: {model}{RESET}")
    print(f"{BLUE}Reasoning: {reasoning}{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    # Initialize session
    session = NLMSession(
        namespace=f"commonsense_test_{model}",
        model=model,
        reasoning_effort=reasoning
    )
    
    # Test cases with expected score ranges
    test_cases = [
        # Definitely True (90-100)
        {
            "statement": "The sun rises in the east",
            "expected_range": (90, 100),
            "category": "Natural Facts"
        },
        {
            "statement": "Water boils at 100 degrees Celsius at sea level",
            "expected_range": (90, 100),
            "category": "Scientific Facts"
        },
        {
            "statement": "Cats are mammals",
            "expected_range": (90, 100),
            "category": "Biological Facts"
        },
        {
            "statement": "Paris is the capital of France",
            "expected_range": (90, 100),
            "category": "Geographic Facts"
        },
        
        # Very Likely True (80-99)
        {
            "statement": "Exercise is generally good for health",
            "expected_range": (80, 95),
            "category": "Health Common Sense"
        },
        {
            "statement": "People need sleep to function properly",
            "expected_range": (85, 100),
            "category": "Human Biology"
        },
        
        # Probably True (60-79)
        {
            "statement": "Most people prefer sunny weather to rainy weather",
            "expected_range": (60, 80),
            "category": "Social Tendencies"
        },
        {
            "statement": "Reading books improves vocabulary",
            "expected_range": (70, 90),
            "category": "Educational Benefits"
        },
        
        # Uncertain/Context Dependent (40-59)
        {
            "statement": "Coffee helps people stay awake",
            "expected_range": (70, 90),
            "category": "Physiological Effects"
        },
        {
            "statement": "Expensive products are always better quality",
            "expected_range": (20, 40),
            "category": "Economic Assumptions"
        },
        
        # Probably False (20-39)
        {
            "statement": "All swans are white",
            "expected_range": (10, 30),
            "category": "Overgeneralization"
        },
        {
            "statement": "Money always brings happiness",
            "expected_range": (10, 40),
            "category": "Life Philosophy"
        },
        
        # Definitely False (0-19)
        {
            "statement": "Humans can breathe underwater without equipment",
            "expected_range": (0, 10),
            "category": "Physical Impossibility"
        },
        {
            "statement": "The Earth is flat",
            "expected_range": (0, 5),
            "category": "Scientific Falsehood"
        },
        {
            "statement": "Fish live on land",
            "expected_range": (0, 10),
            "category": "Biological Impossibility"
        }
    ]
    
    results = []
    total_time = 0
    
    print(f"{CYAN}Testing {len(test_cases)} common sense statements:{RESET}\n")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"{CYAN}Test {i}/{len(test_cases)}: {test_case['category']}{RESET}")
        print(f"  Statement: \"{test_case['statement']}\"")
        print(f"  Expected Range: {test_case['expected_range'][0]}-{test_case['expected_range'][1]}")
        
        start_time = time.time()
        score, reasoning = test_common_sense_judgment(
            session,
            test_case['statement'],
            test_case['expected_range']
        )
        elapsed = time.time() - start_time
        total_time += elapsed
        
        print(f"  Assigned Score: {score if score is not None else 'Failed to parse'}")
        
        # Check if score is in expected range
        success = False
        if score is not None:
            min_expected, max_expected = test_case['expected_range']
            success = min_expected <= score <= max_expected
        
        if success:
            print(f"  {GREEN}✅ IN RANGE{RESET}")
        else:
            print(f"  {RED}❌ OUT OF RANGE{RESET}")
        
        # Show reasoning (truncated)
        if reasoning:
            reasoning_short = reasoning[:100] + "..." if len(reasoning) > 100 else reasoning
            print(f"  Reasoning: {reasoning_short}")
        
        print(f"  Time: {elapsed:.2f}s\n")
        
        results.append({
            "statement": test_case['statement'],
            "category": test_case['category'],
            "expected_range": test_case['expected_range'],
            "actual_score": score,
            "success": success,
            "reasoning": reasoning,
            "time": elapsed
        })
    
    # Analysis
    print(f"{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}📊 Common Sense Evaluation Results{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    # Overall accuracy
    successful = sum(1 for r in results if r['success'] and r['actual_score'] is not None)
    total_valid = sum(1 for r in results if r['actual_score'] is not None)
    accuracy = (successful / total_valid * 100) if total_valid > 0 else 0
    
    print(f"Overall Accuracy: {successful}/{total_valid} ({accuracy:.1f}%)")
    print(f"Average Time: {total_time/len(results):.2f}s per test")
    print(f"Total Time: {total_time:.2f}s\n")
    
    # Category analysis
    categories = {}
    for r in results:
        cat = r['category']
        if cat not in categories:
            categories[cat] = {'total': 0, 'success': 0, 'scores': []}
        categories[cat]['total'] += 1
        if r['success'] and r['actual_score'] is not None:
            categories[cat]['success'] += 1
        if r['actual_score'] is not None:
            categories[cat]['scores'].append(r['actual_score'])
    
    print(f"{CYAN}Performance by Category:{RESET}")
    for cat, stats in categories.items():
        if stats['total'] > 0:
            cat_accuracy = (stats['success'] / stats['total']) * 100
            avg_score = sum(stats['scores']) / len(stats['scores']) if stats['scores'] else 0
            print(f"  {cat}: {stats['success']}/{stats['total']} ({cat_accuracy:.0f}%) - Avg Score: {avg_score:.1f}")
    
    # Score distribution analysis
    print(f"\n{CYAN}Score Distribution Analysis:{RESET}")
    score_ranges = {
        "Definitely True (90-100)": [r for r in results if r['actual_score'] and 90 <= r['actual_score'] <= 100],
        "Very Likely True (80-89)": [r for r in results if r['actual_score'] and 80 <= r['actual_score'] <= 89],
        "Probably True (60-79)": [r for r in results if r['actual_score'] and 60 <= r['actual_score'] <= 79],
        "Uncertain (40-59)": [r for r in results if r['actual_score'] and 40 <= r['actual_score'] <= 59],
        "Probably False (20-39)": [r for r in results if r['actual_score'] and 20 <= r['actual_score'] <= 39],
        "Very Likely False (1-19)": [r for r in results if r['actual_score'] and 1 <= r['actual_score'] <= 19],
        "Definitely False (0)": [r for r in results if r['actual_score'] == 0]
    }
    
    for range_name, items in score_ranges.items():
        if items:
            print(f"  {range_name}: {len(items)} statements")
            for item in items:
                print(f"    - \"{item['statement'][:50]}...\" (Score: {item['actual_score']})")
    
    # Failed cases
    failed_cases = [r for r in results if not r['success'] and r['actual_score'] is not None]
    if failed_cases:
        print(f"\n{RED}Cases Outside Expected Range:{RESET}")
        for case in failed_cases:
            expected_min, expected_max = case['expected_range']
            print(f"  \"{case['statement'][:60]}...\"")
            print(f"    Expected: {expected_min}-{expected_max}, Got: {case['actual_score']}")
    
    return results, accuracy


def compare_reasoning_levels_commonsense(model="gpt-5-mini"):
    """Compare common sense performance across reasoning levels"""
    
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}🔬 Reasoning Level Comparison for Common Sense{RESET}")
    print(f"{BLUE}Model: {model}{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    levels = ["low", "medium", "high"]
    comparison_results = {}
    
    for level in levels:
        print(f"\n{CYAN}━━━ Testing with reasoning={level} ━━━{RESET}")
        results, accuracy = run_common_sense_tests(model, level)
        comparison_results[level] = {
            "results": results,
            "accuracy": accuracy
        }
    
    # Comparison summary
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}📈 Reasoning Level Impact on Common Sense{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    print("Overall Accuracy by Reasoning Level:")
    for level in levels:
        acc = comparison_results[level]["accuracy"]
        print(f"  {level}: {acc:.1f}%")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test common sense judgment in NLM system")
    parser.add_argument("-m", "--model", default="gpt-5-mini",
                       help="Model to test")
    parser.add_argument("-r", "--reasoning", default="low",
                       choices=["low", "medium", "high"],
                       help="Reasoning effort level")
    parser.add_argument("--compare", action="store_true",
                       help="Compare across reasoning levels")
    
    args = parser.parse_args()
    
    if args.compare:
        compare_reasoning_levels_commonsense(args.model)
    else:
        run_common_sense_tests(args.model, args.reasoning)


if __name__ == "__main__":
    main()