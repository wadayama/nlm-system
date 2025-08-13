#!/usr/bin/env python3
"""Simple test of blind optimization without full loop"""

from nlm_interpreter import NLMSession
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from optimization_agent import BlindOptimizationAgent
from test_functions import get_test_function

# Create components
function = get_test_function('sphere')
session = NLMSession(namespace="test_blind")
agent = BlindOptimizationAgent(agent_id="test", model="gpt-oss:20b")

# Test single evaluation
print("Testing single evaluation...")
history = []

# Get first point
point, reasoning = agent.suggest_next_point(history, session)
print(f"Point: {point}")
print(f"Reasoning: {reasoning}")

# Evaluate
value = function(point[0], point[1])
print(f"Value: {value}")

# Update history
history.append({'point': point, 'value': value})

# Get second point
point, reasoning = agent.suggest_next_point(history, session)
print(f"\nSecond point: {point}")
print(f"Reasoning: {reasoning}")

print("\nTest completed successfully!")