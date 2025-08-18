#!/usr/bin/env python3
"""Test script for Simple Packet Scheduler"""

import argparse
from simple_scheduler import SimplePacketScheduler, run_scheduler_simulation
from packet import Packet


def test_basic_functionality():
    """Test basic scheduler functionality."""
    print("Testing Basic Scheduler Functionality")
    print("=" * 40)
    
    scheduler = SimplePacketScheduler()
    
    # Test 1: Empty queues
    print("\n1. Testing empty queues:")
    selected = scheduler.select_packet()
    print(f"   Selected from empty queues: {selected}")
    assert selected is None, "Should return None for empty queues"
    
    # Test 2: Single packet selection
    print("\n2. Testing single packet selection:")
    p1 = Packet(value=5, deadline=3)
    scheduler.add_packet_to_queue_a(p1)
    selected = scheduler.select_packet()
    print(f"   Added {p1} to Queue A")
    print(f"   Selected: {selected}")
    assert selected == p1, "Should select the only available packet"
    
    # Test 3: Highest value selection
    print("\n3. Testing highest value selection:")
    scheduler = SimplePacketScheduler()  # Reset
    p1 = Packet(value=3, deadline=5)
    p2 = Packet(value=8, deadline=2)
    p3 = Packet(value=5, deadline=4)
    
    scheduler.add_packet_to_queue_a(p1)
    scheduler.add_packet_to_queue_a(p2)
    scheduler.add_packet_to_queue_b(p3)
    
    print(f"   Queue A: {p1}, {p2}")
    print(f"   Queue B: {p3}")
    
    selected = scheduler.select_packet()
    print(f"   Selected: {selected}")
    assert selected == p2, "Should select highest value packet (v=8)"
    
    # Test 4: Packet sending and statistics
    print("\n4. Testing packet sending:")
    source = scheduler.send_packet(selected)
    stats = scheduler.get_statistics()
    print(f"   Sent {selected} from {source}")
    print(f"   Statistics: {stats}")
    assert stats['packets_sent'] == 1, "Should count sent packet"
    assert stats['total_value_sent'] == 8, "Should track total value"
    
    # Test 5: Deadline updates
    print("\n5. Testing deadline updates:")
    expired_a, expired_b = scheduler.update_deadlines()
    print(f"   Expired: {len(expired_a)} from A, {len(expired_b)} from B")
    
    print("\n✅ All basic tests passed!")


def test_deterministic_scenario():
    """Test scheduler with predetermined packets."""
    print("\nTesting Deterministic Scenario")
    print("=" * 40)
    
    scheduler = SimplePacketScheduler()
    
    # Create specific test scenario
    test_packets = [
        (Packet(value=10, deadline=1), "A"),  # High value, urgent
        (Packet(value=3, deadline=5), "A"),   # Low value, safe
        (Packet(value=7, deadline=2), "B"),   # Medium value, urgent
        (Packet(value=9, deadline=4), "B"),   # High value, medium deadline
    ]
    
    print("\nAdding test packets:")
    for packet, queue in test_packets:
        if queue == "A":
            scheduler.add_packet_to_queue_a(packet)
        else:
            scheduler.add_packet_to_queue_b(packet)
        print(f"  {queue}: {packet}")
    
    print("\nQueue status:")
    for line in scheduler.get_queue_display():
        print(line)
    
    # Test selection order (should be by value: 10, 9, 7, 3)
    print("\nSelection sequence:")
    expected_values = [10, 9, 7, 3]
    
    for i, expected_value in enumerate(expected_values):
        selected = scheduler.select_packet()
        if selected:
            print(f"  Turn {i+1}: {selected}")
            assert selected.value == expected_value, f"Expected value {expected_value}, got {selected.value}"
            scheduler.send_packet(selected)
        else:
            print(f"  Turn {i+1}: No packets available")
    
    print("\n✅ Deterministic test passed!")


def test_performance_comparison():
    """Compare performance across multiple runs."""
    print("\nPerformance Comparison Test")
    print("=" * 40)
    
    num_runs = 5
    results = []
    
    for run in range(num_runs):
        print(f"\nRun {run + 1}:")
        stats = run_scheduler_simulation(num_turns=15, verbose=False)
        results.append(stats)
        print(f"  Avg value per turn: {stats['avg_value_per_turn']:.2f}")
        print(f"  Packets sent: {stats['packets_sent']}")
        print(f"  Packets expired: {stats['packets_expired']}")
    
    # Calculate averages
    avg_value_per_turn = sum(r['avg_value_per_turn'] for r in results) / num_runs
    avg_packets_sent = sum(r['packets_sent'] for r in results) / num_runs
    avg_packets_expired = sum(r['packets_expired'] for r in results) / num_runs
    
    print(f"\n📊 AVERAGE PERFORMANCE OVER {num_runs} RUNS:")
    print(f"  Average value per turn: {avg_value_per_turn:.2f}")
    print(f"  Average packets sent: {avg_packets_sent:.1f}")
    print(f"  Average packets expired: {avg_packets_expired:.1f}")
    
    print("\n✅ Performance test completed!")


def main():
    """Main test runner."""
    parser = argparse.ArgumentParser(description='Test Simple Packet Scheduler')
    parser.add_argument('--test', '-t', choices=['basic', 'deterministic', 'performance', 'all'],
                        default='all', help='Which test to run')
    parser.add_argument('--turns', '-n', type=int, default=20,
                        help='Number of turns for simulation test')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Verbose output for simulation')
    
    args = parser.parse_args()
    
    print("🧪 Simple Packet Scheduler Test Suite")
    print("=" * 50)
    
    if args.test in ['basic', 'all']:
        test_basic_functionality()
    
    if args.test in ['deterministic', 'all']:
        test_deterministic_scenario()
    
    if args.test in ['performance', 'all']:
        test_performance_comparison()
    
    if args.test == 'simulation':
        print(f"\nRunning simulation with {args.turns} turns:")
        run_scheduler_simulation(num_turns=args.turns, verbose=args.verbose)
    
    print(f"\n🎉 Test suite completed!")


if __name__ == "__main__":
    main()