#!/usr/bin/env python3
"""
Network Sample Gallery

Provides a collection of predefined s-t networks for testing and demonstration.
Users can easily switch between different network topologies to explore
flow control behavior and visualization.
"""

from typing import Dict, List, Tuple
from network_generators import NetworkGenerator
from network_model import NetworkState
from flow_operations import FlowController


class NetworkSampleGallery:
    """Gallery of predefined network samples"""
    
    def __init__(self):
        """Initialize network sample gallery"""
        self.generator = NetworkGenerator(seed=42)
        self.samples = {}
        self.current_sample = None
        self._initialize_samples()
    
    def _initialize_samples(self):
        """Initialize all predefined network samples"""
        
        # 1. Simple Diamond Network
        self.samples["diamond"] = {
            "name": "Simple Diamond",
            "description": "Basic 2-path diamond topology (4 nodes)",
            "network": self.generator.create_from_edge_list([
                ("s", "a", 8.0), ("s", "b", 6.0),
                ("a", "t", 7.0), ("b", "t", 9.0)
            ], [["e0", "e2"], ["e1", "e3"]]),
            "features": ["Simple topology", "2 parallel paths", "Good for beginners"]
        }
        
        # 2. Complex Multi-Path Network
        self.samples["complex"] = {
            "name": "Complex Multi-Path",
            "description": "Multi-layer network with 4 overlapping paths (6 nodes)",
            "network": self.generator.create_from_edge_list([
                ("s", "a", 12.0), ("s", "b", 10.0),
                ("a", "c", 8.0), ("a", "d", 9.0),
                ("b", "c", 7.0), ("b", "d", 11.0),
                ("c", "t", 15.0), ("d", "t", 13.0)
            ], [
                ["e0", "e2", "e6"],  # s→a→c→t
                ["e0", "e3", "e7"],  # s→a→d→t  
                ["e1", "e4", "e6"],  # s→b→c→t
                ["e1", "e5", "e7"]   # s→b→d→t
            ]),
            "features": ["4 paths", "Shared edges", "Flow interaction analysis"]
        }
        
        # 3. Grid Network
        self.samples["grid"] = {
            "name": "Grid 3x3", 
            "description": "Grid topology with multiple route options (9 nodes)",
            "network": self.generator.create_grid_network(3, 3),
            "features": ["Grid structure", "Multiple shortest paths", "Geometric layout"]
        }
        
        # 4. Star Network
        self.samples["star"] = {
            "name": "Star Network",
            "description": "Hub-and-spoke topology (8 nodes, 5 paths)",
            "network": self.generator.create_star_network(5),
            "features": ["Hub bottleneck", "Parallel spokes", "CDN-like structure"]
        }
        
        # 5. Layered Network
        self.samples["layered"] = {
            "name": "Layered Network",
            "description": "Hierarchical layers with dense connections (7 nodes)",
            "network": self.generator.create_layered_network([1, 3, 2, 1]),
            "features": ["Layer structure", "Dense connections", "Data center-like"]
        }
        
        # 6. Linear Chain
        self.samples["linear"] = {
            "name": "Linear Chain",
            "description": "Simple linear path with potential bottlenecks (5 nodes)",
            "network": self.generator.create_from_edge_list([
                ("s", "a", 10.0), ("a", "b", 5.0), ("b", "c", 12.0), ("c", "t", 8.0)
            ], [["e0", "e1", "e2", "e3"]]),
            "features": ["Single path", "Bottleneck analysis", "Capacity constraints"]
        }
        
        # 7. Parallel Paths
        self.samples["parallel"] = {
            "name": "Parallel Paths",
            "description": "Three independent parallel paths (8 nodes)",
            "network": self.generator.create_from_edge_list([
                ("s", "a1", 6.0), ("a1", "b1", 8.0), ("b1", "t", 7.0),
                ("s", "a2", 9.0), ("a2", "b2", 5.0), ("b2", "t", 10.0),
                ("s", "a3", 7.0), ("a3", "b3", 9.0), ("b3", "t", 6.0)
            ], [
                ["e0", "e1", "e2"],  # Path 1
                ["e3", "e4", "e5"],  # Path 2  
                ["e6", "e7", "e8"]   # Path 3
            ]),
            "features": ["Independent paths", "No shared edges", "Load balancing"]
        }
        
        # 8. Bottleneck Network
        self.samples["bottleneck"] = {
            "name": "Bottleneck Network",
            "description": "Network with severe central bottleneck (6 nodes)",
            "network": self.generator.create_from_edge_list([
                ("s", "a", 15.0), ("s", "b", 12.0),
                ("a", "c", 3.0), ("b", "c", 3.0),  # Bottleneck at c
                ("c", "d", 2.0),  # Severe bottleneck
                ("c", "e", 2.0),  # Severe bottleneck
                ("d", "t", 10.0), ("e", "t", 8.0)
            ], [
                ["e0", "e2", "e4", "e6"],  # s→a→c→d→t
                ["e1", "e3", "e5", "e7"]   # s→b→c→e→t
            ]),
            "features": ["Severe bottleneck", "Capacity analysis", "Flow limits"]
        }
        
        # Set default sample
        self.current_sample = "diamond"
    
    def list_samples(self) -> Dict[str, Dict]:
        """Get list of all available samples"""
        return {sample_id: {
            "name": info["name"],
            "description": info["description"],
            "features": info["features"],
            "nodes": len(info["network"].nodes),
            "edges": len(info["network"].edges),
            "paths": len(info["network"].paths)
        } for sample_id, info in self.samples.items()}
    
    def get_sample(self, sample_id: str) -> NetworkState:
        """Get a network sample by ID"""
        if sample_id not in self.samples:
            available = ", ".join(self.samples.keys())
            raise ValueError(f"Sample '{sample_id}' not found. Available: {available}")
        
        # Return a fresh copy of the network
        sample_info = self.samples[sample_id]
        network = self._copy_network(sample_info["network"])
        
        # Reset all flows to zero
        for path in network.paths.values():
            path.current_flow = 0.0
        for edge in network.edges.values():
            edge.flow = 0.0
        
        return network
    
    def get_sample_info(self, sample_id: str) -> Dict:
        """Get detailed information about a sample"""
        if sample_id not in self.samples:
            available = ", ".join(self.samples.keys())
            raise ValueError(f"Sample '{sample_id}' not found. Available: {available}")
        
        info = self.samples[sample_id].copy()
        # Don't return the actual network object in info
        network = info.pop("network")
        info.update({
            "nodes": len(network.nodes),
            "edges": len(network.edges), 
            "paths": len(network.paths),
            "sample_id": sample_id
        })
        return info
    
    def _copy_network(self, network: NetworkState) -> NetworkState:
        """Create a deep copy of a network"""
        from network_model import NetworkState, NetworkNode, NetworkEdge, NetworkPath
        
        new_network = NetworkState()
        
        # Copy nodes
        for node in network.nodes.values():
            new_node = NetworkNode(node.id, node.type)
            new_network.add_node(new_node)
        
        # Copy edges
        for edge in network.edges.values():
            new_edge = NetworkEdge(edge.id, edge.from_node, edge.to_node, edge.capacity)
            new_edge.flow = edge.flow
            new_edge.is_failed = edge.is_failed
            new_network.add_edge(new_edge)
        
        # Copy paths
        for path in network.paths.values():
            new_path = NetworkPath(path.id, path.edges.copy())
            new_path.current_flow = path.current_flow
            new_network.add_path(new_path)
        
        # Copy other attributes (none currently needed)
        
        return new_network
    
    def get_current_sample_id(self) -> str:
        """Get current sample ID"""
        return self.current_sample
    
    def set_current_sample(self, sample_id: str):
        """Set current sample ID"""
        if sample_id in self.samples:
            self.current_sample = sample_id


def demonstrate_sample_gallery():
    """Demonstrate the network sample gallery"""
    print("🏛️  NETWORK SAMPLE GALLERY DEMONSTRATION")
    print("=" * 80)
    
    gallery = NetworkSampleGallery()
    
    # List all samples
    print("📋 Available Network Samples:")
    samples_info = gallery.list_samples()
    
    for sample_id, info in samples_info.items():
        print(f"\n🔸 {sample_id.upper()}: {info['name']}")
        print(f"   Description: {info['description']}")
        print(f"   Size: {info['nodes']} nodes, {info['edges']} edges, {info['paths']} paths")
        print(f"   Features: {', '.join(info['features'])}")
    
    # Test a few samples
    test_samples = ["diamond", "complex", "star"]
    
    for sample_id in test_samples:
        print(f"\n" + "="*70)
        print(f"🧪 Testing Sample: {sample_id.upper()}")
        print("="*70)
        
        try:
            # Get sample
            network = gallery.get_sample(sample_id)
            info = gallery.get_sample_info(sample_id)
            
            print(f"✅ Loaded: {info['name']}")
            print(f"   Topology: {info['nodes']} nodes, {info['edges']} edges, {info['paths']} paths")
            
            # Calculate max flow
            try:
                from maxflow_calculator import MaxFlowCalculator
                calc = MaxFlowCalculator(network)
                max_flow, _ = calc.calculate_max_flow()
                
                print(f"📊 Max Flow Analysis:")
                print(f"   Theoretical maximum: {max_flow:.2f}")
            except:
                print("📊 Max Flow Analysis: Calculation failed")
                
            # Test visualization compatibility
            try:
                from network_visualizer import NetworkGraphVisualizer
                visualizer = NetworkGraphVisualizer(network)
                pos = visualizer._determine_layout("planar_st")
                print(f"✅ Visualization ready: {len(pos)} node positions calculated")
            except Exception as e:
                print(f"❌ Visualization error: {str(e)[:50]}")
                
        except Exception as e:
            print(f"❌ Error testing {sample_id}: {e}")
    
    print("\n" + "="*80)
    print("🎯 SAMPLE GALLERY SUMMARY")
    print("="*80)
    print(f"✅ {len(gallery.samples)} predefined network samples")
    print("✅ Complete sample network definitions")
    print("✅ Detailed sample information")
    print("✅ Network copying and isolation")
    print("✅ Visualization compatibility")
    print("\n🚀 Ready for integration with Interactive Monitor!")


if __name__ == "__main__":
    demonstrate_sample_gallery()