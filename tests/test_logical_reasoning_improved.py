#!/usr/bin/env python3
"""Test logical reasoning capabilities with improved prompting

This version emphasizes intellectual honesty and appropriate uncertainty expression
to improve handling of indeterminate cases.
"""

from nlm_interpreter import NLMSession
import time

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
CYAN = '\033[96m'
BLUE = '\033[94m'
RESET = '\033[0m'


def test_logical_reasoning_improved(session, premises, question, expected_answer, reasoning_type):
    """Test a single logical reasoning problem with improved prompting"""
    
    # Clear previous state
    session.clear_local()
    
    # Save premises and question
    session.save("premises", premises)
    session.save("question", question)
    
    # Execute logical reasoning with improved prompt
    result = session.execute(f"""
Given the following premises:
{{{{premises}}}}

Answer this question: {{{{question}}}}

CRITICAL INSTRUCTIONS FOR LOGICAL REASONING:

1. INTELLECTUAL HONESTY FIRST:
   - If the premises provide insufficient information to reach a definitive conclusion, respond with "Cannot be determined"
   - If you are not confident in your reasoning, explicitly state your uncertainty
   - Do NOT guess or use external knowledge to fill logical gaps
   - It is better to admit uncertainty than to provide a potentially incorrect definitive answer

2. REASONING PROCESS:
   - Identify the logical structure of the premises
   - Apply only valid logical rules (modus ponens, modus tollens, etc.)
   - Check if the premises provide sufficient information for the conclusion
   - Assess your confidence level in the reasoning

3. AVOID COMMON ERRORS:
   - Do not commit logical fallacies (affirming the consequent, etc.)
   - Do not use real-world knowledge that is not stated in the premises
   - Do not assume information that is not explicitly given

4. CONFIDENCE ASSESSMENT:
   - High confidence (clear logical path from premises) → True/False
   - Medium confidence (some logical gaps or assumptions) → mention uncertainty
   - Low confidence (insufficient information) → "Cannot be determined"

Provide:
- Your step-by-step logical reasoning process
- Your confidence assessment
- Your final answer: (True/False/Cannot be determined/Invalid)

Save your reasoning process to {{{{reasoning_process}}}}.
Save your confidence level to {{{{confidence_level}}}}.
Save your final answer to {{{{final_answer}}}}.
""")
    
    # Get results
    final_answer = session.get("final_answer")
    reasoning_process = session.get("reasoning_process")
    confidence_level = session.get("confidence_level")
    
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
    
    return final_answer, reasoning_process, confidence_level


def run_logical_reasoning_tests_improved(model="gpt-5-mini", reasoning="low"):
    """Run improved logical reasoning test suite"""
    
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}🧮 Improved Logical Reasoning Test Suite{RESET}")
    print(f"{BLUE}Model: {model}{RESET}")
    print(f"{BLUE}Reasoning: {reasoning}{RESET}")
    print(f"{BLUE}Focus: Intellectual honesty & uncertainty handling{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    # Initialize session
    session = NLMSession(
        namespace=f"logic_improved_test_{model}",
        model=model,
        reasoning_effort=reasoning
    )
    
    # Focus on the previously failed cases plus some controls
    test_cases = [
        # Previously failed cases - main focus
        {
            "premises": "Some birds can fly.\nPenguins are birds.",
            "question": "Can penguins fly?",
            "expected": "cannot be determined",
            "type": "Partial Syllogism",
            "description": "Some-quantifier limitation (PREVIOUSLY FAILED)",
            "priority": "HIGH"
        },
        {
            "premises": "If it rains, then the ground gets wet.\nThe ground is wet.",
            "question": "Is it raining?",
            "expected": "cannot be determined",
            "type": "Affirming Consequent",
            "description": "Logical fallacy - should not conclude (PREVIOUSLY FAILED)",
            "priority": "HIGH"
        },
        {
            "premises": "All squares are rectangles.\nSome rectangles are squares.\nX is a rectangle.",
            "question": "Is X a square?",
            "expected": "cannot be determined",
            "type": "Quantifier Reasoning",
            "description": "Universal vs existential quantifiers (PREVIOUSLY FAILED)",
            "priority": "HIGH"
        },
        {
            "premises": "Either you are with us or against us.\nJohn is not actively supporting us.",
            "question": "Is John against us?",
            "expected": "cannot be determined",
            "type": "False Dilemma",
            "description": "Recognizing oversimplified either-or (PREVIOUSLY FAILED)",
            "priority": "HIGH"
        },
        
        # Control cases - should still work correctly
        {
            "premises": "All humans are mortal.\nSocrates is a human.",
            "question": "Is Socrates mortal?",
            "expected": "true",
            "type": "Classical Syllogism",
            "description": "Basic universal syllogism (CONTROL)",
            "priority": "CONTROL"
        },
        {
            "premises": "If it rains, then the ground gets wet.\nIt is raining.",
            "question": "Is the ground wet?",
            "expected": "true",
            "type": "Modus Ponens",
            "description": "If P then Q, P, therefore Q (CONTROL)",
            "priority": "CONTROL"
        },
        {
            "premises": "If it rains, then the ground gets wet.\nThe ground is not wet.",
            "question": "Is it raining?",
            "expected": "false",
            "type": "Modus Tollens",
            "description": "If P then Q, not Q, therefore not P (CONTROL)",
            "priority": "CONTROL"
        },
        
        # Additional challenging cases
        {
            "premises": "Some cats are black.\nMittens is a cat.",
            "question": "Is Mittens black?",
            "expected": "cannot be determined",
            "type": "Existential Limitation",
            "description": "Some-quantifier with specific individual",
            "priority": "MEDIUM"
        },
        {
            "premises": "If John studies, he will pass.\nJohn passed.",
            "question": "Did John study?",
            "expected": "cannot be determined",
            "type": "Affirming Consequent Variant",
            "description": "Another affirming consequent case",
            "priority": "MEDIUM"
        },
        {
            "premises": "All A are B.\nC is not B.",
            "question": "Is C an A?",
            "expected": "false",
            "type": "Contrapositive",
            "description": "Valid contrapositive reasoning",
            "priority": "MEDIUM"
        }
    ]
    
    results = []
    total_time = 0
    
    print(f"{CYAN}Testing {len(test_cases)} logical reasoning problems:{RESET}")
    print(f"{CYAN}Focus on previously failed 'Cannot be determined' cases{RESET}\n")
    
    for i, test_case in enumerate(test_cases, 1):
        priority_marker = {
            "HIGH": "🔥",
            "CONTROL": "✅", 
            "MEDIUM": "🔸"
        }.get(test_case.get("priority", ""), "")
        
        print(f"{CYAN}Test {i}/{len(test_cases)}: {priority_marker} {test_case['type']}{RESET}")
        print(f"  Description: {test_case['description']}")
        print(f"  Priority: {test_case.get('priority', 'STANDARD')}")
        print(f"  Premises: {test_case['premises'][:80]}...")
        print(f"  Question: {test_case['question']}")
        print(f"  Expected: {test_case['expected']}")
        
        start_time = time.time()
        answer, reasoning_process, confidence_level = test_logical_reasoning_improved(
            session,
            test_case['premises'],
            test_case['question'],
            test_case['expected'],
            test_case['type']
        )
        elapsed = time.time() - start_time
        total_time += elapsed
        
        print(f"  Got: {answer if answer else 'No answer'}")
        print(f"  Confidence: {confidence_level if confidence_level else 'Not specified'}")
        
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
            reasoning_short = reasoning_process[:120] + "..." if len(reasoning_process) > 120 else reasoning_process
            print(f"  Reasoning: {reasoning_short}")
        
        print(f"  Time: {elapsed:.2f}s\n")
        
        results.append({
            "type": test_case['type'],
            "description": test_case['description'],
            "priority": test_case.get('priority', 'STANDARD'),
            "premises": test_case['premises'],
            "question": test_case['question'],
            "expected": test_case['expected'],
            "actual": answer,
            "confidence": confidence_level,
            "success": success,
            "reasoning": reasoning_process,
            "time": elapsed
        })
    
    # Analysis
    print(f"{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}📊 Improved Logical Reasoning Results{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    # Overall accuracy
    successful = sum(1 for r in results if r['success'])
    total = len(results)
    accuracy = (successful / total * 100) if total > 0 else 0
    
    print(f"Overall Accuracy: {successful}/{total} ({accuracy:.1f}%)")
    print(f"Average Time: {total_time/len(results):.2f}s per test")
    print(f"Total Time: {total_time:.2f}s\n")
    
    # Priority-based analysis
    priority_stats = {}
    for r in results:
        priority = r['priority']
        if priority not in priority_stats:
            priority_stats[priority] = {'total': 0, 'success': 0, 'cases': []}
        priority_stats[priority]['total'] += 1
        priority_stats[priority]['cases'].append(r)
        if r['success']:
            priority_stats[priority]['success'] += 1
    
    print(f"{CYAN}Performance by Priority:{RESET}")
    for priority in ['HIGH', 'CONTROL', 'MEDIUM', 'STANDARD']:
        if priority in priority_stats:
            stats = priority_stats[priority]
            priority_accuracy = (stats['success'] / stats['total']) * 100 if stats['total'] > 0 else 0
            print(f"  {priority}: {stats['success']}/{stats['total']} ({priority_accuracy:.1f}%)")
    
    # Detailed analysis of HIGH priority cases (previously failed)
    high_priority_cases = [r for r in results if r['priority'] == 'HIGH']
    if high_priority_cases:
        print(f"\n{CYAN}🔥 HIGH PRIORITY Cases (Previously Failed):{RESET}")
        improvement_count = sum(1 for r in high_priority_cases if r['success'])
        print(f"Improvement: {improvement_count}/{len(high_priority_cases)} ({(improvement_count/len(high_priority_cases)*100):.1f}%)")
        
        for case in high_priority_cases:
            status = "✅ FIXED" if case['success'] else "❌ STILL FAILING"
            print(f"  {status}: {case['type']}")
            print(f"    Expected: {case['expected']} | Got: {case['actual']}")
            if case['confidence']:
                print(f"    Confidence: {case['confidence'][:50]}...")
    
    # Control cases verification
    control_cases = [r for r in results if r['priority'] == 'CONTROL']
    if control_cases:
        control_success = sum(1 for r in control_cases if r['success'])
        print(f"\n{CYAN}✅ CONTROL Cases (Should still work):{RESET}")
        print(f"Maintained accuracy: {control_success}/{len(control_cases)} ({(control_success/len(control_cases)*100):.1f}%)")
    
    # Failed cases
    failed_cases = [r for r in results if not r['success']]
    if failed_cases:
        print(f"\n{RED}Remaining Failed Cases:{RESET}")
        for case in failed_cases:
            print(f"  {case['type']}: {case['description'][:60]}...")
            print(f"    Expected: {case['expected']} | Got: {case['actual']}")
    
    return results, accuracy, priority_stats


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test improved logical reasoning with uncertainty handling")
    parser.add_argument("-m", "--model", default="gpt-5-mini",
                       help="Model to test")
    parser.add_argument("-r", "--reasoning", default="low",
                       choices=["low", "medium", "high"],
                       help="Reasoning effort level")
    
    args = parser.parse_args()
    
    run_logical_reasoning_tests_improved(args.model, args.reasoning)


if __name__ == "__main__":
    main()