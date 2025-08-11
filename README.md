# NLM System - Natural Language Macro Interpreter

A Python orchestrator for natural language macros with unified variable syntax, session management, and OpenAI-compatible API integration.

## Prerequisites

**⚠️ Important: This project requires [uv](https://github.com/astral-sh/uv) for package management and execution**

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install project dependencies
uv sync                 # ✅ Installs all dependencies from pyproject.toml

# All Python scripts must be run with uv:
uv run script.py        # ✅ Correct
python script.py        # ❌ Won't work with src/ structure
```

**Why uv is required:**
- Project uses `src/` layout with automatic package discovery
- uv handles Python path configuration from `pyproject.toml`
- uv manages dependencies more efficiently than pip
- Standard `python` command cannot find modules in `src/` directory

**Adding dependencies:**
```bash
# Add a new dependency to the project
uv add package_name        # ✅ Correct way to add dependencies
pip install package_name   # ❌ Won't persist in project configuration
```

## Features

- **Natural Language Macros**: Execute human-like instructions with `{{variable}}` syntax
- **Unified Variable Syntax**: `@prefix` for global variables across NLM and Python
- **Session-based Architecture**: Isolated namespaces with controlled sharing
- **Multi-Agent Support**: Externalized state for distributed agent systems
- **OpenAI-compatible**: Works with Ollama, LMStudio, and OpenAI APIs

## Quick Start

```bash
# Install dependencies
uv sync

# Verify installation
uv run python -c "from nlm_interpreter import NLMSession; print('NLM System ready!')"
```

## Command Line Usage

```bash
# Execute natural language macros
uv run nlm_interpreter.py "Save 'production' to {{@environment}}"

# Execute from file
uv run nlm_interpreter.py -f my_workflow.md

# Custom model/endpoint
uv run nlm_interpreter.py -m llama3.1:8b -e http://localhost:11434/v1 "Save today to {{@date}}"
```

## Model Support

The NLM system supports 4 models with automatic provider switching based on model name:

### 🌐 OpenAI Models (Requires API Key)
- `gpt-5` - Most capable model (Premium tier)
- `gpt-5-mini` - Balanced performance and cost (Standard tier) 
- `gpt-5-nano` - Fast and economical (Economy tier)

### 💻 Local Model (Default - No API charges)
- `gpt-oss:20b` - Local LLM via LMStudio

## OpenAI API Setup

### First Time Setup
```bash
# Interactive setup assistant
uv run setup_openai.py

# Or check current setup
uv run setup_openai.py check
```

### Manual Setup
Create an API key file in one of these locations:
```bash
# Option 1: Project-specific (current directory)
echo "sk-your-api-key-here" > .openai_key
chmod 600 .openai_key

# Option 2: User-wide configuration
mkdir -p ~/.config/nlm
echo "sk-your-api-key-here" > ~/.config/nlm/openai_key
chmod 600 ~/.config/nlm/openai_key
```

Get your API key from: https://platform.openai.com/api-keys

### Usage Examples

```python
from nlm_interpreter import NLMSession

# Automatic provider selection based on model name
session_openai = NLMSession(model="gpt-5-mini")  # Uses OpenAI API
session_local = NLMSession()                     # Uses local LLM (default)

# All models support the same API
session_openai.execute("Save 'Hello OpenAI' to {{message}}")
session_local.execute("Save 'Hello Local' to {{message}}")
```

### Command Line Usage with Models
```bash
# OpenAI models (requires API key)
uv run nlm_interpreter.py -m gpt-5 "Save 'test' to {{var}}"
uv run nlm_interpreter.py -m gpt-5-mini "Process {{task}}"
uv run nlm_interpreter.py -m gpt-5-nano "Quick task: {{task}}"

# Local model (default - no API key needed)
uv run nlm_interpreter.py "Save 'test' to {{var}}"
uv run nlm_interpreter.py -m gpt-oss:20b "Save 'test' to {{var}}"
```

## Try Multi-Haiku Example

Experience natural language macros with our multi-agent haiku generation system:

```bash
# Navigate to multi-haiku directory
cd multi_haiku

# Quick test with local model (no API key needed)
uv run simple_orchestrator.py --model local

# Or with OpenAI models (requires API key)
uv run simple_orchestrator.py --model gpt-5-mini
```

This example demonstrates:
- **Natural language macro execution**: Agents use human-like instructions
- **Multi-agent coordination**: Theme generation → Haiku creation → Selection process
- **Global variable sharing**: Agents communicate through shared variables
- **Unified syntax**: `{{variable}}` patterns work across all agents

Expected output:
```
🎨 Generated theme: "Mountain sunrise"
📝 Generated 3 haiku variations
🏆 Selected best haiku based on imagery and emotion
```

## Python API Usage

```python
from nlm_interpreter import NLMSession

# Create a session with isolated namespace
session = NLMSession(namespace="my_agent")

# Save local variables (session-scoped)
session.save("task", "data_processing")
session.save("status", "running")

# Save global variables (shared across all sessions)
session.save("@project_name", "AI Research 2024")
session.save("@environment", "production")

# Retrieve variables
print(session.get("task"))           # "data_processing" 
print(session.get("@project_name"))  # "AI Research 2024"

# Execute natural language macros
session.execute("Save 'Hello World' to {{greeting}}")
print(session.get("greeting"))       # "Hello World"

session.execute("Save current timestamp to {{@last_updated}}")
print(session.get("@last_updated"))  # Timestamp value

# List variables
print(session.list_local())   # {"task": "data_processing", "status": "running", ...}
print(session.list_global())  # {"project_name": "AI Research 2024", ...}

# Delete variables
session.delete("task")         # Delete local variable
session.delete("@environment") # Delete global variable

# Clear all local variables
session.clear_local()
```

## Multi-Session Communication

```python
# Session 1: Data preparation
data_session = NLMSession(namespace="data_prep")
data_session.save("dataset", "/data/train.csv")
data_session.save("@pipeline_status", "data_ready")  # Global

# Session 2: Model training  
model_session = NLMSession(namespace="training")
status = model_session.get("@pipeline_status")      # "data_ready"
model_session.save("@model_status", "training")      # Global

# Both sessions see global updates
print(data_session.get("@model_status"))   # "training"
print(model_session.get("@model_status"))  # "training"
```

## Intermediate Features

### SystemSession - Unified Global Variable Access

For cleaner global variable management with unified @-prefixed syntax:

```python
from system_session import SystemSession

# Create system session with unified @-syntax
system = SystemSession()

# Set global variables - both ways work the same
system.set_global("status", "active")        # Auto @-prefix
system.set_global("@config", "production")   # Explicit @-prefix

# Get global variables - consistent interface
status = system.get_global("status")         # Returns "active"  
config = system.get_global("@config")        # Returns "production"

# Natural language macros use same @-syntax
system.execute("Save 'ready' to {{@system_status}}")
system_status = system.get_global("system_status")  # Returns "ready"

# List all global variables (clean keys without @)
globals_dict = system.list_globals()
# Returns: {"status": "active", "config": "production", "system_status": "ready"}

# Context manager support
with SystemSession() as system:
    system.set_global("temp_config", "test_mode")
    system.execute("Process configuration from {{@temp_config}}")
    
# Inherits all NLMSession functionality
system.set_reasoning_effort("high")
system.set_verbosity("medium")
# All NLMSession methods available
```

**Key Benefits:**
- **Interface Consistency**: `{{@variable}}` in macros matches `system.get_global("@variable")` in Python
- **Auto @ Handling**: `set_global("var")` automatically becomes `@var` internally
- **Full Inheritance**: All NLMSession features (execute, settings, context) work unchanged
- **Backward Compatible**: Existing code continues to work without changes

### Executing Multi-line Macro Files

#### From Python Code

```python
from nlm_interpreter import NLMSession
from pathlib import Path

# Create a session
session = NLMSession(namespace="workflow")

# Create and execute a multi-line macro
macro_content = """
Initialize data processing pipeline.

Save 'started' to {{@pipeline_status}}.
Set {{input_file}} to '/data/raw/dataset.csv'.
Set {{output_file}} to '/data/processed/clean_data.csv'.

Process the file {{input_file}} and save results to {{output_file}}.
Update {{@pipeline_status}} to 'completed'.
Save current timestamp to {{@last_run}}.
"""

# Execute the entire macro file
result = session.execute(macro_content)
print(f"Execution result: {result}")

# Check the variables that were set
print(f"Pipeline status: {session.get('@pipeline_status')}")
print(f"Output file: {session.get('output_file')}")
```

Example macro content:
```
Initialize data processing pipeline.

Save 'started' to {{@pipeline_status}}.
Set {{input_file}} to '/data/raw/dataset.csv'.
Set {{output_file}} to '/data/processed/clean_data.csv'.

Process the file {{input_file}} and save results to {{output_file}}.
Update {{@pipeline_status}} to 'completed'.
Save current timestamp to {{@last_run}}.
```

#### Batch Processing Multiple Macro Files

```python
from nlm_interpreter import NLMSession
from pathlib import Path

session = NLMSession(namespace="batch_process")

# Process all macro files in a directory (example with custom directory)
macro_dir = Path("my_macros")  # User-created directory
for macro_file in macro_dir.glob("*.md"):
    print(f"\nExecuting: {macro_file.name}")
    
    content = macro_file.read_text()
    result = session.execute(content)
    
    # Log results
    session.save(f"@last_macro", macro_file.name)
    session.save(f"@last_result", result[:100])  # First 100 chars
    
print("\nAll macros executed successfully")
print(f"Last macro: {session.get('@last_macro')}")
```

## Multi-Agent System

Execute multiple agents in parallel for complex workflows:

```python
from multi_agent_system import MultiAgentSystem
from agent_base import BaseAgent
from agent_examples import DataCollectorAgent, ResearchAgent, MonitorAgent

# Create custom agent by inheriting from BaseAgent
class CustomTaskAgent(BaseAgent):
    def __init__(self, agent_id: str, task_description: str):
        super().__init__(agent_id)
        self.task_description = task_description
        
    def run(self):
        """Define your agent's behavior here"""
        self.set_status("working")
        
        # Execute natural language task
        result = self.execute_macro(
            f"Perform this task: {self.task_description}. "
            f"Save the result to {{{{task_result}}}}"
        )
        
        self.set_status("completed")
        return result

# Create system
system = MultiAgentSystem("my_project")

# Add custom agent alongside built-in agents
custom_agent = CustomTaskAgent("custom1", "Analyze sales data trends")
collector = DataCollectorAgent("collector1", "database_source")
researcher = ResearchAgent("researcher1", "AI trends analysis")

system.add_agent(custom_agent)
system.add_agent(collector)
system.add_agent(researcher)

# Execute agents
results = system.run_parallel()  # Run simultaneously
print(f"Results: {results['successful']} successful, {results['failed']} failed")
```

**Available Agent Types:**
- `DataCollectorAgent`: One-time data collection
- `MonitorAgent`: Continuous system monitoring
- `ResearchAgent`: Multi-phase research workflow
- `CoordinatorAgent`: Team management and coordination

For detailed multi-agent usage, see [docs/multi_agent_guide.md](docs/multi_agent_guide.md)


## Helper Tools

```bash
# Real-time variable monitoring
uv run watch_variables.py

# View variable change history
uv run history_viewer.py recent --hours 24
uv run history_viewer.py stats
uv run history_viewer.py export history.json -f json
```


## API Reference

```python
class NLMSession:
    def __init__(self, namespace=None, model=None, endpoint=None)
    
    # Python API with @prefix support
    def save(self, key, value)      # Use @key for global
    def get(self, key)               # Use @key for global
    def delete(self, key)            # Use @key for global
    def list_local()                 # Session variables
    def list_global()                # Global variables  
    def clear_local()                # Clear session vars
    
    # Natural language execution
    def execute(self, macro_content)
```

## Advanced Features

### Variable History Logging

```python
from variable_history import enable_logging, disable_logging, reset_logging

# Enable logging (default: OFF)
enable_logging()

# Your session operations will be logged
session = NLMSession(namespace="tracked")
session.save("data", "value")  # This change is logged

# Disable when done
disable_logging()

# Reset all history if needed  
reset_logging()
```

## Testing

```bash
# Run core tests
uv run tests/test_nlm_interpreter.py
uv run tests/test_variable_db_basic.py
uv run tests/test_at_prefix_api.py
uv run tests/test_global_sharing.py
```

## Configuration

Default settings (no configuration needed):
- Model: `gpt-oss:20b` (Local LLM via LMStudio)
- Endpoint: `http://localhost:1234/v1` for local, auto-configured for OpenAI
- Database: `variables.db`
- API Key: Auto-loaded from `.openai_key` file for OpenAI models

## Documentation

### 📚 Complete Documentation

- **[User Guide](docs/user_guide.md)** - Comprehensive usage guide with examples
- **[API Reference](docs/api_reference.md)** - Complete API documentation for developers
- **[Multi-Agent Guide](docs/multi_agent_guide.md)** - Multi-agent system patterns and usage
- **[Test Overview](tests/TEST_OVERVIEW.md)** - Test suite organization and priority guide
- **[Prompt Standards](docs/prompt_standards.md)** - Standard prompt writing conventions

### 📋 Quick References

- **Core Classes**: `NLMSession`, `SystemSession`, `BaseAgent`, `MultiAgentSystem`
- **Variable Syntax**: `{{variable}}` for macros, `@prefix` for global variables
- **Test Commands**: Use `uv run` for all Python script execution
- **Models**: `gpt-5`, `gpt-5-mini`, `gpt-5-nano` (OpenAI), `gpt-oss:20b` (Local)

## Requirements

- Python 3.7+
- [uv](https://github.com/astral-sh/uv) package manager (required)
- Dependencies managed via `uv sync` (includes OpenAI library)
- Ollama/LMStudio/OpenAI API endpoint
- SQLite (included with Python)

## Author

**Tadashi Wadayama**

## License

This project is licensed under the [MIT License](https://choosealicense.com/licenses/mit/).

Copyright (c) 2025 Tadashi Wadayama