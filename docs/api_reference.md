# NLM System API Reference

## Overview

This document provides comprehensive API reference for the NLM (Natural Language Macro) system. The NLM system provides a unified interface for natural language macro execution with session-based variable management and multi-agent coordination.

---

## 🔧 Core Classes

### 📋 NLMSession

> **Primary Interface** - Natural language macro execution and variable management
> 
> **Key Methods**: `save()`, `get()`, `execute()`, `list_local()`, `list_global()`

The primary interface for natural language macro execution and variable management.

#### Constructor

```python
NLMSession(namespace=None, model=None, endpoint=None)
```

**Parameters:**
- `namespace` (str, optional): Session namespace for variable isolation. Auto-generated if not provided.
- `model` (str, optional): LLM model name. Defaults to `"gpt-oss:20b"` (local).
- `endpoint` (str, optional): API endpoint URL. Auto-configured based on model.

**Supported Models:**
- `"gpt-5"` - OpenAI GPT-5 (Premium tier)
- `"gpt-5-mini"` - OpenAI GPT-5-mini (Standard tier) 
- `"gpt-5-nano"` - OpenAI GPT-5-nano (Economy tier)
- `"gpt-oss:20b"` - Local LLM via LMStudio (default)

**Example:**
```python
from nlm_interpreter import NLMSession

# Default session (local LLM)
session = NLMSession()

# Named session with OpenAI model
session = NLMSession(namespace="data_processing", model="gpt-5-mini")
```

#### Variable Management Methods

##### save(key, value)

Save a variable to the session or globally.

**Parameters:**
- `key` (str): Variable name. Use `@` prefix for global variables.
- `value` (any): Variable value (automatically serialized).

**Returns:** None

**Examples:**
```python
# Save local variable (session-scoped)
session.save("task_status", "processing")

# Save global variable (shared across all sessions)
session.save("@project_config", "production")
```

• • •

##### get(key)

Retrieve a variable value.

**Parameters:**
- `key` (str): Variable name. Use `@` prefix for global variables.

**Returns:** Variable value or None if not found

**Examples:**
```python
# Get local variable
status = session.get("task_status")  # Returns "processing"

# Get global variable
config = session.get("@project_config")  # Returns "production"
```

##### delete(key)

Delete a variable.

**Parameters:**
- `key` (str): Variable name. Use `@` prefix for global variables.

**Returns:** bool - True if variable was deleted, False if not found

**Examples:**
```python
# Delete local variable
session.delete("task_status")

# Delete global variable  
session.delete("@project_config")
```

• • •

##### list_local()

List all local variables in the session.

**Returns:** dict - Dictionary of local variables

**Example:**
```python
local_vars = session.list_local()
# Returns: {"task_status": "processing", "data_count": "1000"}
```

• • •

##### list_global()

List all global variables.

**Returns:** dict - Dictionary of global variables (without @ prefix)

**Example:**
```python
global_vars = session.list_global()
# Returns: {"project_config": "production", "last_update": "2024-01-15"}
```

• • •

##### clear_local()

Clear all local variables in the session.

**Returns:** None

**Example:**
```python
session.clear_local()
```

• • •

#### Natural Language Execution

##### execute(macro_content)

Execute natural language macro commands.

**Parameters:**
- `macro_content` (str): Natural language macro text with `{{variable}}` syntax

**Returns:** str - LLM response or execution result

**Examples:**
```python
# Simple variable assignment
result = session.execute("Save 'Hello World' to {{greeting}}")

# Complex operations
result = session.execute("""
Process the data in {{input_file}} and:
1. Clean the data
2. Calculate statistics  
3. Save results to {{@analysis_results}}
""")

# Multi-variable operations
result = session.execute("Set {{name}} to 'Alice' and {{age}} to '30'")
```

• • •

#### Configuration Methods

##### set_reasoning_effort(effort)

Set the reasoning effort level for LLM processing.

**Parameters:**
- `effort` (str): One of `"minimal"`, `"low"`, `"medium"`, `"high"`

**Example:**
```python
session.set_reasoning_effort("low")  # Faster processing
```

• • •

##### set_verbosity(level)

Set the verbosity level for LLM responses (OpenAI models only).

**Parameters:**
- `level` (str): One of `"low"`, `"medium"`, `"high"`

**Example:**
```python
session.set_verbosity("low")  # More concise responses
```

• • •

#### Long-term Memory Methods

##### append(key, value, separator="\\n")

Append string to existing variable for experience accumulation.

**Parameters:**
- `key` (str): Variable name (use `@key` for global variables)
- `value` (str): String value to append
- `separator` (str): Separator between entries (default: newline)

**Examples:**
```python
# Build experience log
session.append("decisions", "Choice A → Success")
session.append("decisions", "Choice B → Failure")

# Use custom separator
session.append("tags", "python", separator=", ")
session.append("tags", "ai", separator=", ")  # Result: "python, ai"
```

• • •

##### append_with_timestamp(key, value)

Append string to variable with automatic timestamp prefix.

**Parameters:**
- `key` (str): Variable name
- `value` (str): String value to append

**Examples:**
```python
session.append_with_timestamp("audit", "User logged in")
session.append_with_timestamp("audit", "Data updated")
# Creates: "[2024-01-11T10:30:45] User logged in\\n[2024-01-11T10:31:12] Data updated"
```

• • •

##### get_tail(key, n_lines=10, separator="\\n")

Get last N lines of a variable efficiently (prevents memory bloat).

**Parameters:**
- `key` (str): Variable name
- `n_lines` (int): Number of recent lines to retrieve (default: 10)
- `separator` (str): Line separator (default: newline)

**Returns:** str - Last N lines as string

**Examples:**
```python
# Get recent experiences for decision-making
recent_log = session.get_tail("experience_log", n_lines=5)

# Get recent tags
recent_tags = session.get_tail("tag_list", n_lines=3, separator=", ")
```

• • •

##### count_lines(key, separator="\\n")

Count lines/entries in a variable.

**Parameters:**
- `key` (str): Variable name
- `separator` (str): Line separator (default: newline)

**Returns:** int - Number of lines/entries

**Examples:**
```python
# Check experience count
total_decisions = session.count_lines("decisions")

# Count comma-separated items
tag_count = session.count_lines("tags", separator=", ")
```

• • •

##### save_to_file(key, filename, mode='w')

Save variable content to file for persistence.

**Parameters:**
- `key` (str): Variable name
- `filename` (str): Target file path
- `mode` (str): File mode - 'w' (overwrite) or 'a' (append)

**Returns:** bool - True if successful

**Examples:**
```python
# Save agent memory to file
success = session.save_to_file("long_term_memory", "data/agent_memory.txt")

# Append to log file
session.save_to_file("daily_log", "logs/today.log", mode='a')
```

• • •

##### load_from_file(key, filename, append=False)

Load content from file to variable.

**Parameters:**
- `key` (str): Variable name
- `filename` (str): Source file path
- `append` (bool): If True, append to existing variable; if False, overwrite

**Returns:** bool - True if successful

**Examples:**
```python
# Restore agent memory on startup
success = session.load_from_file("memory", "data/agent_memory.txt")

# Append external data to existing variable
session.load_from_file("knowledge", "external_data.txt", append=True)
```

---

### 🌐 SystemSession

> **Unified Global Access** - Enhanced global variable handling with automatic @-prefix
> 
> **Key Features**: Auto @-prefix handling, clean key listing, context manager support

A specialized session class providing unified global variable access with `@`-prefix syntax consistency.

#### Constructor

```python
SystemSession()
```

Inherits all NLMSession functionality with enhanced global variable handling.

#### Enhanced Global Variable Methods

##### set_global(key, value)

Set a global variable with automatic `@` prefix handling.

**Parameters:**
- `key` (str): Variable name (with or without `@` prefix)
- `value` (any): Variable value

**Examples:**
```python
from system_session import SystemSession

system = SystemSession()

# Both work the same - auto @-prefix
system.set_global("config", "production")     # Becomes @config
system.set_global("@status", "active")       # Already has @prefix
```

##### get_global(key)

Get a global variable with automatic `@` prefix handling.

**Parameters:**
- `key` (str): Variable name (with or without `@` prefix)

**Returns:** Variable value or None

**Examples:**
```python
# Both work the same
value1 = system.get_global("config")     # Gets @config
value2 = system.get_global("@config")    # Gets @config
```

##### list_globals()

List all global variables with clean keys (without `@` prefix).

**Returns:** dict - Global variables with clean keys

**Example:**
```python
globals_dict = system.list_globals()
# Returns: {"config": "production", "status": "active"}
```

#### Context Manager Support

```python
with SystemSession() as system:
    system.set_global("temp_var", "value")
    system.execute("Process {{@temp_var}}")
    # Automatic cleanup
```

---

## 🤖 Multi-Agent System Classes

### 🏷️ BaseAgent

> **Abstract Base Class** - Foundation for creating custom agents
> 
> **Key Methods**: `run()` (abstract), `set_status()`, `execute_macro()`

Base class for creating custom agents.

#### Constructor

```python
BaseAgent(agent_id, model=None, **session_kwargs)
```

**Parameters:**
- `agent_id` (str): Unique identifier for the agent
- `model` (str, optional): LLM model for the agent's session
- `**session_kwargs`: Additional arguments passed to NLMSession

#### Abstract Methods

##### run()

Execute the agent's main logic. Must be implemented by subclasses.

**Returns:** any - Agent execution result

**Example:**
```python
from agent_base import BaseAgent

class CustomAgent(BaseAgent):
    def __init__(self, agent_id, task_description):
        super().__init__(agent_id)
        self.task_description = task_description
        
    def run(self):
        self.set_status("working")
        result = self.execute_macro(f"Execute: {self.task_description}")
        self.set_status("completed")
        return result
```

#### Utility Methods

##### set_status(status)

Set the agent's status in its session.

**Parameters:**
- `status` (str): Status description

##### get_status()

Get the current agent status.

**Returns:** str - Current status

##### execute_macro(macro_text)

Execute a natural language macro.

**Parameters:**
- `macro_text` (str): Macro text with `{{variable}}` syntax

**Returns:** str - Execution result

---

### ⚡ MultiAgentSystem

> **Agent Orchestration** - System for coordinating multiple agents
> 
> **Key Methods**: `add_agent()`, `run_sequential()`, `run_parallel()`

System for coordinating multiple agents.

#### Constructor

```python
MultiAgentSystem(system_id)
```

**Parameters:**
- `system_id` (str): Unique identifier for the agent system

#### Agent Management

##### add_agent(agent)

Add an agent to the system.

**Parameters:**
- `agent` (BaseAgent): Agent instance to add

##### remove_agent(agent_id)

Remove an agent by ID.

**Parameters:**
- `agent_id` (str): Agent ID to remove

**Returns:** bool - True if removed, False if not found

##### get_agent(agent_id)

Get an agent by ID.

**Parameters:**
- `agent_id` (str): Agent ID to retrieve

**Returns:** BaseAgent or None

#### Execution Methods

##### run_sequential()

Execute all agents sequentially.

**Returns:** dict - Execution results with `"successful"` and `"failed"` counts

##### run_parallel()

Execute all agents in parallel.

**Returns:** dict - Execution results with `"successful"` and `"failed"` counts

**Example:**
```python
from multi_agent_system import MultiAgentSystem

system = MultiAgentSystem("data_pipeline")
system.add_agent(CustomAgent("worker1", "Process dataset A"))
system.add_agent(CustomAgent("worker2", "Process dataset B"))

# Execute agents
results = system.run_parallel()
print(f"Completed: {results['successful']}, Failed: {results['failed']}")
```

---

## 🛠️ Built-in Agent Types

### 📊 DataCollectorAgent

> **Data Collection** - One-time execution agent for data gathering tasks

One-time execution agent for data collection tasks.

```python
from agent_examples import DataCollectorAgent

collector = DataCollectorAgent("collector1", "database_source")
result = collector.run()
```

### 📈 MonitorAgent

> **System Monitoring** - Continuous execution agent for system monitoring

Continuous execution agent for system monitoring.

```python
from agent_examples import MonitorAgent

monitor = MonitorAgent("monitor1", check_interval=5.0)
# Run in background thread
```

### 🔬 ResearchAgent

> **Research Workflows** - Multi-phase execution agent for research tasks

Multi-phase execution agent for research workflows.

```python
from agent_examples import ResearchAgent

researcher = ResearchAgent("researcher1", "AI trends analysis")
result = researcher.run()  # Executes all research phases
```

### 👥 CoordinatorAgent

> **Agent Management** - Agent for managing and coordinating other agents

Agent for managing and coordinating other agents.

```python
from agent_examples import CoordinatorAgent

coordinator = CoordinatorAgent("coord1", "team_management")
coordinator.run()  # Manages team coordination
```

---

## 🔧 Utility Functions

### nlm_execute(macro_content, namespace=None)

Simple function interface for executing natural language macros.

**Parameters:**
- `macro_content` (str): Natural language macro text
- `namespace` (str, optional): Session namespace

**Returns:** str - Execution result

**Example:**
```python
from nlm_interpreter import nlm_execute

result = nlm_execute("Save 'test data' to {{sample_data}}")
```

• • •

## 📜 Variable History Functions

### enable_logging()

Enable variable change history logging.

**Example:**
```python
from variable_history import enable_logging
enable_logging()
```

• • •

### disable_logging()

Disable variable change history logging.

• • •

### reset_logging()

Reset/clear all variable change history.

---

## ⚙️ Configuration

### Default Settings

- **Model**: `"gpt-oss:20b"` (Local LLM)
- **Endpoint**: `http://localhost:1234/v1` (LMStudio default)
- **Database**: `variables.db` (SQLite)
- **History Logging**: Disabled by default

### OpenAI API Setup

Create an API key file in one of these locations:
- Project-specific: `.openai_key` (current directory)
- User-wide: `~/.config/nlm/openai_key`

---

## ⚠️ Error Handling

### Common Exceptions

- `ConnectionError`: API endpoint unreachable
- `AuthenticationError`: Invalid API key (OpenAI models)
- `ValueError`: Invalid parameter values
- `KeyError`: Variable not found (when expected)

### Best Practices

1. Always check return values for `None`
2. Use try-catch blocks for API calls
3. Validate variable names before operations
4. Handle session cleanup in long-running applications

---

## 📝 Examples

### Basic Usage

```python
from nlm_interpreter import NLMSession

# Create session
session = NLMSession(namespace="example")

# Basic operations
session.save("user_name", "Alice")
session.execute("Greet {{user_name}} and save response to {{greeting}}")
greeting = session.get("greeting")

print(f"Greeting: {greeting}")
```

### Multi-Session Coordination

```python
# Session 1: Data preparation
data_session = NLMSession(namespace="data_prep")
data_session.save("@pipeline_status", "data_ready")

# Session 2: Processing
process_session = NLMSession(namespace="processing") 
status = process_session.get("@pipeline_status")  # "data_ready"
process_session.execute("Begin processing since {{@pipeline_status}} is ready")
```

### Multi-Agent Workflow

```python
from multi_agent_system import MultiAgentSystem
from agent_examples import DataCollectorAgent, ResearchAgent

# Create system
system = MultiAgentSystem("research_project")

# Add agents
system.add_agent(DataCollectorAgent("collector", "research_database"))
system.add_agent(ResearchAgent("analyst", "market_trends"))

# Execute workflow
results = system.run_sequential()
```

This API reference covers the complete NLM system interface. For usage examples and tutorials, see the [User Guide](user_guide.md) and [Multi-Agent Guide](multi_agent_guide.md).