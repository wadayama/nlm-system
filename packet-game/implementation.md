# LLM Direct Selection Packet Scheduler - Implementation Guide

## Overview

A packet scheduling game where an LLM directly selects 3 packets from 4 queues each turn, without predefined strategies. The LLM observes system state and makes autonomous decisions to maximize value while managing deadlines and preventing queue overflow.

## Core Implementation

### File Structure
```
packet-game/
├── llm_direct_scheduler.py  # Main LLM-based scheduler
├── packet.py                # Packet and queue management
├── implementation.md       # This document
└── archive/                # Old implementations
    ├── game_orchestrator.py     # Two-agent negotiation system
    ├── packet_game_agent.py     # Autonomous negotiation agents
    ├── llm_scheduler.py          # Strategy-based LLM scheduler
    ├── simple_scheduler.py       # Fixed strategy scheduler
    ├── scheduler_test.py         # Test suite for schedulers
    └── basic_rule.md             # Original game rules (Japanese)
```

### Key Components

#### 1. **LLMDirectScheduler Class** (`llm_direct_scheduler.py`)

**Core Features:**
- **Multi-slot selection**: Selects 3 packets per turn
- **LLM-driven decisions**: No predefined strategies
- **Queue overflow management**: Penalty system for queue size > 5
- **Real-time adaptation**: Adjusts decisions based on current state

**Key Methods:**
```python
class LLMDirectScheduler:
    def __init__(num_queues=4, max_queue_size=5, num_slots=3)
    def select_packets_with_llm() -> (packets, reasoning)
    def send_packets(packets) -> sources
    def get_statistics() -> stats_dict
```

#### 2. **Packet System** (`packet.py`)

**Packet Properties:**
- **Value**: Random 1-10
- **Deadline**: Random 5-15 (was fixed 10)
- **Dynamic urgency**: 🔴 Critical (≤3), 🟡 Urgent (≤6), 🟢 Normal (>6)

**PacketQueue Features:**
- Automatic deadline updates
- Expiration handling
- Display formatting with agent IDs

### Game Mechanics

#### **Turn Flow:**
1. **Packet Arrivals**: 3 packets arrive randomly (same as slots)
2. **State Observation**: LLM receives formatted system state
3. **Packet Selection**: LLM chooses 3 packets with reasoning
4. **Transmission**: Selected packets are sent
5. **Deadline Updates**: All remaining packets age by 1
6. **Statistics**: Display current performance metrics

#### **LLM Decision Process:**
```
Input to LLM:
- Queue status with packet IDs [0-0], [1-2], etc.
- Packet values and deadlines with urgency markers
- Queue overflow warnings (⚠️)
- Recent selection history (last 3 turns)

Output from LLM:
- Selected packet IDs: "0-3,1-2,2-1"
- Reasoning: Explanation of selection logic
```

#### **Scoring System:**
```
Final Score = Total Value Sent - (5 × Expired Packets) - (2 × Overflow Penalties)
```

### LLM Prompt Design

The LLM receives structured information:
```
Turn 5 - Current System State:
Statistics: Value Sent=93, Expired=0, Penalties=1
Max Queue Size: 5 (⚠️ = over limit)

Queue 0: 4 packets [OK]
  [0-0] value=9, deadline=11 🟢 NORMAL
  [0-1] value=5, deadline=8 🟡 URGENT
  [0-2] value=2, deadline=4 🔴 CRITICAL
  [0-3] value=5, deadline=14 🟢 NORMAL

Queue 1: 6 packets [⚠️ OVER LIMIT]
  [1-0] value=6, deadline=8 🟡 URGENT
  [1-1] value=2, deadline=9 🟡 URGENT
  ...

Available packet IDs: 0-0, 0-1, 0-2, 0-3, 1-0, 1-1, ...
Select exactly 3 packets to send this turn.
```

### Performance Characteristics

#### **Observed LLM Behavior:**
1. **Emergent Strategies**: 
   - Priority 1: Prevent imminent expirations (deadline ≤ 3)
   - Priority 2: Manage queue overflow (size > 5)
   - Priority 3: Maximize value when possible

2. **Adaptive Learning**:
   - References previous decisions
   - Adjusts strategy based on system state
   - Balances competing objectives dynamically

3. **Explanation Quality**:
   - Clear reasoning for each selection
   - Multiple factors considered simultaneously
   - Human-interpretable decision logic

#### **Typical Performance:**
- **Value per turn**: 15-25 range
- **Expiration rate**: Near zero with good LLM decisions
- **Overflow management**: Proactive queue balancing
- **Selection patterns**: Distributed across queues with situational focus

### Usage

#### **Basic Execution:**
```bash
uv run llm_direct_scheduler.py
```

#### **Configuration Options:**
```python
run_llm_direct_simulation(
    num_turns=20,        # Game length
    num_queues=4,        # Number of queues
    max_queue_size=5,    # Overflow threshold
    num_slots=3,         # Packets per turn
    verbose=True         # Step-by-step display
)
```

#### **Interactive Features:**
- Press Enter between turns for step-by-step analysis
- Real-time LLM reasoning display
- Queue overflow warnings
- Selection pattern analysis at end

### Design Philosophy

#### **1. Emergent Intelligence**
- No hardcoded strategies
- LLM develops its own decision patterns
- Strategy emerges from situation and constraints

#### **2. Transparency**
- Every decision is explained
- System state clearly presented
- Selection patterns tracked and analyzed

#### **3. Scalability**
- Configurable queue count and packet slots
- Adjustable penalty systems
- Extensible for different LLM models

#### **4. Realism**
- Variable packet deadlines (5-15 range)
- Dynamic arrival patterns
- Realistic queue management challenges

### Future Extensions

#### **Potential Enhancements:**
1. **Multi-objective scoring**: Add fairness metrics across queues
2. **Dynamic slot allocation**: LLM chooses number of packets (1-5)
3. **Packet types**: Different categories with unique properties
4. **Adaptive difficulty**: Deadline ranges adjust based on performance
5. **Comparative analysis**: Multiple LLM models competing simultaneously

#### **Research Applications:**
- Study emergent scheduling strategies in AI systems
- Compare human vs LLM decision-making patterns
- Analyze explanation quality in complex optimization tasks
- Evaluate adaptability to changing system constraints

### Key Insights

#### **LLM Strengths Observed:**
- Excellent at multi-objective optimization
- Natural deadline-driven urgency handling
- Good at explaining complex decisions
- Adapts quickly to new system states

#### **Implementation Lessons:**
- Simple packet ID scheme [queue-index] works well
- Visual urgency markers improve LLM understanding
- History context (3 turns) provides good learning without overload
- Fallback mechanisms essential for robustness

This implementation demonstrates sophisticated autonomous decision-making in resource allocation scenarios, showcasing LLM capabilities in real-time optimization tasks.