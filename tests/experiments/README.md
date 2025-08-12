# Experimental Tests

This directory contains experimental test files used during development to validate system behavior and explore new features.

## Files

### Non-Variable Macro Behavior Experiments
- `test_non_variable_behavior.py` - Comprehensive testing of queries without `{{variable}}` syntax
- `test_detailed_behavior.py` - Detailed analysis of different query patterns  
- `test_non_variable_sample.py` - Simple sample tests for basic behavior verification

## Purpose

These experiments were conducted to understand how the NLM system handles:
1. Pure questions (no variable operations expected)
2. Natural language save requests (without explicit `{{variable}}` syntax)
3. Mixed patterns combining questions and variable operations
4. Ambiguous instructions requiring LLM interpretation

## Results

The experiments revealed that the current NLM system already operates in a "hybrid mode", intelligently determining whether to:
- Provide direct answers for pure questions
- Execute variable operations for save requests
- Handle mixed scenarios appropriately

See `docs/archive/EXPERIMENT_RESULTS.md` for detailed findings.