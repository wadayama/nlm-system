# Flow Control Network System

## 📋 Overview

A static s-t network flow control system for interactive experimentation and visualization of flow control from source to sink nodes in networks.

## ✨ Key Features

### Core Functionality
- **Complete s-t path enumeration**: Automatic exploration of all paths in the network
- **Manual flow control**: Set individual path flows with bottleneck analysis
- **Edge failure simulation**: Enable/disable edges to test network resilience
- **Real-time visualization**: Graph display and status monitoring with NetworkX
- **Flow optimization**: Compare theoretical maximum flow with current flow

### New Advanced Features
- **Path saturation**: One-command path optimization to bottleneck capacity (`saturate P1`)
- **Detailed analysis**: Individual path and edge information with `info` commands  
- **External networks**: Load custom network topologies from YAML files
- **Command-line enhancements**: Readline support with history, editing, and tab completion
- **Case-insensitive IDs**: Use `p1` or `P1`, `e1` or `E1` interchangeably
- **8+ sample networks**: Pre-built topologies plus custom YAML support

## 🚀 Quick Start

### Installing Required Packages

```bash
# Install packages using uv (PyYAML added for external network support)
uv add matplotlib networkx pyyaml
```

### Running the Application

```bash
# Start the interactive monitor
uv run interactive_monitor.py
```

### Basic Usage

1. **Select a network**
   ```
   flow_control> load diamond
   flow_control> loadfile examples/star_network.yaml  # Or load custom YAML
   ```

2. **Set path flows**
   ```
   flow_control> set P1 5.0        # Manual flow setting
   flow_control> saturate P2       # Auto-saturate to maximum capacity
   ```

3. **Analyze network elements**
   ```
   flow_control> info path P1      # Detailed path information
   flow_control> info edge e2      # Detailed edge information
   ```

4. **Visualize and monitor**
   ```
   flow_control> display           # Show network graph
   flow_control> status           # Full network status
   flow_control> observe          # Complete state information
   ```

5. **Simulate failures**
   ```
   flow_control> disable e1       # Simulate edge failure
   flow_control> enable e1        # Restore edge
   ```

### Command-Line Features

The interactive monitor now includes modern CLI enhancements:
- **History**: Use ↑/↓ to navigate command history
- **Editing**: Ctrl+A/E for home/end, Ctrl+U to clear line
- **Tab completion**: Auto-complete commands and IDs (`set P[Tab]` → `P1, P2`)
- **Case-insensitive**: Use `p1` or `P1`, `e2` or `E2` interchangeably

## 📁 Project Structure

```
flow_control/
├── interactive_monitor.py   # Main application (interactive UI with readline)
├── flow_operations.py       # Flow control logic & detailed analysis
├── network_model.py         # Network data structures
├── network_display.py       # CUI display functionality
├── network_visualizer.py    # Graph visualization
├── network_samples.py       # Built-in sample network definitions  
├── network_file_loader.py   # YAML network file loading (NEW)
├── network_generators.py    # Network generation utilities
├── path_enumerator.py       # Complete s-t path enumeration algorithms
├── maxflow_calculator.py    # Max flow calculation
├── examples/                # Sample YAML network files (NEW)
│   ├── simple_diamond.yaml
│   ├── star_network.yaml
│   └── ...
├── docs/
│   ├── API_REFERENCE.md    # API specifications
│   └── COMMAND_REFERENCE.md # Command reference  
└── archive/                 # Test files and old documentation
```

## 📖 Documentation

- [API Reference](docs/API_REFERENCE.md) - Detailed Python API specifications
- [Command Reference](docs/COMMAND_REFERENCE.md) - Interactive command usage guide

## 🎮 Sample Networks

| ID | Name | Description | Nodes | Edges | Paths |
|---|---|---|---|---|---|
| `diamond` | Simple Diamond | Basic 2-path diamond topology | 4 | 4 | 2 |
| `complex` | Complex Multi-Path | Complex network with 4 overlapping paths | 6 | 8 | 4 |
| `grid` | Grid 3x3 | 3×3 grid topology | 9 | 12 | 6 |
| `star` | Star Network | Hub-and-spoke structure | 8 | 10 | 5 |
| `layered` | Layered Network | Hierarchical network | 7 | 9 | 3 |
| `linear` | Linear Chain | Single-path linear structure | 5 | 4 | 1 |
| `parallel` | Parallel Paths | 3 independent parallel paths | 8 | 9 | 3 |
| `bottleneck` | Bottleneck Network | Central bottleneck structure | 6 | 8 | 2 |

## 💡 Usage Examples

### Path Saturation (NEW)

```bash
# Automatically saturate path to maximum capacity
flow_control> saturate P1
✅ Path P1 saturated: 0.0 → 7.0 (bottleneck: e2)

# Check utilization
flow_control> info path P1
```

### Detailed Analysis (NEW)

```bash
# Get comprehensive path information
flow_control> info path P1
📊 PATH INFORMATION: P1
🛤️  Route: s → a → t
🟢 Status: NORMAL (71.4% utilization)

# Analyze edge details
flow_control> info edge e2
🔗 EDGE INFORMATION: e2
⚠️  Critical: Bottleneck for 1 path(s)
```

### External Network Loading (NEW)

```bash
# Load custom YAML network
flow_control> loadfile examples/star_network.yaml
✅ Loaded: Star Network (7 nodes, 9 edges, 4 paths)

# Create custom network (YAML format)
# See examples/ directory for templates
```

### Edge Failure Simulation

```bash
# Disable edge (case insensitive)
flow_control> disable E1    # or e1, both work

# Check affected paths
flow_control> status

# Restore edge
flow_control> enable e1
```

### Flow Optimization

```bash
# Check maximum safe flow for a path
flow_control> maxflow P1

# Distribute flow equally across all paths
flow_control> distribute 10.0

# Compare with theoretical maximum
flow_control> observe
```

### Visualization Options

```bash
# Highlight specific paths
flow_control> display P1 P2

# Change layout
flow_control> display layout planar_st

# Save as image
flow_control> display save network.png
```

## 🛠️ Development Environment

### Requirements

- Python 3.8+
- uv package manager

### Main Dependencies

- `matplotlib` - Graph rendering
- `networkx` - Network analysis and visualization
- `pyyaml` - YAML file parsing for external networks

## 🔄 Recent Updates

### Version 2.0 Features (Latest)

**🎯 Path Saturation**
- `saturate <path>` command for one-click path optimization
- Automatic bottleneck detection and capacity utilization

**📊 Detailed Analysis** 
- `info path <id>` - Comprehensive path information with bottleneck analysis
- `info edge <id>` - Edge utilization, critical path analysis, and status

**📁 External Networks**
- YAML file support for custom network topologies
- `loadfile <path>` command with 5 example networks
- NetworkFileLoader with complete validation and path enumeration

**⌨️ Enhanced CLI**
- Readline support: command history, line editing, tab completion
- Case-insensitive IDs: `p1`/`P1`, `e2`/`E2` work interchangeably
- Smart tab completion for commands, paths, edges, and files

**🎨 UI Improvements**
- Fixed path utilization visualization (100% = full bar)
- Enhanced status displays with detailed bottleneck information
- Improved error handling and user feedback

## 📝 License

This project is published for research and educational purposes.

## 🤝 Contributing

Please create an Issue for bug reports or feature suggestions.

---

**Note**: This system is for static network analysis. Time-based simulation features are not included.