#!/usr/bin/env python3
"""Test causal reasoning capabilities of NLM system

This test evaluates the system's ability to:
- Identify potential causes from observed effects
- Reason about causal chains and indirect causes  
- Distinguish between correlation and causation
- Handle multiple competing causal explanations
- Estimate likelihood of different causal scenarios
- Reason about interventions and counterfactuals

This is crucial for agent decision-making where understanding
cause-and-effect relationships is essential for effective action.
"""

from nlm_interpreter import NLMSession
import time
import json

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
CYAN = '\033[96m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
RESET = '\033[0m'


def evaluate_causal_analysis(identified_causes, expected_causes, reasoning_quality):
    """Evaluate the quality of causal reasoning"""
    score = 0
    max_score = 100
    feedback = []
    
    if not identified_causes:
        return 0, ["No causes identified"]
    
    # Check coverage of expected causes (50 points)
    expected_set = set(cause.lower().strip() for cause in expected_causes)
    identified_set = set(cause.lower().strip() for cause in identified_causes)
    
    # Count how many expected causes were identified (exact or partial match)
    matches = 0
    for expected in expected_set:
        for identified in identified_set:
            if expected in identified or identified in expected:
                matches += 1
                break
    
    coverage_score = (matches / len(expected_causes)) * 50
    score += coverage_score
    feedback.append(f"Identified {matches}/{len(expected_causes)} expected causes")
    
    # Check for reasonable additional causes (bonus, up to 10 points)
    additional_causes = len(identified_causes) - matches
    if additional_causes > 0:
        bonus = min(additional_causes * 2, 10)
        score += bonus
        feedback.append(f"Identified {additional_causes} additional plausible causes")
    
    # Evaluate reasoning quality (40 points)
    reasoning_score = 40
    if not reasoning_quality:
        reasoning_score = 20
        feedback.append("No reasoning provided")
    else:
        # Check for causal thinking indicators
        causal_indicators = ["because", "due to", "caused by", "results from", "leads to", 
                           "consequence of", "triggered by", "stems from", "originates"]
        has_causal_language = any(indicator in reasoning_quality.lower() for indicator in causal_indicators)
        
        if not has_causal_language:
            reasoning_score -= 10
            feedback.append("Lacks clear causal reasoning language")
        
        # Check for consideration of multiple causes
        if "multiple" in reasoning_quality.lower() or "several" in reasoning_quality.lower():
            reasoning_score += 5
            feedback.append("Considered multiple causal factors")
        
        # Check for likelihood assessment
        likelihood_words = ["likely", "probable", "possible", "unlikely", "certain", "percent", "%"]
        if any(word in reasoning_quality.lower() for word in likelihood_words):
            reasoning_score += 5
            feedback.append("Included likelihood assessment")
    
    score += reasoning_score
    
    # Penalize if too few causes (less than 2)
    if len(identified_causes) < 2:
        score -= 10
        feedback.append("Insufficient causal exploration (less than 2 causes)")
    
    # Penalize if too many causes (more than 8 - shows lack of focus)
    if len(identified_causes) > 8:
        score -= 5
        feedback.append("Too many causes listed (lacks focus)")
    
    return min(score, max_score), feedback


def test_causal_reasoning_problem(session, observation, expected_causes, context, problem_type):
    """Test a single causal reasoning problem"""
    
    # Clear previous state
    session.clear_local()
    
    # Save observation and context
    session.save("observation", observation)
    session.save("context", context)
    
    # Execute causal reasoning
    result = session.execute(f"""
You observe: {{{{observation}}}}

Context: {{{{context}}}}

INSTRUCTIONS FOR CAUSAL REASONING:

1. CAUSAL IDENTIFICATION:
   - List all plausible causes that could lead to this observation
   - Consider both direct and indirect causes
   - Think about immediate triggers and underlying conditions
   - Include both common and less obvious potential causes

2. CAUSAL REASONING PROCESS:
   - For each cause, explain WHY it would lead to the observed effect
   - Consider causal chains (A causes B which causes C)
   - Think about necessary vs. sufficient conditions
   - Consider multiple causes working together

3. LIKELIHOOD ASSESSMENT:
   - Estimate the probability or likelihood of each cause
   - Consider available evidence and context
   - Note which causes are more or less likely given the situation
   - Identify what additional information would help determine the true cause

4. CAUSAL DISTINCTION:
   - Distinguish between correlation and actual causation
   - Consider alternative explanations
   - Think about what could rule out certain causes
   - Consider confounding factors

5. OUTPUT FORMAT:
   - List potential causes clearly
   - Provide reasoning for each cause
   - Include likelihood estimates where appropriate
   - Note any assumptions made

Save your list of potential causes to {{{{potential_causes}}}}.
Save your detailed causal reasoning to {{{{causal_reasoning}}}}.
Save likelihood assessments to {{{{likelihood_assessment}}}}.
""")
    
    # Get results
    potential_causes_raw = session.get("potential_causes")
    causal_reasoning = session.get("causal_reasoning")
    likelihood_assessment = session.get("likelihood_assessment")
    
    # Parse potential causes
    potential_causes = []
    if potential_causes_raw:
        # Try to extract causes from various formats
        lines = potential_causes_raw.split('\n')
        for line in lines:
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-') or line.startswith('*') or line.startswith('•')):
                # Clean up formatting
                cause = line.lstrip('0123456789.-*•: ').strip()
                if cause and len(cause) > 3:  # Avoid single words or very short entries
                    potential_causes.append(cause)
        
        # If no structured list found, try splitting by periods or common separators
        if not potential_causes:
            # Split by periods, semicolons, or "and"
            import re
            potential_causes = re.split(r'[.;]|(?:\s+and\s+)', potential_causes_raw)
            potential_causes = [cause.strip() for cause in potential_causes if cause.strip() and len(cause.strip()) > 10]
    
    # Evaluate causal analysis
    score, feedback = evaluate_causal_analysis(potential_causes, expected_causes, causal_reasoning)
    
    return potential_causes, causal_reasoning, likelihood_assessment, score, feedback


def run_causal_reasoning_tests(model="gpt-5-mini", reasoning="low"):
    """Run causal reasoning test suite"""
    
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}🔗 Causal Reasoning Test Suite{RESET}")
    print(f"{BLUE}Model: {model}{RESET}")
    print(f"{BLUE}Reasoning: {reasoning}{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    # Initialize session
    session = NLMSession(
        namespace=f"causal_test_{model}",
        model=model,
        reasoning_effort=reasoning
    )
    
    # Test cases with different types of causal reasoning challenges
    test_cases = [
        # Simple Physical Causation
        {
            "observation": "The road is flooded with water",
            "expected_causes": ["heavy rain", "pipe burst", "dam failure", "storm drain blockage"],
            "context": "Urban residential area, no major rivers nearby",
            "type": "Physical Environmental",
            "description": "Direct physical cause identification"
        },
        
        # Multiple Concurrent Causes
        {
            "observation": "The office building's electricity went out",
            "expected_causes": ["power grid failure", "transformer malfunction", "unpaid electric bill", "circuit breaker trip", "equipment overload"],
            "context": "Large office building during business hours, no storms reported",
            "type": "Infrastructure Failure",
            "description": "Multiple possible technical causes"
        },
        
        # Behavioral/Social Causation
        {
            "observation": "Employee productivity has dropped significantly this month",
            "expected_causes": ["low morale", "increased workload", "system changes", "personal issues", "lack of training", "poor management"],
            "context": "Software company, recent organizational changes",
            "type": "Organizational Behavior",
            "description": "Complex human behavioral factors"
        },
        
        # Chain of Causation
        {
            "observation": "The website is loading very slowly for users",
            "expected_causes": ["server overload", "database issues", "network congestion", "DDoS attack", "poor code optimization", "CDN problems"],
            "context": "E-commerce website during peak shopping season",
            "type": "Technical Performance",
            "description": "Technical system performance issues"
        },
        
        # Economic/Market Causation  
        {
            "observation": "Stock price of the company dropped 20% in one day",
            "expected_causes": ["bad earnings report", "negative news", "market crash", "analyst downgrade", "regulatory issues", "competitor success"],
            "context": "Technology company, no major announcements made",
            "type": "Financial Market",
            "description": "Market behavior and investor psychology"
        },
        
        # Health/Medical Causation
        {
            "observation": "Patient is experiencing persistent headaches",
            "expected_causes": ["stress", "dehydration", "eye strain", "sleep deprivation", "medication side effects", "hypertension"],
            "context": "Office worker, 35 years old, otherwise healthy",
            "type": "Medical Symptoms",
            "description": "Medical diagnostic reasoning"
        },
        
        # Environmental/Ecological
        {
            "observation": "Fish are dying in large numbers in the lake",
            "expected_causes": ["pollution", "oxygen depletion", "temperature change", "disease outbreak", "chemical runoff", "algae bloom"],
            "context": "Small lake near agricultural area, summer season",
            "type": "Environmental Crisis",
            "description": "Ecological system disruption"
        },
        
        # Mechanical/Equipment Failure
        {
            "observation": "The car engine is making strange knocking sounds",
            "expected_causes": ["low oil level", "wrong fuel", "engine knock", "worn bearings", "carbon buildup", "timing issues"],
            "context": "5-year-old sedan, regular maintenance, recently filled with gas",
            "type": "Mechanical Diagnosis",
            "description": "Equipment failure diagnosis"
        },
        
        # Social/Community Issue
        {
            "observation": "Crime rates have increased in the neighborhood",
            "expected_causes": ["economic hardship", "reduced police presence", "drug activity", "youth unemployment", "lack of community programs", "population changes"],
            "context": "Urban neighborhood, recent budget cuts to city services",
            "type": "Social Problem",
            "description": "Complex social causation"
        },
        
        # Educational Performance
        {
            "observation": "Students' test scores have declined significantly",
            "expected_causes": ["curriculum changes", "teacher turnover", "reduced resources", "remote learning effects", "student stress", "family issues"],
            "context": "Elementary school, post-pandemic period",
            "type": "Educational Outcome",
            "description": "Educational system performance"
        }
    ]
    
    results = []
    total_time = 0
    
    print(f"{CYAN}Testing {len(test_cases)} causal reasoning problems:{RESET}\n")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"{CYAN}Test {i}/{len(test_cases)}: {test_case['type']}{RESET}")
        print(f"  Description: {test_case['description']}")
        print(f"  Observation: \"{test_case['observation']}\"")
        print(f"  Context: {test_case['context'][:60]}...")
        print(f"  Expected Causes: {len(test_case['expected_causes'])} cause(s)")
        
        start_time = time.time()
        potential_causes, reasoning, likelihood, score, feedback = test_causal_reasoning_problem(
            session,
            test_case['observation'],
            test_case['expected_causes'],
            test_case['context'],
            test_case['type']
        )
        elapsed = time.time() - start_time
        total_time += elapsed
        
        print(f"  Identified Causes: {len(potential_causes)} cause(s)")
        print(f"  Quality Score: {score:.1f}/100")
        
        # Score interpretation
        if score >= 80:
            print(f"  {GREEN}✅ EXCELLENT ANALYSIS{RESET}")
        elif score >= 60:
            print(f"  {YELLOW}⚠️  GOOD ANALYSIS{RESET}")
        elif score >= 40:
            print(f"  {YELLOW}⚠️  ADEQUATE ANALYSIS{RESET}")
        else:
            print(f"  {RED}❌ POOR ANALYSIS{RESET}")
        
        # Show sample causes
        if potential_causes:
            print(f"  Sample Cause: {potential_causes[0][:60]}...")
        
        # Show key feedback
        if feedback:
            main_feedback = feedback[0] if feedback else "No specific feedback"
            print(f"  Key Feedback: {main_feedback}")
        
        print(f"  Time: {elapsed:.2f}s\n")
        
        results.append({
            "type": test_case['type'],
            "description": test_case['description'],
            "observation": test_case['observation'],
            "context": test_case['context'],
            "expected_causes": test_case['expected_causes'],
            "identified_causes": potential_causes,
            "causal_reasoning": reasoning,
            "likelihood_assessment": likelihood,
            "score": score,
            "feedback": feedback,
            "time": elapsed
        })
    
    # Analysis
    print(f"{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}📊 Causal Reasoning Results{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    # Overall performance
    scores = [r['score'] for r in results]
    avg_score = sum(scores) / len(scores) if scores else 0
    
    print(f"Average Causal Reasoning Score: {avg_score:.1f}/100")
    print(f"Average Time: {total_time/len(results):.2f}s per problem")
    print(f"Total Time: {total_time:.2f}s\n")
    
    # Performance categories
    excellent = sum(1 for s in scores if s >= 80)
    good = sum(1 for s in scores if 60 <= s < 80)
    adequate = sum(1 for s in scores if 40 <= s < 60)
    poor = sum(1 for s in scores if s < 40)
    
    print(f"Performance Distribution:")
    print(f"  Excellent (80-100): {excellent}/{len(results)} ({excellent/len(results)*100:.1f}%)")
    print(f"  Good (60-79): {good}/{len(results)} ({good/len(results)*100:.1f}%)")
    print(f"  Adequate (40-59): {adequate}/{len(results)} ({adequate/len(results)*100:.1f}%)")
    print(f"  Poor (0-39): {poor}/{len(results)} ({poor/len(results)*100:.1f}%)")
    
    # Domain analysis
    print(f"\n{CYAN}Performance by Problem Domain:{RESET}")
    for result in results:
        print(f"  {result['type']}: {result['score']:.1f}/100")
    
    # Cause identification analysis
    total_expected = sum(len(r['expected_causes']) for r in results)
    total_identified = sum(len(r['identified_causes']) for r in results)
    
    print(f"\n{CYAN}Cause Identification Statistics:{RESET}")
    print(f"  Total Expected Causes: {total_expected}")
    print(f"  Total Identified Causes: {total_identified}")
    print(f"  Average Causes per Problem: {total_identified/len(results):.1f}")
    
    # Best and worst performances
    if results:
        best_result = max(results, key=lambda x: x['score'])
        worst_result = min(results, key=lambda x: x['score'])
        
        print(f"\n{GREEN}Best Analysis: {best_result['type']} ({best_result['score']:.1f}/100){RESET}")
        if best_result['identified_causes']:
            print(f"  Causes Found: {len(best_result['identified_causes'])}")
            for cause in best_result['identified_causes'][:3]:
                print(f"    - {cause[:50]}...")
        
        print(f"\n{RED}Most Challenging: {worst_result['type']} ({worst_result['score']:.1f}/100){RESET}")
        if worst_result['feedback']:
            print(f"  Issues: {', '.join(worst_result['feedback'][:2])}")
    
    return results, avg_score


def compare_reasoning_levels_causal(model="gpt-5-mini"):
    """Compare causal reasoning across reasoning levels"""
    
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}🔬 Reasoning Level Comparison for Causal Reasoning{RESET}")
    print(f"{BLUE}Model: {model}{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    levels = ["low", "medium", "high"]
    comparison_results = {}
    
    for level in levels:
        print(f"\n{CYAN}━━━ Testing with reasoning={level} ━━━{RESET}")
        results, avg_score = run_causal_reasoning_tests(model, level)
        comparison_results[level] = {
            "results": results,
            "avg_score": avg_score
        }
    
    # Comparison summary
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}📈 Reasoning Level Impact on Causal Reasoning{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    print("Average Causal Reasoning Score by Reasoning Level:")
    for level in levels:
        score = comparison_results[level]["avg_score"]
        print(f"  {level}: {score:.1f}/100")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test causal reasoning in NLM system")
    parser.add_argument("-m", "--model", default="gpt-5-mini",
                       help="Model to test")
    parser.add_argument("-r", "--reasoning", default="low",
                       choices=["low", "medium", "high"],
                       help="Reasoning effort level")
    parser.add_argument("--compare", action="store_true",
                       help="Compare across reasoning levels")
    
    args = parser.parse_args()
    
    if args.compare:
        compare_reasoning_levels_causal(args.model)
    else:
        run_causal_reasoning_tests(args.model, args.reasoning)


if __name__ == "__main__":
    main()