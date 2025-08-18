#!/usr/bin/env python3
"""LLM-based Dynamic Strategy Packet Scheduler

Uses an LLM to dynamically select scheduling strategies based on system state.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, List, Optional
from enum import Enum
from nlm_interpreter import NLMSession
from simple_scheduler import SchedulingStrategy, SimplePacketScheduler, run_scheduler_simulation
from packet import Packet, PacketQueue, generate_random_packet
import random


class LLMStrategySelector:
    """Selects scheduling strategies using LLM based on system state."""
    
    def __init__(self, model: str = "gpt-5-mini"):
        """Initialize LLM strategy selector.
        
        Args:
            model: LLM model to use for strategy selection
        """
        self.session = NLMSession(namespace="llm_scheduler", model=model)
        self.session.clear_local()
        
        # Available strategies (3 main strategies)
        self.strategies = [
            SchedulingStrategy.HIGHEST_VALUE,
            SchedulingStrategy.MINIMIZE_EXPIRY,
            SchedulingStrategy.PREVENT_OVERFLOW
        ]
        
        # History tracking
        self.strategy_history = []
        self.reasoning_history = []
    
    def observe_state(self, scheduler: SimplePacketScheduler, turn: int, 
                     expired_last_turn: int) -> Dict:
        """Observe current system state.
        
        Returns:
            Dictionary containing system state information
        """
        state = {
            "turn": turn,
            "expired_last_turn": expired_last_turn,
            "total_value_sent": scheduler.total_value_sent,
            "total_expired": scheduler.packets_expired,
            "over_limit_penalty": scheduler.over_limit_penalty,
            "max_queue_size": scheduler.max_queue_size,
            "queues": []
        }
        
        # Detailed queue information
        for i, queue in enumerate(scheduler.queues):
            packets = queue.get_valid_packets()
            queue_info = {
                "index": i,
                "size": queue.size(),
                "over_limit": queue.size() > scheduler.max_queue_size,
                "packets": []
            }
            
            for packet in packets:
                queue_info["packets"].append({
                    "value": packet.value,
                    "deadline": packet.deadline,
                    "urgency": "critical" if packet.deadline <= 1 else "urgent" if packet.deadline <= 2 else "normal"
                })
            
            state["queues"].append(queue_info)
        
        return state
    
    def select_strategy(self, state: Dict) -> tuple[SchedulingStrategy, str]:
        """Select strategy using LLM based on current state.
        
        Returns:
            Tuple of (selected_strategy, reasoning)
        """
        # Format state for LLM
        state_description = self._format_state(state)
        
        # Create prompt for LLM
        prompt = f"""
=== Packet Scheduler Strategy Selection ===

Current System State (Turn {state['turn']}):
{state_description}

Available Strategies:
1. HIGHEST_VALUE: Always select the packet with highest value
   - Pros: Maximizes immediate value
   - Cons: May cause more expirations and overflow penalties

2. MINIMIZE_EXPIRY: Prioritize packets with shortest deadline
   - Pros: Reduces packet expiration
   - Cons: May send lower value packets

3. PREVENT_OVERFLOW: Prioritize packets from queues at/over limit
   - Pros: Reduces overflow penalties
   - Cons: May not optimize value or expiry

Your Task:
Analyze the current state and select the BEST strategy for the NEXT turn.
Consider:
- Queue sizes vs max limit (5)
- Packet deadlines and urgency
- Current penalties (expired: {state['total_expired']}, overflow: {state['over_limit_penalty']})
- Overall goal: Maximize total value while minimizing penalties

Provide your decision in this format:
Strategy: [HIGHEST_VALUE or MINIMIZE_EXPIRY or PREVENT_OVERFLOW]
Reasoning: [Your detailed reasoning in 1-2 sentences]

Save your strategy choice to {{strategy_choice}}
Save your reasoning to {{reasoning}}
"""
        
        # Clear previous values
        self.session.save("strategy_choice", "")
        self.session.save("reasoning", "")
        
        # Execute LLM decision
        self.session.execute(prompt)
        
        # Get LLM's choice
        strategy_name = str(self.session.get("strategy_choice") or "HIGHEST_VALUE").strip()
        reasoning = str(self.session.get("reasoning") or "Default strategy selection").strip()
        
        # Debug: Show raw LLM response
        print(f"  [DEBUG] Raw strategy: '{strategy_name}'")
        
        # Map to strategy enum
        strategy_map = {
            "HIGHEST_VALUE": SchedulingStrategy.HIGHEST_VALUE,
            "MINIMIZE_EXPIRY": SchedulingStrategy.MINIMIZE_EXPIRY,
            "PREVENT_OVERFLOW": SchedulingStrategy.PREVENT_OVERFLOW
        }
        
        # Clean up strategy name (remove extra text if any)
        cleaned_name = strategy_name.upper()
        for key in strategy_map:
            if key in cleaned_name:
                cleaned_name = key
                break
        
        selected_strategy = strategy_map.get(cleaned_name, SchedulingStrategy.HIGHEST_VALUE)
        
        # Debug: Show selected strategy
        print(f"  [DEBUG] Selected: {selected_strategy.value}")
        
        # Record history
        self.strategy_history.append(selected_strategy)
        self.reasoning_history.append(reasoning)
        
        return selected_strategy, reasoning
    
    def _format_state(self, state: Dict) -> str:
        """Format state dictionary into readable string."""
        lines = []
        lines.append(f"Total Value Sent: {state['total_value_sent']}")
        lines.append(f"Packets Expired: {state['total_expired']}")
        lines.append(f"Overflow Penalties: {state['over_limit_penalty']}")
        lines.append(f"Expired Last Turn: {state['expired_last_turn']}")
        lines.append(f"\nQueue Status (Max Size: {state['max_queue_size']}):")
        
        for queue_info in state["queues"]:
            status = "⚠️ OVER LIMIT" if queue_info["over_limit"] else "OK"
            lines.append(f"\nQueue {queue_info['index']}: {queue_info['size']} packets [{status}]")
            
            if queue_info["packets"]:
                # Show up to 3 packets
                for i, packet in enumerate(queue_info["packets"][:3]):
                    urgency_marker = "🔴" if packet["urgency"] == "critical" else "🟡" if packet["urgency"] == "urgent" else "🟢"
                    lines.append(f"  {urgency_marker} Packet: value={packet['value']}, deadline={packet['deadline']}")
                
                if len(queue_info["packets"]) > 3:
                    lines.append(f"  ... and {len(queue_info['packets']) - 3} more packets")
        
        return "\n".join(lines)


def run_llm_scheduler_simulation(num_turns: int = 20, num_queues: int = 4,
                                max_queue_size: int = 5, verbose: bool = True) -> Dict:
    """Run simulation with LLM-based dynamic strategy selection.
    
    Args:
        num_turns: Number of turns to simulate
        num_queues: Number of packet queues
        max_queue_size: Maximum queue size before penalty
        verbose: Whether to show detailed output
        
    Returns:
        Final statistics
    """
    if verbose:
        print("\n🤖 LLM-Based Dynamic Strategy Packet Scheduler")
        print(f"📏 Max Queue Size: {max_queue_size} (penalty for exceeding)")
        print("=" * 60)
    
    # Initialize LLM selector
    llm_selector = LLMStrategySelector(model="gpt-5-mini")
    
    # Start with a default strategy
    current_strategy = SchedulingStrategy.HIGHEST_VALUE
    scheduler = SimplePacketScheduler(num_queues=num_queues, strategy=current_strategy,
                                    max_queue_size=max_queue_size)
    
    # Add initial packets - exactly 3 packets per queue
    if verbose:
        print("\n📦 Initial packet distribution:")
    for queue_idx in range(num_queues):
        for _ in range(3):
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
        
        # LLM Strategy Selection (before packet arrival)
        state = llm_selector.observe_state(scheduler, turn, expired_last_turn)
        new_strategy, reasoning = llm_selector.select_strategy(state)
        
        # Update scheduler strategy
        scheduler.strategy = new_strategy
        
        if verbose:
            strategy_name = new_strategy.value.replace('_', ' ').title()
            print(f"\n🤖 LLM STRATEGY SELECTION:")
            print(f"  Strategy: {strategy_name}")
            print(f"  Reasoning: {reasoning}")
        
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
        
        # 3. Packet selection (using LLM-selected strategy)
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
        
        # Show strategy usage statistics
        print(f"\n📊 STRATEGY USAGE:")
        strategy_counts = {}
        for strategy in llm_selector.strategy_history:
            strategy_name = strategy.value.replace('_', ' ').title()
            strategy_counts[strategy_name] = strategy_counts.get(strategy_name, 0) + 1
        
        for strategy_name, count in strategy_counts.items():
            percentage = (count / len(llm_selector.strategy_history)) * 100
            print(f"  {strategy_name}: {count} times ({percentage:.1f}%)")
    
    return final_stats


if __name__ == "__main__":
    # Run simulation with LLM-based strategy selection
    results = run_llm_scheduler_simulation(num_turns=20, num_queues=4,
                                          max_queue_size=5, verbose=True)