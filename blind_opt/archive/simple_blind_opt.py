#!/usr/bin/env python3
"""
Simplified blind optimization without NLM agent
Just to test the basic structure
"""

import random
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from test_functions import get_test_function


def simple_optimization(function_name='sphere'):
    """Simple optimization without NLM"""
    
    function = get_test_function(function_name)
    
    print("🎯 Simple Blind Optimization (No NLM)")
    print(f"Function: {function_name}")
    print(f"Budget: 10 evaluations")
    print("-" * 50)
    
    history = []
    best_point = None
    best_value = float('inf')
    
    for i in range(10):
        print(f"\n--- Evaluation {i+1}/10 ---")
        
        # Simple strategy
        if i == 0:
            # Start at center
            point = [0.0, 0.0]
            reasoning = "Starting from center"
        elif i < 5:
            # Grid search
            grid_points = [
                [2.0, 0.0], [-2.0, 0.0], [0.0, 2.0], [0.0, -2.0],
                [1.0, 1.0], [-1.0, -1.0], [1.0, -1.0], [-1.0, 1.0]
            ]
            tried = [h['point'] for h in history]
            available = [p for p in grid_points if p not in tried]
            
            if available:
                point = available[0]
                reasoning = f"Grid exploration"
            else:
                point = [random.uniform(-3, 3), random.uniform(-3, 3)]
                reasoning = "Random exploration"
        else:
            # Exploit best region
            if best_point:
                noise = 0.5
                point = [
                    best_point[0] + random.uniform(-noise, noise),
                    best_point[1] + random.uniform(-noise, noise)
                ]
                point[0] = max(-5, min(5, point[0]))
                point[1] = max(-5, min(5, point[1]))
                reasoning = "Exploiting near best point"
            else:
                point = [random.uniform(-3, 3), random.uniform(-3, 3)]
                reasoning = "Random exploration"
        
        print(f"Point: ({point[0]:.3f}, {point[1]:.3f})")
        print(f"Reason: {reasoning}")
        
        # Evaluate
        value = function(point[0], point[1])
        print(f"Value: {value:.6f}")
        
        # Update history and best
        history.append({'point': point, 'value': value})
        
        if value < best_value:
            best_value = value
            best_point = point
            print(f"→ New best!")
    
    # Final results
    print("\n" + "="*50)
    print("Final Results:")
    print(f"Best point: ({best_point[0]:.3f}, {best_point[1]:.3f})")
    print(f"Best value: {best_value:.6f}")
    
    # True minimum
    true_min = function.get_minimum()
    true_value = function(true_min[0], true_min[1])
    print(f"\nTrue minimum: ({true_min[0]:.3f}, {true_min[1]:.3f})")
    print(f"True value: {true_value:.6f}")
    
    distance = ((best_point[0] - true_min[0])**2 + 
               (best_point[1] - true_min[1])**2)**0.5
    print(f"Distance to optimum: {distance:.6f}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--function', '-f', 
                       choices=['sphere', 'rosenbrock', 'himmelblau'],
                       default='sphere')
    
    args = parser.parse_args()
    
    simple_optimization(args.function)