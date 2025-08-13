#!/usr/bin/env python3
"""
Simple blind optimization orchestrator
"""

import argparse
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from test_functions import get_test_function
from optimization_agent import OptimizationAgent


def main():
    """Simple optimization loop"""
    
    # Command line arguments
    parser = argparse.ArgumentParser(description='Blind Optimization')
    parser.add_argument('--function', '-f', 
                       choices=['sphere', 'rosenbrock', 'himmelblau', 'complex'],
                       default='sphere',
                       help='Test function')
    parser.add_argument('--model', '-m',
                       default='gpt-5-mini',
                       help='LLM model')
    parser.add_argument('--evaluations', '-e',
                       type=int, default=10,
                       help='Number of evaluations')
    
    args = parser.parse_args()
    
    # Setup
    function = get_test_function(args.function)
    agent = OptimizationAgent(model=args.model)
    
    # Clear any previous experience for fresh start
    agent.session.save("experience_context", "")
    
    print(f"🎯 Blind Optimization")
    print(f"Function: {args.function}")
    print(f"Model: {args.model}")
    print(f"Evaluations: {args.evaluations}")
    
    # Show function information
    true_minimum = function.get_minimum()
    true_value = function(true_minimum[0], true_minimum[1])
    print(f"📊 Target (unknown to agent):")
    print(f"   Optimal point: ({true_minimum[0]:.3f}, {true_minimum[1]:.3f})")
    print(f"   Optimal value: {true_value:.6f}")
    print("-" * 50)
    
    # Optimization loop
    history = []
    
    for i in range(args.evaluations):
        print(f"\n--- Evaluation {i+1}/{args.evaluations} ---")
        
        # Get next point from agent
        point, reasoning = agent.decide_next_point(history)
        
        # Evaluate function
        value = function(point[0], point[1])
        
        # Display results
        print(f"Point: ({point[0]:.3f}, {point[1]:.3f})")
        print(f"Value: {value:.6f}")
        print(f"Reasoning: {reasoning}")
        
        # Record experience and update history
        agent.record_experience(point, value, reasoning)
        history.append({'point': point, 'value': value})
    
    # Find best result
    best_value = float('inf')
    best_point = None
    for result in history:
        if result['value'] < best_value:
            best_value = result['value']
            best_point = result['point']
    
    # Compare with true optimum
    true_minimum = function.get_minimum()
    true_value = function(true_minimum[0], true_minimum[1])
    distance = ((best_point[0] - true_minimum[0])**2 + 
               (best_point[1] - true_minimum[1])**2)**0.5
    
    print("\n" + "="*50)
    print("🏁 Optimization Results:")
    print(f"📈 Best found: ({best_point[0]:.3f}, {best_point[1]:.3f}) → {best_value:.6f}")
    print(f"🎯 True optimum: ({true_minimum[0]:.3f}, {true_minimum[1]:.3f}) → {true_value:.6f}")
    print(f"📏 Distance to optimum: {distance:.6f}")
    
    if distance < 0.1:
        print("🌟 Excellent! Very close to true optimum!")
    elif distance < 0.5:
        print("✨ Good! Reasonably close to optimum.")
    elif distance < 2.0:
        print("👍 Fair performance.")
    else:
        print("💪 Room for improvement.")


if __name__ == "__main__":
    main()