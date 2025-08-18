#!/usr/bin/env python3
"""LLM Direct Selection Packet Scheduler

LLM directly selects 3 packets to send each turn without predefined strategies.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, List, Optional, Tuple
from nlm_interpreter import NLMSession
from packet import Packet, PacketQueue, generate_random_packet
import random


class LLMDirectScheduler:
    """LLM directly selects packets without predefined strategies."""
    
    def __init__(self, num_queues: int = 4, max_queue_size: int = 5, 
                 num_slots: int = 3, model: str = "gpt-5-mini"):
        """Initialize LLM direct scheduler.
        
        Args:
            num_queues: Number of packet queues to manage
            max_queue_size: Maximum queue size before penalty
            num_slots: Number of packets to select per turn
            model: LLM model to use for selection
        """
        self.num_queues = num_queues
        self.max_queue_size = max_queue_size
        self.num_slots = num_slots
        self.queues = [PacketQueue() for _ in range(num_queues)]
        
        # LLM session for packet selection
        self.session = NLMSession(namespace="llm_direct_scheduler", model=model)
        self.session.clear_local()
        
        # Statistics
        self.total_value_sent = 0
        self.packets_sent = 0
        self.packets_expired = 0
        self.over_limit_penalty = 0
        self.turn_count = 0
        
        # Selection history
        self.selection_history = []
        self.reasoning_history = []
    
    def add_packet_to_queue(self, queue_index: int, packet: Packet):
        """Add a packet to specified queue."""
        if 0 <= queue_index < self.num_queues:
            self.queues[queue_index].add_packet(packet)
            # Check for over-limit penalty
            if self.queues[queue_index].size() > self.max_queue_size:
                self.over_limit_penalty += 1
        else:
            raise ValueError(f"Queue index {queue_index} out of range (0-{self.num_queues-1})")
    
    def get_all_packets_with_ids(self) -> List[Tuple[str, Packet, int]]:
        """Get all packets with their IDs and queue indices.
        
        Returns:
            List of (packet_id, packet, queue_index) tuples
        """
        all_packets = []
        for queue_idx, queue in enumerate(self.queues):
            packets = queue.get_valid_packets()
            for packet_idx, packet in enumerate(packets):
                packet_id = f"{queue_idx}-{packet_idx}"
                all_packets.append((packet_id, packet, queue_idx))
        return all_packets
    
    def format_state_for_llm(self) -> str:
        """Format current state for LLM presentation."""
        lines = []
        lines.append(f"Turn {self.turn_count} - Current System State:")
        lines.append(f"Statistics: Value Sent={self.total_value_sent}, Expired={self.packets_expired}, Penalties={self.over_limit_penalty}")
        lines.append(f"Max Queue Size: {self.max_queue_size} (⚠️ = over limit)")
        lines.append("")
        
        # Show each queue with packets
        for queue_idx, queue in enumerate(self.queues):
            packets = queue.get_valid_packets()
            queue_size = queue.size()
            status = "⚠️ OVER LIMIT" if queue_size > self.max_queue_size else "OK"
            
            lines.append(f"Queue {queue_idx}: {queue_size} packets [{status}]")
            
            if packets:
                for packet_idx, packet in enumerate(packets):
                    packet_id = f"{queue_idx}-{packet_idx}"
                    urgency = ""
                    if packet.deadline <= 3:
                        urgency = "🔴 CRITICAL"
                    elif packet.deadline <= 6:
                        urgency = "🟡 URGENT"
                    else:
                        urgency = "🟢 NORMAL"
                    
                    lines.append(f"  [{packet_id}] value={packet.value}, deadline={packet.deadline} {urgency}")
            else:
                lines.append(f"  [Empty]")
            lines.append("")
        
        return "\n".join(lines)
    
    def select_packets_with_llm(self) -> Tuple[List[Packet], str]:
        """Use LLM to select packets directly.
        
        Returns:
            Tuple of (selected_packets, reasoning)
        """
        # Get all available packets
        all_packets = self.get_all_packets_with_ids()
        
        if not all_packets:
            return [], "No packets available"
        
        # Format state for LLM
        state_description = self.format_state_for_llm()
        
        # Get recent history for context
        history_context = ""
        if self.selection_history:
            recent_selections = self.selection_history[-3:]  # Last 3 turns
            recent_reasoning = self.reasoning_history[-3:]
            history_context = "\n\nRecent selection history:\n"
            for i, (sel, reason) in enumerate(zip(recent_selections, recent_reasoning)):
                turn_num = self.turn_count - len(recent_selections) + i + 1
                history_context += f"Turn {turn_num}: {sel} - {reason}\n"
        
        # Create LLM prompt
        prompt = f"""
=== Packet Selection Task ===

{state_description}{history_context}

Your Task:
Select exactly {self.num_slots} packets to send this turn.

Guidelines:
- You can select from any queue
- Multiple packets from the same queue are allowed
- Consider: packet values, deadlines, queue overflow risks
- Goal: Maximize total value while minimizing penalties

Available packet IDs:
{', '.join([pid for pid, _, _ in all_packets])}

Provide your decision in this format:
Selected: [packet_id1, packet_id2, packet_id3]
Reasoning: [Your reasoning in 1-2 sentences]

Save your packet selections (comma-separated) to {{selected_packets}}
Save your reasoning to {{reasoning}}
"""
        
        # Clear previous values and execute
        self.session.save("selected_packets", "")
        self.session.save("reasoning", "")
        self.session.execute(prompt)
        
        # Get LLM response
        selected_ids_str = str(self.session.get("selected_packets") or "").strip()
        reasoning = str(self.session.get("reasoning") or "No reasoning provided").strip()
        
        print(f"  [DEBUG] LLM selected: '{selected_ids_str}'")
        
        # Parse selected packet IDs
        selected_packets = []
        if selected_ids_str:
            # Clean up the response (remove brackets, extra spaces)
            clean_ids = selected_ids_str.replace("[", "").replace("]", "").replace(" ", "")
            packet_ids = [pid.strip() for pid in clean_ids.split(",") if pid.strip()]
            
            # Map IDs to packets
            id_to_packet = {pid: packet for pid, packet, _ in all_packets}
            
            for packet_id in packet_ids[:self.num_slots]:  # Limit to num_slots
                if packet_id in id_to_packet:
                    selected_packets.append(id_to_packet[packet_id])
                else:
                    print(f"  [WARNING] Invalid packet ID: {packet_id}")
        
        # Fallback if not enough packets selected
        while len(selected_packets) < min(self.num_slots, len(all_packets)):
            # Select highest value packets not yet selected
            remaining_packets = [p for _, p, _ in all_packets if p not in selected_packets]
            if remaining_packets:
                best_packet = max(remaining_packets, key=lambda p: p.value)
                selected_packets.append(best_packet)
                reasoning += f" [Fallback: added {best_packet}]"
        
        # Record history
        selected_ids = [f"{qi}-{pi}" for qi, q in enumerate(self.queues) 
                       for pi, p in enumerate(q.get_valid_packets()) 
                       if p in selected_packets]
        self.selection_history.append(selected_ids)
        self.reasoning_history.append(reasoning)
        
        return selected_packets, reasoning
    
    def send_packets(self, packets: List[Packet]) -> List[str]:
        """Send multiple packets and update statistics.
        
        Returns:
            List of source queue names
        """
        sources = []
        for packet in packets:
            # Find which queue this packet belongs to
            for i, queue in enumerate(self.queues):
                if packet in queue.get_valid_packets():
                    queue.remove_packet(packet)
                    sources.append(f"Queue {i}")
                    self.total_value_sent += packet.value
                    self.packets_sent += 1
                    break
            else:
                sources.append("Unknown Queue")
        
        return sources
    
    def update_deadlines(self):
        """Update deadlines in all queues and track expired packets."""
        all_expired = []
        for i, queue in enumerate(self.queues):
            expired = queue.update_deadlines()
            all_expired.append((i, expired))
            self.packets_expired += len(expired)
        return all_expired
    
    def get_statistics(self) -> Dict:
        """Get current scheduler statistics."""
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
        """Get formatted display of all queues side by side."""
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
                header_text = f"Queue {i} ⚠️"
            else:
                header_text = f"Queue {i}"
            padding = max(0, col_width - len(header_text) - 1)
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


def run_llm_direct_simulation(num_turns: int = 20, num_queues: int = 4,
                             max_queue_size: int = 5, num_slots: int = 3,
                             verbose: bool = True, continuous: bool = False) -> Dict:
    """Run simulation with LLM direct packet selection.
    
    Args:
        num_turns: Number of turns to simulate
        num_queues: Number of packet queues
        max_queue_size: Maximum queue size before penalty
        num_slots: Number of packets to select per turn
        verbose: Whether to show detailed output
        continuous: If True, run without pausing between turns
        
    Returns:
        Final statistics
    """
    if verbose:
        mode_text = "Continuous Mode" if continuous else "Step-by-Step Mode"
        print(f"\n🤖 LLM Direct Selection Packet Scheduler ({mode_text})")
        print(f"📦 Selecting {num_slots} packets per turn")
        print(f"📏 Max Queue Size: {max_queue_size} (penalty for exceeding)")
        print("=" * 60)
    
    scheduler = LLMDirectScheduler(num_queues=num_queues, max_queue_size=max_queue_size,
                                  num_slots=num_slots, model="gpt-5-mini")
    
    # Add initial packets - exactly 3 packets per queue for 3-slot system
    if verbose:
        print("\n📦 Initial packet distribution:")
    for queue_idx in range(num_queues):
        for _ in range(3):  # 3 initial packets per queue
            initial_packet = generate_random_packet(turn=0)
            scheduler.add_packet_to_queue(queue_idx, initial_packet)
            if verbose:
                print(f"  Queue {queue_idx} receives: {initial_packet}")
    
    # Main simulation loop
    for turn in range(1, num_turns + 1):
        scheduler.turn_count = turn
        
        if verbose:
            print(f"\n╔═══ TURN {turn} ═══╗")
        
        # 1. Packet arrival (fixed number per turn)
        num_arrivals = num_slots  # Same as number of slots
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
        
        # 3. LLM packet selection
        selected_packets, reasoning = scheduler.select_packets_with_llm()
        
        if verbose:
            print(f"\n🤖 LLM SELECTION:")
            print(f"  Reasoning: {reasoning}")
        
        if selected_packets:
            sources = scheduler.send_packets(selected_packets)
            if verbose:
                print(f"\n📤 SENDING {len(selected_packets)} PACKETS:")
                total_value = 0
                for packet, source in zip(selected_packets, sources):
                    print(f"  ✓ {packet} from {source}")
                    total_value += packet.value
                print(f"  📊 Total value: {total_value}")
        else:
            if verbose:
                print(f"\n📤 SELECTED: No packets available")
        
        # 4. Update deadlines
        all_expired = scheduler.update_deadlines()
        
        if verbose:
            expired_info = []
            for queue_idx, expired_packets in all_expired:
                if expired_packets:
                    expired_info.append(f"{len(expired_packets)} from Queue {queue_idx}")
            if expired_info:
                print(f"\n⏰ EXPIRED: {', '.join(expired_info)}")
        
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
            
            # Wait for user input to continue (unless in continuous mode)
            if turn < num_turns and not continuous:
                input("\nPress Enter to continue to next turn...")
    
    # Final results
    final_stats = scheduler.get_statistics()
    if verbose:
        print(f"\n🏁 FINAL RESULTS:")
        print(f"  Total value sent: {final_stats['total_value_sent']}")
        print(f"  Packets expired: {final_stats['packets_expired']}")
        print(f"  Over-limit penalty: {final_stats['over_limit_penalty']}")
        
        # Calculate final score
        final_score = final_stats['total_value_sent'] - (final_stats['packets_expired'] * 5) - (final_stats['over_limit_penalty'] * 2)
        print(f"  📈 Final Score: {final_score} (value - 5×expired - 2×penalties)")
        
        # Display final remaining packets per queue
        for i in range(num_queues):
            queue_size = final_stats.get(f'queue_{i}_size', 0)
            warning = " ⚠️" if queue_size > max_queue_size else ""
            print(f"  Queue {i} remaining: {queue_size} packets{warning}")
        
        # Show selection pattern summary
        if scheduler.selection_history:
            print(f"\n🎯 SELECTION PATTERNS:")
            queue_selections = {i: 0 for i in range(num_queues)}
            for selections in scheduler.selection_history:
                for sel_id in selections:
                    if '-' in sel_id:
                        queue_idx = int(sel_id.split('-')[0])
                        queue_selections[queue_idx] += 1
            
            for queue_idx, count in queue_selections.items():
                percentage = (count / sum(queue_selections.values())) * 100 if queue_selections.values() else 0
                print(f"  Queue {queue_idx}: {count} selections ({percentage:.1f}%)")
    
    return final_stats


if __name__ == "__main__":
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='LLM Direct Selection Packet Scheduler')
    parser.add_argument('--turns', '-t', type=int, default=20,
                        help='Number of turns to simulate (default: 20)')
    parser.add_argument('--queues', '-q', type=int, default=4,
                        help='Number of packet queues (default: 4)')
    parser.add_argument('--max-size', '-m', type=int, default=5,
                        help='Maximum queue size before penalty (default: 5)')
    parser.add_argument('--slots', '-s', type=int, default=3,
                        help='Number of packets to select per turn (default: 3)')
    parser.add_argument('--continuous', '-c', action='store_true',
                        help='Run in continuous mode without pausing between turns')
    parser.add_argument('--quiet', action='store_true',
                        help='Run with minimal output')
    
    args = parser.parse_args()
    
    # Run simulation with specified parameters
    results = run_llm_direct_simulation(
        num_turns=args.turns,
        num_queues=args.queues,
        max_queue_size=args.max_size,
        num_slots=args.slots,
        verbose=not args.quiet,
        continuous=args.continuous
    )