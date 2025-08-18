#!/usr/bin/env python3
"""Simple Packet Scheduler - Level 1 Implementation

A single-agent packet scheduler that manages two packet queues and selects
the highest-value packet for transmission each turn.
"""

import random
from typing import Optional, List, Dict
from enum import Enum
from packet import Packet, PacketQueue, generate_random_packet


class SchedulingStrategy(Enum):
    """Packet scheduling strategies."""
    HIGHEST_VALUE = "highest_value"
    MINIMIZE_EXPIRY = "minimize_expiry"
    VALUE_PER_DEADLINE = "value_per_deadline"
    PREVENT_OVERFLOW = "prevent_overflow"


class SimplePacketScheduler:
    """
    A packet scheduler managing multiple queues with configurable strategies.
    """
    
    def __init__(self, num_queues: int = 4, strategy: SchedulingStrategy = SchedulingStrategy.HIGHEST_VALUE,
                 max_queue_size: int = 5):
        """Initialize scheduler with specified number of empty queues.
        
        Args:
            num_queues: Number of packet queues to manage (default: 4)
            strategy: Scheduling strategy to use (default: HIGHEST_VALUE)
            max_queue_size: Maximum queue size before penalty (default: 5)
        """
        self.num_queues = num_queues
        self.strategy = strategy
        self.max_queue_size = max_queue_size
        self.queues = [PacketQueue() for _ in range(num_queues)]
        
        # Statistics
        self.total_value_sent = 0
        self.packets_sent = 0
        self.packets_expired = 0
        self.over_limit_penalty = 0
        self.turn_count = 0
    
    def select_packet(self) -> Optional[Packet]:
        """
        Select packet based on the configured strategy.
        
        Returns:
            The selected packet, or None if no valid packets
        """
        # Get all valid packets from all queues with queue info
        all_packets_with_queue = []
        for i, queue in enumerate(self.queues):
            for packet in queue.get_valid_packets():
                all_packets_with_queue.append((packet, i, queue.size()))
        
        if not all_packets_with_queue:
            return None
        
        # Apply strategy-specific selection
        if self.strategy == SchedulingStrategy.HIGHEST_VALUE:
            return max(all_packets_with_queue, key=lambda x: x[0].value)[0]
        
        elif self.strategy == SchedulingStrategy.MINIMIZE_EXPIRY:
            # Priority: deadline (ascending), then value (descending)
            return min(all_packets_with_queue, key=lambda x: (x[0].deadline, -x[0].value))[0]
        
        elif self.strategy == SchedulingStrategy.VALUE_PER_DEADLINE:
            # Priority: value/deadline ratio (descending)
            return max(all_packets_with_queue, key=lambda x: x[0].value / max(x[0].deadline, 0.1))[0]
        
        elif self.strategy == SchedulingStrategy.PREVENT_OVERFLOW:
            # Priority: 1) From queues at or over limit, 2) deadline, 3) value
            def overflow_priority(item):
                packet, queue_idx, queue_size = item
                # High priority if queue is at or over limit
                overflow_urgency = 0 if queue_size >= self.max_queue_size else 1
                return (overflow_urgency, packet.deadline, -packet.value)
            
            return min(all_packets_with_queue, key=overflow_priority)[0]
        
        else:
            # Fallback to highest value
            return max(all_packets_with_queue, key=lambda x: x[0].value)[0]
    
    def send_packet(self, packet: Packet) -> str:
        """
        Send a packet and update statistics.
        
        Args:
            packet: The packet to send
            
        Returns:
            String indicating which queue the packet came from
        """
        # Determine source queue
        for i, queue in enumerate(self.queues):
            if packet in queue.get_valid_packets():
                queue.remove_packet(packet)
                source = f"Queue {i}"
                break
        else:
            source = "Unknown Queue"
        
        # Update statistics
        self.total_value_sent += packet.value
        self.packets_sent += 1
        
        return source
    
    def update_deadlines(self):
        """Update deadlines in all queues and track expired packets."""
        all_expired = []
        for i, queue in enumerate(self.queues):
            expired = queue.update_deadlines()
            all_expired.append((i, expired))
            self.packets_expired += len(expired)
        
        return all_expired
    
    def add_packet_to_queue(self, queue_index: int, packet: Packet):
        """Add a packet to specified queue.
        
        Args:
            queue_index: Index of the queue (0 to num_queues-1)
            packet: The packet to add
        """
        if 0 <= queue_index < self.num_queues:
            self.queues[queue_index].add_packet(packet)
            # Check for over-limit penalty
            if self.queues[queue_index].size() > self.max_queue_size:
                self.over_limit_penalty += 1
        else:
            raise ValueError(f"Queue index {queue_index} out of range (0-{self.num_queues-1})")
    
    def get_statistics(self) -> Dict:
        """
        Get current scheduler statistics.
        
        Returns:
            Dictionary with performance metrics
        """
        avg_value = self.total_value_sent / self.packets_sent if self.packets_sent > 0 else 0
        avg_per_turn = self.total_value_sent / self.turn_count if self.turn_count > 0 else 0
        
        # Calculate queue sizes
        queue_sizes = {f"queue_{i}_size": queue.size() for i, queue in enumerate(self.queues)}
        total_packets = sum(queue.size() for queue in self.queues)
        
        stats = {
            "total_value_sent": self.total_value_sent,
            "packets_sent": self.packets_sent,
            "packets_expired": self.packets_expired,
            "over_limit_penalty": self.over_limit_penalty,
            "avg_value_per_packet": avg_value,
            "avg_value_per_turn": avg_per_turn,
            "total_packets": total_packets,
            "num_queues": self.num_queues,
            "max_queue_size": self.max_queue_size
        }
        stats.update(queue_sizes)
        
        return stats
    
    def get_queue_display(self) -> List[str]:
        """
        Get formatted display of all queues side by side.
        
        Returns:
            List of strings for display
        """
        # Get display lines for each queue
        queue_lines = []
        max_lines = 0
        
        for i, queue in enumerate(self.queues):
            lines = queue.get_display_list(str(i))
            queue_lines.append(lines)
            max_lines = max(max_lines, len(lines))
        
        # Calculate column width
        col_width = 19
        
        display = []
        
        # Top border
        top_border = "┌" + ("─" * col_width + "┬") * (self.num_queues - 1) + "─" * col_width + "┐"
        display.append(top_border)
        
        # Header row
        header_parts = []
        for i, queue in enumerate(self.queues):
            queue_size = queue.size()
            if queue_size > self.max_queue_size:
                header_text = f"Queue {i} ⚠️"  # Warning for over-limit
            else:
                header_text = f"Queue {i}"
            padding = max(0, col_width - len(header_text) - 1)  # -1 for leading space
            header_parts.append(f" {header_text}{' ' * padding}")
        display.append("│" + "│".join(header_parts) + "│")
        
        # Separator
        sep_border = "├" + ("─" * col_width + "┼") * (self.num_queues - 1) + "─" * col_width + "┤"
        display.append(sep_border)
        
        # Data rows
        for row in range(max_lines):
            row_parts = []
            for queue_idx in range(self.num_queues):
                if row < len(queue_lines[queue_idx]):
                    line_text = queue_lines[queue_idx][row]
                else:
                    line_text = "[Empty queue]" if row == 0 and len(queue_lines[queue_idx]) == 0 else ""
                row_parts.append(f" {line_text:<{col_width-1}}")
            display.append("│" + "│".join(row_parts) + "│")
        
        # Bottom border
        bottom_border = "└" + ("─" * col_width + "┴") * (self.num_queues - 1) + "─" * col_width + "┘"
        display.append(bottom_border)
        
        return display


def run_scheduler_simulation(num_turns: int = 20, num_queues: int = 4, 
                           strategy: SchedulingStrategy = SchedulingStrategy.HIGHEST_VALUE,
                           max_queue_size: int = 5, verbose: bool = True) -> Dict:
    """
    Run a complete packet scheduling simulation.
    
    Args:
        num_turns: Number of turns to simulate
        num_queues: Number of packet queues (default: 4)
        strategy: Scheduling strategy to use (default: HIGHEST_VALUE)
        max_queue_size: Maximum queue size before penalty (default: 5)
        verbose: Whether to show detailed output
        
    Returns:
        Final statistics
    """
    if verbose:
        strategy_name = strategy.value.replace('_', ' ').title()
        print(f"\n🚀 Packet Scheduler - Strategy: {strategy_name}")
        print(f"📏 Max Queue Size: {max_queue_size} (penalty for exceeding)")
        print("=" * 60)
    
    scheduler = SimplePacketScheduler(num_queues=num_queues, strategy=strategy, 
                                    max_queue_size=max_queue_size)
    
    # Add initial packets - exactly 3 packets per queue
    if verbose:
        print("\n📦 Initial packet distribution:")
    for queue_idx in range(num_queues):
        for _ in range(3):  # 3 packets per queue
            initial_packet = generate_random_packet(turn=0)
            scheduler.add_packet_to_queue(queue_idx, initial_packet)
            if verbose:
                print(f"  Queue {queue_idx} receives: {initial_packet}")
    
    # Track expired packets from previous turn
    expired_last_turn = 0
    
    # Main simulation loop
    for turn in range(1, num_turns + 1):
        scheduler.turn_count = turn
        
        if verbose:
            print(f"\n╔═══ TURN {turn} ═══╗")
        
        # 1. Packet arrival (expired_last_turn + 1 packets)
        num_arrivals = expired_last_turn + 1
        arrival_info_list = []
        
        for _ in range(num_arrivals):
            queue_idx = random.randint(0, num_queues - 1)
            new_packet = generate_random_packet(turn)
            scheduler.add_packet_to_queue(queue_idx, new_packet)
            arrival_info_list.append(f"Queue {queue_idx} receives: {new_packet} ✨")
        
        if verbose:
            print(f"\n📦 NEW ARRIVALS ({num_arrivals} packets):")
            for info in arrival_info_list:
                print(f"  {info}")
        
        # 2. Display current queues
        if verbose:
            print(f"\n📋 QUEUE STATUS:")
            for line in scheduler.get_queue_display():
                print(line)
        
        # 3. Packet selection
        selected_packet = scheduler.select_packet()
        
        if selected_packet:
            source_queue = scheduler.send_packet(selected_packet)
            if verbose:
                strategy_name = scheduler.strategy.value.replace('_', ' ').title()
                print(f"\n📤 SELECTED ({strategy_name}): {selected_packet} from {source_queue}")
        else:
            if verbose:
                print(f"\n📤 SELECTED: No packets available")
        
        # 4. Update deadlines
        all_expired = scheduler.update_deadlines()
        expired_last_turn = sum(len(expired_packets) for _, expired_packets in all_expired)
        
        if verbose:
            expired_info = []
            for queue_idx, expired_packets in all_expired:
                if expired_packets:
                    expired_info.append(f"{len(expired_packets)} from Queue {queue_idx}")
            if expired_info:
                print(f"\n⏰ EXPIRED: {', '.join(expired_info)}")
            if expired_last_turn > 0:
                print(f"  → Next turn will have {expired_last_turn + 1} new arrivals")
        
        # 5. Show statistics
        stats = scheduler.get_statistics()
        if verbose:
            print(f"\n📊 TURN STATS:")
            print(f"  Total value sent: {stats['total_value_sent']}")
            print(f"  Packets expired: {stats['packets_expired']}")
            print(f"  Over-limit penalty: {stats['over_limit_penalty']}")
            
            # Display remaining packets per queue
            for i in range(num_queues):
                queue_size = stats.get(f'queue_{i}_size', 0)
                warning = " ⚠️" if queue_size > max_queue_size else ""
                print(f"  Queue {i} remaining: {queue_size} packets{warning}")
            
            # Wait for user input to continue
            if turn < num_turns:
                input("\nPress Enter to continue to next turn...")
    
    # Final results
    final_stats = scheduler.get_statistics()
    if verbose:
        print(f"\n🏁 FINAL RESULTS:")
        print(f"  Total value sent: {final_stats['total_value_sent']}")
        print(f"  Packets expired: {final_stats['packets_expired']}")
        print(f"  Over-limit penalty: {final_stats['over_limit_penalty']}")
        
        # Display final remaining packets per queue
        for i in range(num_queues):
            queue_size = final_stats.get(f'queue_{i}_size', 0)
            warning = " ⚠️" if queue_size > max_queue_size else ""
            print(f"  Queue {i} remaining: {queue_size} packets{warning}")
    
    return final_stats


if __name__ == "__main__":
    # Run a test simulation with 4 queues using prevent overflow strategy
    results = run_scheduler_simulation(num_turns=20, num_queues=4, 
                                     strategy=SchedulingStrategy.PREVENT_OVERFLOW,
                                     max_queue_size=5, verbose=True)