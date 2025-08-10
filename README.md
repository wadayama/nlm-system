# NLM System - Natural Language Macro Interpreter

A Python orchestrator for natural language macros with unified variable syntax, session management, and OpenAI-compatible API integration.

## Features

- **Natural Language Macros**: Execute human-like instructions with `{{variable}}` syntax
- **Unified Variable Syntax**: `@prefix` for global variables across NLM and Python
- **Session-based Architecture**: Isolated namespaces with controlled sharing
- **Multi-Agent Support**: Externalized state for distributed agent systems
- **OpenAI-compatible**: Works with Ollama, LMStudio, and OpenAI APIs

## Quick Start

```bash
pip install openai
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

For detailed multi-agent usage, see [docs/multi_agent_user_guide.md](docs/multi_agent_user_guide.md)

## Executing Multi-line Macro Files

### From Python Code

```python
from nlm_interpreter import NLMSession
from pathlib import Path

# Create a session
session = NLMSession(namespace="workflow")

# Read and execute a multi-line macro file
macro_file = Path("macros/data_pipeline.md")
macro_content = macro_file.read_text()

# Execute the entire macro file
result = session.execute(macro_content)
print(f"Execution result: {result}")

# Check the variables that were set
print(f"Pipeline status: {session.get('@pipeline_status')}")
print(f"Output file: {session.get('output_file')}")
```

Example macro file (`macros/data_pipeline.md`):
```markdown
Initialize data processing pipeline.

Save 'started' to {{@pipeline_status}}.
Set {{input_file}} to '/data/raw/dataset.csv'.
Set {{output_file}} to '/data/processed/clean_data.csv'.

Process the file {{input_file}} and save results to {{output_file}}.
Update {{@pipeline_status}} to 'completed'.
Save current timestamp to {{@last_run}}.
```

### Batch Processing Multiple Macro Files

```python
from nlm_interpreter import NLMSession
from pathlib import Path

session = NLMSession(namespace="batch_process")

# Process all macro files in a directory
macro_dir = Path("macros")
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

## Command Line Usage

```bash
# Execute natural language macros
python nlm_interpreter.py "Save 'production' to {{@environment}}"

# Execute from file
python nlm_interpreter.py -f macros/workflow.md

# Custom model/endpoint
python nlm_interpreter.py -m llama3.1:8b -e http://localhost:11434/v1 "Save today to {{@date}}"
```

## Helper Tools

```bash
# Real-time variable monitoring
python watch_variables.py

# View variable change history
python history_viewer.py recent --hours 24
python history_viewer.py stats
python history_viewer.py export history.json -f json
```

## Variable History Logging

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

## Testing

```bash
# Run core tests
python tests/test_nlm_interpreter.py
python tests/test_variable_db_basic.py
python tests/test_at_prefix_api.py
python tests/test_global_sharing.py
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
python setup_openai.py

# Or check current setup
python setup_openai.py check
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
python nlm_interpreter.py -m gpt-5 "Save 'test' to {{var}}"
python nlm_interpreter.py -m gpt-5-mini "{{name}}を表示してください"
python nlm_interpreter.py -m gpt-5-nano "Quick task: {{task}}"

# Local model (default - no API key needed)
python nlm_interpreter.py "Save 'test' to {{var}}"
python nlm_interpreter.py -m gpt-oss:20b "Save 'test' to {{var}}"
```

## Configuration

Default settings (no configuration needed):
- Model: `gpt-oss:20b` (Local LLM via LMStudio)
- Endpoint: `http://localhost:1234/v1` for local, auto-configured for OpenAI
- Database: `variables.db`
- API Key: Auto-loaded from `.openai_key` file for OpenAI models

## Documentation

For detailed documentation including:
- Advanced usage examples
- Multi-agent architecture patterns
- Batch macro file execution
- History viewer usage
- System architecture details

See [docs/detailed_documentation.md](docs/detailed_documentation.md)

## Requirements

- Python 3.7+
- OpenAI library (`pip install openai`)
- Ollama/LMStudio/OpenAI API endpoint
- SQLite (included with Python)

## License

This project is provided as-is for educational and research purposes.