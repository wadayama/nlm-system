#!/usr/bin/env python3
"""
Interactive Network Monitor

Real-time command-line monitoring and control interface for the flow control system.
Provides live updates and basic manual control capabilities.
"""

import os
import time
import sys
import yaml
import readline
import atexit
from pathlib import Path
from typing import Dict, List
from network_model import create_simple_network
from flow_operations import FlowController
from network_display import NetworkCUIDisplay
from network_samples import NetworkSampleGallery


class InteractiveNetworkMonitor:
    """Interactive command-line network monitor"""
    
    def __init__(self):
        """Initialize interactive monitor"""
        self.gallery = NetworkSampleGallery()
        self.current_sample_id = "diamond"
        self.network = self.gallery.get_sample(self.current_sample_id)
        self.controller = FlowController(self.network)
        self.display = NetworkCUIDisplay()
        self.running = True
        
        # Initialize readline for command editing and history
        self.history_file = Path.home() / ".flow_control_history"
        self._setup_readline()
        
        # Start with zero flows
    
    def _setup_readline(self):
        """Setup readline for command editing and history"""
        try:
            # Enable command completion
            readline.set_completer(self._command_completer)
            readline.parse_and_bind("tab: complete")
            
            # Try to load command history if it exists
            try:
                if self.history_file.exists():
                    readline.read_history_file(str(self.history_file))
            except (OSError, PermissionError):
                # Silently ignore history file errors
                pass
            
            # Limit history size
            readline.set_history_length(1000)
            
            # Register history save on exit
            atexit.register(self._save_history)
            
        except Exception as e:
            print(f"⚠️  Readline setup failed: {e}")
    
    def _save_history(self):
        """Save command history to file"""
        try:
            # Ensure history directory exists
            self.history_file.parent.mkdir(parents=True, exist_ok=True)
            readline.write_history_file(str(self.history_file))
        except (OSError, PermissionError):
            pass  # Silently ignore history save errors
    
    def _command_completer(self, text: str, state: int):
        """Tab completion for commands and parameters"""
        if state == 0:
            # Get current line and parse it
            line = readline.get_line_buffer()
            parts = line.split()
            
            # Complete command names
            if not parts or (len(parts) == 1 and not line.endswith(' ')):
                self._completion_matches = self._get_command_completions(text)
            else:
                # Complete parameters based on command
                cmd = parts[0].lower()
                self._completion_matches = self._get_parameter_completions(cmd, text, parts)
        
        if state < len(self._completion_matches):
            return self._completion_matches[state]
        return None
    
    def _get_command_completions(self, text: str) -> List[str]:
        """Get command name completions"""
        commands = [
            'status', 's', 'compact', 'c', 'observe', 'o', 'display', 'd',
            'help', 'h', 'quit', 'q', 'exit',
            'set', 'adjust', 'saturate', 'clear', 'distribute', 'maxflow',
            'disable', 'enable', 'edges',
            'samples', 'load', 'info', 'loadfile'
        ]
        return [cmd for cmd in commands if cmd.startswith(text.lower())]
    
    def _get_parameter_completions(self, cmd: str, text: str, parts: List[str]) -> List[str]:
        """Get parameter completions based on command"""
        completions = []
        
        if cmd in ['set', 'adjust', 'saturate', 'maxflow'] and len(parts) == 2:
            # Complete path IDs
            path_ids = list(self.network.paths.keys())
            completions = [pid for pid in path_ids if pid.lower().startswith(text.lower())]
            
        elif cmd in ['disable', 'enable'] and len(parts) == 2:
            # Complete edge IDs
            edge_ids = list(self.network.edges.keys())
            completions = [eid for eid in edge_ids if eid.lower().startswith(text.lower())]
            
        elif cmd in ['load', 'info'] and len(parts) == 2:
            # Complete sample names
            sample_names = list(self.gallery.list_samples().keys())
            completions = [name for name in sample_names if name.lower().startswith(text.lower())]
            
        elif cmd == 'loadfile' and len(parts) == 2:
            # Complete file paths
            try:
                import glob
                pattern = text + "*" if text else "*"
                files = glob.glob(pattern) + glob.glob("examples/" + pattern)
                completions = [f for f in files if f.endswith('.yaml') or f.endswith('.yml')]
            except:
                completions = []
        
        elif cmd == 'display' and len(parts) >= 2:
            # Complete display options
            display_options = ['save', 'layout'] + list(self.network.paths.keys())
            if text == '' or any(opt.startswith(text.lower()) for opt in display_options):
                completions = [opt for opt in display_options if opt.lower().startswith(text.lower())]
        
        elif cmd == 'info':
            if len(parts) == 2:
                # Complete info type (path or edge)
                info_types = ['path', 'edge']
                completions = [itype for itype in info_types if itype.startswith(text.lower())]
            elif len(parts) == 3:
                # Complete item ID based on info type
                info_type = parts[1].lower()
                if info_type == 'path':
                    path_ids = list(self.network.paths.keys())
                    completions = [pid for pid in path_ids if pid.lower().startswith(text.lower())]
                elif info_type == 'edge':
                    edge_ids = list(self.network.edges.keys())
                    completions = [eid for eid in edge_ids if eid.lower().startswith(text.lower())]
        
        return completions
    
    def _normalize_id(self, item_id: str, item_type: str) -> str:
        """
        Normalize ID for case-insensitive lookup.
        
        Args:
            item_id: Input ID (any case)
            item_type: Type of item ('path', 'edge', 'node')
            
        Returns:
            Actual ID as stored in network, or original if not found
        """
        if item_type == 'path':
            for actual_id in self.network.paths:
                if actual_id.lower() == item_id.lower():
                    return actual_id
        elif item_type == 'edge':
            for actual_id in self.network.edges:
                if actual_id.lower() == item_id.lower():
                    return actual_id
        elif item_type == 'node':
            for actual_id in self.network.nodes:
                if actual_id.lower() == item_id.lower():
                    return actual_id
        
        # Return original if not found (will trigger appropriate error)
        return item_id
    
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def show_help(self):
        """Display help information"""
        help_text = """
🖥️  INTERACTIVE NETWORK MONITOR - COMMANDS
================================================================================

📊 DISPLAY COMMANDS:
  s, status    - Show full network status
  c, compact   - Show compact status line
  o, observe   - Show complete observable state (all values)
  d, display   - Show network graph visualization
  h, help      - Show this help
  q, quit      - Exit monitor

🎛️  CONTROL COMMANDS:
  set <path> <flow>    - Set path flow (e.g., 'set P1 8.0')
  adjust <path> <delta> - Adjust path flow (e.g., 'adjust P2 +2.0')
  saturate <path>      - Set path flow to bottleneck capacity (e.g., 'saturate P1')
  clear                - Clear all flows to zero
  distribute <total>   - Distribute total flow equally across paths
  maxflow <path>       - Show maximum safe flow for path
  
🔧 EDGE MANIPULATION:
  disable <edge>       - Disable edge (set capacity to 0)
  enable <edge>        - Enable disabled edge  
  edges                - List all edges with status
  

🏛️  SAMPLE COMMANDS:
  samples      - List all available network samples
  load <name>  - Load a network sample (e.g., 'load complex')
  
  Available samples: diamond, complex, grid, star, layered, linear, parallel, bottleneck

📁 FILE COMMANDS:
  loadfile <path>      - Load network from YAML file

📊 INFO COMMANDS:
  info path <path_id>  - Show detailed path information (e.g., 'info path P1')
  info edge <edge_id>  - Show detailed edge information (e.g., 'info edge e2')

🎨 VISUALIZATION COMMANDS:
  display              - Show network graph (auto: s-t optimized)
  display P1           - Highlight path P1
  display save graph.png - Save visualization to file
  display layout <type> - Layout: planar_st/planar/spring/grid/hierarchical

📋 EXAMPLES:
  set P1 6.0           - Set P1 flow to 6.0
  adjust P2 -2.5       - Reduce P2 flow by 2.5
  saturate P1          - Set P1 to its maximum capacity
  info path P1         - Show detailed P1 path information
  info edge e2         - Show detailed e2 edge information
  disable e1           - Disable edge e1 (simulates failure)
  enable e1            - Re-enable edge e1
  edges                - Show all edge statuses
  load star            - Load star network sample
  loadfile examples/simple_diamond.yaml - Load from YAML file
  display P1 P2        - Show graph highlighting P1 and P2
  display layout planar_st - Use s-t optimized planar layout
  display save net.png - Save current visualization

================================================================================
"""
        print(help_text)
    
    def process_command(self, command: str) -> bool:
        """
        Process user command.
        
        Args:
            command: User input command
            
        Returns:
            True to continue, False to exit
        """
        command = command.strip().lower()
        
        if not command:
            return True
        
        parts = command.split()
        cmd = parts[0]
        
        try:
            if cmd in ['q', 'quit', 'exit']:
                return False
            
            elif cmd in ['h', 'help']:
                self.show_help()
            
            elif cmd in ['s', 'status']:
                self.display.display_network_status(self.network)
            
            elif cmd in ['c', 'compact']:
                self.display.display_compact_status(self.network)
            
            elif cmd in ['o', 'observe']:
                self._display_complete_state()
            
            elif cmd == 'set' and len(parts) == 3:
                path_id = self._normalize_id(parts[1], 'path')
                flow = float(parts[2])
                success, msg, alternatives = self.controller.set_path_flow_with_alternatives(path_id, flow)
                print(f"{'✅' if success else '❌'} {msg}")
            
            elif cmd == 'adjust' and len(parts) == 3:
                path_id = self._normalize_id(parts[1], 'path')
                delta = float(parts[2].replace('+', ''))
                success, msg = self.controller.update_path_flow(path_id, delta)
                print(f"{'✅' if success else '❌'} {msg}")
            
            elif cmd == 'clear':
                self.controller.clear_all_flows()
                print("✅ All flows cleared to zero")
            
            elif cmd == 'distribute' and len(parts) == 2:
                total_flow = float(parts[1])
                success, msg = self.controller.distribute_flow_equally(total_flow)
                print(f"{'✅' if success else '❌'} {msg}")
            
            elif cmd == 'maxflow' and len(parts) == 2:
                path_id = self._normalize_id(parts[1], 'path')
                alternatives = self.controller.calculate_max_safe_flow(path_id)
                if 'error' in alternatives:
                    print(f"❌ {alternatives['error']}")
                else:
                    self._display_path_alternatives(alternatives)
            
            elif cmd == 'saturate' and len(parts) == 2:
                path_id = self._normalize_id(parts[1], 'path')
                success, msg, info = self.controller.saturate_path_flow(path_id)
                print(f"{'✅' if success else '❌'} {msg}")
                if success and info and not info.get('error'):
                    # Show compact status to see the change
                    self.display.display_compact_status(self.network)
            
            elif cmd in ['display', 'd']:
                # Display network graph visualization
                self._display_network_graph(parts[1:])
            
            elif cmd == 'samples':
                # List available network samples
                self._list_samples()
            
            elif cmd == 'load':
                # Load a network sample
                if len(parts) < 2:
                    print("❌ Usage: load <sample_name>")
                    self._list_samples()
                else:
                    self._load_sample(parts[1])
            
            elif cmd == 'info':
                # Show detailed information about path/edge OR sample information
                if len(parts) >= 3 and parts[1].lower() in ['path', 'edge']:
                    # New detailed info command: info path P1, info edge e2
                    info_type = parts[1].lower()
                    item_id = self._normalize_id(parts[2], info_type)
                    self._show_item_info(info_type, item_id)
                elif len(parts) >= 2:
                    # Original sample info command: info diamond
                    sample_name = parts[1]
                    self._show_sample_info(sample_name)
                else:
                    # Show current sample info
                    self._show_sample_info(self.current_sample_id)
            
            elif cmd == 'disable' and len(parts) == 2:
                # Disable an edge
                edge_id = self._normalize_id(parts[1], 'edge')
                success, msg = self.controller.disable_edge(edge_id)
                print(f"{'✅' if success else '❌'} {msg}")
            
            elif cmd == 'enable' and len(parts) == 2:
                # Enable an edge
                edge_id = self._normalize_id(parts[1], 'edge')
                success, msg = self.controller.enable_edge(edge_id)
                print(f"{'✅' if success else '❌'} {msg}")
            
            elif cmd == 'edges':
                # List edge status
                self._list_edge_status()
            
            elif cmd == 'loadfile' and len(parts) >= 2:
                # Load network from YAML file
                file_path = ' '.join(parts[1:])
                self._load_network_file(file_path)
            
            else:
                print(f"❌ Unknown command: {command}")
                print("💡 Type 'help' for available commands")
        
        except Exception as e:
            print(f"❌ Error: {e}")
        
        return True
    
    def _display_network_graph(self, args: List[str]):
        """Display network graph visualization"""
        try:
            from network_visualizer import display_network
            
            # Parse arguments
            highlight_paths = []
            layout = "auto"
            save_file = None
            
            i = 0
            while i < len(args):
                arg = args[i]
                
                if arg == "save" and i + 1 < len(args):
                    save_file = args[i + 1]
                    i += 2
                elif arg == "layout" and i + 1 < len(args):
                    layout = args[i + 1]
                    i += 2
                elif arg.startswith("P") or arg in self.network.paths:
                    # Path ID to highlight
                    highlight_paths.append(arg)
                    i += 1
                else:
                    print(f"⚠️  Unknown display option: {arg}")
                    i += 1
            
            # Validate path IDs
            valid_paths = []
            for path_id in highlight_paths:
                if path_id in self.network.paths:
                    valid_paths.append(path_id)
                else:
                    print(f"⚠️  Path {path_id} not found. Available: {list(self.network.paths.keys())}")
            
            # Display graph
            print(f"🎨 Displaying network graph...")
            if valid_paths:
                print(f"   Highlighting paths: {valid_paths}")
            if layout != "auto":
                print(f"   Using layout: {layout}")
            if save_file:
                print(f"   Saving to: {save_file}")
            
            display_network(self.network, 
                          highlight_paths=valid_paths if valid_paths else None,
                          layout=layout,
                          save_file=save_file,
                          show_max_flow=True)
            
            print("✅ Graph visualization displayed")
            
        except ImportError:
            print("❌ Network visualization not available (matplotlib/networkx required)")
        except Exception as e:
            print(f"❌ Error displaying graph: {e}")
    
    def _list_samples(self):
        """List all available network samples"""
        print("🏛️  AVAILABLE NETWORK SAMPLES")
        print("=" * 70)
        
        samples_info = self.gallery.list_samples()
        current = self.current_sample_id
        
        for sample_id, info in samples_info.items():
            marker = "👉" if sample_id == current else "🔸"
            print(f"\n{marker} {sample_id.upper()}: {info['name']}")
            print(f"   {info['description']}")
            print(f"   Size: {info['nodes']} nodes, {info['edges']} edges, {info['paths']} paths")
            print(f"   Features: {', '.join(info['features'])}")
        
        print(f"\n💡 Current sample: {current.upper()}")
        print("💡 Use 'load <sample_name>' to switch networks")
    
    def _load_sample(self, sample_name: str):
        """Load a network sample"""
        try:
            # Get the sample
            new_network = self.gallery.get_sample(sample_name)
            info = self.gallery.get_sample_info(sample_name)
            
            # Update monitor state
            self.network = new_network
            self.controller = FlowController(self.network)
            self.current_sample_id = sample_name
            
            print(f"✅ Loaded: {info['name']}")
            print(f"   Topology: {info['nodes']} nodes, {info['edges']} edges, {info['paths']} paths")
            print(f"   Features: {', '.join(info['features'])}")
            
            # Show current status
            self.display.display_compact_status(self.network)
            
            print("💡 Use 'set' command to configure flows")
            
        except ValueError as e:
            print(f"❌ {e}")
        except Exception as e:
            print(f"❌ Error loading sample: {e}")
    
    def _show_sample_info(self, sample_name: str):
        """Show detailed information about a sample"""
        try:
            info = self.gallery.get_sample_info(sample_name)
            current = sample_name == self.current_sample_id
            
            status = " (CURRENT)" if current else ""
            print(f"📊 SAMPLE INFO: {sample_name.upper()}{status}")
            print("=" * 60)
            print(f"Name: {info['name']}")
            print(f"Description: {info['description']}")
            print(f"Topology: {info['nodes']} nodes, {info['edges']} edges, {info['paths']} paths")
            print(f"Features:")
            for feature in info['features']:
                print(f"  • {feature}")
            
            if not current:
                print(f"\n💡 Use 'load {sample_name}' to switch to this sample")
                
        except ValueError as e:
            print(f"❌ {e}")
        except Exception as e:
            print(f"❌ Error getting sample info: {e}")
    
    def _load_network_file(self, file_path: str):
        """Load network from YAML file"""
        try:
            from network_file_loader import NetworkFileLoader
            loader = NetworkFileLoader()
            
            # Load the network
            self.network = loader.load_yaml(file_path)
            self.controller = FlowController(self.network)
            
            # Get name and description from YAML if available
            try:
                with open(file_path, 'r') as f:
                    data = yaml.safe_load(f)
                    name = data.get('name', 'Custom Network')
                    description = data.get('description', '')
            except:
                name = 'Custom Network'
                description = ''
            
            print(f"✅ Loaded: {name}")
            if description:
                print(f"   Description: {description}")
            print(f"   File: {file_path}")
            print(f"   Topology: {len(self.network.nodes)} nodes, "
                  f"{len(self.network.edges)} edges, "
                  f"{len(self.network.paths)} paths")
            
            # Show compact status
            self.display.display_compact_status(self.network)
            
        except FileNotFoundError:
            print(f"❌ File not found: {file_path}")
        except yaml.YAMLError as e:
            print(f"❌ Invalid YAML format: {e}")
        except ValueError as e:
            print(f"❌ Invalid network definition: {e}")
        except Exception as e:
            print(f"❌ Error loading network: {e}")
    
    def _list_edge_status(self):
        """List all edges with their current status"""
        edge_status = self.controller.list_edge_status()
        
        print("🔗 EDGE STATUS")
        print("=" * 70)
        print(f"{'Edge':<6} {'From':<6} {'To':<6} {'Capacity':<10} {'Flow':<8} {'Util%':<8} {'Status'}")
        print("-" * 70)
        
        for edge_id, status in edge_status.items():
            util_str = f"{status['utilization']*100:.0f}%" if status['utilization'] != float('inf') else "∞"
            
            # Status icons
            if status['is_failed']:
                status_icon = "🔴 DISABLED"
            elif status['status'] == 'OVERLOAD':
                status_icon = "🟡 OVERLOAD"
            else:
                status_icon = "🟢 OK"
            
            print(f"{edge_id:<6} {status['from']:<6} {status['to']:<6} "
                  f"{status['capacity']:<10.1f} {status['flow']:<8.1f} {util_str:<8} {status_icon}")
        
        disabled_count = sum(1 for s in edge_status.values() if s['is_failed'])
        print(f"\n📊 Summary: {len(edge_status)} total edges, {disabled_count} disabled")
    
    def run(self):
        """Main interactive loop"""
        self.clear_screen()
        
        print("🖥️  FLOW CONTROL INTERACTIVE MONITOR")
        print("=" * 80)
        print("💡 Type 'help' for commands, 'status' for current state, 'quit' to exit")
        print("💡 Editing: Ctrl+A/E (home/end), ↑/↓ (history), Tab (completion)")
        print("=" * 80)
        
        # Show initial status
        self.display.display_compact_status(self.network)
        print()
        
        while self.running:
            try:
                command = input("🔧 flow_control> ").strip()
                if command:  # Only add non-empty commands to history
                    readline.add_history(command)
                if not self.process_command(command):
                    break
                    
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except EOFError:
                break
        
        print("🏁 Interactive monitor session ended.")
    
    def _display_complete_state(self):
        """Display complete observable network state"""
        state = self.controller.get_complete_network_state()
        
        print("\n" + "=" * 80)
        print("🔍 COMPLETE OBSERVABLE NETWORK STATE")
        print("=" * 80)
        
        # System overview
        metrics = state['system_metrics']
        print(f"📊 System Overview:")
        print(f"   Throughput: {metrics['total_throughput']:.2f} / {metrics['theoretical_max_flow']:.2f} (efficiency: {metrics['network_efficiency']:.1%})")
        print(f"   Edges: {metrics['operational_edges']} operational, {metrics['failed_edges']} failed")
        print(f"   Paths: {len(state['paths'])} total, {metrics['blocked_paths']} blocked")
        
        # Edge details
        print(f"\n🔗 Edge States:")
        print(f"{'ID':<4} {'From':<4} {'To':<4} {'Capacity':<8} {'Flow':<8} {'Available':<9} {'Util%':<6} {'Status'}")
        print("-" * 60)
        for edge_id, edge_data in state['edges'].items():
            status = "FAIL" if edge_data['is_failed'] else "OK"
            util_pct = edge_data['utilization'] * 100 if edge_data['utilization'] != float('inf') else 999
            print(f"{edge_id:<4} {edge_data['from_node']:<4} {edge_data['to_node']:<4} "
                  f"{edge_data['capacity']:<8.1f} {edge_data['current_flow']:<8.1f} "
                  f"{edge_data['available_capacity']:<9.1f} {util_pct:<6.0f} {status}")
        
        # Path details
        print(f"\n🛤️  Path States:")
        print(f"{'ID':<4} {'Edges':<12} {'Flow':<8} {'Capacity':<8} {'Available':<9} {'Util%':<6} {'Status'}")
        print("-" * 65)
        for path_id, path_data in state['paths'].items():
            status = "BLOCKED" if path_data['is_blocked'] else "OK"
            edges_str = "→".join(path_data['edge_sequence'])
            util_pct = path_data['utilization'] * 100 if path_data['utilization'] != float('inf') else 999
            print(f"{path_id:<4} {edges_str:<12} {path_data['current_flow']:<8.1f} "
                  f"{path_data['bottleneck_capacity']:<8.1f} {path_data['available_capacity']:<9.1f} "
                  f"{util_pct:<6.0f} {status}")
            if path_data['bottleneck_edge']:
                print(f"     └─ Bottleneck: {path_data['bottleneck_edge']}")
        
        
        print("=" * 80)
    
    def _display_path_alternatives(self, alternatives: Dict):
        """Display path flow alternatives information"""
        print(f"\n📊 Path Flow Analysis: {alternatives['path_id']}")
        print("─" * 50)
        
        if alternatives.get('is_blocked'):
            print("❌ Path is BLOCKED (bottleneck capacity = 0)")
            print(f"   Blocked at: {alternatives['bottleneck_edge']}")
            return
        
        print(f"📈 Current State:")
        print(f"   Current flow: {alternatives['current_flow']:.1f}")
        print(f"   Available capacity: {alternatives['available_capacity']:.1f}")
        
        print(f"\n🎯 Flow Limits:")
        print(f"   Maximum safe flow: {alternatives['max_safe_flow']:.1f}")
        print(f"   Suggested flow: {alternatives['suggested_flow']:.1f}")
        
        print(f"\n🔗 Bottleneck Information:")
        print(f"   Bottleneck edge: {alternatives['bottleneck_edge']}")
        print(f"   Bottleneck capacity: {alternatives['bottleneck_capacity']:.1f}")
        print(f"   Path edges: {' → '.join(alternatives['edge_sequence'])}")
        
        # Utilization info
        if alternatives['max_safe_flow'] > 0:
            current_util = (alternatives['current_flow'] / alternatives['max_safe_flow']) * 100
            print(f"\n📊 Utilization:")
            print(f"   Current: {current_util:.1f}%")
            
            # Visual bar
            bar_length = 20
            filled = int((current_util / 100) * bar_length)
            bar = "█" * filled + "░" * (bar_length - filled)
            print(f"   [{bar}] {alternatives['current_flow']:.1f}/{alternatives['max_safe_flow']:.1f}")
    
    def _show_item_info(self, info_type: str, item_id: str):
        """Show detailed information about a path or edge"""
        if info_type == 'path':
            info = self.controller.get_path_info(item_id)
            if 'error' in info:
                print(f"❌ {info['error']}")
            else:
                self._display_path_info(info)
        elif info_type == 'edge':
            info = self.controller.get_edge_info(item_id)
            if 'error' in info:
                print(f"❌ {info['error']}")
            else:
                self._display_edge_info(info)
        else:
            print(f"❌ Unknown info type: {info_type}")
            print("💡 Use 'path' or 'edge'")
    
    def _display_path_info(self, info: Dict):
        """Display detailed path information"""
        path_id = info['path_id']
        status_icons = {
            'BLOCKED': '🔴',
            'SATURATED': '🟠',
            'HIGH': '🟡',
            'NORMAL': '🟢',
            'LOW': '🔵'
        }
        status_icon = status_icons.get(info['status'], '⚪')
        
        print(f"\n📊 PATH INFORMATION: {path_id}")
        print("=" * 60)
        
        # Basic information
        print(f"🛤️  Route: {info['route_description']}")
        print(f"📏 Edges: {' → '.join(info['edges'])} ({info['edge_count']} total)")
        print(f"{status_icon} Status: {info['status']}")
        
        # Flow information
        print(f"\n💧 Flow Information:")
        print(f"   Current flow: {info['current_flow']:.1f}")
        print(f"   Maximum capacity: {info['bottleneck_capacity']:.1f}")
        print(f"   Available capacity: {info['available_capacity']:.1f}")
        print(f"   Utilization: {info['utilization']:.1%}")
        
        # Bottleneck information
        print(f"\n🔗 Bottleneck:")
        print(f"   Limiting edge: {info['bottleneck_edge']}")
        print(f"   Bottleneck capacity: {info['bottleneck_capacity']:.1f}")
        
        # Edge details
        print(f"\n🔗 Edge Details:")
        print(f"{'Edge':<6} {'From':<6} {'To':<6} {'Capacity':<10} {'Flow':<8} {'Util%':<8} {'Bottleneck'}")
        print("-" * 60)
        for edge_detail in info['edge_details']:
            util_str = f"{edge_detail['utilization']:.0%}" if edge_detail['utilization'] != float('inf') else "∞"
            bottleneck_mark = "🔴 YES" if edge_detail['is_bottleneck'] else ""
            print(f"{edge_detail['id']:<6} {edge_detail['from']:<6} {edge_detail['to']:<6} "
                  f"{edge_detail['capacity']:<10.1f} {edge_detail['flow']:<8.1f} {util_str:<8} {bottleneck_mark}")
        
        # Shared paths
        if info['shared_paths']:
            print(f"\n🔗 Shared with paths: {', '.join(info['shared_paths'])}")
        else:
            print(f"\n🔗 No edge sharing with other paths")
        
        print("=" * 60)
    
    def _display_edge_info(self, info: Dict):
        """Display detailed edge information"""
        edge_id = info['edge_id']
        status_icons = {
            'DISABLED': '🔴',
            'OVERLOAD': '🟠',
            'HIGH': '🟡',
            'NORMAL': '🟢',
            'LOW': '🔵'
        }
        status_icon = status_icons.get(info['status'], '⚪')
        
        print(f"\n🔗 EDGE INFORMATION: {edge_id}")
        print("=" * 60)
        
        # Basic information
        print(f"🔗 Connection: {info['from_node']} → {info['to_node']}")
        print(f"📊 Capacity: {info['capacity']:.1f}")
        print(f"{status_icon} Status: {info['status']}")
        if info['is_critical']:
            print(f"⚠️  Critical: Bottleneck for {len(info['bottleneck_for'])} path(s)")
        
        # Flow information
        print(f"\n💧 Flow Information:")
        print(f"   Current flow: {info['current_flow']:.1f}")
        print(f"   Available capacity: {info['available_capacity']:.1f}")
        print(f"   Utilization: {info['utilization']:.1%}")
        
        # Path usage
        print(f"\n🛤️  Used by {info['path_count']} path(s):")
        if info['using_paths']:
            print(f"{'Path':<6} {'Flow':<8} {'Position':<10} {'Total Edges'}")
            print("-" * 40)
            for path_usage in info['using_paths']:
                position_str = f"{path_usage['path_position']}/{path_usage['total_edges']}"
                print(f"{path_usage['path_id']:<6} {path_usage['path_flow']:<8.1f} {position_str:<10} {path_usage['total_edges']}")
        else:
            print("   None")
        
        # Bottleneck information
        if info['bottleneck_for']:
            print(f"\n🔴 Bottleneck for paths: {', '.join(info['bottleneck_for'])}")
        
        print("=" * 60)


def main():
    """Main entry point"""
    monitor = InteractiveNetworkMonitor()
    monitor.run()


if __name__ == "__main__":
    main()