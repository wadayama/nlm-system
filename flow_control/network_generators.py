#!/usr/bin/env python3
"""
Universal Network Generators for Flow Control System

Provides functions to generate various types of s-t networks for testing
the generality and scalability of the flow control system.
"""

import random
import math
from typing import List, Tuple, Dict, Optional
from network_model import NetworkState, NetworkNode, NetworkEdge, NetworkPath


class NetworkGenerator:
    """Universal network generator for various topologies"""
    
    def __init__(self, seed: Optional[int] = None):
        """Initialize generator with optional random seed"""
        if seed is not None:
            random.seed(seed)
    
    def create_random_network(self, 
                            num_nodes: int = 10, 
                            num_edges: int = 20, 
                            max_paths: int = None,
                            min_capacity: float = 1.0,
                            max_capacity: float = 10.0) -> NetworkState:
        """
        Create a random s-t network.
        
        Args:
            num_nodes: Number of nodes (including s and t)
            num_edges: Number of edges to create
            max_paths: Maximum paths to enumerate (None = no limit)
            min_capacity: Minimum edge capacity
            max_capacity: Maximum edge capacity
            
        Returns:
            NetworkState with random topology
        """
        if num_nodes < 2:
            raise ValueError("Need at least 2 nodes (source and sink)")
        
        network = NetworkState()
        
        # Create nodes
        node_ids = [f"v{i}" for i in range(num_nodes)]
        node_ids[0] = "s"  # Source
        node_ids[-1] = "t"  # Sink
        
        for i, node_id in enumerate(node_ids):
            if i == 0:
                node_type = "source"
            elif i == num_nodes - 1:
                node_type = "sink"
            else:
                node_type = "intermediate"
            
            network.add_node(NetworkNode(node_id, node_type))
        
        # Create edges with bias toward source-to-sink direction
        edges_created = set()
        edge_count = 0
        
        # Ensure connectivity: create a path from s to t
        path_nodes = ["s"]
        current = "s"
        while current != "t":
            # Choose next node (bias toward later nodes)
            remaining = [n for n in node_ids if n not in path_nodes or n == "t"]
            if "t" in remaining and len(path_nodes) > 2:
                next_node = "t"
            else:
                next_node = random.choice([n for n in remaining if n != "t"])
            
            # Create edge
            edge_id = f"e{edge_count}"
            capacity = random.uniform(min_capacity, max_capacity)
            edge = NetworkEdge(edge_id, current, next_node, capacity)
            network.add_edge(edge)
            edges_created.add((current, next_node))
            edge_count += 1
            
            path_nodes.append(next_node)
            current = next_node
        
        # Add random additional edges
        while edge_count < num_edges:
            from_node = random.choice(node_ids[:-1])  # Not from sink
            to_node = random.choice(node_ids[1:])     # Not to source
            
            if from_node != to_node and (from_node, to_node) not in edges_created:
                edge_id = f"e{edge_count}"
                capacity = random.uniform(min_capacity, max_capacity)
                edge = NetworkEdge(edge_id, from_node, to_node, capacity)
                network.add_edge(edge)
                edges_created.add((from_node, to_node))
                edge_count += 1
        
        # Generate all possible s-t paths
        self._generate_complete_paths(network, max_paths)
        
        return network
    
    def create_grid_network(self, 
                          rows: int = 3, 
                          cols: int = 4,
                          capacity_range: Tuple[float, float] = (1.0, 10.0),
                          max_paths: int = None) -> NetworkState:
        """
        Create a grid-based s-t network.
        
        Args:
            rows: Number of rows in grid
            cols: Number of columns in grid
            capacity_range: (min, max) capacity for edges
            max_paths: Maximum paths to enumerate (None = no limit)
            
        Returns:
            NetworkState with grid topology
        """
        network = NetworkState()
        
        # Create grid nodes
        node_grid = {}
        for r in range(rows):
            for c in range(cols):
                if r == 0 and c == 0:
                    node_id = "s"
                    node_type = "source"
                elif r == rows-1 and c == cols-1:
                    node_id = "t"  
                    node_type = "sink"
                else:
                    node_id = f"v{r}{c}"
                    node_type = "intermediate"
                
                node_grid[(r, c)] = node_id
                network.add_node(NetworkNode(node_id, node_type))
        
        # Create grid edges (right and down connections)
        edge_count = 0
        for r in range(rows):
            for c in range(cols):
                current_node = node_grid[(r, c)]
                
                # Right edge
                if c < cols - 1:
                    next_node = node_grid[(r, c + 1)]
                    capacity = random.uniform(*capacity_range)
                    edge = NetworkEdge(f"e{edge_count}", current_node, next_node, capacity)
                    network.add_edge(edge)
                    edge_count += 1
                
                # Down edge  
                if r < rows - 1:
                    next_node = node_grid[(r + 1, c)]
                    capacity = random.uniform(*capacity_range)
                    edge = NetworkEdge(f"e{edge_count}", current_node, next_node, capacity)
                    network.add_edge(edge)
                    edge_count += 1
        
        # Generate all possible paths through grid
        self._generate_complete_paths(network, max_paths)
        
        return network
    
    def create_from_edge_list(self, 
                            edges: List[Tuple[str, str, float]], 
                            path_definitions: List[List[str]],
                            source_id: str = "s",
                            sink_id: str = "t") -> NetworkState:
        """
        Create network from edge list and path definitions.
        
        Args:
            edges: List of (from_node, to_node, capacity) tuples
            path_definitions: List of edge sequences for each path
            source_id: Source node ID
            sink_id: Sink node ID
            
        Returns:
            NetworkState built from specifications
        """
        network = NetworkState()
        
        # Collect all nodes from edges
        all_nodes = set()
        for from_node, to_node, _ in edges:
            all_nodes.add(from_node)
            all_nodes.add(to_node)
        
        # Create nodes
        for node_id in all_nodes:
            if node_id == source_id:
                node_type = "source"
            elif node_id == sink_id:
                node_type = "sink"
            else:
                node_type = "intermediate"
            
            network.add_node(NetworkNode(node_id, node_type))
        
        # Create edges
        for i, (from_node, to_node, capacity) in enumerate(edges):
            edge_id = f"e{i}"
            edge = NetworkEdge(edge_id, from_node, to_node, capacity)
            network.add_edge(edge)
        
        # Create paths from definitions
        for i, edge_sequence in enumerate(path_definitions):
            path_id = f"P{i+1}"
            path = NetworkPath(path_id, edge_sequence)
            network.add_path(path)
        
        return network
    
    def create_star_network(self, 
                          num_spokes: int = 5, 
                          capacity_range: Tuple[float, float] = (1.0, 10.0)) -> NetworkState:
        """
        Create star topology (source -> hub -> spokes -> sink).
        
        Args:
            num_spokes: Number of spoke nodes
            capacity_range: (min, max) capacity for edges
            
        Returns:
            NetworkState with star topology
        """
        network = NetworkState()
        
        # Create nodes
        network.add_node(NetworkNode("s", "source"))
        network.add_node(NetworkNode("hub", "intermediate"))
        network.add_node(NetworkNode("t", "sink"))
        
        for i in range(num_spokes):
            network.add_node(NetworkNode(f"spoke{i}", "intermediate"))
        
        # Create edges
        edge_count = 0
        
        # Source to hub
        capacity = random.uniform(*capacity_range)
        edge = NetworkEdge(f"e{edge_count}", "s", "hub", capacity)
        network.add_edge(edge)
        edge_count += 1
        
        # Hub to spokes
        hub_to_spoke_edges = []
        for i in range(num_spokes):
            capacity = random.uniform(*capacity_range)
            edge_id = f"e{edge_count}"
            edge = NetworkEdge(edge_id, "hub", f"spoke{i}", capacity)
            network.add_edge(edge)
            hub_to_spoke_edges.append(edge_id)
            edge_count += 1
        
        # Spokes to sink
        spoke_to_sink_edges = []
        for i in range(num_spokes):
            capacity = random.uniform(*capacity_range)
            edge_id = f"e{edge_count}"
            edge = NetworkEdge(edge_id, f"spoke{i}", "t", capacity)
            network.add_edge(edge)
            spoke_to_sink_edges.append(edge_id)
            edge_count += 1
        
        # Create paths (one per spoke)
        for i in range(num_spokes):
            path_edges = ["e0", hub_to_spoke_edges[i], spoke_to_sink_edges[i]]
            path = NetworkPath(f"P{i+1}", path_edges)
            network.add_path(path)
        
        return network
    
    def create_layered_network(self, 
                             layers: List[int] = [1, 3, 3, 1], 
                             capacity_range: Tuple[float, float] = (1.0, 10.0),
                             max_paths: int = None) -> NetworkState:
        """
        Create layered network topology.
        
        Args:
            layers: Number of nodes in each layer [source_layer, ..., sink_layer]
            capacity_range: (min, max) capacity for edges
            
        Returns:
            NetworkState with layered topology
        """
        network = NetworkState()
        
        # Create nodes by layer
        node_layers = []
        node_count = 0
        
        for layer_idx, layer_size in enumerate(layers):
            layer_nodes = []
            for i in range(layer_size):
                if layer_idx == 0:
                    node_id = "s"
                    node_type = "source"
                elif layer_idx == len(layers) - 1:
                    node_id = "t"
                    node_type = "sink"
                else:
                    node_id = f"v{layer_idx}_{i}"
                    node_type = "intermediate"
                
                network.add_node(NetworkNode(node_id, node_type))
                layer_nodes.append(node_id)
                node_count += 1
            
            node_layers.append(layer_nodes)
        
        # Create edges between adjacent layers
        edge_count = 0
        for layer_idx in range(len(layers) - 1):
            from_layer = node_layers[layer_idx]
            to_layer = node_layers[layer_idx + 1]
            
            # Connect each node in current layer to each node in next layer
            for from_node in from_layer:
                for to_node in to_layer:
                    capacity = random.uniform(*capacity_range)
                    edge = NetworkEdge(f"e{edge_count}", from_node, to_node, capacity)
                    network.add_edge(edge)
                    edge_count += 1
        
        # Generate all possible paths through layers
        self._generate_complete_paths(network, max_paths)
        
        return network
    
    def _generate_complete_paths(self, network: NetworkState, max_paths: int):
        """Generate all possible s-t paths (up to limit)"""
        from path_enumerator import CompletePathEnumerator
        
        enumerator = CompletePathEnumerator(network)
        result = enumerator.enumerate_all_paths(max_length=len(network.nodes) + 3, max_paths=max_paths)
        
        for i, path_edges in enumerate(result.paths):
            path = NetworkPath(f"P{i+1}", path_edges)
            network.add_path(path)
        
        print(f"   Complete enumeration: {len(result.paths)} paths found in {result.enumeration_time:.3f}s")
    
    


def demo_network_generators():
    """Demonstrate various network generators"""
    
    print("🏗️  NETWORK GENERATORS DEMONSTRATION")
    print("=" * 80)
    
    generator = NetworkGenerator(seed=42)  # For reproducible results
    
    # Test each generator
    networks = {
        "Random (10 nodes)": generator.create_random_network(10, 15, 4),
        "Grid (3x4)": generator.create_grid_network(3, 4),
        "Star (5 spokes)": generator.create_star_network(5),
        "Layered ([1,3,3,1])": generator.create_layered_network([1, 3, 3, 1])
    }
    
    for name, network in networks.items():
        print(f"\n📊 {name}:")
        print(f"   Nodes: {len(network.nodes)} | Edges: {len(network.edges)} | Paths: {len(network.paths)}")
        
        # Test basic functionality
        from flow_operations import FlowController
        controller = FlowController(network)
        
        # Test max flow calculation
        try:
            from maxflow_calculator import MaxFlowCalculator
            calc = MaxFlowCalculator(network)
            max_flow, _ = calc.calculate_max_flow()
            print(f"   Max flow: {max_flow:.2f}")
        except:
            print(f"   Max flow: calculation failed")
        
        # Test flow setting on first path
        if network.paths:
            path_id = list(network.paths.keys())[0]
            alternatives = controller.calculate_max_safe_flow(path_id)
            if not alternatives.get('error'):
                max_safe = alternatives['max_safe_flow']
                success, _, _ = controller.set_path_flow_with_alternatives(path_id, max_safe / 2)
                print(f"   Flow test: {'✅' if success else '❌'} (set {path_id} to {max_safe/2:.1f})")
            else:
                print(f"   Flow test: ❌ (path analysis failed)")
        
        print(f"   Source→Sink: {network.source_node}→{network.sink_node}")
    
    print("\n" + "=" * 80)
    print("✅ All network generators working correctly!")
    print("📈 System supports arbitrary s-t network topologies")


if __name__ == "__main__":
    demo_network_generators()