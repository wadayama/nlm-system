#!/usr/bin/env python3
"""
Network Model for Flow Control System

Core data structures for representing network topology, flow states, and capacity dynamics
in the s-t flow control problem with random capacity variations.
"""

import random
import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass




class NetworkNode:
    """Represents a node in the network graph"""
    
    def __init__(self, node_id: str, node_type: str):
        """
        Initialize network node.
        
        Args:
            node_id: Unique identifier for the node
            node_type: Type of node ('source', 'intermediate', 'sink')
        """
        self.id = node_id
        self.type = node_type
        self.incoming_edges: List[str] = []  # List of incoming edge IDs
        self.outgoing_edges: List[str] = []  # List of outgoing edge IDs
    
    def add_incoming_edge(self, edge_id: str):
        """Add an incoming edge to this node"""
        if edge_id not in self.incoming_edges:
            self.incoming_edges.append(edge_id)
    
    def add_outgoing_edge(self, edge_id: str):
        """Add an outgoing edge from this node"""
        if edge_id not in self.outgoing_edges:
            self.outgoing_edges.append(edge_id)
    
    def validate_flow_conservation(self, edges: Dict) -> Tuple[bool, float]:
        """
        Check flow conservation at this node.
        
        Args:
            edges: Dictionary of NetworkEdge objects
            
        Returns:
            Tuple of (is_conserved, flow_imbalance)
        """
        if self.type != 'intermediate':
            return True, 0.0  # Flow conservation only applies to intermediate nodes
        
        inflow = sum(edges[eid].flow for eid in self.incoming_edges)
        outflow = sum(edges[eid].flow for eid in self.outgoing_edges)
        
        imbalance = abs(inflow - outflow)
        is_conserved = imbalance < 1e-6  # Small tolerance for floating point errors
        
        return is_conserved, imbalance
    
    def __repr__(self) -> str:
        return f"Node({self.id}, {self.type})"


class NetworkEdge:
    """Represents an edge in the network graph with capacity and flow"""
    
    def __init__(self, edge_id: str, from_node: str, to_node: str, initial_capacity: float):
        """
        Initialize network edge.
        
        Args:
            edge_id: Unique identifier for the edge
            from_node: ID of source node
            to_node: ID of destination node
            initial_capacity: Initial capacity value
        """
        self.id = edge_id
        self.from_node = from_node
        self.to_node = to_node
        self.capacity = max(0.0, initial_capacity)  # Current capacity c_e(t)
        self.flow = 0.0  # Current flow f_e(t)
        self.base_capacity = initial_capacity  # Original capacity for recovery
        self.is_failed = False  # True if capacity = 0 due to failure
        
        # Parameters for capacity dynamics (simplified model)
        self.random_walk_std = 0.1  # UNUSED: Standard deviation for random walk (removed)
    
    
    
    def get_utilization(self) -> float:
        """Get current utilization ratio (flow/capacity)"""
        if self.capacity <= 0:
            return float('inf') if self.flow > 0 else 0.0
        return self.flow / self.capacity
    
    def __repr__(self) -> str:
        status = ""
        if self.is_failed:
            status = " [FAILED]"
        
        return f"Edge({self.id}: {self.from_node}→{self.to_node}, " \
               f"c={self.capacity:.2f}, f={self.flow:.2f}{status})"


class NetworkPath:
    """Represents a path from source to sink through the network"""
    
    def __init__(self, path_id: str, edge_sequence: List[str]):
        """
        Initialize network path.
        
        Args:
            path_id: Unique identifier for the path
            edge_sequence: Ordered list of edge IDs comprising this path
        """
        self.id = path_id
        self.edges = edge_sequence.copy()  # List of edge IDs in path order
        self.current_flow = 0.0  # Current flow through this path
        self.bottleneck_capacity = 0.0  # Minimum capacity along path
        self.bottleneck_edge = None  # Edge ID with minimum capacity
    
    def calculate_bottleneck(self, edges: Dict) -> Tuple[float, Optional[str]]:
        """
        Find the bottleneck capacity (minimum capacity along path).
        
        Args:
            edges: Dictionary of NetworkEdge objects
            
        Returns:
            Tuple of (bottleneck_capacity, bottleneck_edge_id)
        """
        if not self.edges:
            return 0.0, None
        
        min_capacity = float('inf')
        bottleneck_edge = None
        
        for edge_id in self.edges:
            if edge_id in edges:
                edge = edges[edge_id]
                if edge.capacity < min_capacity:
                    min_capacity = edge.capacity
                    bottleneck_edge = edge_id
        
        self.bottleneck_capacity = min_capacity if min_capacity != float('inf') else 0.0
        self.bottleneck_edge = bottleneck_edge
        
        return self.bottleneck_capacity, self.bottleneck_edge
    
    def can_accommodate_flow(self, delta_flow: float, edges: Dict) -> Tuple[bool, str]:
        """
        Check if path can accommodate a flow change with strict capacity constraints.
        
        Args:
            delta_flow: Proposed flow change (positive = increase, negative = decrease)
            edges: Dictionary of NetworkEdge objects
            
        Returns:
            Tuple of (can_accommodate, reason_if_not)
        """
        if delta_flow == 0:
            return True, "No flow change"
        
        # For flow decrease, always allow
        if delta_flow < 0:
            new_flow = self.current_flow + delta_flow
            if new_flow < 0:
                return False, f"Flow would become negative: {new_flow:.2f}"
            return True, "Flow decrease allowed"
        
        # For flow increase, enforce strict capacity constraints
        self.calculate_bottleneck(edges)
        
        if self.bottleneck_capacity <= 0:
            return False, f"Path blocked at edge {self.bottleneck_edge}"
        
        # Check if new flow would exceed bottleneck capacity
        new_flow = self.current_flow + delta_flow
        if new_flow > self.bottleneck_capacity:
            excess = new_flow - self.bottleneck_capacity
            return False, f"Flow increase of {delta_flow:.2f} would exceed capacity by {excess:.2f} at edge {self.bottleneck_edge}"
        
        return True, "Flow increase allowed within capacity limits"
    
    def get_path_description(self, nodes: Dict) -> str:
        """
        Get human-readable description of the path.
        
        Args:
            nodes: Dictionary of NetworkNode objects
            
        Returns:
            String description of the path
        """
        if not self.edges:
            return f"Path {self.id}: empty"
        
        # Try to reconstruct node sequence from edges
        node_sequence = []
        if self.edges:
            # Add first node
            first_edge_id = self.edges[0]
            # We'll need to look up the edge to get from_node
            # For now, just show edge sequence
            pass
        
        edge_desc = " → ".join(self.edges)
        return f"Path {self.id}: {edge_desc} (flow={self.current_flow:.2f})"
    
    def __repr__(self) -> str:
        return f"Path({self.id}: {len(self.edges)} edges, flow={self.current_flow:.2f})"


class NetworkState:
    """Complete network state including nodes, edges, paths, and system status"""
    
    def __init__(self):
        """Initialize empty network state"""
        self.nodes: Dict[str, NetworkNode] = {}
        self.edges: Dict[str, NetworkEdge] = {}
        self.paths: Dict[str, NetworkPath] = {}
        self.total_flow: float = 0.0
        
        # Network topology info
        self.source_node: Optional[str] = None
        self.sink_node: Optional[str] = None
        
        # Performance tracking
        self.total_throughput_history: List[float] = []
        self.violation_count = 0
    
    def add_node(self, node: NetworkNode):
        """Add a node to the network"""
        self.nodes[node.id] = node
        
        if node.type == 'source':
            self.source_node = node.id
        elif node.type == 'sink':
            self.sink_node = node.id
    
    def add_edge(self, edge: NetworkEdge):
        """Add an edge to the network and update node connections"""
        self.edges[edge.id] = edge
        
        # Update node connections
        if edge.from_node in self.nodes:
            self.nodes[edge.from_node].add_outgoing_edge(edge.id)
        if edge.to_node in self.nodes:
            self.nodes[edge.to_node].add_incoming_edge(edge.id)
    
    def add_path(self, path: NetworkPath):
        """Add a path to the network"""
        self.paths[path.id] = path
    
    
    def calculate_total_throughput(self) -> float:
        """Calculate total throughput (flow into sink node)"""
        if not self.sink_node or self.sink_node not in self.nodes:
            return 0.0
        
        sink = self.nodes[self.sink_node]
        total = sum(self.edges[eid].flow for eid in sink.incoming_edges 
                   if eid in self.edges)
        
        self.total_flow = total
        return total
    
    def validate_flow_conservation(self) -> List[Tuple[str, float]]:
        """
        Validate flow conservation at all intermediate nodes.
        
        Returns:
            List of (node_id, imbalance) for nodes violating conservation
        """
        violations = []
        
        for node in self.nodes.values():
            is_conserved, imbalance = node.validate_flow_conservation(self.edges)
            if not is_conserved:
                violations.append((node.id, imbalance))
        
        return violations
    
    def get_system_snapshot(self) -> Dict:
        """
        Get complete system state snapshot for logging/analysis.
        
        Returns:
            Dictionary containing all relevant state information
        """
        return {
            'total_flow': self.total_flow,
            'nodes': {nid: {'type': n.type} for nid, n in self.nodes.items()},
            'edges': {
                eid: {
                    'from': e.from_node,
                    'to': e.to_node,
                    'capacity': e.capacity,
                    'flow': e.flow,
                    'failed': e.is_failed,
                    'utilization': e.get_utilization()
                } for eid, e in self.edges.items()
            },
            'paths': {
                pid: {
                    'edges': p.edges,
                    'flow': p.current_flow,
                    'bottleneck_capacity': p.bottleneck_capacity
                } for pid, p in self.paths.items()
            },
        }
    
    
    def get_network_summary(self) -> str:
        """Get human-readable network summary"""
        summary_lines = [
            "Network State:",
            f"  Nodes: {len(self.nodes)} (Source: {self.source_node}, Sink: {self.sink_node})",
            f"  Edges: {len(self.edges)}",
            f"  Paths: {len(self.paths)}",
            f"  Total Flow: {self.total_flow:.2f}",
        ]
        
        
        return "\n".join(summary_lines)
    
    def __repr__(self) -> str:
        return f"NetworkState(nodes={len(self.nodes)}, " \
               f"edges={len(self.edges)}, flow={self.total_flow:.2f})"


# Utility functions for network construction and manipulation

def create_simple_network(source_id: str = "s", sink_id: str = "t") -> NetworkState:
    """
    Create a simple 2-path network for testing.
    
    Args:
        source_id: ID for source node
        sink_id: ID for sink node
        
    Returns:
        NetworkState with simple topology
    """
    network = NetworkState()
    
    # Create nodes
    source = NetworkNode(source_id, "source")
    intermediate1 = NetworkNode("v1", "intermediate")
    intermediate2 = NetworkNode("v2", "intermediate")
    sink = NetworkNode(sink_id, "sink")
    
    network.add_node(source)
    network.add_node(intermediate1)
    network.add_node(intermediate2)
    network.add_node(sink)
    
    # Create edges with different capacities
    edge1 = NetworkEdge("e1", source_id, "v1", 10.0)
    edge2 = NetworkEdge("e2", "v1", sink_id, 8.0)
    edge3 = NetworkEdge("e3", source_id, "v2", 6.0)
    edge4 = NetworkEdge("e4", "v2", sink_id, 12.0)
    
    network.add_edge(edge1)
    network.add_edge(edge2)
    network.add_edge(edge3)
    network.add_edge(edge4)
    
    # Create paths
    path1 = NetworkPath("P1", ["e1", "e2"])
    path2 = NetworkPath("P2", ["e3", "e4"])
    
    network.add_path(path1)
    network.add_path(path2)
    
    return network


if __name__ == "__main__":
    # Basic testing
    print("Creating simple network...")
    network = create_simple_network()
    
    print(network.get_network_summary())
    
    # Display final network state
    print("\nFinal network state:")
    print(network.get_network_summary())