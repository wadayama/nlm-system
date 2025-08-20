#!/usr/bin/env python3
"""
Network Visualizer for Flow Control System

Real-time visualization of network topology, flow states, alerts, and performance metrics.
Provides essential visual feedback for development, debugging, and analysis.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as ticker
import networkx as nx
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

from network_model import NetworkState, NetworkNode, NetworkEdge


@dataclass
class VisualizationConfig:
    """Configuration for network visualization"""
    figsize: Tuple[float, float] = (18, 10)
    node_size: int = 800
    edge_width_scale: float = 3.0
    alert_highlight_width: float = 4.0
    update_interval: float = 1.0  # seconds
    max_history_points: int = 100
    
    # Colors
    source_color: str = '#2E8B57'  # Sea Green
    sink_color: str = '#DC143C'    # Crimson
    intermediate_color: str = '#4682B4'  # Steel Blue
    
    normal_edge_color: str = '#708090'  # Slate Gray
    overload_edge_color: str = '#FF4500'  # Orange Red
    failed_edge_color: str = '#8B0000'   # Dark Red
    
    flow_color: str = '#1E90FF'  # Dodger Blue
    capacity_color: str = '#32CD32'  # Lime Green


class NetworkVisualizer:
    """Main visualization class for network flow control system"""
    
    def __init__(self, config: VisualizationConfig = None):
        """
        Initialize network visualizer.
        
        Args:
            config: Visualization configuration
        """
        self.config = config or VisualizationConfig()
        self.fig = None
        self.axes = None
        self.graph = None
        self.pos = None
        
        # Performance tracking removed - static network only
        
        # Current network state
        self.current_network: Optional[NetworkState] = None
        
        # Interactive mode flag
        self.interactive_mode = False
    
    def setup_figure(self, network: NetworkState):
        """
        Set up the matplotlib figure with multiple subplots.
        
        Args:
            network: Network state to visualize
        """
        self.current_network = network
        
        # Create figure with subplots
        self.fig, self.axes = plt.subplots(2, 2, figsize=self.config.figsize)
        self.fig.suptitle('Flow Control Network Visualization', fontsize=16, fontweight='bold')
        
        # Subplot arrangement:
        # [0,0]: Network topology    [0,1]: Performance metrics
        # [1,0]: Flow distribution   [1,1]: System status
        
        self.axes[0,0].set_title('Network Topology')
        self.axes[0,1].set_title('Performance Metrics')
        self.axes[1,0].set_title('Flow Distribution')
        self.axes[1,1].set_title('System Status')
        
        # Create NetworkX graph for layout
        self._build_networkx_graph(network)
        
        plt.tight_layout(rect=[0, 0, 1, 0.95])  # Leave space for legend at the top
        return self.fig, self.axes
    
    def _build_networkx_graph(self, network: NetworkState):
        """Build NetworkX graph for layout calculation"""
        self.graph = nx.DiGraph()
        
        # Add nodes
        for node_id, node in network.nodes.items():
            self.graph.add_node(node_id, node_type=node.type)
        
        # Add edges
        for edge_id, edge in network.edges.items():
            self.graph.add_edge(edge.from_node, edge.to_node, 
                              edge_id=edge_id, edge_obj=edge)
        
        # Calculate layout positions optimized for s-t networks
        self.pos = self._calculate_optimized_layout(network)
    
    def _calculate_optimized_layout(self, network: NetworkState) -> Dict:
        """
        Calculate optimized node positions to minimize edge crossings for s-t networks.
        
        Args:
            network: NetworkState to layout
            
        Returns:
            Dictionary of node_id -> (x, y) positions
        """
        positions = {}
        
        # For the simple 2-path s-t network, use manual positioning
        if (len(network.nodes) == 4 and network.source_node == 's' and 
            network.sink_node == 't' and 'v1' in network.nodes and 'v2' in network.nodes):
            
            # Optimized layout for 2-path network to avoid crossings
            positions = {
                's': (-2.0, 0.0),     # Source on the left center
                'v1': (-0.5, 0.8),    # Upper intermediate node
                'v2': (-0.5, -0.8),   # Lower intermediate node  
                't': (2.0, 0.0)       # Sink on the right center
            }
        else:
            # Fall back to automatic layout for other topologies
            try:
                # Try hierarchical layout first
                positions = self._hierarchical_layout(network)
            except:
                # Fall back to spring layout if hierarchical fails
                if len(self.graph.nodes) <= 10:
                    positions = nx.spring_layout(self.graph, k=2, iterations=50, seed=42)
                else:
                    positions = nx.kamada_kawai_layout(self.graph)
                
                # Adjust for s-t placement
                if network.source_node and network.sink_node:
                    positions[network.source_node] = (-1.5, 0)
                    positions[network.sink_node] = (1.5, 0)
        
        return positions
    
    def _hierarchical_layout(self, network: NetworkState) -> Dict:
        """
        Create hierarchical layout for s-t networks.
        
        Args:
            network: NetworkState to layout
            
        Returns:
            Dictionary of node_id -> (x, y) positions
        """
        positions = {}
        
        # Identify layers: source -> intermediate -> sink
        source_nodes = [nid for nid, node in network.nodes.items() if node.type == 'source']
        sink_nodes = [nid for nid, node in network.nodes.items() if node.type == 'sink']
        intermediate_nodes = [nid for nid, node in network.nodes.items() if node.type == 'intermediate']
        
        # Layer 0: Source nodes
        for i, node_id in enumerate(source_nodes):
            y_offset = (i - (len(source_nodes) - 1) / 2) * 0.5
            positions[node_id] = (-2.0, y_offset)
        
        # Layer 1: Intermediate nodes
        for i, node_id in enumerate(intermediate_nodes):
            y_offset = (i - (len(intermediate_nodes) - 1) / 2) * 1.0
            positions[node_id] = (0.0, y_offset)
        
        # Layer 2: Sink nodes
        for i, node_id in enumerate(sink_nodes):
            y_offset = (i - (len(sink_nodes) - 1) / 2) * 0.5
            positions[node_id] = (2.0, y_offset)
        
        return positions
    
    def update_visualization(self, network: NetworkState):
        """
        Update all visualization components with current network state.
        
        Args:
            network: Current network state
        """
        self.current_network = network
        
        # Clear all axes
        for ax in self.axes.flat:
            ax.clear()
        
        # Update each subplot
        self._draw_network_topology(network)
        self._draw_performance_metrics(network)
        self._draw_flow_distribution(network)
        self._draw_alert_dashboard(network)
        
        self.fig.canvas.draw()
    
    def _draw_network_topology(self, network: NetworkState):
        """Draw the network topology with current state"""
        ax = self.axes[0,0]
        ax.set_title('Network Topology')
        
        if not self.graph or not self.pos:
            ax.text(0.5, 0.5, 'No network topology available', 
                   ha='center', va='center', transform=ax.transAxes)
            return
        
        # Draw nodes
        node_colors = []
        for node_id in self.graph.nodes():
            node = network.nodes.get(node_id)
            if node:
                if node.type == 'source':
                    node_colors.append(self.config.source_color)
                elif node.type == 'sink':
                    node_colors.append(self.config.sink_color)
                else:
                    node_colors.append(self.config.intermediate_color)
            else:
                node_colors.append(self.config.intermediate_color)
        
        nx.draw_networkx_nodes(self.graph, self.pos, ax=ax,
                              node_color=node_colors,
                              node_size=self.config.node_size,
                              alpha=0.8)
        
        # Draw edges with different styles based on state
        normal_edges = []
        overload_edges = []
        failed_edges = []
        
        edge_labels = {}
        
        for (u, v, data) in self.graph.edges(data=True):
            edge_obj = data.get('edge_obj')
            edge_id = data.get('edge_id')
            
            if edge_obj:
                # Create edge label with capacity and flow
                label = f'{edge_id}\nc={edge_obj.capacity:.1f}\nf={edge_obj.flow:.1f}'
                edge_labels[(u, v)] = label
                
                # Categorize edge by state
                if edge_obj.is_failed or edge_obj.capacity == 0:
                    failed_edges.append((u, v))
                elif edge_obj.overload_alert or edge_obj.flow > edge_obj.capacity:
                    overload_edges.append((u, v))
                else:
                    normal_edges.append((u, v))
        
        # Draw edges by category
        if normal_edges:
            nx.draw_networkx_edges(self.graph, self.pos, ax=ax,
                                  edgelist=normal_edges,
                                  edge_color=self.config.normal_edge_color,
                                  width=2, alpha=0.7)
        
        if overload_edges:
            nx.draw_networkx_edges(self.graph, self.pos, ax=ax,
                                  edgelist=overload_edges,
                                  edge_color=self.config.overload_edge_color,
                                  width=self.config.alert_highlight_width, alpha=0.9)
        
        if failed_edges:
            nx.draw_networkx_edges(self.graph, self.pos, ax=ax,
                                  edgelist=failed_edges,
                                  edge_color=self.config.failed_edge_color,
                                  width=self.config.alert_highlight_width, 
                                  style='dashed', alpha=0.9)
        
        # Draw labels
        nx.draw_networkx_labels(self.graph, self.pos, ax=ax, 
                               font_size=10, font_weight='bold')
        
        # Draw edge labels
        nx.draw_networkx_edge_labels(self.graph, self.pos, edge_labels, ax=ax,
                                    font_size=7, bbox=dict(boxstyle='round,pad=0.1',
                                                          facecolor='white', alpha=0.9))
        
        ax.set_aspect('equal')
        ax.axis('off')
        
        # Add legend above the network topology plot
        legend_elements = [
            mpatches.Circle((0, 0), 1, facecolor=self.config.source_color, label='Source'),
            mpatches.Circle((0, 0), 1, facecolor=self.config.sink_color, label='Sink'),
            mpatches.Circle((0, 0), 1, facecolor=self.config.intermediate_color, label='Intermediate'),
            plt.Line2D([0], [0], color=self.config.normal_edge_color, lw=2, label='Normal'),
            plt.Line2D([0], [0], color=self.config.overload_edge_color, lw=3, label='Overload'),
            plt.Line2D([0], [0], color=self.config.failed_edge_color, lw=3, linestyle='--', label='Failed')
        ]
        ax.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, 1.15), 
                 ncol=3, fontsize=8, frameon=True, fancybox=True, shadow=True)
    
    def _draw_performance_metrics(self, network: NetworkState):
        """Draw current performance metrics (static view)"""
        ax = self.axes[0,1]
        ax.set_title('Performance Metrics')
        
        # Calculate current metrics
        throughput = network.calculate_total_throughput()
        operational_edges = len([e for e in network.edges.values() if not e.is_failed])
        active_paths = len([p for p in network.paths.values() if p.current_flow > 0])
        
        # Calculate max flow if available
        max_flow_text = ""
        try:
            from maxflow_calculator import MaxFlowCalculator
            calc = MaxFlowCalculator(network)
            max_flow, _ = calc.calculate_max_flow()
            utilization = (throughput / max_flow * 100) if max_flow > 0 else 0
            max_flow_text = f"\nTheoretical Max Flow: {max_flow:.2f}\nUtilization: {utilization:.1f}%"
        except:
            pass
        
        # Display current metrics as text
        metrics_text = f"""Current Performance Metrics

Total Throughput: {throughput:.2f}{max_flow_text}

Network Status:
• Operational Edges: {operational_edges}/{len(network.edges)}
• Active Paths: {active_paths}/{len(network.paths)}
• Failed Edges: {len([e for e in network.edges.values() if e.is_failed])}
        """
        
        ax.text(0.1, 0.5, metrics_text, 
               ha='left', va='center', fontsize=11,
               transform=ax.transAxes)
        ax.axis('off')
    
    def _draw_flow_distribution(self, network: NetworkState):
        """Draw current flow distribution across paths"""
        ax = self.axes[1,0]
        ax.set_title('Path Flow Distribution')
        
        if not network.paths:
            ax.text(0.5, 0.5, 'No paths defined', 
                   ha='center', va='center', transform=ax.transAxes)
            return
        
        path_names = list(network.paths.keys())
        path_flows = [path.current_flow for path in network.paths.values()]
        path_capacities = []
        
        # Calculate bottleneck capacities
        for path in network.paths.values():
            bottleneck_capacity, _ = path.calculate_bottleneck(network.edges)
            path_capacities.append(bottleneck_capacity)
        
        x_pos = np.arange(len(path_names))
        width = 0.35
        
        # Draw bars
        bars1 = ax.bar(x_pos - width/2, path_flows, width, 
                      color=self.config.flow_color, alpha=0.8, label='Current Flow')
        bars2 = ax.bar(x_pos + width/2, path_capacities, width,
                      color=self.config.capacity_color, alpha=0.8, label='Bottleneck Capacity')
        
        ax.set_xlabel('Path ID')
        ax.set_ylabel('Flow/Capacity')
        ax.set_xticks(x_pos)
        ax.set_xticklabels(path_names)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Add value labels on bars
        for i, (flow, capacity) in enumerate(zip(path_flows, path_capacities)):
            ax.text(i - width/2, flow + 0.1, f'{flow:.1f}', 
                   ha='center', va='bottom', fontsize=8)
            ax.text(i + width/2, capacity + 0.1, f'{capacity:.1f}', 
                   ha='center', va='bottom', fontsize=8)
    
    def _draw_alert_dashboard(self, network: NetworkState):
        """Draw current alerts and system status"""
        ax = self.axes[1,1]
        ax.set_title('System Status & s-t Paths')
        ax.axis('off')
        
        # System summary
        summary_text = f"""SYSTEM STATUS
Total Throughput: {network.total_flow:.2f}"""
        
        ax.text(0.05, 0.95, summary_text, transform=ax.transAxes, 
               verticalalignment='top', fontsize=10, fontweight='bold')
        
        # s-t Paths listing
        paths_y = 0.75
        ax.text(0.05, paths_y, 'AVAILABLE s-t PATHS:', transform=ax.transAxes,
               verticalalignment='top', fontsize=9, fontweight='bold', color='navy')
        
        for i, (path_id, path) in enumerate(network.paths.items()):
            path_y = paths_y - 0.06 - i * 0.04
            
            # Build path description with edge sequence
            edge_sequence = " → ".join(path.edges)
            bottleneck_capacity, bottleneck_edge = path.calculate_bottleneck(network.edges)
            
            path_text = f"• {path_id}: {edge_sequence}"
            ax.text(0.08, path_y, path_text, transform=ax.transAxes,
                   verticalalignment='top', fontsize=8, color='black')
            
            # Add flow and capacity info
            flow_info = f"  Flow={path.current_flow:.1f}, Capacity={bottleneck_capacity:.1f}, Util={path.current_flow/bottleneck_capacity*100:.1f}%" if bottleneck_capacity > 0 else f"  Flow={path.current_flow:.1f}, Capacity=0.0, Util=∞"
            ax.text(0.08, path_y - 0.025, flow_info, transform=ax.transAxes,
                   verticalalignment='top', fontsize=7, color='gray')
        
        # Current alerts section
        alert_start_y = max(0.45, paths_y - len(network.paths) * 0.08)
        ax.text(0.05, alert_start_y, 'CURRENT ALERTS:', transform=ax.transAxes,
               verticalalignment='top', fontsize=9, fontweight='bold', color='red')
        
        # List alerts (fewer to make room for paths)
        max_alerts = min(4, len(network.alerts))
        for i, alert in enumerate(network.alerts[:max_alerts]):
            alert_color = (self.config.overload_edge_color if alert.alert_type == 'overload' 
                          else self.config.failed_edge_color)
            
            alert_text = f"• {alert.description}"
            ax.text(0.08, alert_start_y - 0.04 - i * 0.04, alert_text, 
                   transform=ax.transAxes, verticalalignment='top', 
                   fontsize=8, color=alert_color)
        
        if len(network.alerts) > max_alerts:
            ax.text(0.08, alert_start_y - 0.04 - max_alerts * 0.04, 
                   f"... and {len(network.alerts) - max_alerts} more alerts", 
                   transform=ax.transAxes, verticalalignment='top', 
                   fontsize=8, style='italic', color='gray')
        
        # Network statistics at the bottom
        stats_y = max(0.15, alert_start_y - max_alerts * 0.05 - 0.05)
        conservation_violations = network.validate_flow_conservation()
        overload_count = sum(1 for edge in network.edges.values() 
                           if edge.flow > edge.capacity and edge.capacity > 0)
        failed_count = sum(1 for edge in network.edges.values() 
                         if edge.is_failed or edge.capacity == 0)
        
        stats_text = f"""NETWORK STATISTICS:
Nodes: {len(network.nodes)} | Edges: {len(network.edges)} | Paths: {len(network.paths)}
Violations: {len(conservation_violations)} | Overloads: {overload_count} | Failures: {failed_count}"""
        
        ax.text(0.05, stats_y, stats_text, transform=ax.transAxes, 
               verticalalignment='top', fontsize=8, 
               bbox=dict(boxstyle='round,pad=0.3', facecolor='lightgray', alpha=0.3))
    
    
    def save_snapshot(self, filename: str):
        """Save current visualization as image"""
        if self.fig:
            self.fig.savefig(filename, dpi=300, bbox_inches='tight', 
                           facecolor='white', edgecolor='none')
            print(f"Visualization saved to {filename}")
    
    def start_interactive_mode(self, network: NetworkState, update_callback=None):
        """
        Start interactive visualization mode with real-time updates.
        
        Args:
            network: Network state to visualize
            update_callback: Optional callback function to update network state
        """
        self.interactive_mode = True
        
        # Set up the figure
        self.setup_figure(network)
        
        # Initial visualization
        self.update_visualization(network)
        
        plt.ion()  # Turn on interactive mode
        plt.show()
        
        print("Interactive mode started. Close the window to stop.")
        print("Network visualization will update automatically.")
        
        try:
            while plt.fignum_exists(self.fig.number):
                if update_callback:
                    update_callback(network)
                
                self.update_visualization(network)
                plt.pause(self.config.update_interval)
        except KeyboardInterrupt:
            print("\nInteractive mode stopped by user.")
        finally:
            self.interactive_mode = False
            plt.ioff()


def create_demo_visualization():
    """Create a demonstration of the visualization system"""
    from network_model import create_simple_network
    from flow_operations import FlowController
    
    # Create test network
    network = create_simple_network()
    controller = FlowController(network)
    
    # Add some flows
    controller.set_path_flow("P1", 5.0)
    controller.set_path_flow("P2", 3.0)
    
    # Create some alerts by overloading
    controller.set_path_flow("P1", 12.0)  # Should cause overload
    network.generate_alerts()
    
    # Create visualizer
    visualizer = NetworkVisualizer()
    
    # Set up and show visualization
    fig, axes = visualizer.setup_figure(network)
    visualizer.update_visualization(network)
    
    # Save snapshot
    visualizer.save_snapshot("network_demo.png")
    
    return visualizer, network


class NetworkGraphVisualizer:
    """Simple NetworkX-based graph visualizer for s-t networks"""
    
    def __init__(self, network: NetworkState):
        """Initialize graph visualizer"""
        self.network = network
        self.nx_graph = None
        self._build_nx_graph()
        
        # Color scheme
        self.colors = {
            'source': '#4CAF50',      # Green
            'sink': '#F44336',        # Red  
            'intermediate': '#2196F3', # Blue
            'path_colors': ['#FF9800', '#9C27B0', '#00BCD4', '#795548', 
                           '#607D8B', '#E91E63', '#FFC107', '#8BC34A']
        }
    
    def _build_nx_graph(self) -> nx.DiGraph:
        """Build NetworkX graph from network model"""
        G = nx.DiGraph()
        
        # Add nodes with type information
        for node_id, node in self.network.nodes.items():
            G.add_node(node_id, node_type=node.type)
        
        # Add edges with capacity and flow information
        for edge_id, edge in self.network.edges.items():
            G.add_edge(edge.from_node, edge.to_node, 
                      edge_id=edge_id,
                      capacity=edge.capacity,
                      flow=edge.flow,
                      is_failed=edge.is_failed)
        
        self.nx_graph = G
        return G
    
    def _determine_layout(self, layout: str = "auto") -> Dict[str, Tuple[float, float]]:
        """Determine node positions based on layout strategy"""
        if layout == "auto":
            # Auto-select s-t optimized layout
            layout = "planar_st"
        
        if layout == "spring":
            return nx.spring_layout(self.nx_graph, k=2, iterations=50, seed=42)
        elif layout == "circular":
            return nx.circular_layout(self.nx_graph)
        elif layout == "grid":
            return self._create_grid_layout()
        elif layout == "hierarchical":
            return self._create_hierarchical_layout()
        elif layout == "planar":
            return self._create_planar_layout()
        elif layout == "planar_st":
            return self._create_planar_st_layout()
        elif layout == "kamada_kawai":
            return nx.kamada_kawai_layout(self.nx_graph)
        else:
            # Default to s-t optimized planar layout
            return self._create_planar_st_layout()
    
    def _is_grid_like(self) -> bool:
        """Check if network has grid-like structure"""
        node_names = list(self.nx_graph.nodes())
        grid_pattern = any('v' in name and any(c.isdigit() for c in name) 
                          for name in node_names if name not in ['s', 't'])
        return grid_pattern
    
    def _create_grid_layout(self) -> Dict[str, Tuple[float, float]]:
        """Create grid-based layout"""
        pos = {}
        grid_nodes = []
        special_nodes = []
        
        for node in self.nx_graph.nodes():
            if node == 's':
                special_nodes.append(('source', node))
            elif node == 't':
                special_nodes.append(('sink', node))
            else:
                grid_nodes.append(node)
        
        # Arrange grid nodes
        if grid_nodes:
            n = len(grid_nodes)
            cols = int(np.ceil(np.sqrt(n)))
            rows = int(np.ceil(n / cols))
            
            for i, node in enumerate(grid_nodes):
                row = i // cols
                col = i % cols
                pos[node] = (col, rows - row - 1)
        
        # Position special nodes
        if special_nodes:
            for i, (node_type, node) in enumerate(special_nodes):
                if node_type == 'source':
                    pos[node] = (-1, rows // 2 if 'rows' in locals() else 0)
                else:  # sink
                    pos[node] = (cols if 'cols' in locals() else 1, rows // 2 if 'rows' in locals() else 0)
        
        return pos
    
    def _create_hierarchical_layout(self) -> Dict[str, Tuple[float, float]]:
        """Create hierarchical layout (left-to-right)"""
        pos = {}
        
        # Group nodes by distance from source
        if 's' in self.nx_graph.nodes():
            try:
                distances = nx.single_source_shortest_path_length(self.nx_graph, 's')
                
                # Group nodes by layer
                layers = {}
                for node, dist in distances.items():
                    if dist not in layers:
                        layers[dist] = []
                    layers[dist].append(node)
                
                # Position nodes
                for layer, nodes in layers.items():
                    x = layer
                    for i, node in enumerate(nodes):
                        y = i - len(nodes) / 2
                        pos[node] = (x, y)
                
                return pos
            except:
                pass
        
        # Fallback to spring layout
        return nx.spring_layout(self.nx_graph, seed=42)
    
    def _create_planar_layout(self) -> Dict[str, Tuple[float, float]]:
        """Create planar layout minimizing edge crossings"""
        try:
            # Try NetworkX planar layout if graph is planar
            if nx.is_planar(self.nx_graph):
                pos = nx.planar_layout(self.nx_graph)
                # Ensure s is on left, t is on right
                return self._adjust_for_st_placement(pos)
            else:
                # Use Kamada-Kawai for non-planar graphs (minimizes edge crossings)
                pos = nx.kamada_kawai_layout(self.nx_graph)
                return self._adjust_for_st_placement(pos)
        except:
            # Fallback to spring layout
            pos = nx.spring_layout(self.nx_graph, k=3, iterations=100, seed=42)
            return self._adjust_for_st_placement(pos)
    
    def _create_planar_st_layout(self) -> Dict[str, Tuple[float, float]]:
        """Create s-t optimized planar layout with minimal crossings"""
        # Start with the best available layout for crossing minimization
        try:
            # First try: Check if graph is planar
            if nx.is_planar(self.nx_graph):
                pos = nx.planar_layout(self.nx_graph)
            else:
                # Use Kamada-Kawai (good for minimizing crossings)
                pos = nx.kamada_kawai_layout(self.nx_graph)
        except:
            # Fallback: Spring layout with more iterations
            pos = nx.spring_layout(self.nx_graph, k=3, iterations=200, seed=42)
        
        # Optimize for s-t structure
        return self._optimize_st_layout(pos)
    
    def _adjust_for_st_placement(self, pos: Dict[str, Tuple[float, float]]) -> Dict[str, Tuple[float, float]]:
        """Adjust layout to place s on left and t on right"""
        if 's' not in pos or 't' not in pos:
            return pos
        
        # Get current positions
        s_pos = pos['s']
        t_pos = pos['t']
        
        # If s is not leftmost or t is not rightmost, rotate/flip the layout
        if s_pos[0] > t_pos[0]:  # s is to the right of t
            # Flip horizontally
            max_x = max(x for x, y in pos.values())
            min_x = min(x for x, y in pos.values())
            for node in pos:
                x, y = pos[node]
                pos[node] = (max_x + min_x - x, y)
        
        return pos
    
    def _optimize_st_layout(self, pos: Dict[str, Tuple[float, float]]) -> Dict[str, Tuple[float, float]]:
        """Optimize layout specifically for s-t flow networks"""
        if 's' not in pos or 't' not in pos:
            return pos
        
        # 1. Ensure s is leftmost, t is rightmost
        pos = self._adjust_for_st_placement(pos)
        
        # 2. Create layered structure based on distance from s
        try:
            # Calculate shortest path distances from s
            distances = nx.single_source_shortest_path_length(self.nx_graph, 's')
            max_distance = max(distances.values()) if distances else 1
            
            # Group nodes by layer (distance from s)
            layers = {}
            for node, dist in distances.items():
                if dist not in layers:
                    layers[dist] = []
                layers[dist].append(node)
            
            # 3. Position nodes in layers, minimizing crossings
            optimized_pos = {}
            
            for layer_dist, nodes in layers.items():
                x = (layer_dist / max_distance) * 4.0 - 2.0  # Spread from -2 to +2
                
                # Sort nodes in this layer to minimize crossings
                if layer_dist == 0:
                    # Source layer
                    optimized_pos['s'] = (x, 0.0)
                elif layer_dist == max_distance:
                    # Sink layer
                    optimized_pos['t'] = (x, 0.0)
                else:
                    # Intermediate layers - arrange to minimize crossings
                    sorted_nodes = self._sort_nodes_to_minimize_crossings(nodes, layer_dist, layers, pos)
                    
                    for i, node in enumerate(sorted_nodes):
                        y_offset = (i - (len(sorted_nodes) - 1) / 2) * 1.2
                        optimized_pos[node] = (x, y_offset)
            
            return optimized_pos
            
        except Exception as e:
            # If optimization fails, return adjusted original positions
            return self._adjust_for_st_placement(pos)
    
    def _sort_nodes_to_minimize_crossings(self, nodes, current_layer, all_layers, original_pos):
        """Sort nodes in a layer to minimize edge crossings"""
        if current_layer == 0 or len(nodes) <= 1:
            return nodes
        
        # Get previous layer nodes and their positions
        prev_layer = current_layer - 1
        if prev_layer not in all_layers:
            return nodes
        
        prev_nodes = all_layers[prev_layer]
        
        # Calculate connection weights for each node
        node_weights = {}
        for node in nodes:
            weight = 0
            connections = 0
            
            # Check connections to previous layer
            for prev_node in prev_nodes:
                if self.nx_graph.has_edge(prev_node, node):
                    # Use original y-position as weight
                    if prev_node in original_pos:
                        weight += original_pos[prev_node][1]
                        connections += 1
            
            # Average weight (y-position of connected nodes in previous layer)
            node_weights[node] = weight / connections if connections > 0 else 0
        
        # Sort by weight to minimize crossings
        return sorted(nodes, key=lambda n: node_weights.get(n, 0))
    
    def display_network(self, 
                       highlight_paths: Optional[List[str]] = None,
                       layout: str = "auto",
                       save_file: Optional[str] = None,
                       show_max_flow: bool = True,
                       figsize: Tuple[float, float] = (12, 8)) -> None:
        """
        Display network visualization.
        
        Args:
            highlight_paths: List of path IDs to highlight
            layout: Layout algorithm ("auto", "spring", "circular", "grid", "hierarchical")
            save_file: File path to save visualization (optional)
            show_max_flow: Whether to show max flow information
            figsize: Figure size (width, height)
        """
        # Create figure
        fig, ax = plt.subplots(figsize=figsize)
        
        # Determine layout
        pos = self._determine_layout(layout)
        
        # Draw nodes
        self._draw_nodes(pos, ax)
        
        # Draw edges
        self._draw_edges(pos, ax, highlight_paths)
        
        # Add title and information
        title = f"s-t Network: {len(self.network.nodes)} nodes, {len(self.network.edges)} edges"
        if highlight_paths:
            title += f" (Highlighting: {', '.join(highlight_paths)})"
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        
        # Add network statistics
        total_throughput = self.network.calculate_total_throughput()
        info_text = f"Total Throughput: {total_throughput:.2f}"
        
        if show_max_flow:
            try:
                from maxflow_calculator import MaxFlowCalculator
                calc = MaxFlowCalculator(self.network)
                max_flow, _ = calc.calculate_max_flow()
                utilization = (total_throughput / max_flow * 100) if max_flow > 0 else 0
                info_text += f"\nMax Flow: {max_flow:.2f} ({utilization:.1f}% utilized)"
            except:
                pass
        
        if len(self.network.paths) > 0:
            info_text += f"\nActive Paths: {len(self.network.paths)}"
        
        ax.text(0.02, 0.98, info_text, transform=ax.transAxes, fontsize=10,
                verticalalignment='top', bbox=dict(boxstyle="round,pad=0.3", 
                                                  facecolor="lightblue", alpha=0.8))
        
        # Add legend
        self._add_legend(ax, highlight_paths)
        
        # Remove axes
        ax.axis('off')
        
        # Adjust layout
        plt.tight_layout()
        
        # Save if requested
        if save_file:
            try:
                plt.savefig(save_file, dpi=300, bbox_inches='tight')
                print(f"💾 Network visualization saved to: {save_file}")
            except Exception as e:
                print(f"❌ Error saving file: {e}")
        
        # Show plot
        plt.show()
    
    def _draw_nodes(self, pos: Dict, ax):
        """Draw network nodes with appropriate colors"""
        for node_type in ['source', 'intermediate', 'sink']:
            nodes = [n for n, d in self.nx_graph.nodes(data=True) 
                    if d.get('node_type') == node_type]
            
            if nodes:
                node_color = self.colors[node_type]
                node_size = 800 if node_type in ['source', 'sink'] else 600
                
                nx.draw_networkx_nodes(self.nx_graph, pos, nodelist=nodes,
                                     node_color=node_color, node_size=node_size,
                                     ax=ax, alpha=0.8)
        
        # Draw node labels
        nx.draw_networkx_labels(self.nx_graph, pos, ax=ax, 
                               font_size=10, font_weight='bold')
    
    def _draw_edges(self, pos: Dict, ax, highlight_paths: Optional[List[str]] = None):
        """Draw network edges with capacity and flow information"""
        highlight_paths = highlight_paths or []
        
        # Get edges that are part of highlighted paths
        highlighted_edges = set()
        if highlight_paths:
            for path_id in highlight_paths:
                if path_id in self.network.paths:
                    path = self.network.paths[path_id]
                    for edge_id in path.edges:
                        if edge_id in self.network.edges:
                            edge = self.network.edges[edge_id]
                            highlighted_edges.add((edge.from_node, edge.to_node))
        
        # Draw normal edges
        normal_edges = []
        failed_edges = []
        for u, v, d in self.nx_graph.edges(data=True):
            if (u, v) not in highlighted_edges:
                if d.get('is_failed', False):
                    failed_edges.append((u, v))
                else:
                    normal_edges.append((u, v))
        
        if normal_edges:
            nx.draw_networkx_edges(self.nx_graph, pos, edgelist=normal_edges,
                                 edge_color='gray', width=1.5, alpha=0.6,
                                 arrows=True, arrowsize=20, ax=ax)
        
        if failed_edges:
            nx.draw_networkx_edges(self.nx_graph, pos, edgelist=failed_edges,
                                 edge_color='red', width=2, alpha=0.8,
                                 style='dashed', arrows=True, arrowsize=20, ax=ax)
        
        # Draw highlighted path edges
        if highlighted_edges:
            path_color_idx = 0
            for path_id in highlight_paths:
                if path_id in self.network.paths:
                    path_edges = []
                    path = self.network.paths[path_id]
                    for edge_id in path.edges:
                        if edge_id in self.network.edges:
                            edge = self.network.edges[edge_id]
                            path_edges.append((edge.from_node, edge.to_node))
                    
                    if path_edges:
                        color = self.colors['path_colors'][path_color_idx % len(self.colors['path_colors'])]
                        nx.draw_networkx_edges(self.nx_graph, pos, edgelist=path_edges,
                                             edge_color=color, width=3, alpha=0.8,
                                             arrows=True, arrowsize=25, ax=ax)
                        path_color_idx += 1
        
        # Add edge labels (capacity/flow)
        edge_labels = {}
        for u, v, d in self.nx_graph.edges(data=True):
            capacity = d.get('capacity', 0)
            flow = d.get('flow', 0)
            edge_labels[(u, v)] = f"{flow:.1f}/{capacity:.1f}"
        
        nx.draw_networkx_edge_labels(self.nx_graph, pos, edge_labels,
                                    font_size=8, ax=ax, bbox=dict(boxstyle="round,pad=0.2", 
                                                                 facecolor="white", alpha=0.8))
    
    def _add_legend(self, ax, highlight_paths: Optional[List[str]] = None):
        """Add legend to the plot"""
        from matplotlib.patches import Patch
        from matplotlib.lines import Line2D
        
        legend_elements = [
            Patch(facecolor=self.colors['source'], label='Source Node'),
            Patch(facecolor=self.colors['intermediate'], label='Intermediate Node'),
            Patch(facecolor=self.colors['sink'], label='Sink Node'),
            Line2D([0], [0], color='gray', label='Normal Edge'),
            Line2D([0], [0], color='red', linestyle='--', label='Failed Edge')
        ]
        
        # Add path colors to legend
        if highlight_paths:
            for i, path_id in enumerate(highlight_paths):
                color = self.colors['path_colors'][i % len(self.colors['path_colors'])]
                legend_elements.append(Line2D([0], [0], color=color, linewidth=3, label=f'Path {path_id}'))
        
        ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(0.98, 0.95))


def display_network(network: NetworkState, 
                   highlight_paths: Optional[List[str]] = None,
                   layout: str = "auto",
                   save_file: Optional[str] = None,
                   show_max_flow: bool = True) -> None:
    """
    Convenience function to display network visualization.
    
    Args:
        network: NetworkState to visualize
        highlight_paths: List of path IDs to highlight
        layout: Layout algorithm
        save_file: File path to save visualization
        show_max_flow: Whether to show max flow information
    """
    visualizer = NetworkGraphVisualizer(network)
    visualizer.display_network(highlight_paths, layout, save_file, show_max_flow)


def demonstrate_graph_visualization():
    """Demonstrate graph visualization capabilities"""
    print("🎨 GRAPH VISUALIZATION DEMONSTRATION")
    print("=" * 70)
    
    from network_generators import NetworkGenerator
    from flow_operations import FlowController
    
    generator = NetworkGenerator(seed=42)
    
    # Test different network types
    networks = {
        "Small Diamond": generator.create_from_edge_list([
            ("s", "a", 5.0), ("s", "b", 4.0), 
            ("a", "t", 6.0), ("b", "t", 3.0)
        ], [["e0", "e2"], ["e1", "e3"]]),
        
        "Grid 3x3": generator.create_grid_network(3, 3),
        "Star Network": generator.create_star_network(5),
        "Random Network": generator.create_random_network(8, 15, 6, path_strategy="complete")
    }
    
    for name, network in networks.items():
        print(f"\n📊 Visualizing: {name}")
        
        # Set some flows for demonstration
        controller = FlowController(network)
        if network.paths:
            path_ids = list(network.paths.keys())[:2]
            for path_id in path_ids:
                alternatives = controller.calculate_max_safe_flow(path_id)
                if not alternatives.get('error'):
                    max_safe = alternatives['max_safe_flow']
                    if max_safe > 0:
                        controller.set_path_flow_with_alternatives(path_id, max_safe * 0.7)
        
        # Display with path highlighting
        highlight_paths = list(network.paths.keys())[:2] if network.paths else None
        print(f"   Highlighting paths: {highlight_paths}")
        
        # For demonstration, create the visualizer
        visualizer = NetworkGraphVisualizer(network)
        print(f"   ✅ Visualizer created for {name}")
        print(f"   Nodes: {len(network.nodes)}, Edges: {len(network.edges)}, Paths: {len(network.paths)}")


if __name__ == "__main__":
    print("Creating network visualization demo...")
    
    # Original demo
    visualizer, network = create_demo_visualization()
    print("\nOriginal visualization created. Check network_demo.png for saved snapshot.")
    
    # Graph visualization demo
    demonstrate_graph_visualization()
    
    print("\n" + "="*70)
    print("🎯 USAGE EXAMPLES:")
    print("="*70)
    print("# Basic usage:")
    print("from network_visualizer import display_network")
    print("display_network(network)")
    print()
    print("# With path highlighting:")
    print("display_network(network, highlight_paths=['P1', 'P2'])")
    print()
    print("# Different layouts:")
    print("display_network(network, layout='planar_st')   # s-t optimized (default)")
    print("display_network(network, layout='planar')      # Planar/minimal crossings")
    print("display_network(network, layout='hierarchical') # Layer-based")
    print("display_network(network, layout='grid')        # Grid-based")
    print()
    print("# Save to file:")
    print("display_network(network, save_file='my_network.png')")
    
    plt.show()