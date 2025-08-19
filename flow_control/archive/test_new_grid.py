#!/usr/bin/env python3
"""Test updated grid generation with complete enumeration"""

from network_generators import NetworkGenerator

def test_new_grid():
    print("🧪 Testing Updated Grid Generation")
    print("=" * 60)
    
    generator = NetworkGenerator(seed=42)
    
    print("🔍 Creating 3x3 grid with complete enumeration...")
    network = generator.create_grid_network(3, 3)
    
    print(f"\n📊 Results:")
    print(f"   Nodes: {len(network.nodes)}")
    print(f"   Edges: {len(network.edges)}")
    print(f"   Paths: {len(network.paths)}")
    
    print(f"\n🛤️  All Paths:")
    for path_id, path in network.paths.items():
        print(f"   {path_id}: {' → '.join(path.edges)}")

if __name__ == "__main__":
    test_new_grid()
