#!/usr/bin/env python3
"""
Blind Optimization Tutorial - Main Execution Script
Demonstrates NLM-based optimization of unknown functions
"""

import argparse
import json
from pathlib import Path

# Import from NLM system (uv handles path)
from nlm_interpreter import NLMSession

# Import from same directory
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from optimization_agent import BlindOptimizationAgent
from test_functions import get_test_function


class BlindOptimizer:
    """Main orchestrator for blind optimization"""
    
    def __init__(self, function_name='sphere', model='gpt-5-mini'):
        """
        Initialize optimizer
        
        Args:
            function_name: Name of test function ('sphere', 'rosenbrock', 'himmelblau')
            model: LLM model to use
        """
        # Get test function (hidden from agent)
        self.function = get_test_function(function_name)
        self.function_name = function_name
        
        # Initialize NLM session
        self.session = NLMSession(namespace="blind_opt")
        
        # Create optimization agent
        self.agent = BlindOptimizationAgent(
            agent_id="optimizer",
            model=model
        )
        
        # Track optimization progress
        self.history = []
        self.best_point = None
        self.best_value = float('inf')
    
    def run_optimization(self):
        """Run the optimization process"""
        
        print("🎯 Blind Optimization Tutorial")
        print(f"Function: {self.function_name} (unknown to agent)")
        print(f"Budget: 10 evaluations")
        print("-" * 50)
        
        # Initialize NLM variables
        self.session.execute("""
        Initialize blind optimization:
        - Set {{@evaluation_history}} to '[]'
        - Set {{@best_value}} to '999999'
        - Set {{@best_point}} to 'None'
        """)
        
        # Main optimization loop - exactly 10 evaluations
        for i in range(10):
            print(f"\n--- Evaluation {i+1}/10 ---")
            
            # Agent suggests next point with reasoning
            next_point, reasoning = self.agent.suggest_next_point(
                history=self.history,
                session=self.session
            )
            
            # Display selection
            print(f"Point: ({next_point[0]:.3f}, {next_point[1]:.3f})")
            print(f"Reason: {reasoning}")
            
            # Evaluate function
            value = self.function(next_point[0], next_point[1])
            print(f"Value: {value:.6f}")
            
            # Update history
            self.history.append({
                'point': next_point,
                'value': value
            })
            
            # Track best
            if value < self.best_value:
                self.best_value = value
                self.best_point = next_point
                print(f"→ New best!")
            
            # Update agent's strategy
            strategy = self.agent.update_strategy(
                new_result={'point': next_point, 'value': value},
                session=self.session
            )
        
        # Show final results
        self.show_results()
    
    def show_results(self):
        """Display final optimization results"""
        
        print("\n" + "="*50)
        print("Final Results:")
        print(f"Best point: ({self.best_point[0]:.3f}, {self.best_point[1]:.3f})")
        print(f"Best value: {self.best_value:.6f}")
        
        # Compare with true minimum
        true_min = self.function.get_minimum()
        true_value = self.function(true_min[0], true_min[1])
        
        print(f"\nTrue minimum: ({true_min[0]:.3f}, {true_min[1]:.3f})")
        print(f"True value: {true_value:.6f}")
        
        # Calculate distance to optimum
        distance = ((self.best_point[0] - true_min[0])**2 + 
                   (self.best_point[1] - true_min[1])**2)**0.5
        print(f"Distance to optimum: {distance:.6f}")


def main():
    """Command line interface"""
    
    parser = argparse.ArgumentParser(
        description='Blind Optimization Tutorial using NLM'
    )
    
    parser.add_argument(
        '--function', '-f',
        choices=['sphere', 'rosenbrock', 'himmelblau'],
        default='sphere',
        help='Test function to optimize (default: sphere)'
    )
    
    parser.add_argument(
        '--model', '-m',
        choices=['gpt-5', 'gpt-5-mini', 'gpt-5-nano', 'local', 'gpt-oss:20b'],
        default='gpt-5-mini',
        help='LLM model to use (default: gpt-5-mini)'
    )
    
    args = parser.parse_args()
    
    # Map 'local' to actual model name
    model = 'gpt-oss:20b' if args.model == 'local' else args.model
    
    # Run optimization
    optimizer = BlindOptimizer(
        function_name=args.function,
        model=model
    )
    
    optimizer.run_optimization()


if __name__ == "__main__":
    main()