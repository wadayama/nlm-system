#!/usr/bin/env python3
"""Test path counts for various grid sizes"""

from network_generators import NetworkGenerator
from path_enumerator import CompletePathEnumerator

def test_grid_sizes():
    generator = NetworkGenerator(seed=42)
    
    print("🔍 GRID NETWORK PATH ANALYSIS")
    print("=" * 70)
    
    grid_sizes = [(2,3), (3,3), (3,4), (4,4), (4,5)]
    
    for rows, cols in grid_sizes:
        print(f"\n📊 Grid {rows}x{cols}:")
        
        try:
            network = generator.create_grid_network(rows, cols)
            enumerator = CompletePathEnumerator(network)
            result = enumerator.enumerate_all_paths()
            
            print(f"   Nodes: {len(network.nodes)}, Edges: {len(network.edges)}")
            print(f"   Predefined paths: {len(network.paths)}")
            print(f"   All possible paths: {result.total_paths_found}")
            print(f"   Enumeration time: {result.enumeration_time:.4f}s")
            print(f"   Complete: {result.is_complete}")
            
            # Show theoretical vs actual
            theoretical = 1  # Catalan-like calculation would be complex
            ratio = result.total_paths_found / max(1, len(network.paths))
            print(f"   Missing paths ratio: {ratio:.1f}x")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_grid_sizes()
