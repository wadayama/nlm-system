# Command Reference

Complete reference for all commands available in the Flow Control Network System interactive monitor.

## Table of Contents

- [Display Commands](#display-commands)
- [Flow Control Commands](#flow-control-commands) ⭐ Enhanced
- [Information Commands](#information-commands) ⭐ NEW
- [Edge Operations](#edge-operations)
- [Sample Management](#sample-management)
- [File Operations](#file-operations) ⭐ NEW
- [Visualization Commands](#visualization-commands)
- [System Commands](#system-commands)
- [CLI Features](#cli-features) ⭐ NEW

---

## Display Commands

Command group for displaying network status and information.

### `status` / `s`

Displays complete network status.

**Display Content:**
- System overview (node count, edge count, path count)
- Throughput summary
- Path details (flow, capacity, utilization)
- Edge status

**Usage:**
```
flow_control> status
```

**Example Output:**
```
📊 System Overview
   Nodes: 4 | Edges: 4 | Paths: 2
   Total Throughput: 9.0

📊 s-t Path Details
Path ID  Route        Flow    Capacity  Utilization  Status
P1       e0→e2        5.0     8.0       62.5%        🟢 NORMAL
P2       e1→e3        4.0     6.0       66.7%        🟢 NORMAL
```

### `compact` / `c`

Displays compact one-line status.

**Usage:**
```
flow_control> compact
```

**Example Output:**
```
Throughput:   9.0 | P1:63% P2:67%
```

### `observe` / `o`

Displays complete observable network state with detailed information.

**Display Content:**
- System metrics (efficiency, theoretical max flow)
- Detailed status of all edges
- Detailed status of all paths
- Bottleneck information

**Usage:**
```
flow_control> observe
```

---

## Flow Control Commands

Command group for controlling path flows.

### `set <path> <flow>`

Sets the flow of a specified path to an absolute value.

**Arguments:**
- `path`: Path ID (P1, P2, etc.)
- `flow`: Flow value to set (decimal allowed)

**Usage:**
```
flow_control> set P1 6.0
✅ Updated path P1 flow by 1.00

flow_control> set P2 10.0
❌ Cannot update flow: Flow increase of 6.00 would exceed capacity by 4.00 at edge e3
```

### `adjust <path> <delta>`

Adjusts path flow by a relative amount.

**Arguments:**
- `path`: Path ID
- `delta`: Change amount (+ for increase, - for decrease)

**Usage:**
```
flow_control> adjust P1 +2.0
✅ Updated path P1 flow by 2.00

flow_control> adjust P2 -1.5
✅ Updated path P2 flow by -1.50
```

### `clear`

Resets all flows to zero.

**Usage:**
```
flow_control> clear
✅ All flows cleared to zero
```

### `saturate <path>` ⭐ NEW

Automatically saturates the specified path to its bottleneck capacity.

**Arguments:**
- `path`: Path ID (case insensitive: P1, p1)

**Features:**
- Automatic bottleneck edge detection
- Sets flow from current value to bottleneck capacity in one command
- Appropriate messaging when already saturated

**Usage:**
```
flow_control> saturate P1
✅ Path P1 saturated: 0.0 → 7.0 (bottleneck: e2)

flow_control> saturate p2  # lowercase also works
✅ Path P2 saturated: 2.0 → 6.0 (bottleneck: e1)

flow_control> saturate P1  # already saturated
✅ Path P1 already saturated at 7.0 (bottleneck: e2)
```

### `distribute <total>`

Distributes the specified total flow equally among all paths.

**Arguments:**
- `total`: Total flow amount to distribute

**Usage:**
```
flow_control> distribute 12.0
✅ Successfully distributed 12.00 flow equally among 2 paths
# Distributes 6.0 to each path
```

### `maxflow <path>`

Displays maximum safe flow and detailed information for the specified path.

**Arguments:**
- `path`: Path ID

**Usage:**
```
flow_control> maxflow P1
```

**Example Output:**
```
📊 Path Flow Analysis: P1
──────────────────────────────────────────────────
📈 Current State:
   Current flow: 5.0
   Available capacity: 3.0

🎯 Flow Limits:
   Maximum safe flow: 8.0
   Suggested flow: 8.0

🔗 Bottleneck Information:
   Bottleneck edge: e2
   Bottleneck capacity: 8.0
   Path edges: e0 → e2

📊 Utilization:
   Current: 62.5%
   [████████████░░░░░░░░] 5.0/8.0
```

---

## Edge Operations

Command group for controlling edge enable/disable status.

### `disable <edge>`

Disables an edge (sets capacity to 0). Flows on affected paths are automatically cleared.

**Arguments:**
- `edge`: Edge ID (e1, e2, etc.)

**Usage:**
```
flow_control> disable e1
✅ Edge e1 disabled (cleared flows: P2)
```

### `enable <edge>`

Enables a disabled edge (restores original capacity).

**Arguments:**
- `edge`: Edge ID

**Usage:**
```
flow_control> enable e1
✅ Edge e1 enabled (capacity: 6.0)
```

### `edges`

Lists the status of all edges.

**Usage:**
```
flow_control> edges
```

**Example Output:**
```
🔗 EDGE STATUS
======================================================================
Edge   From   To     Capacity   Flow     Util%    Status
----------------------------------------------------------------------
e0     s      a      8.0        5.0      63%      🟢 OK
e1     s      b      0.0        0.0      0%       🔴 DISABLED
e2     a      t      7.0        5.0      71%      🟢 OK
e3     b      t      9.0        0.0      0%       🟢 OK

📊 Summary: 4 total edges, 1 disabled
```

---

## Information Commands ⭐ NEW

Command group for getting detailed information about individual paths and edges.

### `info path <path_id>`

Displays comprehensive information about the specified path.

**Arguments:**
- `path_id`: Path ID (case insensitive: P1, p1)

**Display Content:**
- Basic information (route, edge composition, status)
- Flow information (current flow, max capacity, utilization)
- Bottleneck analysis (limiting edge and capacity)
- Edge details (utilization status of each edge)
- Relationships (shared edges with other paths)

**Usage:**
```
flow_control> info path P1
📊 PATH INFORMATION: P1
============================================================
🛤️  Route: s → a → t
📏 Edges: e0 → e2 (2 total)
🟢 Status: NORMAL

💧 Flow Information:
   Current flow: 5.0
   Maximum capacity: 7.0
   Available capacity: 2.0
   Utilization: 71.4%

🔗 Bottleneck:
   Limiting edge: e2
   Bottleneck capacity: 7.0

🔗 Edge Details:
Edge   From   To     Capacity   Flow     Util%    Bottleneck
------------------------------------------------------------
e0     s      a      8.0        5.0      62%      
e2     a      t      7.0        5.0      71%      🔴 YES

🔗 No edge sharing with other paths
============================================================
```

### `info edge <edge_id>`

Displays detailed information about the specified edge.

**Arguments:**
- `edge_id`: Edge ID (case insensitive: e1, E1)

**Display Content:**
- Basic information (connected nodes, capacity, status)
- Utilization status (current flow, utilization, remaining capacity)
- Path usage (list of paths using this edge)
- Importance (bottleneck paths, criticality assessment)

**Usage:**
```
flow_control> info edge e2
🔗 EDGE INFORMATION: e2
============================================================
🔗 Connection: a → t
📊 Capacity: 7.0
🟢 Status: NORMAL
⚠️  Critical: Bottleneck for 1 path(s)

💧 Flow Information:
   Current flow: 5.0
   Available capacity: 2.0
   Utilization: 71.4%

🛤️  Used by 1 path(s):
Path   Flow     Position   Total Edges
----------------------------------------
P1     5.0      2/2        2

🔴 Bottleneck for paths: P1
============================================================
```

---

## File Operations ⭐ NEW

Command group for loading custom networks from external YAML files.

### `loadfile <path>`

Loads a network from a YAML file.

**Arguments:**
- `path`: Path to the YAML file

**Features:**
- Complete validation (nodes, edges, connectivity check)
- Automatic path enumeration (all s-t path detection)
- Network information display

**Usage:**
```
flow_control> loadfile examples/star_network.yaml
✅ Loaded: Star Network
   Description: Hub-and-spoke topology with central bottleneck
   File: examples/star_network.yaml
   Topology: 7 nodes, 9 edges, 4 paths

flow_control> loadfile custom/my_network.yaml
❌ File not found: custom/my_network.yaml

flow_control> loadfile invalid.yaml
❌ Invalid network definition: No paths found from source to sink - network is disconnected
```

### YAML File Format

**Basic Structure:**
```yaml
name: Custom Network
description: Network description

nodes:
  s: source      # Single source node (required)
  a: intermediate # Intermediate node
  b: intermediate
  t: sink        # Single sink node (required)

edges:
  e1: {from: s, to: a, capacity: 10.0}
  e2: {from: s, to: b, capacity: 8.0}
  e3: {from: a, to: t, capacity: 7.0}
  e4: {from: b, to: t, capacity: 9.0}
```

**Node Types:**
- `source`: Source node (exactly one required)
- `intermediate`: Intermediate nodes (any number)
- `sink`: Sink node (exactly one required)

**Edge Format:**
- `from`/`to`: Node IDs (must exist in nodes section)
- `capacity`: Edge capacity (positive number)

---

## Sample Management

Command group for managing predefined network samples.

### `samples`

Lists all available sample networks.

**Usage:**
```
flow_control> samples
```

**Example Output:**
```
🏛️  AVAILABLE NETWORK SAMPLES
======================================================================

🔸 DIAMOND: Simple Diamond
   Basic 2-path diamond topology (4 nodes)
   Size: 4 nodes, 4 edges, 2 paths
   Features: Simple topology, 2 parallel paths, Good for beginners

🔸 COMPLEX: Complex Multi-Path
   Multi-layer network with 4 overlapping paths (6 nodes)
   Size: 6 nodes, 8 edges, 4 paths
   Features: 4 paths, Shared edges, Flow interaction analysis

[Other samples...]

💡 Current sample: DIAMOND
💡 Use 'load <sample_name>' to switch networks
```

### `load <name>`

Loads the specified sample network.

**Arguments:**
- `name`: Sample ID (diamond, complex, grid, star, layered, linear, parallel, bottleneck)

**Usage:**
```
flow_control> load complex
✅ Loaded: Complex Multi-Path
   Topology: 6 nodes, 8 edges, 4 paths
   Features: 4 paths, Shared edges, Flow interaction analysis
```

### `info [name]`

Displays detailed information about a sample. Without arguments, shows current sample information.

**Arguments (Optional):**
- `name`: Sample ID

**Usage:**
```
flow_control> info star
```

**Example Output:**
```
📊 SAMPLE INFO: STAR
============================================================
Name: Star Network
Description: Hub-and-spoke topology (8 nodes, 5 paths)
Topology: 8 nodes, 10 edges, 5 paths
Features:
  • Hub bottleneck
  • Parallel spokes
  • CDN-like structure
Suggested flows:
  • P1: 2.0
  • P2: 3.0
  • P3: 2.5
  • P4: 1.5
  • P5: 2.8

💡 Use 'load star' to switch to this sample
```

---

## Visualization Commands

Command group for visualizing network graphs.

### `display` / `d`

Displays the network graph (default: s-t optimized layout).

**Usage:**
```
flow_control> display
🎨 Displaying network graph...
✅ Graph visualization displayed
```

### `display <path1> [path2] ...`

Displays the graph with specified paths highlighted.

**Arguments:**
- `path1, path2, ...`: Path IDs to highlight

**Usage:**
```
flow_control> display P1 P2
🎨 Displaying network graph...
   Highlighting paths: ['P1', 'P2']
✅ Graph visualization displayed
```

### `display layout <type>`

Changes the graph layout.

**Arguments:**
- `type`: Layout type
  - `planar_st`: s-t optimized planar layout (default)
  - `planar`: Planar graph layout
  - `spring`: Spring model layout
  - `grid`: Grid layout
  - `hierarchical`: Hierarchical layout

**Usage:**
```
flow_control> display layout spring
🎨 Displaying network graph...
   Using layout: spring
✅ Graph visualization displayed
```

### `display save <filename>`

Saves the graph as an image file.

**Arguments:**
- `filename`: Save destination filename (.png recommended)

**Usage:**
```
flow_control> display save network_state.png
🎨 Displaying network graph...
   Saving to: network_state.png
✅ Graph visualization displayed
```

### Combined Usage Example

Multiple options can be combined:

```
flow_control> display P1 P3 layout planar_st save result.png
🎨 Displaying network graph...
   Highlighting paths: ['P1', 'P3']
   Using layout: planar_st
   Saving to: result.png
✅ Graph visualization displayed
```

---

## System Commands

System control commands.

### `help` / `h`

Displays help information.

**Usage:**
```
flow_control> help
```

### `quit` / `q` / `exit`

Exits the interactive monitor.

**Usage:**
```
flow_control> quit
🏁 Interactive monitor session ended.
```

---

## CLI Features ⭐ NEW

Command-line features that enhance the usability of the interactive monitor.

### Command History

**Features:**
- Remembers previously executed commands
- Persistent across sessions (`~/.flow_control_history`)
- Stores up to 1000 commands

**Operation:**
- `↑` / `Ctrl+P`: Previous command
- `↓` / `Ctrl+N`: Next command
- Press `↑` on empty prompt to recall last command

**Usage:**
```
flow_control> set P1 5.0
✅ Updated path P1 flow by 5.00

flow_control> [Press ↑]
flow_control> set P1 5.0  # Previous command is displayed
```

### Command Line Editing

**Features:**
- Cursor movement, character deletion, line editing capabilities
- Easy modification of long commands

**Key Bindings:**
- `Ctrl+A`: Move to beginning of line
- `Ctrl+E`: Move to end of line  
- `Ctrl+B` / `←`: Move cursor left
- `Ctrl+F` / `→`: Move cursor right
- `Ctrl+D`: Delete character at cursor
- `Ctrl+K`: Delete from cursor to end
- `Ctrl+U`: Delete entire line

**Usage:**
```
flow_control> set P1 10.0
             ↑Press Ctrl+A to move cursor to beginning
flow_control> set P1 10.0
         ↑Move here, can edit just the number part
```

### Tab Completion

**Features:**
- Auto-completion for command names, path IDs, edge IDs, file paths
- Press `Tab` during input to show/select candidates

**Completion Targets:**

1. **Command Names**
   ```
   flow_control> s[Tab]
   status  set  saturate  samples
   
   flow_control> sat[Tab]
   flow_control> saturate
   ```

2. **Path IDs** (set, adjust, saturate, maxflow, info path)
   ```
   flow_control> set P[Tab]
   P1  P2
   
   flow_control> info path p[Tab]  # case insensitive
   P1  P2
   ```

3. **Edge IDs** (disable, enable, info edge)
   ```
   flow_control> disable e[Tab]
   e0  e1  e2  e3
   
   flow_control> info edge E[Tab]  # case insensitive
   e0  e1  e2  e3
   ```

4. **Sample Names** (load, info)
   ```
   flow_control> load c[Tab]
   complex
   
   flow_control> load [Tab]
   diamond  complex  grid  star  layered  linear  parallel  bottleneck
   ```

5. **File Paths** (loadfile)
   ```
   flow_control> loadfile examples/[Tab]
   examples/simple_diamond.yaml    examples/star_network.yaml
   examples/complex_network.yaml   examples/bottleneck_network.yaml
   examples/grid_3x3.yaml
   ```

6. **info Command Subtypes**
   ```
   flow_control> info [Tab]
   path  edge
   
   flow_control> info p[Tab]
   flow_control> info path
   ```

### Case-Insensitive Input

**Features:**
- Path names, edge names, node names are case insensitive
- Command names remain case sensitive

**Supported Commands:**
- `set p1 5.0` ≡ `set P1 5.0`
- `info edge E2` ≡ `info edge e2`  
- `disable E1` ≡ `disable e1`
- `saturate p2` ≡ `saturate P2`

**Usage:**
```
flow_control> set p1 5.0      # lowercase input
✅ Updated path P1 flow by 5.00  # recognized as P1

flow_control> info edge E2    # uppercase input  
🔗 EDGE INFORMATION: e2         # recognized as e2

flow_control> saturate P1
flow_control> saturate p1     # both work the same
```

---

## Error Messages and Troubleshooting

### Common Errors

#### Capacity Exceeded Error
```
❌ Cannot update flow: Flow increase of 5.00 would exceed capacity by 2.00 at edge e3
```
**Solution:** Use `maxflow` command to check available capacity and set appropriate value

#### Path/Edge Not Found
```
❌ Path P5 not found
```
**Solution:** Use `status` command to check available path/edge IDs

#### Edge Already Disabled
```
❌ Edge e1 is already disabled
```
**Solution:** Use `edges` command to check current status

---

## Practical Workflows

### 1. Basic Experiment Flow

```bash
# 1. Select network
flow_control> load diamond

# 2. Apply suggested flows
flow_control> suggest

# 3. Check status
flow_control> status

# 4. Visualize
flow_control> display

# 5. Simulate edge failure
flow_control> disable e1

# 6. Check impact
flow_control> observe

# 7. Restore
flow_control> enable e1
```

### 2. Optimization Experiment Flow

```bash
# 1. Load complex network
flow_control> load complex

# 2. Check maximum capacity for each path
flow_control> maxflow P1
flow_control> maxflow P2
flow_control> maxflow P3
flow_control> maxflow P4

# 3. Set optimal flow distribution
flow_control> set P1 6.0
flow_control> set P2 7.0
flow_control> set P3 5.0
flow_control> set P4 8.0

# 4. Check network efficiency
flow_control> observe
```

### 3. Visual Analysis Flow

```bash
# 1. Load grid network
flow_control> load grid

# 2. Save initial state
flow_control> display save initial.png

# 3. Set flows
flow_control> distribute 15.0

# 4. Highlight flow paths
flow_control> display P1 P2 P3 save with_flow.png

# 5. Identify bottleneck paths
flow_control> maxflow P1
flow_control> display P1 save bottleneck.png
```

---

## Tips & Tricks

1. **Tab Completion**: Tab key auto-completion is available for most terminals
2. **Command History**: Use up/down arrow keys to access previous commands
3. **Pipeline Processing**: When executing multiple commands sequentially, confirm success of each command
4. **State Saving**: Use `display save` to record important states as images