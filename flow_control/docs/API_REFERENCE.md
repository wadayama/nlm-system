# API Reference

Python API reference for the Flow Control Network System.

## Table of Contents

- [FlowController](#flowcontroller)
- [NetworkFileLoader](#networkfileloader) ⭐ NEW
- [InteractiveNetworkMonitor](#interactivenetworkmonitor) ⭐ ENHANCED
- [NetworkSampleGallery](#networksamplegallery)
- [NetworkState](#networkstate)
- [NetworkPath](#networkpath)
- [NetworkEdge](#networkedge)
- [NetworkNode](#networknode)

---

## FlowController

Core class for flow control. Manages path flow settings, edge enable/disable operations, and state validation.

### Class Definition

```python
from flow_operations import FlowController
from network_model import NetworkState

network = NetworkState()
controller = FlowController(network)
```

### Methods

#### `set_path_flow(path_id: str, target_flow: float) -> Tuple[bool, str]`

Sets the flow for a specified path to an absolute value.

**Arguments:**
- `path_id`: Path ID (e.g., "P1", "P2")
- `target_flow`: Target flow value

**Returns:**
- `(success, message)`: Success flag and message

**Example:**
```python
success, msg = controller.set_path_flow("P1", 5.0)
if success:
    print(f"Flow set successfully: {msg}")
```

#### `update_path_flow(path_id: str, delta_flow: float) -> Tuple[bool, str]`

Updates path flow by a relative amount.

**Arguments:**
- `path_id`: Path ID
- `delta_flow`: Flow change amount (positive: increase, negative: decrease)

**Returns:**
- `(success, message)`: Success flag and message

**Example:**
```python
controller.update_path_flow("P1", 2.0)  # Increase by 2.0
controller.update_path_flow("P2", -1.5)  # Decrease by 1.5
```

#### `clear_all_flows() -> None`

Resets all flows to zero.

**Example:**
```python
controller.clear_all_flows()
```

#### `distribute_flow_equally(total_flow: float) -> Tuple[bool, str]`

Distributes the specified total flow equally among all paths.

**Arguments:**
- `total_flow`: Total flow amount to distribute

**Example:**
```python
success, msg = controller.distribute_flow_equally(12.0)
# For 3 paths, distributes 4.0 to each path
```

#### `disable_edge(edge_id: str) -> Tuple[bool, str]`

Disables an edge (sets capacity to 0). Flows on affected paths are automatically cleared.

**Arguments:**
- `edge_id`: Edge ID (e.g., "e1", "e2")

**Example:**
```python
success, msg = controller.disable_edge("e1")
# Flows on paths using edge e1 are automatically set to 0
```

#### `enable_edge(edge_id: str) -> Tuple[bool, str]`

Enables a disabled edge (restores original capacity).

**Arguments:**
- `edge_id`: Edge ID

**Example:**
```python
success, msg = controller.enable_edge("e1")
```

#### `saturate_path_flow(path_id: str) -> Tuple[bool, str, Dict]` ⭐ NEW

Automatically saturates a path by setting its flow to the bottleneck capacity.

**Arguments:**
- `path_id`: Path ID (case insensitive: "P1", "p1")

**Returns:**
- `(success, message, info_dict)`: Success flag, message, and path information

**Example:**
```python
success, msg, info = controller.saturate_path_flow("P1")
if success:
    print(f"Path saturated: {msg}")
    print(f"New utilization: {info['utilization']:.1%}")
```

#### `get_path_info(path_id: str) -> Dict` ⭐ NEW

Gets comprehensive information about a specific path.

**Arguments:**
- `path_id`: Path ID (case insensitive)

**Returns:**
- Dictionary with detailed path information including:
  - `current_flow`, `bottleneck_capacity`, `utilization`
  - `status` ("LOW", "NORMAL", "HIGH", "SATURATED", "BLOCKED")
  - `edge_details`: Information about each edge in the path
  - `shared_paths`: Other paths sharing edges

**Example:**
```python
info = controller.get_path_info("P1")
print(f"Path {info['path_id']}: {info['current_flow']}/{info['bottleneck_capacity']}")
print(f"Status: {info['status']}, Utilization: {info['utilization']:.1%}")
print(f"Bottleneck: {info['bottleneck_edge']}")
```

#### `get_edge_info(edge_id: str) -> Dict` ⭐ NEW

Gets comprehensive information about a specific edge.

**Arguments:**
- `edge_id`: Edge ID (case insensitive: "e1", "E1")

**Returns:**
- Dictionary with detailed edge information including:
  - `current_flow`, `capacity`, `utilization`, `available_capacity`
  - `status` ("LOW", "NORMAL", "HIGH", "OVERLOAD", "DISABLED")
  - `using_paths`: List of paths using this edge
  - `bottleneck_for`: Paths for which this edge is the bottleneck

**Example:**
```python
info = controller.get_edge_info("e2")
print(f"Edge {info['edge_id']}: {info['current_flow']}/{info['capacity']}")
print(f"Status: {info['status']}, Utilization: {info['utilization']:.1%}")
print(f"Used by paths: {[p['path_id'] for p in info['using_paths']]}")
if info['is_critical']:
    print(f"⚠️ Critical bottleneck for: {info['bottleneck_for']}")
```

#### `list_edge_status() -> Dict`

Gets the status of all edges.

**Returns:**
```python
{
    "e1": {
        "from": "s",
        "to": "a",
        "capacity": 10.0,
        "flow": 5.0,
        "is_failed": False,
        "utilization": 0.5,
        "status": "OK"
    },
    # ...
}
```

#### `calculate_max_safe_flow(path_id: str) -> Dict`

Calculates the maximum safe flow and detailed information for a path.

**Returns:**
```python
{
    "path_id": "P1",
    "current_flow": 3.0,
    "max_safe_flow": 8.0,
    "available_capacity": 5.0,
    "suggested_flow": 8.0,
    "bottleneck_edge": "e2",
    "bottleneck_capacity": 8.0,
    "edge_sequence": ["e1", "e2"],
    "is_blocked": False
}
```

#### `get_complete_network_state() -> Dict`

Gets complete network state information.

**Returns:**
```python
{
    "edges": {
        # Detailed information for all edges
    },
    "paths": {
        # Detailed information for all paths
    },
    "system_metrics": {
        "total_throughput": 9.0,
        "theoretical_max_flow": 14.0,
        "network_efficiency": 0.643,
        "flow_conservation_violations": 0,
        "operational_edges": 8,
        "failed_edges": 0,
        "blocked_paths": 0
    }
}
```

#### `validate_and_report() -> Dict`

Validates flow conservation and capacity constraints.

**Returns:**
```python
{
    "conservation_violations": [],  # List of violating nodes
    "capacity_overloads": [],      # List of overloaded edges
    "total_throughput": 9.0,
    "path_utilizations": {"P1": 0.625, "P2": 0.667},
    "is_valid": True,
    "has_overloads": False
}
```

---

## NetworkFileLoader ⭐ NEW

Class for loading custom network definitions from YAML files.

### Class Definition

```python
from network_file_loader import NetworkFileLoader

loader = NetworkFileLoader()
```

### Methods

#### `load_yaml(file_path: str) -> NetworkState`

Loads a network from a YAML file with complete validation and path enumeration.

**Arguments:**
- `file_path`: Path to the YAML file

**Returns:**
- `NetworkState` object with all paths enumerated

**Raises:**
- `FileNotFoundError`: If the file doesn't exist
- `yaml.YAMLError`: If the YAML is invalid
- `ValueError`: If required fields are missing or network is invalid

**Example:**
```python
try:
    network = loader.load_yaml("examples/star_network.yaml")
    print(f"Loaded: {len(network.nodes)} nodes, {len(network.paths)} paths")
except ValueError as e:
    print(f"Invalid network: {e}")
```

#### `get_network_info(file_path: str) -> Dict`

Gets basic information about a network file without fully loading it.

**Arguments:**
- `file_path`: Path to the YAML file

**Returns:**
- Dictionary with network metadata:
```python
{
    'name': 'Star Network',
    'description': 'Hub-and-spoke topology',
    'num_nodes': 7,
    'num_edges': 9,
    'file_path': '/absolute/path/to/file.yaml'
}
```

**Example:**
```python
info = loader.get_network_info("examples/star_network.yaml")
print(f"{info['name']}: {info['num_nodes']} nodes, {info['num_edges']} edges")
```

### YAML Format

Network files use the following YAML structure:

```yaml
name: Custom Network
description: Description of the network

nodes:
  s: source
  a: intermediate  
  b: intermediate
  t: sink

edges:
  e1: {from: s, to: a, capacity: 10.0}
  e2: {from: s, to: b, capacity: 8.0}
  e3: {from: a, to: t, capacity: 7.0}
  e4: {from: b, to: t, capacity: 9.0}
```

**Node Types:**
- `source`: Single source node required
- `intermediate`: Internal network nodes
- `sink`: Single sink node required

**Edge Format:**
- `from`/`to`: Node IDs (must exist in nodes section)
- `capacity`: Edge capacity (positive number)

---

## InteractiveNetworkMonitor ⭐ ENHANCED

Enhanced interactive command-line interface with readline support.

### New Features

- **Readline Support**: Command history (↑/↓), line editing (Ctrl+A/E), tab completion
- **Case-Insensitive IDs**: Use `p1`/`P1`, `e1`/`E1` interchangeably  
- **Smart Tab Completion**: Context-aware completion for commands and parameters

### Usage

```python
from interactive_monitor import InteractiveNetworkMonitor

monitor = InteractiveNetworkMonitor()
monitor.run()  # Start interactive session
```

### Key Methods

#### `_normalize_id(item_id: str, item_type: str) -> str` ⭐ NEW

Normalizes IDs for case-insensitive lookup.

**Arguments:**
- `item_id`: Input ID (any case)
- `item_type`: Type ("path", "edge", "node")

**Returns:**
- Actual ID as stored in network

**Example:**
```python
# Both return "P1" if P1 exists in network
normalized = monitor._normalize_id("p1", "path")
normalized = monitor._normalize_id("P1", "path")
```

---

## NetworkSampleGallery

Class for managing predefined network samples.

### Class Definition

```python
from network_samples import NetworkSampleGallery

gallery = NetworkSampleGallery()
```

### Methods

#### `list_samples() -> Dict[str, Dict]`

Gets a list of all available samples.

**Returns:**
```python
{
    "diamond": {
        "name": "Simple Diamond",
        "description": "Basic 2-path diamond topology (4 nodes)",
        "features": ["Simple topology", "2 parallel paths", "Good for beginners"],
        "nodes": 4,
        "edges": 4,
        "paths": 2
    },
    # ...
}
```

#### `get_sample(sample_id: str) -> NetworkState`

Gets a network instance for the specified sample.

**Arguments:**
- `sample_id`: Sample ID ("diamond", "complex", "grid", etc.)

**Example:**
```python
network = gallery.get_sample("diamond")
```

#### `get_sample_info(sample_id: str) -> Dict`

Gets detailed information about a sample.

**Returns:**
```python
{
    "name": "Simple Diamond",
    "description": "Basic 2-path diamond topology (4 nodes)",
    "features": [...],
    "suggested_flows": {"P1": 5.0, "P2": 4.0},
    "nodes": 4,
    "edges": 4,
    "paths": 2
}
```

#### `apply_suggested_flows(network: NetworkState, sample_id: str) -> bool`

Applies suggested flow values for a sample.

**Arguments:**
- `network`: Target network
- `sample_id`: Sample ID

**Returns:**
- `success`: True if all flows were successfully set

---

## NetworkState

Class for managing overall network state.

### Attributes

- `nodes: Dict[str, NetworkNode]` - Dictionary of nodes
- `edges: Dict[str, NetworkEdge]` - Dictionary of edges
- `paths: Dict[str, NetworkPath]` - Dictionary of paths
- `source_node: str` - Source node ID
- `sink_node: str` - Sink node ID
- `total_flow: float` - Total throughput

### Methods

#### `add_node(node: NetworkNode) -> None`

Adds a node.

#### `add_edge(edge: NetworkEdge) -> None`

Adds an edge and updates connection information for related nodes.

#### `add_path(path: NetworkPath) -> None`

Adds a path.

#### `calculate_total_throughput() -> float`

Calculates total inflow to the sink node.

**Returns:**
- Total throughput value

#### `validate_flow_conservation() -> List[Tuple[str, float]]`

Validates flow conservation at intermediate nodes.

**Returns:**
- `[(node_id, imbalance), ...]` - List of violating nodes and imbalance amounts

#### `get_network_summary() -> str`

Returns network summary as a string.

---

## NetworkPath

Class representing an s-t path.

### Attributes

- `id: str` - Path ID
- `edges: List[str]` - List of edge IDs comprising the path
- `current_flow: float` - Current flow value
- `bottleneck_capacity: float` - Bottleneck capacity
- `bottleneck_edge: str` - Bottleneck edge ID

### Methods

#### `calculate_bottleneck(edges: Dict) -> Tuple[float, Optional[str]]`

Calculates the bottleneck (minimum capacity) of the path.

**Arguments:**
- `edges`: Edge dictionary

**Returns:**
- `(bottleneck_capacity, bottleneck_edge_id)`

#### `can_accommodate_flow(delta_flow: float, edges: Dict) -> Tuple[bool, str]`

Checks if a flow change is possible.

**Arguments:**
- `delta_flow`: Flow change amount
- `edges`: Edge dictionary

**Returns:**
- `(can_accommodate, reason)`

---

## NetworkEdge

Class representing a network edge.

### Attributes

- `id: str` - Edge ID
- `from_node: str` - Source node ID
- `to_node: str` - Destination node ID
- `capacity: float` - Current capacity
- `flow: float` - Current flow
- `base_capacity: float` - Base capacity
- `is_failed: bool` - Failure flag

### Methods

#### `get_utilization() -> float`

Calculates utilization ratio (flow/capacity).

**Returns:**
- Utilization ratio (0.0~1.0, special value when capacity is 0)

---

## NetworkNode

Class representing a network node.

### Attributes

- `id: str` - Node ID
- `type: str` - Node type ("source", "intermediate", "sink")
- `incoming_edges: List[str]` - List of incoming edge IDs
- `outgoing_edges: List[str]` - List of outgoing edge IDs

### Methods

#### `validate_flow_conservation(edges: Dict) -> Tuple[bool, float]`

Validates flow conservation at the node.

**Arguments:**
- `edges`: Edge dictionary

**Returns:**
- `(is_conserved, imbalance)` - Whether conservation is satisfied, imbalance amount

---

## Usage Examples

### Basic Flow Control

```python
from network_samples import NetworkSampleGallery
from flow_operations import FlowController

# Load network
gallery = NetworkSampleGallery()
network = gallery.get_sample("diamond")

# Initialize controller
controller = FlowController(network)

# Set flows
controller.set_path_flow("P1", 5.0)
controller.set_path_flow("P2", 3.0)

# Check state
state = controller.get_complete_network_state()
print(f"Total throughput: {state['system_metrics']['total_throughput']}")

# Simulate edge failure
controller.disable_edge("e1")

# Check impact
validation = controller.validate_and_report()
print(f"Validity: {validation['is_valid']}")
```

### Creating a Custom Network

```python
from network_model import NetworkState, NetworkNode, NetworkEdge, NetworkPath

# Create empty network
network = NetworkState()

# Add nodes
network.add_node(NetworkNode("s", "source"))
network.add_node(NetworkNode("v1", "intermediate"))
network.add_node(NetworkNode("t", "sink"))

# Add edges
network.add_edge(NetworkEdge("e1", "s", "v1", 10.0))
network.add_edge(NetworkEdge("e2", "v1", "t", 8.0))

# Add paths
network.add_path(NetworkPath("P1", ["e1", "e2"]))
```