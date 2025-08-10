#!/usr/bin/env python3
"""Simple Orchestrator for Multi-Haiku System"""

import sys
import argparse
from pathlib import Path

# Add parent directory to path for NLM system imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from system_session import SystemSession
from multi_agent_system import MultiAgentSystem
from theme_generator_agent import ThemeGeneratorAgent
from haiku_generator_agent import HaikuGeneratorAgent
from haiku_selector_agent import HaikuSelectorAgent


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Multi-Haiku System - Generate themes, haiku, and select the best one')
    
    parser.add_argument('--model', '-m', 
                       choices=['gpt-5', 'gpt-5-mini', 'gpt-5-nano', 'local', 'gpt-oss:20b'],
                       default='gpt-5-mini',
                       help='LLM model to use (default: gpt-5-mini)')
    
    parser.add_argument('--reasoning', '-r',
                       choices=['low', 'medium', 'high'], 
                       default='low',
                       help='Reasoning effort level (default: low)')
    
    return parser.parse_args()


def main():
    """Main orchestrator function"""
    # Parse command line arguments
    args = parse_arguments()
    
    # Map 'local' to actual local model name
    model = 'gpt-oss:20b' if args.model == 'local' else args.model
    
    print(f"🚀 Starting Multi-Haiku System")
    print(f"Model: {model}")
    print(f"Reasoning: {args.reasoning}")
    print("-" * 50)

    # Create SystemSession for global variable management
    system_session = SystemSession(model=model, reasoning_effort=args.reasoning)

    # Clear ALL variables (global and local) from database for clean start
    from variable_db import VariableDB
    db = VariableDB()
    db.clear_all()
    print("All previous variables cleared")

    # Step 1: Generate themes
    theme_agent = ThemeGeneratorAgent("theme_gen", model=model, reasoning_effort=args.reasoning)
    theme_agent.run()
    print("Theme generation completed!")

    # Step 2: Create and run 4 haiku generator agents in parallel
    multi_agent_system = MultiAgentSystem("haiku_generation", model=model)

    # Create 4 haiku generator agents
    for i in range(1, 5):
        haiku_agent = HaikuGeneratorAgent(f"haiku_gen_{i}", i, model=model, reasoning_effort=args.reasoning)
        multi_agent_system.add_agent(haiku_agent)

    # Run all haiku generators in parallel
    print("Starting parallel haiku generation...")
    results = multi_agent_system.run_parallel(max_concurrent=4)
    print(f"Haiku generation completed: {results['successful']} successful, {results['failed']} failed")

    # Step 3: Select best haiku
    print("\nSelecting best haiku...")
    selector_agent = HaikuSelectorAgent("haiku_selector", model=model, reasoning_effort=args.reasoning)
    selector_agent.run()
    print("Best haiku selection completed!")

    # Display all results
    print("\n=== Generated Themes and Haiku ===")
    for i in range(1, 5):
        theme = system_session.get_global(f"@theme_{i}")
        haiku = system_session.get_global(f"@haiku_{i}")
        print(f"\nTheme {i}: {theme}")
        print(f"Haiku {i}:")
        if haiku:
            print(haiku)
        else:
            print("  (generation failed)")

    # Display best selection
    print("\n" + "="*50)
    print("🏆 BEST HAIKU SELECTION 🏆")
    print("="*50)

    best_haiku = system_session.get_global("@best_haiku")
    best_theme = system_session.get_global("@best_theme")
    best_number = system_session.get_global("@best_haiku_number")
    selection_reasoning = system_session.get_global("@selection_reasoning")

    if best_haiku:
        print(f"Winner: Haiku #{best_number}")
        print(f"Theme: {best_theme}")
        print(f"\nSelected Haiku:")
        print(best_haiku)
        print(f"\nSelection Reasoning:")
        print(selection_reasoning)
    else:
        print("Best haiku selection failed.")


if __name__ == "__main__":
    main()