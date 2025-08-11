# NLM System - Claude Code Development Guide

This document provides essential context for Claude Code sessions working on the NLM (Natural Language Macro) system. Read this first for efficient project continuity.

## Project Overview

### What is NLM?
**Natural Language Macro Interpreter** - A Python system that enables natural language programming through intelligent variable manipulation and LLM-driven macro execution.

**Core Innovation**: The `{{variable}}` syntax allows intuitive, natural language variable operations:
```python
# Instead of traditional programming:
session.execute("Save the user's name 'Alice' to {{user_name}}")
session.execute("Greet {{user_name}} and save response to {{greeting}}")
```

### Key Features
- **Variable System**: `{{local}}`, `{{@global}}`, `{{namespace.var}}` syntax
- **LLM Integration**: OpenAI API with automatic prompt caching
- **Agent Framework**: Multi-agent coordination system
- **SQLite Backend**: Persistent variable storage with namespace isolation
- **Zero Learning Curve**: Natural language replaces traditional programming syntax

## Critical Files to Understand

### Essential Source Code
- **`src/nlm_interpreter.py`**: Core engine - variable resolution, LLM interaction, macro execution
- **`src/agent_base.py`**: Foundation for all agent implementations
- **`src/agent_examples.py`**: Concrete agent implementations (updated to current APIs)
- **`src/variable_db.py`**: SQLite-based variable persistence

### Documentation
- **`README.md`**: User-facing overview and quick start
- **`docs/user_guide.md`**: Comprehensive usage patterns
- **`docs/api_reference.md`**: Detailed API documentation
- **`tests/TEST_OVERVIEW.md`**: Testing framework overview

### Current Test Suite (8 Capability Tests)
- `test_conditional_logic.py` - Branch logic handling (57% accuracy)
- `test_ambiguity_tolerance.py` - Ambiguous input classification (75% accuracy)  
- `test_common_sense_evaluation.py` - 0-100 scoring of statements (66.7% accuracy)
- `test_logical_reasoning.py` - Syllogistic reasoning (73.3% accuracy)
- `test_logical_reasoning_improved.py` - Enhanced uncertainty handling
- `test_probabilistic_reasoning.py` - Bayesian inference (90% accuracy)
- `test_planning_capability.py` - Multi-step goal planning (72.8/100 average)
- `test_causal_reasoning.py` - Cause identification (56.8/100 average)

## Standard Development Patterns

### 1. Variable Syntax (Critical)
```python
# Local variables (session-scoped)
session.execute("Save 'value' to {{local_var}}")

# Global variables (cross-session)
session.execute("Set {{@global_var}} to 'shared_value'")

# Cross-namespace access
value = session.get("other_session.their_variable")
```

### 2. Agent Development Pattern
```python
class MyAgent(BaseAgent):
    def __init__(self, agent_id: str, model: str = None, 
                 reasoning_effort: str = "low", verbosity: str = "low"):
        super().__init__(agent_id, model, reasoning_effort, verbosity)
        # Agent-specific initialization
        
    def run(self):
        """Main agent execution - implement your logic here"""
        self.set_status("running")
        # Your agent logic
        self.set_status("completed")
```

### 3. Test Creation Template
```python
def test_capability_problem(session, input_data, expected_output, problem_type):
    session.clear_local()
    session.save("input", input_data)
    
    result = session.execute("""
    Analyze: {{input}}
    INSTRUCTIONS: [Your specific evaluation criteria]
    Save analysis to {{analysis_result}}.
    """)
    
    analysis = session.get("analysis_result")
    score = evaluate_response(analysis, expected_output)
    return analysis, score

def run_capability_tests(model="gpt-5-mini", reasoning="low"):
    # Standard test suite structure
    session = NLMSession(namespace=f"test_{model}", model=model, reasoning_effort=reasoning)
    # Run test cases and collect statistics
```

### 4. Execution Environment
```bash
# Standard execution (always use uv run)
uv run script_name.py

# With parameters
uv run tests/test_planning_capability.py -r medium -m gpt-4

# Comparison testing
uv run tests/test_logical_reasoning.py --compare
```

## Important Design Decisions

### Development Philosophy
- **Incremental Changes**: Add new methods before removing old ones
- **Backward Compatibility**: Maintain existing APIs when possible
- **Test-Driven**: Every capability change should have corresponding tests


## Common Development Workflows

### Adding a New Capability Test
1. Create `tests/test_new_capability.py`
2. Follow standard test structure (see existing tests)
3. Include scoring system (0-100 or percentage accuracy)
4. Add command-line arguments (`-m`, `-r`, `--compare`)
5. Test with: `uv run tests/test_new_capability.py`

### Modifying Core NLM System
1. **READ FIRST**: Understand `src/nlm_interpreter.py` variable resolution
2. **Test Impact**: Run existing tests to ensure no regression
3. **Incremental**: Add new functionality alongside existing
4. **Document**: Update this CLAUDE.md if APIs change

### Debugging Common Issues
```bash
# Check variable state
session.list_variables()  # Shows all variables in database

# Clear problematic state
session.clear_local()     # Clear session variables
session.delete_all()      # Nuclear option - clear everything

# Test basic functionality
session.execute("Save 'test' to {{debug_var}}")
print(session.get("debug_var"))  # Should print: test
```

## Key Architecture Insights

### Variable Resolution Flow
1. LLM receives raw `{{variable}}` syntax in prompt
2. LLM decides whether to read (get_variable) or write (save_variable) 
3. NLMSession executes appropriate SQLite operations
4. Results flow back to LLM for final response

### Agent Communication Patterns
- **Direct**: Via shared namespace variables
- **Global Broadcast**: Using `@variable_name` syntax
- **Message Passing**: Coordinator-mediated via global variables

### Testing Philosophy
- **Capability-Focused**: Test LLM reasoning abilities, not system mechanics
- **Quantitative**: Always provide numerical scores (0-100 or percentage)
- **Comparative**: Support model and reasoning level comparisons
- **Realistic**: Use scenarios relevant to agent decision-making

## Safety & Rollback Procedures

### Before Major Changes
1. **Commit Current State**: `git add . && git commit -m "Before [change]"`
2. **Incremental Implementation**: Add new alongside old
3. **Test Thoroughly**: Run full test suite
4. **Safe Rollback**: Use `git restore [file]` if needed

### Emergency Recovery
```bash
# Restore specific file
git restore src/nlm_interpreter.py

# Check what changed
git status
git diff

# Clean up test files if needed
rm test_*.py
```

---

## Quick Start Checklist for New Claude Code Sessions

1. ✅ Read this CLAUDE.md file
2. ✅ Understand variable syntax: `{{local}}`, `{{@global}}`, `{{namespace.var}}`
3. ✅ Check `git status` to see current work
4. ✅ Run a simple test: `uv run tests/test_conditional_logic.py`
5. ✅ Examine current test results and identify areas for improvement
6. ✅ Use incremental development with safety rollbacks

**Remember**: This system enables natural language programming. The `{{variable}}` syntax is the core innovation that makes complex LLM coordination possible.

