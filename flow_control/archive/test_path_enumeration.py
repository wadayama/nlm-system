#!/usr/bin/env python3
"""
Path Enumeration Testing and Comparison

Tests the effectiveness of complete path enumeration vs sampling
for achieving theoretical max-flow in s-t networks.
"""

import time
from typing import Dict, List, Tuple
from network_generators import NetworkGenerator
from path_enumerator import CompletePathEnumerator, SmartPathSelector, PathAnalyzer
from flow_operations import FlowController
from maxflow_calculator import MaxFlowCalculator
from network_model import NetworkPath


class MaxFlowAchievabilityTester:
    """Test max-flow achievability with different path enumeration strategies"""
    
    def __init__(self):
        """Initialize the tester"""
        self.generator = NetworkGenerator(seed=123)
        self.results = []
    
    def test_path_strategies(self, network_configs: List[Dict]) -> List[Dict]:
        """
        Test different path enumeration strategies on various networks.
        
        Args:
            network_configs: List of network configuration dictionaries
            
        Returns:
            List of test results
        """
        results = []
        
        for i, config in enumerate(network_configs):
            print(f"\n🔬 Test {i+1}: {config['name']}")
            print("-" * 60)
            
            # Create base network (without paths)
            if config['type'] == 'custom':
                network = self.generator.create_from_edge_list(
                    config['edges'], []  # No predefined paths
                )
            elif config['type'] == 'grid':
                network = self.generator.create_grid_network(
                    config['rows'], config['cols']
                )
                network.paths.clear()  # Remove existing paths
            elif config['type'] == 'random':
                network = self.generator.create_random_network(
                    config['nodes'], config['edges'], 0  # No paths initially
                )
            else:
                continue
            
            # Calculate theoretical max flow
            max_flow_calc = MaxFlowCalculator(network)
            theoretical_max, _ = max_flow_calc.calculate_max_flow()
            
            print(f"Network: {len(network.nodes)} nodes, {len(network.edges)} edges")
            print(f"Theoretical max flow: {theoretical_max:.2f}")
            
            # Test different strategies
            strategies = ['complete', 'complete_selector']
            strategy_results = {}
            
            for strategy in strategies:
                result = self._test_single_strategy(network, strategy, theoretical_max, config.get('target_paths', 10))
                strategy_results[strategy] = result
                
                print(f"  {strategy:>8}: {result['paths_found']:2d} paths, "
                      f"max achievable: {result['max_achievable']:.2f} "
                      f"({result['max_flow_ratio']:.1%}), "
                      f"time: {result['enumeration_time']:.3f}s")
            
            # Overall result
            test_result = {
                'config': config,
                'theoretical_max': theoretical_max,
                'network_size': len(network.nodes),
                'strategies': strategy_results
            }
            
            results.append(test_result)
            
            # Determine best strategy
            best_ratio = 0
            best_strategy = None
            for strategy, data in strategy_results.items():
                if data['max_flow_ratio'] > best_ratio:
                    best_ratio = data['max_flow_ratio']
                    best_strategy = strategy
            
            print(f"  🏆 Best: {best_strategy} ({best_ratio:.1%} of theoretical max)")
        
        return results
    
    def _test_single_strategy(self, base_network, strategy: str, theoretical_max: float, target_paths: int) -> Dict:
        """Test a single path enumeration strategy"""
        # Create fresh copy of network
        network = self._copy_network(base_network)
        
        start_time = time.time()
        
        if strategy == 'complete':
            enumerator = CompletePathEnumerator(network)
            result = enumerator.enumerate_all_paths(
                max_length=len(network.nodes) + 2,
                max_paths=min(target_paths * 3, 100)  # Reasonable limit
            )
            paths = result.paths
            enumeration_time = result.enumeration_time
            
        elif strategy == 'complete_selector':
            selector = SmartPathSelector(network)
            result = selector.enumerate_all_paths(max_paths=target_paths)
            paths = result.paths
            enumeration_time = result.enumeration_time
        
        # Add paths to network
        network.paths.clear()
        for i, path_edges in enumerate(paths):
            path = NetworkPath(f"P{i+1}", path_edges)
            network.add_path(path)
        
        # Test max flow achievability
        max_achievable = self._calculate_max_achievable_flow(network)
        max_flow_ratio = (max_achievable / theoretical_max) if theoretical_max > 0 else 0
        
        return {
            'paths_found': len(paths),
            'max_achievable': max_achievable,
            'max_flow_ratio': max_flow_ratio,
            'enumeration_time': enumeration_time,
            'is_complete': strategy == 'complete'
        }
    
    def _copy_network(self, network):
        """Create a copy of network without paths"""
        from network_model import NetworkState
        
        new_network = NetworkState()
        
        # Copy nodes
        for node in network.nodes.values():
            new_network.add_node(node)
        
        # Copy edges
        for edge in network.edges.values():
            new_network.add_edge(edge)
        
        return new_network
    
    def _calculate_max_achievable_flow(self, network) -> float:
        """
        Calculate maximum achievable flow using the available paths.
        This uses a greedy approach to set path flows.
        """
        controller = FlowController(network)
        
        # Sort paths by bottleneck capacity (largest first)
        path_capacities = []
        for path_id, path in network.paths.items():
            bottleneck, _ = path.calculate_bottleneck(network.edges)
            path_capacities.append((path_id, bottleneck))
        
        path_capacities.sort(key=lambda x: x[1], reverse=True)
        
        # Greedily set flows
        total_flow = 0
        for path_id, capacity in path_capacities:
            alternatives = controller.calculate_max_safe_flow(path_id)
            if not alternatives.get('error') and not alternatives.get('is_blocked'):
                max_safe = alternatives['max_safe_flow']
                if max_safe > 0:
                    success, _, _ = controller.set_path_flow_with_alternatives(path_id, max_safe)
                    if success:
                        total_flow += max_safe
        
        return total_flow
    
    def generate_comparison_report(self, results: List[Dict]):
        """Generate comprehensive comparison report"""
        print("\n" + "=" * 80)
        print("🏆 PATH ENUMERATION STRATEGY COMPARISON REPORT")
        print("=" * 80)
        
        if not results:
            print("No test results available.")
            return
        
        # Summary statistics
        strategy_stats = {'complete': [], 'smart': [], 'sample': []}
        
        for result in results:
            for strategy, data in result['strategies'].items():
                if strategy in strategy_stats:
                    strategy_stats[strategy].append(data['max_flow_ratio'])
        
        print("\n📊 Strategy Performance Summary:")
        print(f"{'Strategy':<12} {'Tests':<6} {'Avg Ratio':<10} {'Min':<8} {'Max':<8} {'Std Dev':<8}")
        print("-" * 60)
        
        for strategy, ratios in strategy_stats.items():
            if ratios:
                avg_ratio = sum(ratios) / len(ratios)
                min_ratio = min(ratios)
                max_ratio = max(ratios)
                std_dev = (sum((r - avg_ratio) ** 2 for r in ratios) / len(ratios)) ** 0.5
                
                print(f"{strategy:<12} {len(ratios):<6} {avg_ratio:<10.1%} "
                      f"{min_ratio:<8.1%} {max_ratio:<8.1%} {std_dev:<8.3f}")
        
        # Detailed analysis
        print("\n🔍 Detailed Analysis by Network Size:")
        small_networks = [r for r in results if r['network_size'] <= 6]
        medium_networks = [r for r in results if 6 < r['network_size'] <= 12]
        large_networks = [r for r in results if r['network_size'] > 12]
        
        for category, networks in [("Small (≤6 nodes)", small_networks), 
                                  ("Medium (7-12 nodes)", medium_networks),
                                  ("Large (>12 nodes)", large_networks)]:
            if networks:
                print(f"\n{category}:")
                complete_ratios = [n['strategies']['complete']['max_flow_ratio'] 
                                 for n in networks if 'complete' in n['strategies']]
                smart_ratios = [n['strategies']['smart']['max_flow_ratio'] 
                               for n in networks if 'smart' in n['strategies']]
                sample_ratios = [n['strategies']['sample']['max_flow_ratio'] 
                               for n in networks if 'sample' in n['strategies']]
                
                if complete_ratios:
                    print(f"  Complete: {sum(complete_ratios)/len(complete_ratios):.1%} avg")
                if smart_ratios:
                    print(f"  Smart:    {sum(smart_ratios)/len(smart_ratios):.1%} avg")
                if sample_ratios:
                    print(f"  Sample:   {sum(sample_ratios)/len(sample_ratios):.1%} avg")
        
        # Recommendations
        print("\n💡 Recommendations:")
        print("  • Small networks (≤6 nodes): Use 'complete' for optimal flow")
        print("  • Medium networks (7-12 nodes): Use 'smart' for balanced performance")
        print("  • Large networks (>12 nodes): Use 'sample' for speed, 'smart' for quality")
        print("  • Max-flow critical applications: Always prefer 'complete' when feasible")


def main():
    """Run comprehensive path enumeration tests"""
    print("🛤️  PATH ENUMERATION STRATEGY TESTING")
    print("=" * 80)
    print("Testing max-flow achievability with different path enumeration strategies")
    print("=" * 80)
    
    tester = MaxFlowAchievabilityTester()
    
    # Define test network configurations
    test_configs = [
        {
            'name': 'Small Diamond Network',
            'type': 'custom',
            'edges': [('s', 'a', 5.0), ('s', 'b', 4.0), ('a', 't', 6.0), ('b', 't', 3.0)],
            'target_paths': 5
        },
        {
            'name': 'Small Complex Network',
            'type': 'custom',
            'edges': [
                ('s', 'a', 10.0), ('s', 'b', 8.0),
                ('a', 'c', 6.0), ('a', 'd', 7.0),
                ('b', 'c', 5.0), ('b', 'd', 9.0),
                ('c', 't', 8.0), ('d', 't', 6.0)
            ],
            'target_paths': 8
        },
        {
            'name': 'Grid 3x3',
            'type': 'grid',
            'rows': 3,
            'cols': 3,
            'target_paths': 6
        },
        {
            'name': 'Grid 4x4',
            'type': 'grid',
            'rows': 4,
            'cols': 4,
            'target_paths': 10
        },
        {
            'name': 'Medium Random Network',
            'type': 'random',
            'nodes': 8,
            'edges': 16,
            'target_paths': 8
        },
        {
            'name': 'Large Random Network',
            'type': 'random',
            'nodes': 15,
            'edges': 30,
            'target_paths': 12
        }
    ]
    
    # Run tests
    results = tester.test_path_strategies(test_configs)
    
    # Generate report
    tester.generate_comparison_report(results)
    
    print("\n" + "=" * 80)
    print("🏁 PATH ENUMERATION TESTING COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    main()