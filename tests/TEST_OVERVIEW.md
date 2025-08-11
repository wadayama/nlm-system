# NLM System Test Suite Overview

## Purpose

This document provides a comprehensive overview of all test files in the NLM system, categorized by priority and functionality. This classification helps new Claude Code sessions understand which tests are essential for development work and which can be run for specific scenarios.

## Test Categories by Priority

### 🔴 Critical Tests - Always Run First

These tests validate core functionality and should always pass before any code changes.

#### Core System Tests
- **`test_nlm_interpreter.py`** - Core NLM interpreter functionality
  - Basic session creation and namespace handling
  - Variable resolution and tool functions
  - Essential for any interpreter changes

- **`test_variable_db_basic.py`** - Database operations
  - Variable storage, retrieval, deletion
  - Namespace isolation testing
  - Critical for data persistence

- **`test_at_prefix_api.py`** - Global variable API
  - @-prefix global variable functionality
  - Cross-session variable sharing
  - Essential for multi-agent coordination

#### Agent System Tests
- **`test_agent_basic.py`** - BaseAgent core functionality
  - Agent instantiation and basic operations
  - Session management and variable access
  - Foundation for all agent-based features

- **`test_multi_agent_system.py`** - Multi-agent orchestration
  - Agent coordination and communication
  - System-level integration testing
  - Critical for complex workflows

### 🟡 Important Tests - Run for Feature Work

These tests cover important functionality that should be validated when working on related features.

#### API and Integration Tests
- **`test_global_sharing.py`** - Cross-session data sharing
  - Global variable synchronization
  - Multi-session coordination
  - Important for collaborative features

- **`test_system_session.py`** - SystemSession unified interface
  - @-prefix API integration
  - Session management patterns
  - Key for system-wide operations

- **`test_tool_execution.py`** - LLM tool execution
  - Variable management tools
  - LLM integration testing
  - Essential for macro execution

#### Variable Management Tests  
- **`test_multi_variable_operations.py`** - Complex variable operations
  - Multi-variable macro commands
  - Advanced NLM syntax testing
  - Important for sophisticated macros

- **`test_variable_expansion.py`** - Variable substitution
  - {{variable}} syntax processing
  - Template expansion logic
  - Critical for macro interpretation

- **`test_variable_patterns.py`** - Variable name patterns
  - Special character handling
  - Naming convention validation
  - Important for robust variable handling

### 🟢 Functional Tests - Run for Specific Features

These tests validate specific features and should be run when working on related functionality.

#### Edge Case and Error Handling
- **`test_edge_cases.py`** - Integrated edge case testing
  - Combined edge case scenarios
  - Comprehensive error conditions
  - Run for stability validation

- **`test_difficult_edge_cases.py`** - Complex edge scenarios
  - Advanced error conditions
  - Stress testing scenarios
  - Run for robustness validation

- **`test_error_handling.py`** - Error recovery testing
  - Exception handling validation
  - Error message accuracy
  - Run for error handling improvements

#### Model and Performance Tests
- **`test_model_switching.py`** - LLM model switching
  - Dynamic model configuration
  - Model-specific behavior testing
  - Run when adding new models

- **`test_rate_limiting.py`** - API rate limiting
  - Request throttling validation
  - API quota management
  - Run for API integration work

- **`test_gpt5_mini_edge_cases.py`** - GPT-5-mini specific testing
  - Model-specific edge cases
  - Performance validation
  - Run for GPT-5-mini optimization

- **`test_gpt5_mini_final.py`** - GPT-5-mini final validation
  - Comprehensive model testing
  - Production readiness check
  - Run before GPT-5-mini deployment

#### Application Examples
- **`test_haiku_generation.py`** - Haiku generation example
  - Creative content generation
  - Multi-step macro execution
  - Run for creative application validation

- **`test_role_continuation.py`** - Role-playing continuity
  - Context preservation testing
  - Long conversation handling
  - Run for conversational applications

- **Conversation history tests removed** - Feature deprecated for performance

### 🔵 Specialized Tests - Run for Specific Scenarios

These tests cover specialized functionality for specific use cases.

#### Model Comparison Tests
- **`test_local_vs_mini_edge_cases.py`** - Local vs OpenAI comparison
  - Performance benchmarking
  - Quality comparison testing
  - Run for model evaluation

- **`test_local_vs_nano_edge_cases.py`** - Local vs nano comparison
  - Alternative model testing
  - Cost/performance analysis
  - Run for model selection

#### Advanced Features
- **`test_agent_examples.py`** - Agent usage examples
  - Practical agent implementations
  - Usage pattern validation
  - Run for agent development

- **`test_simple_history.py`** - Basic history functionality
  - Simple history operations
  - Lightweight history testing
  - Run for basic history features

- **`test_settings.py`** - Configuration management
  - Settings validation
  - Configuration loading
  - Run for config changes

- **`test_cli.py`** - Command line interface
  - CLI command validation
  - User interface testing
  - Run for CLI development

## Performance Test Suite

Located in `tests/performance/`, these tests focus on optimization and benchmarking.

### Core Performance Tests
- **`test_final_optimization.py`** - Overall system optimization
- **`test_reasoning_effort.py`** - Reasoning effort parameter testing  
- **`test_verbosity_parameter.py`** - Output verbosity optimization
- **`test_variable_correctness.py`** - Variable operation accuracy

### Model Performance Tests
- **`test_all_models_improved.py`** - Comprehensive model comparison
- **`test_gpt5_mini_performance.py`** - GPT-5-mini specific performance
- **`test_gpt5_nano_speed.py`** - GPT-5-nano speed testing
- **`test_quality_verification.py`** - Output quality validation

### Specialized Performance Tests
- **`test_api_latency.py`** - API response time testing
- **`test_local_reasoning.py`** - Local model reasoning performance
- **`test_reasoning_comparison.py`** - Cross-model reasoning comparison

## Usage Guidelines

### For New Claude Code Sessions

1. **Start with Critical Tests**: Always run 🔴 critical tests first to ensure basic functionality
2. **Feature-Specific Testing**: Run 🟡 important tests when working on related features
3. **Edge Case Validation**: Use 🟢 functional tests for comprehensive validation
4. **Specialized Scenarios**: Run 🔵 specialized tests only when needed

### Running Tests

```bash
# Critical tests - always run these first
uv run tests/test_nlm_interpreter.py
uv run tests/test_variable_db_basic.py
uv run tests/test_at_prefix_api.py
uv run tests/test_agent_basic.py

# Important tests - run for feature work
uv run tests/test_global_sharing.py
uv run tests/test_system_session.py
uv run tests/test_multi_variable_operations.py

# Performance validation
uv run tests/performance/test_final_optimization.py
```

### Test Execution Notes

- Use `uv run` command as specified in CLAUDE.md
- Tests are configured for gpt-5-mini by default
- Some tests may require API keys or local LLM setup
- Performance tests may take longer to execute

## Archived Tests

The following tests have been moved to `tests/archive/` as they test deprecated functionality or are duplicates:

- `test_broadcast.py` - Removed broadcast functionality
- `test_edge_[1,2,3,6,7].py` - Individual edge cases (covered by integrated tests)
- Performance test duplicates and temporary model tests

## Maintenance

This document should be updated when:
- New tests are added
- Test priorities change
- Test functionality is modified
- Features are deprecated

---

*This overview is designed to help Claude Code sessions quickly understand and utilize the NLM test suite effectively.*