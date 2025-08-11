#!/usr/bin/env python3
"""Test planning capability of NLM system

This test evaluates the system's ability to:
- Break down complex goals into actionable steps
- Handle resource constraints and dependencies
- Sequence tasks optimally
- Adapt plans when constraints change
- Reason about multi-step goal achievement

This is crucial for agent decision-making applications where LLMs must
plan sequences of actions to achieve objectives.
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


def evaluate_plan_quality(plan_steps, expected_elements, constraints):
    """Evaluate the quality of a generated plan"""
    score = 0
    max_score = 100
    feedback = []
    
    if not plan_steps or not isinstance(plan_steps, list):
        return 0, ["Plan not provided in proper format"]
    
    # Check if plan addresses required elements (40 points)
    elements_covered = 0
    for element in expected_elements:
        if any(element.lower() in step.lower() for step in plan_steps):
            elements_covered += 1
    
    element_score = (elements_covered / len(expected_elements)) * 40
    score += element_score
    feedback.append(f"Covered {elements_covered}/{len(expected_elements)} required elements")
    
    # Check constraint compliance (30 points)
    constraint_score = 30
    for constraint in constraints:
        constraint_met = True
        if constraint["type"] == "resource_limit":
            # Check if plan respects resource limits
            if constraint["resource"] == "budget":
                budget_steps = [s for s in plan_steps if "cost" in s.lower() or "budget" in s.lower() or "$" in s]
                if not budget_steps:
                    constraint_met = False
            elif constraint["resource"] == "time":
                time_steps = [s for s in plan_steps if "day" in s.lower() or "week" in s.lower() or "deadline" in s.lower()]
                if not time_steps:
                    constraint_met = False
        
        elif constraint["type"] == "dependency":
            # Check if dependencies are respected in order
            dep_found = False
            for i, step in enumerate(plan_steps):
                if constraint["prerequisite"].lower() in step.lower():
                    for j in range(i+1, len(plan_steps)):
                        if constraint["dependent"].lower() in plan_steps[j].lower():
                            dep_found = True
                            break
                    break
            constraint_met = dep_found
        
        if not constraint_met:
            constraint_score -= 10
            feedback.append(f"Constraint violation: {constraint}")
    
    score += max(0, constraint_score)
    
    # Check logical sequencing (20 points)
    sequence_score = 20
    if len(plan_steps) < 3:
        sequence_score -= 10
        feedback.append("Plan too short for effective sequencing")
    
    # Look for logical ordering keywords
    ordering_indicators = ["first", "then", "next", "after", "before", "finally", "step 1", "step 2"]
    has_ordering = any(indicator in " ".join(plan_steps).lower() for indicator in ordering_indicators)
    if not has_ordering:
        sequence_score -= 10
        feedback.append("Lacks clear step ordering indicators")
    
    score += sequence_score
    
    # Check feasibility (10 points)
    feasibility_score = 10
    if len(plan_steps) > 20:
        feasibility_score -= 5
        feedback.append("Plan may be overly complex")
    
    if any(len(step) < 10 for step in plan_steps):
        feasibility_score -= 5
        feedback.append("Some steps lack sufficient detail")
    
    score += feasibility_score
    
    return min(score, max_score), feedback


def test_planning_problem(session, problem_description, expected_elements, constraints, problem_type):
    """Test a single planning problem"""
    
    # Clear previous state
    session.clear_local()
    
    # Save problem
    session.save("problem", problem_description)
    session.save("constraints", json.dumps(constraints))
    
    # Execute planning
    result = session.execute(f"""
Solve this planning problem: {{{{problem}}}}

Constraints: {{{{constraints}}}}

INSTRUCTIONS FOR PLANNING:

1. GOAL DECOMPOSITION:
   - Break the main goal into specific, actionable sub-goals
   - Identify all necessary steps to achieve the objective
   - Consider both direct actions and supporting activities

2. CONSTRAINT ANALYSIS:
   - Carefully analyze all given constraints (time, budget, resources, dependencies)
   - Ensure your plan respects all constraints
   - Identify potential constraint conflicts early

3. SEQUENCING AND DEPENDENCIES:
   - Order tasks based on logical dependencies
   - Identify which tasks can be done in parallel
   - Consider critical path and bottlenecks
   - Account for setup time and prerequisites

4. RESOURCE ALLOCATION:
   - Consider resource requirements for each step
   - Avoid over-allocation or conflicts
   - Plan for contingencies and buffers

5. FEASIBILITY CHECK:
   - Ensure each step is realistic and achievable
   - Verify that the sequence leads to the goal
   - Check for missing steps or logical gaps

6. OUTPUT FORMAT:
   - Provide a numbered list of concrete, actionable steps
   - Include timing estimates where relevant
   - Specify resource requirements for each step
   - Note any assumptions made

Save your detailed plan as a list of steps to {{{{plan_steps}}}}.
Save your reasoning about constraints and dependencies to {{{{planning_reasoning}}}}.
Save any identified risks or assumptions to {{{{risk_analysis}}}}.
""")
    
    # Get results
    plan_steps_raw = session.get("plan_steps")
    planning_reasoning = session.get("planning_reasoning")
    risk_analysis = session.get("risk_analysis")
    
    # Parse plan steps
    plan_steps = []
    if plan_steps_raw:
        # Try to extract numbered list or bullet points
        lines = plan_steps_raw.split('\n')
        for line in lines:
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-') or line.startswith('*')):
                # Clean up formatting
                step = line.lstrip('0123456789.-*• ').strip()
                if step:
                    plan_steps.append(step)
    
    # Evaluate plan quality
    score, feedback = evaluate_plan_quality(plan_steps, expected_elements, constraints)
    
    return plan_steps, planning_reasoning, risk_analysis, score, feedback


def run_planning_capability_tests(model="gpt-5-mini", reasoning="low"):
    """Run planning capability test suite"""
    
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}🎯 Planning Capability Test Suite{RESET}")
    print(f"{BLUE}Model: {model}{RESET}")
    print(f"{BLUE}Reasoning: {reasoning}{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    # Initialize session
    session = NLMSession(
        namespace=f"planning_test_{model}",
        model=model,
        reasoning_effort=reasoning
    )
    
    # Test cases with different planning challenges
    test_cases = [
        # Simple Linear Planning
        {
            "problem": """
You need to organize a small birthday party for 10 people at your home this Saturday.
Budget: $200
Available time: 3 days to prepare
Goal: Successful party with food, decorations, and entertainment
""",
            "expected_elements": ["food", "decorations", "invitations", "entertainment", "cleanup"],
            "constraints": [
                {"type": "resource_limit", "resource": "budget", "value": 200},
                {"type": "resource_limit", "resource": "time", "value": "3 days"}
            ],
            "type": "Simple Event Planning",
            "description": "Basic sequential task planning"
        },
        
        # Dependency-Heavy Planning
        {
            "problem": """
You're starting a small online business selling handmade crafts.
Goals: Launch website, create initial inventory, establish payment system, market to customers
Constraints: Must have inventory before marketing, payment system before website launch, 
legal registration before accepting payments
Budget: $1000, Timeline: 2 months
""",
            "expected_elements": ["legal registration", "inventory creation", "payment system", "website", "marketing"],
            "constraints": [
                {"type": "dependency", "prerequisite": "legal registration", "dependent": "payment system"},
                {"type": "dependency", "prerequisite": "payment system", "dependent": "website"},
                {"type": "dependency", "prerequisite": "inventory creation", "dependent": "marketing"},
                {"type": "resource_limit", "resource": "budget", "value": 1000},
                {"type": "resource_limit", "resource": "time", "value": "2 months"}
            ],
            "type": "Business Launch Planning",
            "description": "Complex dependency management"
        },
        
        # Resource Optimization
        {
            "problem": """
Plan a 7-day educational workshop for 25 participants on data science.
Resources: 2 instructors, 1 conference room (available 9-5 daily), $5000 budget
Requirements: Cover Python basics, statistics, machine learning, final project
Each topic needs minimum 1.5 days, final project needs 1 day
""",
            "expected_elements": ["Python basics", "statistics", "machine learning", "final project", "materials"],
            "constraints": [
                {"type": "resource_limit", "resource": "instructors", "value": 2},
                {"type": "resource_limit", "resource": "time", "value": "7 days"},
                {"type": "resource_limit", "resource": "budget", "value": 5000},
                {"type": "dependency", "prerequisite": "Python basics", "dependent": "machine learning"},
                {"type": "dependency", "prerequisite": "statistics", "dependent": "machine learning"}
            ],
            "type": "Educational Resource Planning",
            "description": "Resource allocation and scheduling"
        },
        
        # Multi-objective Optimization
        {
            "problem": """
Your software team needs to reduce technical debt while maintaining feature development.
Constraints: 6-month timeline, 5 developers, cannot stop new features entirely
Goals: Refactor 3 legacy modules, implement 2 new major features, maintain bug fix rate
Each legacy module takes 3 weeks, each feature takes 4 weeks, bugs need 20% time allocation
""",
            "expected_elements": ["legacy refactoring", "new features", "bug fixes", "team allocation", "timeline"],
            "constraints": [
                {"type": "resource_limit", "resource": "developers", "value": 5},
                {"type": "resource_limit", "resource": "time", "value": "6 months"},
                {"type": "resource_limit", "resource": "bug_allocation", "value": "20%"}
            ],
            "type": "Software Development Planning",
            "description": "Balancing competing priorities"
        },
        
        # Crisis Response Planning
        {
            "problem": """
Your company's main server crashed and customer data is at risk.
Immediate needs: Assess damage, restore service, communicate with customers, prevent data loss
Resources: 3 IT staff, 1 backup server, emergency budget $10000
Timeline: Service must be restored within 24 hours, communication within 4 hours
""",
            "expected_elements": ["damage assessment", "service restoration", "customer communication", "data recovery"],
            "constraints": [
                {"type": "resource_limit", "resource": "time", "value": "24 hours"},
                {"type": "resource_limit", "resource": "staff", "value": 3},
                {"type": "dependency", "prerequisite": "damage assessment", "dependent": "service restoration"},
                {"type": "resource_limit", "resource": "communication_deadline", "value": "4 hours"}
            ],
            "type": "Crisis Response Planning",
            "description": "High-pressure sequential planning"
        },
        
        # Long-term Strategic Planning
        {
            "problem": """
Plan your personal career transition from marketing to data science over 18 months.
Current: Marketing manager with basic Excel skills
Goal: Junior data scientist role at tech company
Resources: $3000 learning budget, evenings/weekends for study, can take 2 weeks vacation for bootcamp
""",
            "expected_elements": ["skill assessment", "learning plan", "portfolio building", "networking", "job search"],
            "constraints": [
                {"type": "resource_limit", "resource": "budget", "value": 3000},
                {"type": "resource_limit", "resource": "time", "value": "18 months"},
                {"type": "dependency", "prerequisite": "skill assessment", "dependent": "learning plan"},
                {"type": "dependency", "prerequisite": "learning plan", "dependent": "portfolio building"}
            ],
            "type": "Career Transition Planning",
            "description": "Long-term goal achievement"
        },
        
        # Parallel Task Coordination
        {
            "problem": """
Coordinate a research project with 4 parallel workstreams that must integrate at the end.
Workstreams: Literature review (3 weeks), Data collection (4 weeks), 
Analysis method development (5 weeks), Pilot testing (2 weeks)
Integration phase needs all workstreams complete, final report needs 2 weeks
Total project timeline: 8 weeks, 6 team members to allocate
""",
            "expected_elements": ["literature review", "data collection", "analysis methods", "pilot testing", "integration", "final report"],
            "constraints": [
                {"type": "resource_limit", "resource": "time", "value": "8 weeks"},
                {"type": "resource_limit", "resource": "team_members", "value": 6},
                {"type": "dependency", "prerequisite": "all workstreams", "dependent": "integration"},
                {"type": "dependency", "prerequisite": "integration", "dependent": "final report"}
            ],
            "type": "Parallel Project Coordination",
            "description": "Managing concurrent workstreams"
        }
    ]
    
    results = []
    total_time = 0
    
    print(f"{CYAN}Testing {len(test_cases)} planning problems:{RESET}\n")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"{CYAN}Test {i}/{len(test_cases)}: {test_case['type']}{RESET}")
        print(f"  Description: {test_case['description']}")
        print(f"  Problem: {test_case['problem'][:100].replace(chr(10), ' ')}...")
        print(f"  Expected Elements: {', '.join(test_case['expected_elements'])}")
        print(f"  Constraints: {len(test_case['constraints'])} constraint(s)")
        
        start_time = time.time()
        plan_steps, reasoning, risk_analysis, score, feedback = test_planning_problem(
            session,
            test_case['problem'],
            test_case['expected_elements'],
            test_case['constraints'],
            test_case['type']
        )
        elapsed = time.time() - start_time
        total_time += elapsed
        
        print(f"  Plan Steps: {len(plan_steps)} steps")
        print(f"  Quality Score: {score:.1f}/100")
        
        # Score interpretation
        if score >= 80:
            print(f"  {GREEN}✅ EXCELLENT PLAN{RESET}")
        elif score >= 60:
            print(f"  {YELLOW}⚠️  GOOD PLAN{RESET}")
        elif score >= 40:
            print(f"  {YELLOW}⚠️  ADEQUATE PLAN{RESET}")
        else:
            print(f"  {RED}❌ POOR PLAN{RESET}")
        
        # Show plan summary
        if plan_steps:
            print(f"  Plan Preview: {plan_steps[0][:60]}..." if plan_steps[0] else "")
        
        # Show key feedback
        if feedback:
            main_feedback = feedback[0] if feedback else "No specific feedback"
            print(f"  Key Feedback: {main_feedback}")
        
        print(f"  Time: {elapsed:.2f}s\n")
        
        results.append({
            "type": test_case['type'],
            "description": test_case['description'],
            "problem": test_case['problem'],
            "expected_elements": test_case['expected_elements'],
            "constraints": test_case['constraints'],
            "plan_steps": plan_steps,
            "reasoning": reasoning,
            "risk_analysis": risk_analysis,
            "score": score,
            "feedback": feedback,
            "time": elapsed
        })
    
    # Analysis
    print(f"{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}📊 Planning Capability Results{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    # Overall performance
    scores = [r['score'] for r in results]
    avg_score = sum(scores) / len(scores) if scores else 0
    
    print(f"Average Planning Score: {avg_score:.1f}/100")
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
    
    # Problem type analysis
    print(f"\n{CYAN}Performance by Problem Type:{RESET}")
    for result in results:
        print(f"  {result['type']}: {result['score']:.1f}/100")
    
    # Best and worst plans
    if results:
        best_result = max(results, key=lambda x: x['score'])
        worst_result = min(results, key=lambda x: x['score'])
        
        print(f"\n{GREEN}Best Plan: {best_result['type']} ({best_result['score']:.1f}/100){RESET}")
        if best_result['plan_steps']:
            print(f"  Steps: {len(best_result['plan_steps'])}")
            for i, step in enumerate(best_result['plan_steps'][:3], 1):
                print(f"    {i}. {step[:60]}...")
        
        print(f"\n{RED}Most Challenging: {worst_result['type']} ({worst_result['score']:.1f}/100){RESET}")
        if worst_result['feedback']:
            print(f"  Issues: {', '.join(worst_result['feedback'][:2])}")
    
    return results, avg_score


def compare_reasoning_levels_planning(model="gpt-5-mini"):
    """Compare planning capability across reasoning levels"""
    
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}🔬 Reasoning Level Comparison for Planning{RESET}")
    print(f"{BLUE}Model: {model}{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    levels = ["low", "medium", "high"]
    comparison_results = {}
    
    for level in levels:
        print(f"\n{CYAN}━━━ Testing with reasoning={level} ━━━{RESET}")
        results, avg_score = run_planning_capability_tests(model, level)
        comparison_results[level] = {
            "results": results,
            "avg_score": avg_score
        }
    
    # Comparison summary
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}📈 Reasoning Level Impact on Planning{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    print("Average Planning Score by Reasoning Level:")
    for level in levels:
        score = comparison_results[level]["avg_score"]
        print(f"  {level}: {score:.1f}/100")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test planning capability in NLM system")
    parser.add_argument("-m", "--model", default="gpt-5-mini",
                       help="Model to test")
    parser.add_argument("-r", "--reasoning", default="low",
                       choices=["low", "medium", "high"],
                       help="Reasoning effort level")
    parser.add_argument("--compare", action="store_true",
                       help="Compare across reasoning levels")
    
    args = parser.parse_args()
    
    if args.compare:
        compare_reasoning_levels_planning(args.model)
    else:
        run_planning_capability_tests(args.model, args.reasoning)


if __name__ == "__main__":
    main()