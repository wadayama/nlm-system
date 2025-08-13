# Blind Optimization Tutorial

A tutorial demonstrating how NLM (Natural Language Macro) system can perform optimization of unknown functions using natural language reasoning.

## Overview

This example shows how an AI agent can find the minimum of an unknown 2D function with only 10 function evaluations, using natural language to reason about the optimization strategy.

## Quick Start

```bash
# Run with default settings (sphere function, gpt-5-mini)
uv run blind_opt/blind_optimizer.py

# Try different test functions
uv run blind_opt/blind_optimizer.py --function rosenbrock
uv run blind_opt/blind_optimizer.py --function himmelblau

# Use local model (no API key needed)
uv run blind_opt/blind_optimizer.py --model local
```

## Test Functions

1. **Sphere**: `f(x,y) = x² + y²`
   - Simple convex function
   - Minimum at (0, 0)

2. **Rosenbrock**: `f(x,y) = (1-x)² + 100(y-x²)²`
   - Classic non-convex benchmark
   - Minimum at (1, 1)

3. **Himmelblau**: Complex function with 4 equal minima
   - Multiple local optima
   - Tests exploration vs exploitation

## How It Works

1. Agent starts with no knowledge of the function
2. Selects points to evaluate based on natural language reasoning
3. Updates strategy based on observed values
4. Balances exploration of new areas with exploitation of promising regions
5. Finds approximate minimum in just 10 evaluations

## Example Output

```
🎯 Blind Optimization Tutorial
Function: sphere (unknown to agent)
Budget: 10 evaluations
--------------------------------------------------

--- Evaluation 1/10 ---
Point: (0.000, 0.000)
Reason: Starting from center to understand the landscape
Value: 0.000000
→ New best!

--- Evaluation 2/10 ---
Point: (1.000, 0.000)
Reason: Exploring along x-axis to understand gradient
Value: 1.000000

...
```

## Files

- `blind_optimizer.py` - Main execution script
- `optimization_agent.py` - NLM-based optimization agent
- `test_functions.py` - Test function implementations

## Learning Points

- How to use NLM for optimization tasks
- Natural language reasoning for decision making
- Balancing exploration and exploitation
- Working with limited evaluation budgets