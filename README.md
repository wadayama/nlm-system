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

## Configuration

Default settings work out-of-the-box:
- Model: `gpt-oss:20b`  
- Endpoint: `http://localhost:1234/v1` (LMStudio)
- Database: `variables.db`

Optional environment variables (only if using different LLM setup):
```bash
export NLM_MODEL="llama3.1:8b"
export NLM_ENDPOINT="http://localhost:11434/v1"  # For Ollama
```

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