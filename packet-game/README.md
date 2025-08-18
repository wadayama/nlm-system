# LLM Direct Selection Packet Scheduler

An intelligent packet scheduling system where an LLM autonomously selects packets from 4 queues each turn, demonstrating emergent optimization strategies without predefined rules. Now with variable slot availability and future prediction capabilities.

## Quick Start

```bash
# Run the fixed 3-slot scheduler
uv run llm_direct_scheduler.py

# Run the variable slot scheduler (1-4 slots with prediction)
uv run variable_slot_scheduler.py

# Custom probability distribution for slots
uv run variable_slot_scheduler.py -p 0.1 0.2 0.5 0.2  # Favors 3 slots

# Natural language strategy instructions
uv run variable_slot_scheduler.py -s "Deadline priority, never let packets expire!"
uv run llm_direct_scheduler.py -s "High-value packets first, maximize total value"
```

The system will:
1. Initialize 4 queues with 3 packets each
2. Run for 20 turns with LLM making decisions each turn
3. Display step-by-step reasoning and queue states
4. Show final performance statistics

## System Overview

### Core Concept
- **4 packet queues** with size limit of 5 (overflow penalties apply)
- **Variable or fixed slots**: 3 fixed slots OR 1-4 variable slots per turn
- **Future prediction**: LLM sees next turn's slot availability (variable mode)
- **Natural language strategy**: Custom user instructions guide LLM decisions
- **Dynamic packet properties**: value (1-10), deadline (5-15)
- **Real-time adaptation** based on queue states and urgency

### LLM Decision Process
Each turn, the LLM:
1. Receives user strategy instruction (if provided)
2. Observes all queue states with packet details
3. Sees current and next turn slot availability (variable mode)
4. Considers urgency levels (🔴 Critical, 🟡 Urgent, 🟢 Normal)
5. Selects packets following user strategy with clear reasoning
6. Adapts strategy based on previous outcomes and future predictions

## Key Features

### Intelligent Scheduling
- **User-guided strategies**: Natural language instructions drive LLM decisions
- **Emergent behaviors**: LLM interprets and adapts user intent to system constraints
- **Multi-objective balance**: Value, deadlines, queue management, and user priorities
- **Explanation-driven**: Every decision comes with clear reasoning including strategy adherence

### Visual Interface
```
Queue 0: 4 packets [OK]
  [0-0] value=9, deadline=11 🟢 NORMAL
  [0-1] value=5, deadline=8 🟡 URGENT
  [0-2] value=2, deadline=4 🔴 CRITICAL

Queue 1: 6 packets [⚠️ OVER LIMIT]
  [1-0] value=6, deadline=8 🟡 URGENT
  ...
```

### Performance Tracking
- Total value sent
- Packets expired (deadline reached 0)
- Overflow penalties (queue size > 5)
- Final score calculation
- Selection pattern analysis

## Files

### Core Implementation
- **`llm_direct_scheduler.py`** - Fixed 3-slot LLM scheduler
- **`variable_slot_scheduler.py`** - Variable slot scheduler with prediction
- **`packet.py`** - Packet and queue management classes
- **`implementation.md`** - Detailed technical documentation
- **`future_extensions_plan.md`** - Design for advanced features (Japanese)

### Archive
- **`archive/`** - Previous implementations including:
  - Two-agent negotiation system
  - Fixed strategy schedulers  
  - Test suites and original game rules

## Example LLM Decision

```
🤖 LLM SELECTION:
  Reasoning: Send critical packets 0-1 and 3-1 to avoid immediate 
  expirations (deadlines=3), and send high-value packet 3-3 (value=10) 
  to maximize total value while reducing overflow risk in Queue 3.

📤 SENDING 3 PACKETS:
  ✓ (v=2, d=3) from Queue 0
  ✓ (v=2, d=3) from Queue 3  
  ✓ (v=10, d=9) from Queue 3
  📊 Total value: 14
```

## Observed LLM Strategies

### Emergent Priorities
1. **Prevent expiration**: Critical deadlines (≤3) get highest priority
2. **Manage overflow**: Reduce queue sizes exceeding limit
3. **Maximize value**: Select high-value packets when constraints allow
4. **Balance queues**: Distribute selections across queues situationally

### Adaptive Behavior
- References previous decisions for learning
- Adjusts strategy based on current system state
- Balances competing objectives dynamically
- Provides human-interpretable explanations

## Configuration

### Basic Parameters
```python
run_llm_direct_simulation(
    num_turns=20,        # Game length
    num_queues=4,        # Number of queues  
    max_queue_size=5,    # Overflow threshold
    num_slots=3,         # Packets selected per turn
    verbose=True         # Step-by-step display
)
```

### Packet Properties
- **Value**: Random integer 1-10
- **Deadline**: Random integer 5-15  
- **Arrival rate**: Matches slot count per turn
- **Queue limit**: 5 packets (penalties for exceeding)

### Variable Slot Configuration
```bash
# Equal probability for all slot counts (default)
uv run variable_slot_scheduler.py  # 25% each for 1,2,3,4 slots

# Custom distributions
uv run variable_slot_scheduler.py -p 0.1 0.2 0.5 0.2  # 3-slot heavy
uv run variable_slot_scheduler.py -p 0.4 0.1 0.1 0.4  # Extreme variance
uv run variable_slot_scheduler.py -p 0.05 0.45 0.45 0.05  # Stable 2-3 slots
```

### Natural Language Strategy Examples
```bash
# Deadline-focused strategies
uv run variable_slot_scheduler.py -s "Deadline priority, never let packets expire!"
uv run llm_direct_scheduler.py -s "Critical deadlines only, prevent all expirations"

# Value-focused strategies  
uv run variable_slot_scheduler.py -s "High-value packets first, maximize total value"
uv run llm_direct_scheduler.py -s "Focus on high-value packets only"

# Balance strategies
uv run variable_slot_scheduler.py -s "Balance all queues, avoid penalties"
uv run llm_direct_scheduler.py -s "Safe operation, maintain queue balance"

# Custom strategies
uv run variable_slot_scheduler.py -s "Empty Queue 0 but wait for value 8+ packets"
```

## Performance Metrics

### Typical Results
- **Value per turn**: 15-25 range
- **Expiration rate**: Near zero with good LLM decisions
- **Overflow management**: Proactive queue balancing
- **Selection distribution**: Balanced across queues with strategic focus

### Scoring System
```
Final Score = Total Value Sent - (5 × Expired Packets) - (2 × Overflow Penalties)
```

## Research Applications

This implementation demonstrates:
- **Emergent optimization strategies** in AI systems
- **Real-time multi-objective decision making**
- **Explanation quality** in complex resource allocation
- **Adaptability** to dynamic system constraints

Perfect for studying LLM capabilities in autonomous system management and decision-making transparency.

## Technical Requirements

- Python 3.8+
- NLM system (Natural Language Macro interpreter)
- OpenAI API access (gpt-5-mini recommended)
- uv package manager

## Evolution

This project evolved from:
1. Two-agent negotiation system
2. Strategy-based LLM scheduler  
3. Fixed algorithm comparisons
4. Direct LLM selection with emergent strategies
5. **Current**: Variable slot scheduler with future prediction

The latest implementation adds temporal reasoning capabilities, allowing the LLM to make strategic decisions based on predicted future resource availability.