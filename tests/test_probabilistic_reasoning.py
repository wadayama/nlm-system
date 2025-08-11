#!/usr/bin/env python3
"""Test probabilistic reasoning capabilities of NLM system

This test evaluates various forms of probabilistic and statistical reasoning including:
- Bayesian inference
- Conditional probability
- Independence and correlation
- Base rate fallacy avoidance
- Expected value calculations
- Statistical inference
"""

from nlm_interpreter import NLMSession
import time
import re

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
CYAN = '\033[96m'
BLUE = '\033[94m'
RESET = '\033[0m'


def extract_probability(text):
    """Extract probability percentage from text"""
    if not text:
        return None
    
    # Look for percentages
    percent_matches = re.findall(r'(\d+(?:\.\d+)?)%', text)
    if percent_matches:
        return float(percent_matches[-1])  # Take the last one (usually the final answer)
    
    # Look for decimal probabilities
    decimal_matches = re.findall(r'(?:probability|chance).*?(\d+(?:\.\d+)?)(?:\s|$)', text.lower())
    if decimal_matches:
        val = float(decimal_matches[-1])
        if val <= 1.0:  # Convert decimal to percentage
            return val * 100
        return val
    
    # Look for fractions
    fraction_matches = re.findall(r'(\d+)/(\d+)', text)
    if fraction_matches:
        num, den = fraction_matches[-1]
        return (float(num) / float(den)) * 100
    
    return None


def test_probabilistic_reasoning(session, problem_description, expected_probability, tolerance=5.0):
    """Test a single probabilistic reasoning problem"""
    
    # Clear previous state
    session.clear_local()
    
    # Save problem
    session.save("problem", problem_description)
    
    # Execute probabilistic reasoning
    result = session.execute(f"""
Solve this probability problem step-by-step:

{{{{problem}}}}

INSTRUCTIONS FOR PROBABILISTIC REASONING:

1. SYSTEMATIC APPROACH:
   - Identify what type of probability problem this is (Bayes' theorem, conditional probability, etc.)
   - Define the events and given information clearly
   - Apply appropriate probability formulas and principles
   - Show your calculations step by step

2. COMMON PROBABILITY PRINCIPLES TO CONSIDER:
   - Bayes' theorem: P(A|B) = P(B|A) × P(A) / P(B)
   - Conditional probability: P(A|B) = P(A∩B) / P(B)
   - Independence: P(A∩B) = P(A) × P(B) if independent
   - Law of total probability
   - Base rates and prior probabilities

3. AVOID COMMON ERRORS:
   - Base rate fallacy (ignoring prior probabilities)
   - Conjunction fallacy (assuming specific scenarios are more likely than general ones)
   - Representativeness heuristic (ignoring sample sizes)
   - Gambler's fallacy (assuming independence violations)

4. FINAL ANSWER FORMAT:
   - Provide your final probability as a percentage (e.g., 25.4%)
   - Explain your reasoning process
   - State your confidence level in the answer

Save your step-by-step reasoning to {{{{reasoning_process}}}}.
Save your final probability answer to {{{{final_probability}}}}.
Save your confidence level to {{{{confidence_level}}}}.
""")
    
    # Get results
    final_probability_text = session.get("final_probability")
    reasoning_process = session.get("reasoning_process")
    confidence_level = session.get("confidence_level")
    
    # Extract numerical probability
    final_probability = extract_probability(final_probability_text)
    
    return final_probability, reasoning_process, confidence_level


def run_probabilistic_reasoning_tests(model="gpt-5-mini", reasoning="low"):
    """Run probabilistic reasoning test suite"""
    
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}🎲 Probabilistic Reasoning Test Suite{RESET}")
    print(f"{BLUE}Model: {model}{RESET}")
    print(f"{BLUE}Reasoning: {reasoning}{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    # Initialize session
    session = NLMSession(
        namespace=f"prob_test_{model}",
        model=model,
        reasoning_effort=reasoning
    )
    
    # Test cases with different types of probabilistic reasoning
    test_cases = [
        # Bayesian Inference
        {
            "problem": """
A rare disease affects 1% of the population.
A test for this disease has the following accuracy:
- If someone has the disease, the test is positive 90% of the time (sensitivity = 90%)
- If someone does not have the disease, the test is negative 95% of the time (specificity = 95%)

A person tests positive. What is the probability that they actually have the disease?
""",
            "expected": 15.4,  # Bayes' theorem calculation
            "tolerance": 2.0,
            "type": "Bayesian Inference",
            "description": "Medical diagnosis with base rates"
        },
        
        # Conditional Probability
        {
            "problem": """
You have two boxes:
- Box A contains 2 red balls and 1 blue ball
- Box B contains 1 red ball and 2 blue balls

You randomly select a box and then randomly draw a ball from it. The ball is red.
What is the probability that it came from Box A?
""",
            "expected": 66.7,  # 2/3 ≈ 66.7%
            "tolerance": 3.0,
            "type": "Conditional Probability",
            "description": "Box and balls problem"
        },
        
        # Independence (Gambler's Fallacy)
        {
            "problem": """
You flip a fair coin 5 times and get heads every time: H-H-H-H-H.
What is the probability that the 6th flip will also be heads?
""",
            "expected": 50.0,
            "tolerance": 1.0,
            "type": "Independence",
            "description": "Coin flip independence"
        },
        
        # Sample Size and Law of Large Numbers
        {
            "problem": """
Two surveys about voting preference:
- Survey A: 60 out of 100 people support candidate X (60%)
- Survey B: 7 out of 10 people support candidate X (70%)

Which survey result is more reliable for estimating the true population preference?
Give the probability that Survey A's result is closer to the true population percentage.
""",
            "expected": 85.0,  # Higher sample size is more reliable
            "tolerance": 10.0,
            "type": "Sample Size Reliability",
            "description": "Large vs small sample comparison"
        },
        
        # Base Rate Neglect (Taxi Problem)
        {
            "problem": """
In a city, 85% of taxis are blue and 15% are green.
A witness saw a taxi involved in an accident at night.
The witness identified the taxi as green.
Under similar conditions, witnesses correctly identify taxi colors 80% of the time.

What is the probability that the taxi was actually green?
""",
            "expected": 41.4,  # Bayes with base rates
            "tolerance": 5.0,
            "type": "Base Rate Problem",
            "description": "Taxi color identification with base rates"
        },
        
        # Expected Value
        {
            "problem": """
A lottery ticket costs $2.
There is a 1 in 1,000,000 chance of winning $500,000.
There is a 1 in 10,000 chance of winning $100.
All other tickets win nothing.

What is the expected value of buying this ticket?
Express as a percentage of the ticket price (negative means loss).
""",
            "expected": -25.0,  # Expected value is $0.50 vs $2 cost = -75% return, but we want percentage
            "tolerance": 10.0,
            "type": "Expected Value",
            "description": "Lottery expected value calculation"
        },
        
        # Conjunction Fallacy
        {
            "problem": """
Linda is 31 years old, single, outspoken, and very bright. She majored in philosophy.
As a student, she was deeply concerned with issues of discrimination and social justice,
and also participated in anti-nuclear demonstrations.

Which is more probable?
A) Linda is a bank teller
B) Linda is a bank teller AND is active in the feminist movement

What is the probability that option A is more likely than option B?
""",
            "expected": 100.0,  # A must be more probable than A∩B
            "tolerance": 5.0,
            "type": "Conjunction Fallacy",
            "description": "Linda the bank teller problem"
        },
        
        # Monty Hall Problem
        {
            "problem": """
You're on a game show with 3 doors. Behind one door is a car, behind the others are goats.
You pick door #1. The host, who knows what's behind each door, opens door #3 to reveal a goat.
The host then asks if you want to switch to door #2 or stay with door #1.

What is the probability that you'll win the car if you switch to door #2?
""",
            "expected": 66.7,  # 2/3
            "tolerance": 5.0,
            "type": "Monty Hall Problem",
            "description": "Classic probability puzzle"
        },
        
        # Statistical Significance
        {
            "problem": """
A coin is flipped 100 times and comes up heads 60 times.
Assuming the null hypothesis that the coin is fair (50% heads probability),
what is the approximate probability of getting 60 or more heads by chance?

Use the normal approximation: for n=100, standard deviation ≈ 5.
""",
            "expected": 2.3,  # P(Z ≥ 2) ≈ 2.3%
            "tolerance": 2.0,
            "type": "Statistical Significance",
            "description": "Hypothesis testing with normal approximation"
        },
        
        # Birthday Paradox
        {
            "problem": """
In a room with 23 people, what is the probability that at least two people share the same birthday?
(Assume 365 days in a year and ignore leap years)
""",
            "expected": 50.7,  # Famous birthday paradox result
            "tolerance": 5.0,
            "type": "Birthday Paradox",
            "description": "Counter-intuitive probability"
        }
    ]
    
    results = []
    total_time = 0
    
    print(f"{CYAN}Testing {len(test_cases)} probabilistic reasoning problems:{RESET}\n")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"{CYAN}Test {i}/{len(test_cases)}: {test_case['type']}{RESET}")
        print(f"  Description: {test_case['description']}")
        print(f"  Problem: {test_case['problem'][:100].replace(chr(10), ' ')}...")
        print(f"  Expected: {test_case['expected']:.1f}% (±{test_case['tolerance']:.1f}%)")
        
        start_time = time.time()
        probability, reasoning_process, confidence = test_probabilistic_reasoning(
            session,
            test_case['problem'],
            test_case['expected'],
            test_case['tolerance']
        )
        elapsed = time.time() - start_time
        total_time += elapsed
        
        print(f"  Got: {probability:.1f}%" if probability is not None else "  Got: Could not extract probability")
        
        # Check correctness
        success = False
        if probability is not None:
            error = abs(probability - test_case['expected'])
            success = error <= test_case['tolerance']
            print(f"  Error: {error:.1f}% (tolerance: {test_case['tolerance']:.1f}%)")
        
        if success:
            print(f"  {GREEN}✅ CORRECT{RESET}")
        else:
            print(f"  {RED}❌ INCORRECT{RESET}")
        
        # Show reasoning (truncated)
        if reasoning_process:
            reasoning_short = reasoning_process[:100] + "..." if len(reasoning_process) > 100 else reasoning_process
            print(f"  Reasoning: {reasoning_short}")
        
        # Show confidence
        if confidence:
            confidence_short = confidence[:50] + "..." if len(confidence) > 50 else confidence
            print(f"  Confidence: {confidence_short}")
        
        print(f"  Time: {elapsed:.2f}s\n")
        
        results.append({
            "type": test_case['type'],
            "description": test_case['description'],
            "expected": test_case['expected'],
            "actual": probability,
            "error": abs(probability - test_case['expected']) if probability is not None else float('inf'),
            "tolerance": test_case['tolerance'],
            "success": success,
            "reasoning": reasoning_process,
            "confidence": confidence,
            "time": elapsed
        })
    
    # Analysis
    print(f"{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}📊 Probabilistic Reasoning Results{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    # Overall accuracy
    successful = sum(1 for r in results if r['success'])
    total = len(results)
    accuracy = (successful / total * 100) if total > 0 else 0
    
    print(f"Overall Accuracy: {successful}/{total} ({accuracy:.1f}%)")
    print(f"Average Time: {total_time/len(results):.2f}s per test")
    print(f"Total Time: {total_time:.2f}s\n")
    
    # Error analysis
    valid_results = [r for r in results if r['actual'] is not None]
    if valid_results:
        avg_error = sum(r['error'] for r in valid_results) / len(valid_results)
        median_error = sorted([r['error'] for r in valid_results])[len(valid_results)//2]
        print(f"Average Error: {avg_error:.2f}%")
        print(f"Median Error: {median_error:.2f}%\n")
    
    # Category analysis
    reasoning_types = {}
    for r in results:
        rtype = r['type']
        if rtype not in reasoning_types:
            reasoning_types[rtype] = {'total': 0, 'success': 0, 'errors': []}
        reasoning_types[rtype]['total'] += 1
        if r['success']:
            reasoning_types[rtype]['success'] += 1
        if r['actual'] is not None:
            reasoning_types[rtype]['errors'].append(r['error'])
    
    print(f"{CYAN}Performance by Problem Type:{RESET}")
    for rtype, stats in reasoning_types.items():
        if stats['total'] > 0:
            type_accuracy = (stats['success'] / stats['total']) * 100
            avg_error = sum(stats['errors']) / len(stats['errors']) if stats['errors'] else float('inf')
            print(f"  {rtype}: {stats['success']}/{stats['total']} ({type_accuracy:.0f}%) - Avg Error: {avg_error:.1f}%")
    
    # Failed cases
    failed_cases = [r for r in results if not r['success']]
    if failed_cases:
        print(f"\n{RED}Failed Cases:{RESET}")
        for case in failed_cases:
            print(f"  {case['type']}: Expected {case['expected']:.1f}%, Got {case['actual']:.1f}% (Error: {case['error']:.1f}%)")
    
    # Best performing cases
    successful_cases = [r for r in results if r['success']]
    if successful_cases:
        successful_cases.sort(key=lambda x: x['error'])
        print(f"\n{GREEN}Most Accurate Cases:{RESET}")
        for case in successful_cases[:3]:
            print(f"  {case['type']}: Expected {case['expected']:.1f}%, Got {case['actual']:.1f}% (Error: {case['error']:.1f}%)")
    
    return results, accuracy


def compare_reasoning_levels_probability(model="gpt-5-mini"):
    """Compare probabilistic reasoning across reasoning levels"""
    
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}🔬 Reasoning Level Comparison for Probability{RESET}")
    print(f"{BLUE}Model: {model}{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    levels = ["low", "medium", "high"]
    comparison_results = {}
    
    for level in levels:
        print(f"\n{CYAN}━━━ Testing with reasoning={level} ━━━{RESET}")
        results, accuracy = run_probabilistic_reasoning_tests(model, level)
        comparison_results[level] = {
            "results": results,
            "accuracy": accuracy
        }
    
    # Comparison summary
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}📈 Reasoning Level Impact on Probability{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    print("Overall Accuracy by Reasoning Level:")
    for level in levels:
        acc = comparison_results[level]["accuracy"]
        print(f"  {level}: {acc:.1f}%")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test probabilistic reasoning in NLM system")
    parser.add_argument("-m", "--model", default="gpt-5-mini",
                       help="Model to test")
    parser.add_argument("-r", "--reasoning", default="low",
                       choices=["low", "medium", "high"],
                       help="Reasoning effort level")
    parser.add_argument("--compare", action="store_true",
                       help="Compare across reasoning levels")
    
    args = parser.parse_args()
    
    if args.compare:
        compare_reasoning_levels_probability(args.model)
    else:
        run_probabilistic_reasoning_tests(args.model, args.reasoning)


if __name__ == "__main__":
    main()