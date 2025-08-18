# LLM Direct Selection Packet Scheduler

An intelligent packet scheduling system where an LLM autonomously selects 3 packets from 4 queues each turn, demonstrating emergent optimization strategies without predefined rules.

## Quick Start

```bash
# Run the LLM-based packet scheduler
uv run llm_direct_scheduler.py
```

The system will:
1. Initialize 4 queues with 3 packets each
2. Run for 20 turns with LLM making decisions each turn
3. Display step-by-step reasoning and queue states
4. Show final performance statistics

## System Overview

### Core Concept
- **4 packet queues** with size limit of 5 (overflow penalties apply)
- **3 packets selected per turn** by LLM without predefined strategies
- **Dynamic packet properties**: value (1-10), deadline (5-15)
- **Real-time adaptation** based on queue states and urgency

### LLM Decision Process
Each turn, the LLM:
1. Observes all queue states with packet details
2. Considers urgency levels (🔴 Critical, 🟡 Urgent, 🟢 Normal)
3. Selects 3 packets with clear reasoning
4. Adapts strategy based on previous outcomes

## Key Features

### Intelligent Scheduling
- **Emergent strategies**: LLM develops its own optimization patterns
- **Multi-objective balance**: Value, deadlines, and queue management
- **Explanation-driven**: Every decision comes with clear reasoning

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
- **`llm_direct_scheduler.py`** - Main LLM-based scheduler
- **`packet.py`** - Packet and queue management classes
- **`implementation.md`** - Detailed technical documentation

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
- **Arrival rate**: 3 + expired_count packets per turn
- **Queue limit**: 5 packets (penalties for exceeding)

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
4. **Current**: Direct LLM selection with emergent strategies

The current implementation represents the most sophisticated and autonomous approach, allowing pure LLM intelligence to drive packet scheduling decisions.