# NLM System - Detailed Documentation

## Table of Contents

1. [Understanding Namespaces](#understanding-namespaces)
2. [Direct Full-Name Access](#direct-full-name-access)
3. [Advanced Cross-Session Operations](#advanced-cross-session-operations)
4. [Configuration](#configuration)
5. [Variable History Logging](#variable-history-logging)
6. [History Viewer](#history-viewer)
7. [Natural Language Macro Examples](#natural-language-macro-examples)
8. [Batch Macro File Execution](#batch-macro-file-execution)
9. [Interactive Natural Language Sessions](#interactive-natural-language-sessions)
10. [Architecture](#architecture)
11. [Multi-Agent System Design](#multi-agent-system-design)

## Understanding Namespaces

Each session operates within its own namespace, providing automatic variable isolation:

```python
# Create two different sessions
session1 = NLMSession(namespace="data_team")
session2 = NLMSession(namespace="ml_team")

# Each session can have variables with the same name
session1.save("status", "collecting_data")
session2.save("status", "training_model")

# Variables are automatically isolated
print(session1.get("status"))  # "collecting_data"
print(session2.get("status"))  # "training_model"

# Behind the scenes, these are stored as:
# "data_team:status" = "collecting_data"
# "ml_team:status" = "training_model"
```

**Global variables bypass namespaces:**
```python
# Global variables are shared across all sessions
session1.save("@project_deadline", "2024-12-31")
session2.save("@budget_approved", True)

# Both sessions can access all global variables
print(session1.get("@project_deadline"))  # "2024-12-31"
print(session1.get("@budget_approved"))   # True
print(session2.get("@project_deadline"))  # "2024-12-31"
print(session2.get("@budget_approved"))   # True

# Behind the scenes, these are stored as:
# "global:project_deadline" = "2024-12-31"
# "global:budget_approved" = True
```

**SystemSession - Unified Global Variable Access:**

For cleaner global variable management with consistent @-prefixed syntax:

```python
from system_session import SystemSession

# SystemSession provides unified @-syntax for both Python and natural language
system = SystemSession()

# Set global variables - both styles work identically
system.set_global("project_deadline", "2024-12-31")    # Auto @-prefix
system.set_global("@budget_approved", "true")          # Explicit @-prefix

# Get global variables - consistent interface
deadline = system.get_global("project_deadline")       # Returns "2024-12-31"
approved = system.get_global("@budget_approved")       # Returns "true"

# Natural language macros use the same @-syntax
system.execute("Save 'completed' to {{@task_status}}")
status = system.get_global("task_status")              # Returns "completed"

# Interface consistency between natural language and Python:
# Natural Language: {{@variable_name}}
# Python:          system.get_global("variable_name")
# Both access the same underlying global:variable_name storage

# List all global variables with clean display
globals_dict = system.list_globals()
# Returns: {"project_deadline": "2024-12-31", "budget_approved": "true", "task_status": "completed"}

# SystemSession inherits all NLMSession functionality
system.set_reasoning_effort("high")
system.execute("Process the data using configuration from {{@config}}")
system.reset_context()  # Clear conversation history
```

**Key SystemSession Benefits:**
- **Interface Consistency**: Natural language `{{@var}}` matches Python `system.get_global("var")`
- **Reduced Cognitive Load**: Single @-prefixed syntax pattern across all interfaces
- **Auto @-Handling**: `set_global("var")` automatically becomes `@var` internally
- **Full Inheritance**: All NLMSession features (execute, settings, context) work unchanged
- **Backward Compatible**: Existing NLMSession code continues to work

**Namespace isolation prevents conflicts:**
```python
# Different teams can work independently
data_session = NLMSession(namespace="data_processing")
model_session = NLMSession(namespace="model_training")
web_session = NLMSession(namespace="web_api")

# Each team has their own "config" without conflicts
data_session.save("config", "csv_parser_settings")
model_session.save("config", "neural_network_params") 
web_session.save("config", "flask_app_settings")

# Each team sees only their own config
print(data_session.get("config"))   # "csv_parser_settings"
print(model_session.get("config"))  # "neural_network_params"
print(web_session.get("config"))    # "flask_app_settings"
```

## Direct Full-Name Access

You can also work directly with full variable names using the underlying database:

```python
from variable_db import VariableDB

# Direct database access
db = VariableDB("variables.db")

# Save using full namespace:variable format
db.save_variable("team_alpha:task_status", "in_progress")
db.save_variable("team_beta:task_status", "completed")
db.save_variable("global:project_phase", "testing")

# Retrieve using full names
alpha_status = db.get_variable("team_alpha:task_status")
beta_status = db.get_variable("team_beta:task_status")
phase = db.get_variable("global:project_phase")

print(alpha_status)  # "in_progress"
print(beta_status)   # "completed"
print(phase)         # "testing"

# Cross-session access using sessions
session_alpha = NLMSession(namespace="team_alpha")
session_beta = NLMSession(namespace="team_beta")

# Session can access its own variables normally
print(session_alpha.get("task_status"))  # "in_progress"

# Or access other session's variables using the session's variable_db
other_status = session_alpha.variable_db.get_variable("team_beta:task_status")
print(other_status)  # "completed"

# List all variables to see the full names
all_vars = db.list_variables()
for full_name, value in all_vars.items():
    if "task_status" in full_name:
        print(f"{full_name}: {value}")
# Output:
# team_alpha:task_status: in_progress
# team_beta:task_status: completed
```

## Advanced Cross-Session Operations

```python
# Create multiple sessions
collector = NLMSession(namespace="data_collector")
analyzer = NLMSession(namespace="data_analyzer")
reporter = NLMSession(namespace="report_generator")

# Each saves their status
collector.save("status", "collecting")
analyzer.save("status", "waiting")
reporter.save("status", "idle")

# Monitor all team statuses from any session
def check_all_team_status():
    db = VariableDB("variables.db")
    statuses = {}
    
    # Access each team's status using full names
    statuses["collector"] = db.get_variable("data_collector:status")
    statuses["analyzer"] = db.get_variable("data_analyzer:status") 
    statuses["reporter"] = db.get_variable("report_generator:status")
    
    return statuses

# Check status from any context
team_status = check_all_team_status()
print(team_status)
# {'collector': 'collecting', 'analyzer': 'waiting', 'reporter': 'idle'}

# Update cross-team coordination
coordinator_session = NLMSession(namespace="coordinator")

# Coordinator can check specific team status
collector_status = coordinator_session.variable_db.get_variable("data_collector:status")
if collector_status == "collecting":
    # Update global coordination state
    coordinator_session.save("@collection_in_progress", "true")
    print(coordinator_session.get("@collection_in_progress"))  # "true"
```

## Configuration

Priority order: Command line > Environment variables > Defaults

### Environment Variables
```bash
export NLM_MODEL="llama3.1:8b"
export NLM_ENDPOINT="http://localhost:11434/v1"
```

### Default Settings
- Model: `gpt-oss:20b`
- Endpoint: `http://localhost:1234/v1` (LMStudio)
- Database: `variables.db`

Note: For Ollama, use `-e http://localhost:11434/v1`

## Variable History Logging

The NLM System includes comprehensive logging of all variable changes with user-controlled activation.

### Logging Control

By default, logging is **disabled** to prevent unnecessary data accumulation. Enable it programmatically when needed:

```python
from variable_history import enable_logging, disable_logging, reset_logging, is_logging_enabled

# Enable logging for this session
enable_logging()

# Check if logging is active
if is_logging_enabled():
    print("Logging is active")

# Reset all logged history
reset_logging()  # Clears all history records

# Disable logging
disable_logging()
```

### Session-based Logging

When logging is enabled, all variable changes are automatically tracked:

```python
from variable_history import enable_logging
from nlm_interpreter import NLMSession

# Enable logging
enable_logging()

# Create sessions - all changes will be logged
session1 = NLMSession(namespace="agent1")
session2 = NLMSession(namespace="agent2")

# All these operations will be logged when logging is enabled
session1.save("task", "data_processing")  # Logged
session1.save("@config", "production")    # Logged  
session2.get("@config")                   # No log (read operations)
session1.delete("task")                   # Logged (deletion)
```

## History Viewer

View and analyze variable change history:

```bash
# Show recent changes
uv run history_viewer.py recent --hours 24

# Show history for specific namespace
uv run history_viewer.py history -n my_session

# Show statistics
uv run history_viewer.py stats

# Search for changes
uv run history_viewer.py search "Alice"

# Export to file
uv run history_viewer.py export history.json -f json
```

## Natural Language Macro Examples

### Basic Variable Operations

```python
# Create a session for natural language macros
session = NLMSession(namespace="demo")

# Saving data with natural language
session.execute("Save the user name 'Alice' to {{current_user}}")
session.execute("Store today's date in {{processing_date}}")
session.execute("Set the status to 'active' in {{user_status}}")

# Flexible ways to save the same information
session.execute("Put 'machine_learning' into {{analysis_type}}")
session.execute("Remember that the model accuracy is '94.2%' as {{model_score}}")
session.execute("Keep the file location '/data/results.csv' in {{output_path}}")

# Reading variables with natural language - verify saved values
print(session.get("current_user"))     # "Alice"
print(session.get("processing_date"))  # Saved date
print(session.get("model_score"))      # "94.2%"
print(session.get("output_path"))      # "/data/results.csv"

# Global variables for cross-session sharing
session.execute("Save the project name 'AI Research 2024' to global {{@project}}")
print(session.get("@project"))  # "AI Research 2024"

session.execute("Set {{@environment}} to 'development'")
print(session.get("@environment"))  # "development"

session.execute("Store the API key 'secret123' in {{@api_credentials}}")
print(session.get("@api_credentials"))  # "secret123"
```

### Advanced Natural Language Processing

```python
# Conditional operations
session.execute("If {{@environment}} is production, get {{@prod_settings}}")
session.execute("When {{user_status}} is active, retrieve {{user_preferences}}")

# Batch operations
session.execute("Save multiple values: name 'Bob' to {{user}}, age '25' to {{age}}, role 'admin' to {{role}}")
session.execute("Show me all variables related to user")

# Data transformation
session.execute("Copy {{temp_result}} to {{@final_result}}")
session.execute("Move the value from {{local_config}} to global {{@shared_config}}")

# Cleanup operations
session.execute("Delete all temporary variables starting with 'temp_'")
session.execute("Clear all my local variables but keep globals")
session.execute("Remove {{old_data}} and {{backup_file}}")

# Information queries
session.execute("List all my variables")
session.execute("Show me only global variables")
session.execute("Count how many variables I have")
```

## Batch Macro File Execution

The NLM System supports executing multiple macros from Markdown files, enabling complex workflows and reusable scripts.

### File Format

Macro files use Markdown format (`.md`) where each paragraph is treated as a separate macro instruction:

**basic_workflow.md:**
```markdown
# Basic Data Processing Workflow

Save the input file path '/data/raw_data.csv' to {{input_file}}

Store the processing method 'clean_and_transform' in {{method}}

Set the output directory '/data/processed' in {{output_dir}}

Save project metadata 'Data Cleaning Project' to global {{@project_name}}

Set global processing status to 'started' in {{@status}}

Get {{input_file}} and {{method}} to confirm configuration

Show me the current global {{@project_name}} and {{@status}}
```

### Execution Methods

**Command Line:**
```bash
# Execute a macro file
uv run nlm_interpreter.py -f basic_workflow.md

# Execute with custom model/endpoint
uv run nlm_interpreter.py -f workflow.md -m llama3.1:8b -e http://localhost:11434/v1

# Execute with specific namespace
uv run nlm_interpreter.py -f setup.md --namespace "production_setup"
```

**Python API:**
```python
from nlm_interpreter import NLMSession

# Execute macro file in a session
session = NLMSession(namespace="batch_processing")

# Read and execute file content
with open("workflow.md", "r") as f:
    macro_content = f.read()
    session.execute(macro_content)

# Check results using Python API
project_name = session.get("@project_name")
status = session.get("@status")
print(f"Project: {project_name}, Status: {status}")
```

### Advanced Macro Files

**research_experiment.md:**
```markdown
# Research Experiment Setup

## Initial Configuration
Save experiment name 'Neural Network Classification' to {{experiment_name}}
Set model type to 'ResNet-50' in {{model_type}}
Store learning rate '0.001' in {{learning_rate}}
Save batch size '32' to {{batch_size}}

## Global Experiment Tracking
Save current experiment ID 'EXP_2024_001' to global {{@current_experiment}}
Set global experiment status to 'initializing' in {{@experiment_status}}
Store researcher name 'Dr. Smith' in global {{@researcher}}

## Data Configuration  
Save training data path '/data/train.csv' to {{train_data}}
Set validation split to '0.2' in {{validation_split}}
Store test data location '/data/test.csv' in {{test_data}}

## Model Configuration
If {{model_type}} is ResNet-50, save '/models/resnet50.pth' to {{model_path}}
Set optimizer to 'Adam' in {{optimizer}}
Save loss function 'CrossEntropyLoss' to {{loss_function}}

## Verification
Show me all my experiment variables
Get the global {{@current_experiment}} and {{@experiment_status}}
List all variables containing 'data'

## Start Training
Update global status: set {{@experiment_status}} to 'training'
Save current timestamp to {{@training_start_time}}
```

### File Organization

**Project Structure:**
```
project/
├── macros/
│   ├── setup/
│   │   ├── environment.md
│   │   └── database.md
│   ├── workflows/
│   │   ├── data_processing.md
│   │   ├── model_training.md
│   │   └── evaluation.md
│   └── cleanup/
│       └── reset.md
└── nlm_interpreter.py
```

**Sequential Execution:**
```bash
# Execute setup macros
uv run nlm_interpreter.py -f macros/setup/environment.md
uv run nlm_interpreter.py -f macros/setup/database.md

# Run main workflows
uv run nlm_interpreter.py -f macros/workflows/data_processing.md
uv run nlm_interpreter.py -f macros/workflows/model_training.md
uv run nlm_interpreter.py -f macros/workflows/evaluation.md

# Cleanup
uv run nlm_interpreter.py -f macros/cleanup/reset.md
```

### Best Practices

**1. Use Clear Headers:**
```markdown
# Main Task Description

## Subtask 1: Configuration
Save config value 'production' to {{@environment}}

## Subtask 2: Processing  
Process the data using {{method}}

## Subtask 3: Results
Save results to {{@final_output}}
```

**2. Include Verification Steps:**
```markdown
# Task Execution

Save important data to {{key_variable}}

# Verify the save worked
Get {{key_variable}} and confirm the value
```

**3. Use Global Variables for Coordination:**
```markdown
# Agent Coordination

Save my status 'active' to global {{@agent_1_status}}
Check global {{@system_ready}} before proceeding
Update global {{@task_progress}} with my contribution
```

## Interactive Natural Language Sessions

```python
# Research workflow with natural language
research_session = NLMSession(namespace="research")

research_session.execute("Start a new experiment by saving 'neural_network' to {{model_type}}")
research_session.execute("Set the learning rate to '0.001' in {{lr}}")
research_session.execute("Remember the batch size as '32' in {{batch_size}}")

# Share progress globally
research_session.execute("Update global status: save 'training' to {{@experiment_status}}")
research_session.execute("Store current model 'ResNet-50' in {{@active_model}}")

# Check and report
print("Current experiment settings:")
print(f"Model: {research_session.get('model_type')}")  # "neural_network"
print(f"Learning rate: {research_session.get('lr')}")  # "0.001"
print(f"Batch size: {research_session.get('batch_size')}")  # "32"

print("Global status:")
print(f"Experiment: {research_session.get('@experiment_status')}")  # "training"
print(f"Model: {research_session.get('@active_model')}")  # "ResNet-50"

# Update results
research_session.execute("Save the final accuracy '96.3%' to {{final_accuracy}}")
print(research_session.get("final_accuracy"))  # "96.3%"

research_session.execute("Update {{@experiment_status}} to 'completed'")
print(research_session.get("@experiment_status"))  # "completed"
```

## Architecture

The NLM System follows an orchestrator pattern with **externalized state management** as a core design principle:

### System Architecture Components

- **Python handles**: Control flow, data persistence, namespace management, variable expansion
- **Natural language macros handle**: Ambiguity processing, common sense judgment, dynamic variable operations
- **SQLite database**: Centralized state store with ACID properties
- **Namespace system**: Automatic agent isolation with controlled sharing
- **Unified syntax**: `@prefix` for global variables works identically in both NLM and Python
- **Clean separation**: Traditional programming for deterministic operations, NLM for human-like reasoning

## Multi-Agent System Design

### Multi-Agent System Design Pattern

**The NLM System provides an ideal architecture for multi-agent systems:**

- **Individual Sessions**: Each agent has its own session/context with isolated namespace
- **Local Agent State**: Private agent state stored as local variables (`agent.save("status", "working")`)
- **Inter-Agent Communication**: Asynchronous messaging via global variables (`@msg_*`, `@event_*`)
- **Shared Environment**: Observable environment state through global variables (`@world_state`, `@resources`)
- **External Persistence**: All state externalized to database for crash resilience and monitoring

### Multi-Agent System Benefits

**Traditional approach (problematic):**
```python
class Agent:
    def __init__(self):
        self.status = "idle"          # Internal state - invisible to others
        self.current_task = None      # Lost if agent crashes
        self.progress = 0            # No coordination possible
```

**NLM System approach (externalized):**
```python
class Agent:
    def __init__(self, agent_id):
        self.session = NLMSession(namespace=agent_id)
        # All state externalized - no internal state variables
    
    def set_status(self, status):
        self.session.save("status", status)           # Persistent & visible
        
    def get_status(self):
        return self.session.get("status")             # Always current
        
    def coordinate_with_global(self, key, value):
        self.session.save(f"@{key}", value)           # Share with all agents
```

### Practical Multi-Agent Example

```python
class Agent:
    def __init__(self, agent_id):
        # Each agent gets its own session/context
        self.session = NLMSession(namespace=agent_id)
        self.agent_id = agent_id
    
    def update_local_state(self, key, value):
        # Private agent state - not visible to other agents
        self.session.save(key, value)
    
    def observe_environment(self):
        # Read shared environment state
        world_state = self.session.get("@world_temperature")
        resources = self.session.get("@available_resources") 
        return world_state, resources
    
    def send_message(self, recipient, message):
        # Asynchronous inter-agent communication
        self.session.save(f"@msg_{self.agent_id}_to_{recipient}", message)
    
    def check_messages(self):
        # Check for incoming messages
        return self.session.get(f"@msg_any_to_{self.agent_id}")

# Usage example
agent1 = Agent("explorer")
agent2 = Agent("collector")

# Local state management
agent1.update_local_state("current_location", "forest")
agent2.update_local_state("inventory", "empty")

# Environment observation (shared state)
agent1.session.save("@world_temperature", "25°C")
agent2.session.save("@available_resources", "water, food")

# Inter-agent communication
agent1.send_message("collector", "Found resource location at coordinates 10,20")
message = agent2.check_messages()
```

### Inter-Agent Communication

**Agents communicate through global variables**, enabling various coordination patterns:

```python
# Direct messaging between agents
sender = NLMSession(namespace="agent_a")
receiver = NLMSession(namespace="agent_b")

# Send message
sender.save("@msg_to_agent_b", "Processing complete. Ready for next step.")

# Receive message  
message = receiver.get("@msg_to_agent_b")
print(message)  # "Processing complete. Ready for next step."
```

**Common communication patterns:**
- **Point-to-Point**: `@msg_sender_to_recipient`
- **Broadcast**: `@broadcast_message` with timestamp counters
- **Task Queue**: `@task_queue_item_*` for work distribution  
- **Event System**: `@event_type_latest` for event-driven coordination
- **Status Sharing**: `@system_phase`, `@coordinator_status` for state synchronization

For detailed implementation examples, see the `/examples` directory.

This design provides the reliability of traditional programming with the flexibility of natural language processing, while enabling **sophisticated inter-agent communication patterns** through the shared global variable space.