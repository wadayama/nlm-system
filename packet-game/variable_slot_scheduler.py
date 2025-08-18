#!/usr/bin/env python3
"""Variable Slot LLM Packet Scheduler

LLM directly selects packets with variable slot availability (1-4 slots).
The LLM can see the next turn's slot count for strategic planning.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, List, Optional, Tuple
from nlm_interpreter import NLMSession
from packet import Packet, PacketQueue, generate_random_packet
from llm_direct_scheduler import LLMDirectScheduler
import random


class SlotManager:
    """Manages variable slot allocation with configurable probabilities."""
    
    def __init__(self, probabilities: List[float] = None):
        """Initialize slot manager.
        
        Args:
            probabilities: List of 4 probabilities [p1, p2, p3, p4] for slots [1, 2, 3, 4]
                          Must sum to 1.0. Defaults to uniform distribution.
        """
        if probabilities is None:
            probabilities = [0.25, 0.25, 0.25, 0.25]
        
        # Validate probabilities
        if len(probabilities) != 4:
            raise ValueError("Must provide exactly 4 probabilities")
        if abs(sum(probabilities) - 1.0) > 0.001:
            raise ValueError(f"Probabilities must sum to 1.0, got {sum(probabilities)}")
        
        self.probabilities = probabilities
        self.slot_values = [1, 2, 3, 4]
        
        # Initialize current and next slots
        self.current_slots = self._generate_slots()
        self.next_slots = self._generate_slots()
    
    def _generate_slots(self) -> int:
        """Generate random slot count based on probabilities."""
        return random.choices(self.slot_values, weights=self.probabilities)[0]
    
    def advance_turn(self):
        """Move to next turn, updating slot counts."""
        self.current_slots = self.next_slots
        self.next_slots = self._generate_slots()
    
    def get_current_slots(self) -> int:
        """Get current turn's available slots."""
        return self.current_slots
    
    def get_next_slots(self) -> int:
        """Get next turn's available slots (prediction)."""
        return self.next_slots
    
    def get_probability_string(self) -> str:
        """Get formatted probability distribution string."""
        parts = []
        for slots, prob in zip(self.slot_values, self.probabilities):
            parts.append(f"{slots}slot:{prob:.0%}")
        return ", ".join(parts)


class VariableSlotScheduler(LLMDirectScheduler):
    """LLM scheduler with variable slot availability and future prediction."""
    
    def __init__(self, num_queues: int = 4, max_queue_size: int = 5,
                 slot_probabilities: List[float] = None, model: str = "gpt-5-mini"):
        """Initialize variable slot scheduler.
        
        Args:
            num_queues: Number of packet queues to manage
            max_queue_size: Maximum queue size before penalty
            slot_probabilities: Probabilities for [1, 2, 3, 4] slots
            model: LLM model to use for selection
        """
        # Initialize parent with default slots (will be overridden)
        super().__init__(num_queues=num_queues, max_queue_size=max_queue_size,
                        num_slots=3, model=model)
        
        # Initialize slot manager
        self.slot_manager = SlotManager(slot_probabilities)
        
        # Override num_slots with current value
        self.num_slots = self.slot_manager.get_current_slots()
    
    def format_state_for_llm(self) -> str:
        """Format current state for LLM presentation with slot predictions."""
        lines = []
        
        # Add slot information prominently
        lines.append(f"=== SLOT AVAILABILITY ===")
        lines.append(f"Current Turn Slots: {self.slot_manager.get_current_slots()} 🎰")
        lines.append(f"Next Turn Slots: {self.slot_manager.get_next_slots()} 🔮 (prediction)")
        lines.append("")
        
        lines.append(f"Turn {self.turn_count} - System State:")
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
        """Use LLM to select packets with slot prediction awareness."""
        # Update current slot count
        self.num_slots = self.slot_manager.get_current_slots()
        
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
        
        # Create LLM prompt with slot prediction emphasis
        prompt = f"""
=== Variable Slot Packet Selection Task ===

{state_description}{history_context}

IMPORTANT STRATEGIC INFORMATION:
- You have {self.num_slots} slots available THIS turn
- Next turn will have {self.slot_manager.get_next_slots()} slots available
- Consider: Should you save high-value packets for next turn if more slots will be available?
- Or should you use current slots aggressively if fewer slots are coming?

Your Task:
Select exactly {self.num_slots} packets to send this turn.

Guidelines:
- Balance immediate needs (critical deadlines) with future opportunities
- Consider the slot availability trend in your strategy
- Maximize total value while minimizing penalties
- Use the next turn prediction to make strategic decisions

Available packet IDs:
{', '.join([pid for pid, _, _ in all_packets])}

Provide your decision in this format:
Selected: [packet_id1, packet_id2, ...]
Reasoning: [Your reasoning including how you used the slot prediction]

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
            
            for packet_id in packet_ids[:self.num_slots]:  # Limit to current slots
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
    
    def advance_turn(self):
        """Advance to next turn, updating slot availability."""
        self.slot_manager.advance_turn()
        self.num_slots = self.slot_manager.get_current_slots()


def run_variable_slot_simulation(num_turns: int = 20, num_queues: int = 4,
                                max_queue_size: int = 5, 
                                slot_probabilities: List[float] = None,
                                verbose: bool = True, continuous: bool = False) -> Dict:
    """Run simulation with variable slot LLM packet selection.
    
    Args:
        num_turns: Number of turns to simulate
        num_queues: Number of packet queues
        max_queue_size: Maximum queue size before penalty
        slot_probabilities: Probabilities for [1, 2, 3, 4] slots
        verbose: Whether to show detailed output
        continuous: If True, run without pausing between turns
        
    Returns:
        Final statistics
    """
    if verbose:
        mode_text = "Continuous Mode" if continuous else "Step-by-Step Mode"
        print(f"\n🎰 Variable Slot LLM Packet Scheduler ({mode_text})")
        if slot_probabilities:
            print(f"📊 Slot Distribution: 1={slot_probabilities[0]:.0%}, 2={slot_probabilities[1]:.0%}, 3={slot_probabilities[2]:.0%}, 4={slot_probabilities[3]:.0%}")
        else:
            print(f"📊 Slot Distribution: Uniform (25% each)")
        print(f"📏 Max Queue Size: {max_queue_size} (penalty for exceeding)")
        print("=" * 60)
    
    scheduler = VariableSlotScheduler(num_queues=num_queues, max_queue_size=max_queue_size,
                                     slot_probabilities=slot_probabilities, model="gpt-5-mini")
    
    # Add initial packets - 3 packets per queue
    if verbose:
        print("\n📦 Initial packet distribution:")
    for queue_idx in range(num_queues):
        for _ in range(3):
            initial_packet = generate_random_packet(turn=0)
            scheduler.add_packet_to_queue(queue_idx, initial_packet)
            if verbose:
                print(f"  Queue {queue_idx} receives: {initial_packet}")
    
    # Track slot usage statistics
    slot_usage_stats = {1: 0, 2: 0, 3: 0, 4: 0}
    
    # Main simulation loop
    for turn in range(1, num_turns + 1):
        scheduler.turn_count = turn
        current_slots = scheduler.slot_manager.get_current_slots()
        next_slots = scheduler.slot_manager.get_next_slots()
        slot_usage_stats[current_slots] += 1
        
        if verbose:
            print(f"\n╔═══ TURN {turn} ═══╗")
            print(f"🎰 Current Slots: {current_slots} | Next Turn: {next_slots}")
        
        # 1. Packet arrival (number based on current slots for balance)
        num_arrivals = current_slots  # Match arrivals to slots
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
            print(f"\n🤖 LLM SELECTION ({current_slots} slots):")
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
        
        # Advance to next turn's slot allocation
        scheduler.advance_turn()
        
        # Wait for user input to continue (unless in continuous mode)
        if verbose and turn < num_turns and not continuous:
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
        
        # Display slot usage statistics
        print(f"\n🎰 SLOT USAGE STATISTICS:")
        for slots, count in slot_usage_stats.items():
            percentage = (count / num_turns) * 100
            print(f"  {slots} slots: {count} turns ({percentage:.1f}%)")
        
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
    parser = argparse.ArgumentParser(description='Variable Slot LLM Packet Scheduler')
    parser.add_argument('--turns', '-t', type=int, default=20,
                        help='Number of turns to simulate (default: 20)')
    parser.add_argument('--queues', '-q', type=int, default=4,
                        help='Number of packet queues (default: 4)')
    parser.add_argument('--max-size', '-m', type=int, default=5,
                        help='Maximum queue size before penalty (default: 5)')
    parser.add_argument('--probabilities', '-p', type=float, nargs=4,
                        metavar=('P1', 'P2', 'P3', 'P4'),
                        help='Probabilities for 1,2,3,4 slots (must sum to 1.0)')
    parser.add_argument('--continuous', '-c', action='store_true',
                        help='Run in continuous mode without pausing between turns')
    parser.add_argument('--quiet', action='store_true',
                        help='Run with minimal output')
    
    args = parser.parse_args()
    
    # Validate probabilities if provided
    if args.probabilities:
        if abs(sum(args.probabilities) - 1.0) > 0.001:
            print(f"Error: Probabilities must sum to 1.0, got {sum(args.probabilities)}")
            sys.exit(1)
    
    # Run simulation with specified parameters
    results = run_variable_slot_simulation(
        num_turns=args.turns,
        num_queues=args.queues,
        max_queue_size=args.max_size,
        slot_probabilities=args.probabilities,
        verbose=not args.quiet,
        continuous=args.continuous
    )