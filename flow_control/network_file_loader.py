#!/usr/bin/env python3
"""
Network File Loader for Flow Control System

Load network definitions from YAML files for custom network topologies.
"""

import yaml
from pathlib import Path
from typing import Dict, Any
from network_model import NetworkState, NetworkNode, NetworkEdge, NetworkPath
from path_enumerator import CompletePathEnumerator


class NetworkFileLoader:
    """Load network definitions from YAML files"""
    
    def __init__(self):
        """Initialize the file loader"""
        pass
        
    def load_yaml(self, file_path: str) -> NetworkState:
        """
        Load network from YAML file.
        
        Args:
            file_path: Path to the YAML file
            
        Returns:
            NetworkState object built from YAML definition
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            yaml.YAMLError: If the YAML is invalid
            ValueError: If required fields are missing
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
            
        return self._build_network(data)
        
    def _build_network(self, data: Dict[str, Any]) -> NetworkState:
        """
        Build NetworkState from parsed YAML data.
        
        Args:
            data: Parsed YAML data dictionary
            
        Returns:
            NetworkState object
            
        Raises:
            ValueError: If required fields are missing or invalid
        """
        network = NetworkState()
        
        # Validate required fields
        if 'nodes' not in data:
            raise ValueError("YAML must contain 'nodes' section")
        if 'edges' not in data:
            raise ValueError("YAML must contain 'edges' section")
        
        # Create nodes
        nodes = data['nodes']
        source_found = False
        sink_found = False
        
        for node_id, node_type in nodes.items():
            if node_type not in ['source', 'intermediate', 'sink']:
                raise ValueError(f"Invalid node type '{node_type}' for node '{node_id}'")
                
            network.add_node(NetworkNode(node_id, node_type))
            
            if node_type == 'source':
                if source_found:
                    raise ValueError("Multiple source nodes found")
                source_found = True
                
            if node_type == 'sink':
                if sink_found:
                    raise ValueError("Multiple sink nodes found")
                sink_found = True
        
        if not source_found:
            raise ValueError("No source node found")
        if not sink_found:
            raise ValueError("No sink node found")
            
        # Create edges
        edges = data['edges']
        for edge_id, edge_info in edges.items():
            # Validate edge info
            if 'from' not in edge_info:
                raise ValueError(f"Edge '{edge_id}' missing 'from' field")
            if 'to' not in edge_info:
                raise ValueError(f"Edge '{edge_id}' missing 'to' field")
            if 'capacity' not in edge_info:
                raise ValueError(f"Edge '{edge_id}' missing 'capacity' field")
                
            from_node = edge_info['from']
            to_node = edge_info['to']
            capacity = float(edge_info['capacity'])
            
            # Validate nodes exist
            if from_node not in nodes:
                raise ValueError(f"Edge '{edge_id}' references unknown node '{from_node}'")
            if to_node not in nodes:
                raise ValueError(f"Edge '{edge_id}' references unknown node '{to_node}'")
                
            # Create edge
            edge = NetworkEdge(edge_id, from_node, to_node, capacity)
            network.add_edge(edge)
            
        # Enumerate all s-t paths
        path_enumerator = CompletePathEnumerator(network)
        result = path_enumerator.enumerate_all_paths()
        
        # Add paths to network
        for i, path_edges in enumerate(result.paths, 1):
            path_id = f"P{i}"
            network_path = NetworkPath(path_id, path_edges)
            network.add_path(network_path)
        
        # Validate connectivity
        if len(network.paths) == 0:
            raise ValueError("No paths found from source to sink - network is disconnected")
            
        return network
        
    def get_network_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get basic information about a network file without fully loading it.
        
        Args:
            file_path: Path to the YAML file
            
        Returns:
            Dictionary with network metadata
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
            
        info = {
            'name': data.get('name', 'Unnamed Network'),
            'description': data.get('description', ''),
            'num_nodes': len(data.get('nodes', {})),
            'num_edges': len(data.get('edges', {})),
            'file_path': str(path.absolute())
        }
        
        return info


def test_loader():
    """Test the network file loader with a simple example"""
    
    # Create a test YAML file
    test_yaml = """
name: Test Network
description: Simple test network

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
"""
    
    # Save to temporary file
    test_file = Path("test_network.yaml")
    with open(test_file, 'w') as f:
        f.write(test_yaml)
    
    try:
        # Load the network
        loader = NetworkFileLoader()
        network = loader.load_yaml(str(test_file))
        
        print("✅ Network loaded successfully!")
        print(f"   Nodes: {len(network.nodes)}")
        print(f"   Edges: {len(network.edges)}")
        print(f"   Paths: {len(network.paths)}")
        
        # Get network info
        info = loader.get_network_info(str(test_file))
        print(f"\n📊 Network Info:")
        print(f"   Name: {info['name']}")
        print(f"   Description: {info['description']}")
        
    finally:
        # Clean up test file
        if test_file.exists():
            test_file.unlink()


if __name__ == "__main__":
    test_loader()