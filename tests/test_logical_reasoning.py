#!/usr/bin/env python3
"""Test logical reasoning capabilities of NLM system

This test evaluates various forms of logical reasoning including:
- Syllogistic reasoning (三段論法)
- Deductive reasoning
- Inductive reasoning
- Conditional reasoning (if-then)
- Causal reasoning
"""

from nlm_interpreter import NLMSession
import time

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
CYAN = '\033[96m'
BLUE = '\033[94m'
RESET = '\033[0m'


def test_logical_reasoning(session, premises, question, expected_answer, reasoning_type):
    """Test a single logical reasoning problem"""
    
    # Clear previous state
    session.clear_local()
    
    # Save premises and question
    session.save("premises", premises)
    session.save("question", question)
    
    # Execute logical reasoning
    result = session.execute(f"""
Given the following premises:
{{{{premises}}}}

Answer this question: {{{{question}}}}

Perform step-by-step logical reasoning:
1. Identify the logical structure
2. Apply appropriate reasoning rules
3. Derive the conclusion

Provide:
- Your logical reasoning process
- Your final answer (True/False/Cannot be determined/Invalid)

Save your reasoning process to {{{{reasoning_process}}}}.
Save your final answer to {{{{final_answer}}}}.
""")
    
    # Get results
    final_answer = session.get("final_answer")
    reasoning_process = session.get("reasoning_process")
    
    # Clean up the answer
    if final_answer:
        final_answer = final_answer.strip().lower()
        # Normalize various forms of answers
        if "true" in final_answer or "yes" in final_answer or "valid" in final_answer:
            final_answer = "true"
        elif "false" in final_answer or "no" in final_answer or "invalid" in final_answer:
            final_answer = "false"
        elif "cannot" in final_answer or "indeterminate" in final_answer or "unknown" in final_answer:
            final_answer = "cannot be determined"
    
    return final_answer, reasoning_process


def run_logical_reasoning_tests(model="gpt-5-mini", reasoning="low"):
    """Run logical reasoning test suite"""
    
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}🧮 Logical Reasoning Test Suite{RESET}")
    print(f"{BLUE}Model: {model}{RESET}")
    print(f"{BLUE}Reasoning: {reasoning}{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    # Initialize session
    session = NLMSession(
        namespace=f"logic_test_{model}",
        model=model,
        reasoning_effort=reasoning
    )
    
    # Test cases with different types of logical reasoning
    test_cases = [
        # Classical Syllogisms (三段論法)
        {
            "premises": "All humans are mortal.\nSocrates is a human.",
            "question": "Is Socrates mortal?",
            "expected": "true",
            "type": "Classical Syllogism",
            "description": "Basic universal syllogism"
        },
        {
            "premises": "No cats are dogs.\nFluffy is a cat.",
            "question": "Is Fluffy a dog?",
            "expected": "false",
            "type": "Negative Syllogism",
            "description": "Universal negative syllogism"
        },
        {
            "premises": "Some birds can fly.\nPenguins are birds.",
            "question": "Can penguins fly?",
            "expected": "cannot be determined",
            "type": "Partial Syllogism",
            "description": "Some-quantifier limitation"
        },
        
        # Conditional Reasoning
        {
            "premises": "If it rains, then the ground gets wet.\nIt is raining.",
            "question": "Is the ground wet?",
            "expected": "true",
            "type": "Modus Ponens",
            "description": "If P then Q, P, therefore Q"
        },
        {
            "premises": "If it rains, then the ground gets wet.\nThe ground is not wet.",
            "question": "Is it raining?",
            "expected": "false",
            "type": "Modus Tollens",
            "description": "If P then Q, not Q, therefore not P"
        },
        {
            "premises": "If it rains, then the ground gets wet.\nThe ground is wet.",
            "question": "Is it raining?",
            "expected": "cannot be determined",
            "type": "Affirming Consequent",
            "description": "Logical fallacy - should not conclude"
        },
        
        # Disjunctive Reasoning
        {
            "premises": "Either Alice or Bob will attend the meeting.\nAlice will not attend the meeting.",
            "question": "Will Bob attend the meeting?",
            "expected": "true",
            "type": "Disjunctive Syllogism",
            "description": "Either A or B, not A, therefore B"
        },
        
        # Chain Reasoning
        {
            "premises": "If A then B.\nIf B then C.\nA is true.",
            "question": "Is C true?",
            "expected": "true",
            "type": "Hypothetical Syllogism",
            "description": "Chained conditional reasoning"
        },
        
        # Mathematical Logic
        {
            "premises": "All prime numbers greater than 2 are odd.\n17 is a prime number greater than 2.",
            "question": "Is 17 odd?",
            "expected": "true",
            "type": "Mathematical Syllogism",
            "description": "Mathematical property reasoning"
        },
        
        # Set Logic
        {
            "premises": "All members of set A are in set B.\nAll members of set B are in set C.\nX is in set A.",
            "question": "Is X in set C?",
            "expected": "true",
            "type": "Transitive Reasoning",
            "description": "Set inclusion transitivity"
        },
        
        # Complex Reasoning
        {
            "premises": "If someone studies hard, they will pass the exam.\nIf someone passes the exam, they will graduate.\nMary studies hard.",
            "question": "Will Mary graduate?",
            "expected": "true",
            "type": "Multi-step Conditional",
            "description": "Multiple conditional steps"
        },
        
        # Quantifier Logic
        {
            "premises": "All squares are rectangles.\nSome rectangles are squares.\nX is a rectangle.",
            "question": "Is X a square?",
            "expected": "cannot be determined",
            "type": "Quantifier Reasoning",
            "description": "Universal vs existential quantifiers"
        },
        
        # Contradiction Detection
        {
            "premises": "All birds can fly.\nPenguins are birds.\nPenguins cannot fly.",
            "question": "Are these premises consistent?",
            "expected": "false",
            "type": "Consistency Check",
            "description": "Detecting logical contradictions"
        },
        
        # Biconditional Reasoning
        {
            "premises": "A number is even if and only if it is divisible by 2.\n8 is divisible by 2.",
            "question": "Is 8 even?",
            "expected": "true",
            "type": "Biconditional",
            "description": "If and only if reasoning"
        },
        
        # False Dilemma
        {
            "premises": "Either you are with us or against us.\nJohn is not actively supporting us.",
            "question": "Is John against us?",
            "expected": "cannot be determined",
            "type": "False Dilemma",
            "description": "Recognizing oversimplified either-or"
        }
    ]
    
    results = []
    total_time = 0
    
    print(f"{CYAN}Testing {len(test_cases)} logical reasoning problems:{RESET}\n")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"{CYAN}Test {i}/{len(test_cases)}: {test_case['type']}{RESET}")
        print(f"  Description: {test_case['description']}")
        print(f"  Premises: {test_case['premises'][:100]}...")
        print(f"  Question: {test_case['question']}")
        print(f"  Expected: {test_case['expected']}")
        
        start_time = time.time()
        answer, reasoning_process = test_logical_reasoning(
            session,
            test_case['premises'],
            test_case['question'],
            test_case['expected'],
            test_case['type']
        )
        elapsed = time.time() - start_time
        total_time += elapsed
        
        print(f"  Got: {answer if answer else 'No answer'}")
        
        # Check correctness
        success = False
        if answer and test_case['expected']:
            success = answer.lower() == test_case['expected'].lower()
        
        if success:
            print(f"  {GREEN}✅ CORRECT{RESET}")
        else:
            print(f"  {RED}❌ INCORRECT{RESET}")
        
        # Show reasoning (truncated)
        if reasoning_process:
            reasoning_short = reasoning_process[:150] + "..." if len(reasoning_process) > 150 else reasoning_process
            print(f"  Reasoning: {reasoning_short}")
        
        print(f"  Time: {elapsed:.2f}s\n")
        
        results.append({
            "type": test_case['type'],
            "description": test_case['description'],
            "premises": test_case['premises'],
            "question": test_case['question'],
            "expected": test_case['expected'],
            "actual": answer,
            "success": success,
            "reasoning": reasoning_process,
            "time": elapsed
        })
    
    # Analysis
    print(f"{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}📊 Logical Reasoning Results{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    # Overall accuracy
    successful = sum(1 for r in results if r['success'])
    total = len(results)
    accuracy = (successful / total * 100) if total > 0 else 0
    
    print(f"Overall Accuracy: {successful}/{total} ({accuracy:.1f}%)")
    print(f"Average Time: {total_time/len(results):.2f}s per test")
    print(f"Total Time: {total_time:.2f}s\n")
    
    # Category analysis
    reasoning_types = {}
    for r in results:
        rtype = r['type']
        if rtype not in reasoning_types:
            reasoning_types[rtype] = {'total': 0, 'success': 0}
        reasoning_types[rtype]['total'] += 1
        if r['success']:
            reasoning_types[rtype]['success'] += 1
    
    print(f"{CYAN}Performance by Reasoning Type:{RESET}")
    for rtype, stats in reasoning_types.items():
        if stats['total'] > 0:
            type_accuracy = (stats['success'] / stats['total']) * 100
            print(f"  {rtype}: {stats['success']}/{stats['total']} ({type_accuracy:.0f}%)")
    
    # Error analysis
    failed_cases = [r for r in results if not r['success']]
    if failed_cases:
        print(f"\n{RED}Failed Cases:{RESET}")
        for case in failed_cases:
            print(f"  {case['type']}: {case['description']}")
            print(f"    Expected: {case['expected']} | Got: {case['actual']}")
            print(f"    Question: {case['question']}")
    
    # Success patterns
    successful_types = [r['type'] for r in results if r['success']]
    if successful_types:
        from collections import Counter
        success_counts = Counter(successful_types)
        print(f"\n{GREEN}Strong Reasoning Areas:{RESET}")
        for rtype, count in success_counts.most_common():
            total_of_type = reasoning_types[rtype]['total']
            print(f"  {rtype}: {count}/{total_of_type}")
    
    return results, accuracy


def compare_reasoning_levels_logic(model="gpt-5-mini"):
    """Compare logical reasoning across reasoning levels"""
    
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}🔬 Reasoning Level Comparison for Logic{RESET}")
    print(f"{BLUE}Model: {model}{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    levels = ["low", "medium", "high"]
    comparison_results = {}
    
    for level in levels:
        print(f"\n{CYAN}━━━ Testing with reasoning={level} ━━━{RESET}")
        results, accuracy = run_logical_reasoning_tests(model, level)
        comparison_results[level] = {
            "results": results,
            "accuracy": accuracy
        }
    
    # Comparison summary
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}📈 Reasoning Level Impact on Logic{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    print("Overall Accuracy by Reasoning Level:")
    for level in levels:
        acc = comparison_results[level]["accuracy"]
        print(f"  {level}: {acc:.1f}%")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test logical reasoning in NLM system")
    parser.add_argument("-m", "--model", default="gpt-5-mini",
                       help="Model to test")
    parser.add_argument("-r", "--reasoning", default="low",
                       choices=["low", "medium", "high"],
                       help="Reasoning effort level")
    parser.add_argument("--compare", action="store_true",
                       help="Compare across reasoning levels")
    
    args = parser.parse_args()
    
    if args.compare:
        compare_reasoning_levels_logic(args.model)
    else:
        run_logical_reasoning_tests(args.model, args.reasoning)


if __name__ == "__main__":
    main()