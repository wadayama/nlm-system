#!/usr/bin/env python3
"""Simple Orchestrator for Multi-Haiku System"""

import sys
from pathlib import Path

# Add parent directory to path for NLM system imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from system_session import SystemSession
from multi_agent_system import MultiAgentSystem
from theme_generator_agent import ThemeGeneratorAgent
from haiku_generator_agent import HaikuGeneratorAgent
from haiku_selector_agent import HaikuSelectorAgent


# Create SystemSession for global variable management
system_session = SystemSession()

# Clear ALL variables (global and local) from database for clean start
from variable_db import VariableDB
db = VariableDB()
db.clear_all()
print("All previous variables cleared")

# Step 1: Generate themes
theme_agent = ThemeGeneratorAgent("theme_gen")
theme_agent.run()
print("Theme generation completed!")

# Step 2: Create and run 4 haiku generator agents in parallel
multi_agent_system = MultiAgentSystem("haiku_generation")

# Create 4 haiku generator agents
for i in range(1, 5):
    haiku_agent = HaikuGeneratorAgent(f"haiku_gen_{i}", i)
    multi_agent_system.add_agent(haiku_agent)

# Run all haiku generators in parallel
print("Starting parallel haiku generation...")
results = multi_agent_system.run_parallel(max_concurrent=4)
print(f"Haiku generation completed: {results['successful']} successful, {results['failed']} failed")

# Step 3: Select best haiku
print("\nSelecting best haiku...")
selector_agent = HaikuSelectorAgent("haiku_selector")
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