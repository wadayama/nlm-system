#!/usr/bin/env python3
"""Simple Orchestrator for Multi-Haiku System"""

import sys
import argparse
from pathlib import Path

# Import from src/ structure
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
    
    # Show generated themes
    print("\n📝 Generated Themes:")
    for i in range(1, 5):
        theme = system_session.get_global(f"@theme_{i}")
        print(f"  Theme {i}: {theme}")

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
    
    # Show generated haiku progress
    print("\n🎋 Generated Haiku:")
    for i in range(1, 5):
        haiku = system_session.get_global(f"@haiku_{i}")
        theme = system_session.get_global(f"@theme_{i}")
        if haiku:
            print(f"  ✅ Haiku {i} ({theme}):")
            # Indent each line of the haiku
            for line in haiku.split('\n'):
                if line.strip():
                    print(f"     {line.strip()}")
        else:
            print(f"  ❌ Haiku {i} ({theme}): Failed")

    # Step 3: Select best haiku
    print("\nSelecting best haiku...")
    selector_agent = HaikuSelectorAgent("haiku_selector", model=model, reasoning_effort=args.reasoning)
    selector_agent.run()
    print("Best haiku selection completed!")

    # Results will be displayed by external monitoring
    # Orchestration complete


if __name__ == "__main__":
    main()