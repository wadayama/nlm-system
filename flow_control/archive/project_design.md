# Flow Control Project - Overall Design Document

## Project Overview

This project implements a **Random Capacity Variation s-t Network Flow Control Model** designed specifically for LLM-based control evaluation. The system models real-world scenarios like network congestion control, disaster logistics management, and load balancing under uncertainty.

### Key Research Goals
- Evaluate LLM performance in **Partially Observable Markov Decision Processes (POMDPs)**
- Study LLM capabilities in **multi-objective optimization under uncertainty**
- Test **natural language strategy guidance** in complex dynamic environments
- Analyze **long-term planning** with stochastic system dynamics

## Core Model Components

### 1. Network Structure
- **Directed Graph**: G = (V, E) with source node s and sink node t
- **Multiple Paths**: K candidate paths from s to t (P₁, P₂, ..., Pₖ)
- **Edge Properties**: Each edge e has capacity c_e(t) and current flow f_e(t)
- **Flow Conservation**: Maintained at all intermediate nodes

### 2. Dynamic Environment
- **Capacity Variations**: Random walk model with bounded changes
- **Failure Events**: Stochastic edge failures (capacity → 0)
- **Recovery Mechanisms**: Probabilistic capacity restoration
- **Partial Observability**: Limited alert information (max L alerts per timestep)

### 3. Control Actions
- **Path Selection**: Choose from available s-t paths
- **Flow Adjustment**: Increase/decrease flow by Δa on selected path
- **Constraint Handling**: Allow temporary capacity violations with alerts

### 4. LLM Integration
- **Natural Language State Description**: Network conditions in readable format
- **Strategy Instructions**: User-provided control objectives
- **Reasoning Capture**: Detailed explanation of control decisions
- **Adaptive Learning**: Adjust strategies based on observed outcomes

## Project Structure

```
flow_control/
├── README.md                     # Project overview and usage
├── prob_statement.md            # Original problem specification
├── project_design.md           # This design document
│
├── core/
│   ├── network_model.py         # Graph structure and flow dynamics
│   ├── capacity_manager.py      # Stochastic capacity variations
│   ├── flow_calculator.py       # Flow conservation and updates
│   └── alert_system.py          # Partial observation alerts
│
├── control/
│   ├── flow_controller.py       # Main LLM-based controller
│   ├── state_formatter.py       # Convert network state to natural language
│   └── action_parser.py         # Parse LLM decisions to system actions
│
├── simulation/
│   ├── environment.py           # Main simulation environment
│   ├── scenario_generator.py    # Create test scenarios
│   └── metrics_collector.py     # Performance evaluation
│
├── visualization/
│   ├── network_visualizer.py    # Real-time network display
│   ├── flow_plotter.py         # Flow distribution charts
│   └── performance_dashboard.py # Metrics and alerts dashboard
│
└── tests/
    ├── test_network_basic.py    # Basic network functionality
    ├── test_scenarios.py        # Various test scenarios
    └── integration_test.py      # End-to-end system test
```

## Phased Implementation Plan

### Phase 1: Core Network Infrastructure (Foundation)
**Objective**: Solid network handling capabilities

#### 1.1 Data Structures
- **Node representation**: ID, type (source/intermediate/sink)
- **Edge representation**: ID, capacity, flow, failure state
- **Path representation**: Sequence of edges, current utilization
- **Network state**: Complete system snapshot for persistence

#### 1.2 Basic Functions
- **Graph construction**: Build network from configuration
- **Path enumeration**: Find all s-t paths or use predefined paths
- **Flow validation**: Check conservation and capacity constraints
- **State transitions**: Update capacities and flows consistently

#### 1.3 Visualization Foundation
- **Network topology display**: Show nodes, edges, and current flows
- **Real-time updates**: Reflect capacity changes and flow adjustments
- **Alert highlighting**: Visual indication of overloaded/failed edges
- **Performance metrics**: Basic throughput and violation statistics

### Phase 2: LLM Controller Integration
**Objective**: Natural language control interface

#### 2.1 State Representation
- Convert network state to clear natural language descriptions
- Highlight critical information (alerts, utilization, trends)
- Provide historical context for decision making

#### 2.2 Action Interface
- Parse LLM path selection and flow adjustment decisions
- Validate proposed actions against system constraints
- Implement fallback mechanisms for invalid/unclear decisions

#### 2.3 Strategy Integration
- Support user-provided natural language objectives
- Adapt control behavior based on strategic priorities
- Maintain reasoning traces for analysis and debugging

### Phase 3: Advanced Features and Analysis
**Objective**: Research platform capabilities

#### 3.1 Scenario Testing
- Implement various network topologies and failure patterns
- Create standardized benchmarks for LLM evaluation
- Support parameter sweeps for systematic analysis

#### 3.2 Performance Analysis
- Multi-objective optimization metrics
- Uncertainty handling evaluation
- Comparison with traditional control algorithms

#### 3.3 Visualization Enhancement
- Interactive network exploration
- Decision history visualization
- Strategy effectiveness analysis tools

## Key Design Principles

### 1. Modularity and Extensibility
- Clear separation between network model, control logic, and visualization
- Plugin architecture for different network topologies and failure models
- Easy integration of alternative control algorithms for comparison

### 2. Research-Oriented Design
- Comprehensive logging and metrics collection
- Reproducible experiments with configurable parameters
- Support for batch processing and parameter studies

### 3. Natural Language Integration
- Intuitive state descriptions that highlight key information
- Clear action formats that minimize LLM confusion
- Strategy instruction system based on packet-game success

### 4. Robustness and Reliability
- Input validation and error handling throughout
- Graceful degradation under extreme conditions
- Extensive test coverage for critical functionality

## Expected Research Outcomes

### LLM Capabilities Analysis
- **Partial Information Reasoning**: How well can LLMs infer unobserved network state?
- **Multi-Objective Balancing**: Effectiveness in optimizing competing objectives
- **Temporal Planning**: Ability to make decisions considering future uncertainty
- **Strategy Adaptation**: Learning and adjustment based on observed performance

### System Performance Insights
- **Benchmark Comparisons**: LLM vs traditional algorithms under various conditions
- **Scalability Analysis**: Performance as network size and complexity increase
- **Robustness Testing**: Behavior under extreme failure and load scenarios

### Practical Applications
- **Control Strategy Discovery**: Novel approaches identified through LLM reasoning
- **Human-AI Collaboration**: Effectiveness of natural language strategy guidance
- **Real-world Relevance**: Applicability to actual network management scenarios

## Next Steps

1. **Implement Phase 1 Core Infrastructure**
   - Focus on robust network data structures and basic operations
   - Ensure correct flow conservation and capacity constraint handling
   - Create foundation for visualization and state monitoring

2. **Validate Network Model**
   - Test with simple scenarios to ensure correct behavior
   - Verify stochastic capacity variations and failure mechanisms
   - Confirm partial observability and alert system functionality

3. **Build Visualization Tools**
   - Real-time network state display for development and debugging
   - Performance metrics dashboard for evaluation
   - Interactive exploration for understanding system behavior

This foundation will enable effective LLM integration in Phase 2 and sophisticated analysis in Phase 3, creating a valuable research platform for studying AI control in complex, uncertain environments.