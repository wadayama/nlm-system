#!/usr/bin/env python3
"""Game orchestrator for the Packet Game - manages two-agent negotiation."""

import random
import argparse
from typing import Optional, Tuple, Dict, List
from packet import Packet, generate_random_packet
from packet_game_agent import PacketGameAgent


class GameDisplay:
    """Handles visual display of the game state."""
    
    @staticmethod
    def show_turn_header(turn: int, max_turns: int):
        """Display turn header."""
        print("╔" + "═" * 60 + "╗")
        print(f"║{f'TURN {turn} / {max_turns}':^60}║")
        print("╚" + "═" * 60 + "╝")
    
    @staticmethod
    def show_arrivals(agent_a, agent_b, new_a: Optional[Packet], new_b: Optional[Packet]):
        """Display new packet arrivals."""
        print("\n📦 NEW ARRIVALS:")
        if new_a:
            print(f"  Agent {agent_a.agent_id}: {new_a} ✨ NEW")
        else:
            print(f"  Agent {agent_a.agent_id}: No new packet")
            
        if new_b:
            print(f"  Agent {agent_b.agent_id}: {new_b} ✨ NEW")
        else:
            print(f"  Agent {agent_b.agent_id}: No new packet")
    
    @staticmethod
    def show_queues(agent_a, agent_b):
        """Display both agents' queues side by side."""
        print("\n📋 QUEUE STATUS:")
        print("┌" + "─" * 35 + "┬" + "─" * 35 + "┐")
        print(f"│ Agent {agent_a.agent_id} Queue ({agent_a.queue.size()} packets){' ' * (35-25-len(str(agent_a.queue.size())))}│", end="")
        print(f" Agent {agent_b.agent_id} Queue ({agent_b.queue.size()} packets){' ' * (35-25-len(str(agent_b.queue.size())))}│")
        print("├" + "─" * 35 + "┼" + "─" * 35 + "┤")
        
        # Get display lists with agent IDs
        lines_a = agent_a.queue.get_display_list(agent_a.agent_id)
        lines_b = agent_b.queue.get_display_list(agent_b.agent_id)
        max_lines = max(len(lines_a), len(lines_b))
        
        # Display side by side with index numbers
        for i in range(max_lines):
            line_a = lines_a[i] if i < len(lines_a) else ""
            line_b = lines_b[i] if i < len(lines_b) else ""
            # Keep index numbers for better reference
            print(f"│ {line_a:<33} │ {line_b:<33} │")
        
        print("└" + "─" * 35 + "┴" + "─" * 35 + "┘")
    
    @staticmethod
    def show_negotiation(agent_name: str, request: Optional[Packet], accept: bool, reasoning: str):
        """Display agent's negotiation decision (legacy method)."""
        print(f"\n[Agent {agent_name} thinking...]")
        print(f"💭 \"{reasoning[:600]}{'...' if len(reasoning) > 600 else ''}\"")
        
        if request:
            print(f"{agent_name}'s request: {request}")
        else:
            print(f"{agent_name}'s request: None (empty queue)")
        
        if accept:
            print(f"{agent_name}'s stance: ACCEPT opponent's request ✅")
        else:
            print(f"{agent_name}'s stance: REJECT opponent's request ❌")
    
    @staticmethod
    def show_negotiation_with_support(agent_name: str, request: Optional[Packet], support: str, reasoning: str):
        """Display agent's negotiation decision with support format."""
        print(f"\n[Agent {agent_name} thinking...]")
        print(f"💭 \"{reasoning[:600]}{'...' if len(reasoning) > 600 else ''}\"")
        
        if request:
            print(f"{agent_name}'s request: {request}")
        else:
            print(f"{agent_name}'s request: None (empty queue)")
        
        if support == "my_request":
            print(f"{agent_name}'s support: MY REQUEST ✊ (wants own packet sent)")
        elif support == "opponent_request":
            print(f"{agent_name}'s support: OPPONENT'S REQUEST 🤝 (supports opponent)")
        elif support == "abstain":
            print(f"{agent_name}'s support: ABSTAIN 🤷 (no preference, random choice)")
        else:
            print(f"{agent_name}'s support: {support} ❓")
    
    @staticmethod
    def show_negotiation_result(agent_a, agent_b, result: str, sent_packet: Optional[Packet], 
                               agreement_type: str):
        """Display negotiation outcome."""
        print("\n⚖️ NEGOTIATION RESULT:")
        
        if agreement_type == "both_support_a":
            print(f"  Both agents support {agent_a.agent_id}'s request ✅✅")
        elif agreement_type == "both_support_b":
            print(f"  Both agents support {agent_b.agent_id}'s request ✅✅")
        elif agreement_type == "a_yields":
            print(f"  {agent_a.agent_id} supports {agent_b.agent_id}'s request 🤝")
        elif agreement_type == "b_yields":
            print(f"  {agent_b.agent_id} supports {agent_a.agent_id}'s request 🤝")
        elif agreement_type == "random_choice":
            print(f"  No clear agreement → Random selection 🎲")
        elif agreement_type == "mutual_accept_a":
            print(f"  Both agents agreed to send {agent_a.agent_id}'s packet ✅")
        elif agreement_type == "mutual_accept_b":
            print(f"  Both agents agreed to send {agent_b.agent_id}'s packet ✅")
        elif agreement_type == "no_agreement":
            print(f"  Both agents rejected ❌ → Random selection")
        elif agreement_type == "both_accept":
            print(f"  Both agents accepted both packets ✅✅ → Random selection")
        
        if sent_packet:
            winner = agent_a.agent_id if result == "A_sent" else agent_b.agent_id
            print(f"\n📤 TRANSMISSION: Packet {sent_packet} sent by Agent {winner}")
        else:
            print(f"\n📤 TRANSMISSION: No packet sent (both queues empty)")
    
    @staticmethod
    def show_deadline_updates(expired_a: List[Packet], expired_b: List[Packet]):
        """Show deadline updates and expired packets."""
        if expired_a or expired_b:
            print("\n⏰ DEADLINE UPDATES:")
            if expired_a:
                print(f"  Agent A expired: {expired_a}")
            if expired_b:
                print(f"  Agent B expired: {expired_b}")
    
    @staticmethod
    def show_statistics(turn: int, total_value: int, agent_stats_a: dict, agent_stats_b: dict):
        """Display game statistics."""
        avg_value = total_value / turn if turn > 0 else 0
        total_sent = agent_stats_a["packets_sent"] + agent_stats_b["packets_sent"]
        total_expired = agent_stats_a["packets_expired"] + agent_stats_b["packets_expired"]
        
        print("\n📊 STATISTICS:")
        print(f"  Total value sent: {total_value} (avg: {avg_value:.1f} per turn)")
        print(f"  Packets sent: A={agent_stats_a['packets_sent']}, B={agent_stats_b['packets_sent']}")
        print(f"  Packets expired: {total_expired} total")


def resolve_negotiation_with_support(agent_a, agent_b, request_a: Optional[Packet], request_b: Optional[Packet],
                                    support_a: str, support_b: str) -> Tuple[str, Optional[Packet], str]:
    """
    Resolve negotiation using support decisions.
    
    Args:
        support_a/support_b: "my_request", "opponent_request", or "abstain"
    
    Returns:
        Tuple of (result, sent_packet, agreement_type)
    """
    # Handle empty queue cases
    if not request_a and not request_b:
        return "none_sent", None, "both_empty"
    elif not request_a:
        return "B_sent", request_b, "a_empty"
    elif not request_b:
        return "A_sent", request_a, "b_empty"
    
    # Resolve based on support decisions
    a_supports_a = (support_a == "my_request")
    a_supports_b = (support_a == "opponent_request")
    b_supports_a = (support_b == "opponent_request")  # B supporting A's request
    b_supports_b = (support_b == "my_request")
    
    # Check for clear agreements
    if a_supports_a and b_supports_a:
        # Both support A's request
        return "A_sent", request_a, "both_support_a"
    elif a_supports_b and b_supports_b:
        # Both support B's request  
        return "B_sent", request_b, "both_support_b"
    elif a_supports_b and (support_b == "abstain"):
        # A supports B, B abstains -> B wins
        return "B_sent", request_b, "a_yields"
    elif b_supports_a and (support_a == "abstain"):
        # B supports A, A abstains -> A wins
        return "A_sent", request_a, "b_yields"
    else:
        # No clear agreement - random choice
        if random.random() < 0.5:
            return "A_sent", request_a, "random_choice"
        else:
            return "B_sent", request_b, "random_choice"


def resolve_negotiation(agent_a, agent_b, request_a: Optional[Packet], request_b: Optional[Packet],
                       accept_a: bool, accept_b: bool) -> Tuple[str, Optional[Packet], str]:
    """
    Resolve negotiation according to game rules.
    
    Returns:
        Tuple of (result, sent_packet, agreement_type)
    """
    # Handle empty queue cases
    if not request_a and not request_b:
        return "none_sent", None, "both_empty"
    elif not request_a:
        return "B_sent", request_b, "a_empty"
    elif not request_b:
        return "A_sent", request_a, "b_empty"
    
    # Both have packets - check agreement
    if accept_a and accept_b:
        # Both accept both requests - need random selection
        if random.random() < 0.5:
            return "A_sent", request_a, "both_accept"
        else:
            return "B_sent", request_b, "both_accept"
    elif accept_a and not accept_b:
        # A accepts B's request, B rejects A's request -> B wins
        return "B_sent", request_b, "a_yields"
    elif not accept_a and accept_b:
        # B accepts A's request, A rejects B's request -> A wins
        return "A_sent", request_a, "b_yields"
    else:
        # No agreement - random selection
        if random.random() < 0.5:
            return "A_sent", request_a, "no_agreement"
        else:
            return "B_sent", request_b, "no_agreement"


def play_turn(agent_a: PacketGameAgent, agent_b: PacketGameAgent, turn: int, 
              display: GameDisplay) -> Dict:
    """
    Play one turn of the game.
    
    Returns:
        Dictionary with turn results
    """
    display.show_turn_header(turn, 20)  # Default 20 turns
    
    # 1. Packet arrivals (exactly one packet arrives per turn)
    if random.random() < 0.5:
        new_a = generate_random_packet(turn)
        new_b = None
    else:
        new_a = None
        new_b = generate_random_packet(turn)
    
    if new_a:
        agent_a.add_packet(new_a)
    if new_b:
        agent_b.add_packet(new_b)
    
    display.show_arrivals(agent_a, agent_b, new_a, new_b)
    display.show_queues(agent_a, agent_b)
    
    # 2. Enhanced Negotiation Phase (3 stages)
    print("\n🤝 NEGOTIATION PHASE")
    print("─" * 60)
    
    # Stage 1: Initial proposals and messages
    print("📋 Stage 1: Initial Proposals")
    request_a, message_a = agent_a.make_initial_proposal(turn)
    request_b, message_b = agent_b.make_initial_proposal(turn)
    
    print(f"\n{agent_a.agent_id}'s initial proposal:")
    print(f"  Request: {request_a if request_a else 'None (empty queue)'}")
    print(f"  Message: \"{message_a}\"")
    
    print(f"\n{agent_b.agent_id}'s initial proposal:")
    print(f"  Request: {request_b if request_b else 'None (empty queue)'}")
    print(f"  Message: \"{message_b}\"")
    
    # Stage 2: Two rounds of message exchange
    print("\n💬 Stage 2: Message Exchange")
    conversation_log = []
    conversation_log.append(f"{agent_a.agent_id} initial: \"{message_a}\"")
    conversation_log.append(f"{agent_b.agent_id} initial: \"{message_b}\"")
    
    # Round 1
    print("\n  Round 1:")
    # print(f"    DEBUG: A receives B's initial message: \"{message_b[:50]}...\"")
    # print(f"    DEBUG: B receives A's initial message: \"{message_a[:50]}...\"")
    
    response_a_r1 = agent_a.send_negotiation_message(turn, 1, message_b, request_a, request_b)
    response_b_r1 = agent_b.send_negotiation_message(turn, 1, message_a, request_b, request_a)
    
    print(f"    {agent_a.agent_id}: \"{response_a_r1}\"")
    print(f"    {agent_b.agent_id}: \"{response_b_r1}\"")
    
    conversation_log.append(f"{agent_a.agent_id} round 1: \"{response_a_r1}\"")
    conversation_log.append(f"{agent_b.agent_id} round 1: \"{response_b_r1}\"")
    
    # Round 2
    print("\n  Round 2:")
    # print(f"    DEBUG: A receives B's R1 response: \"{response_b_r1[:50]}...\"")
    # print(f"    DEBUG: B receives A's R1 response: \"{response_a_r1[:50]}...\"")
    
    response_a_r2 = agent_a.send_negotiation_message(turn, 2, response_b_r1, request_a, request_b)
    response_b_r2 = agent_b.send_negotiation_message(turn, 2, response_a_r1, request_b, request_a)
    
    print(f"    {agent_a.agent_id}: \"{response_a_r2}\"")
    print(f"    {agent_b.agent_id}: \"{response_b_r2}\"")
    
    conversation_log.append(f"{agent_a.agent_id} round 2: \"{response_a_r2}\"")
    conversation_log.append(f"{agent_b.agent_id} round 2: \"{response_b_r2}\"")
    
    # Stage 3: Final decisions based on full conversation
    print("\n⚖️ Stage 3: Final Decisions")
    full_conversation = "\n".join(conversation_log)
    
    final_request_a, support_a, reasoning_a = agent_a.make_final_decision(turn, request_b, full_conversation)
    final_request_b, support_b, reasoning_b = agent_b.make_final_decision(turn, request_a, full_conversation)
    
    # Use final requests for negotiation resolution
    request_a = final_request_a
    request_b = final_request_b
    
    display.show_negotiation_with_support(agent_a.agent_id, request_a, support_a, reasoning_a)
    print("─" * 60)
    display.show_negotiation_with_support(agent_b.agent_id, request_b, support_b, reasoning_b)
    
    # 3. Resolve negotiation using support decisions
    result, sent_packet, agreement_type = resolve_negotiation_with_support(
        agent_a, agent_b, request_a, request_b, support_a, support_b
    )
    
    display.show_negotiation_result(agent_a, agent_b, result, sent_packet, agreement_type)
    
    # 4. Process sent packet
    total_value_sent = 0
    if result == "A_sent" and sent_packet:
        agent_a.remove_sent_packet(sent_packet)
        total_value_sent = sent_packet.value
    elif result == "B_sent" and sent_packet:
        agent_b.remove_sent_packet(sent_packet)
        total_value_sent = sent_packet.value
    
    # 5. Update deadlines and handle expiration
    expired_a = agent_a.update_deadlines()
    expired_b = agent_b.update_deadlines()
    
    display.show_deadline_updates(expired_a, expired_b)
    
    # 6. Record results in both agents (convert support to accept for history)
    accept_a = (support_a == "opponent_request")
    accept_b = (support_b == "opponent_request")
    
    agent_a.record_turn_result(turn, request_a, request_b, accept_a, accept_b, 
                              "mine_sent" if result == "A_sent" else "opponent_sent" if result == "B_sent" else "none_sent",
                              sent_packet)
    agent_b.record_turn_result(turn, request_b, request_a, accept_b, accept_a,
                              "mine_sent" if result == "B_sent" else "opponent_sent" if result == "A_sent" else "none_sent", 
                              sent_packet)
    
    # 7. Show statistics
    stats_a = agent_a.get_statistics()
    stats_b = agent_b.get_statistics()
    display.show_statistics(turn, total_value_sent, stats_a, stats_b)
    
    print("\n" + "═" * 60)
    
    return {
        "turn": turn,
        "value_sent": total_value_sent,
        "agreement_type": agreement_type,
        "expired_count": len(expired_a) + len(expired_b)
    }


def run_game(num_turns: int = 20, model: str = "gpt-5-mini", verbose: bool = True) -> Dict:
    """
    Run a complete packet game.
    
    Args:
        num_turns: Number of turns to play
        model: LLM model to use for agents
        verbose: Whether to show detailed output
        
    Returns:
        Game statistics
    """
    print("\n🎮 Packet Game - Autonomous Negotiation")
    print("=" * 60)
    
    # Create agents
    agent_a = PacketGameAgent("A", model=model)
    agent_b = PacketGameAgent("B", model=model)
    display = GameDisplay()
    
    # Add initial packets (3 random packets each)
    print("🎲 Initial packet distribution:")
    for i in range(3):
        initial_a = generate_random_packet(turn=0)
        initial_b = generate_random_packet(turn=0)
        agent_a.add_packet(initial_a)
        agent_b.add_packet(initial_b)
        print(f"  Agent A receives: {initial_a}")
        print(f"  Agent B receives: {initial_b}")
    
    print(f"\n📋 Starting queues:")
    display.show_queues(agent_a, agent_b)
    
    # Game statistics
    total_value = 0
    total_agreements = 0
    total_expired = 0
    turn_results = []
    
    # Play turns
    for turn in range(1, num_turns + 1):
        result = play_turn(agent_a, agent_b, turn, display)
        
        total_value += result["value_sent"]
        if result["agreement_type"] in ["mutual_accept_a", "mutual_accept_b", "a_yields", "b_yields"]:
            total_agreements += 1
        total_expired += result["expired_count"]
        
        turn_results.append(result)
        
        # Brief pause for readability
        if verbose and turn < num_turns:
            input("\nPress Enter to continue to next turn...")
    
    # Final results
    print("\n" + "🏁" * 20)
    print("GAME COMPLETE!")
    print("🏁" * 20)
    
    stats_a = agent_a.get_statistics()
    stats_b = agent_b.get_statistics()
    
    avg_value = total_value / num_turns
    agreement_rate = (total_agreements / num_turns) * 100
    
    print(f"\n📊 FINAL STATISTICS:")
    print(f"  Average value per turn: {avg_value:.2f}")
    print(f"  Total value sent: {total_value}")
    print(f"  Agreement rate: {agreement_rate:.1f}%")
    print(f"  Total packets expired: {total_expired}")
    print(f"\n  Agent A: {stats_a['packets_sent']} sent, avg {stats_a['avg_value']:.1f}")
    print(f"  Agent B: {stats_b['packets_sent']} sent, avg {stats_b['avg_value']:.1f}")
    
    return {
        "avg_value_per_turn": avg_value,
        "total_value": total_value,
        "agreement_rate": agreement_rate,
        "total_expired": total_expired,
        "agent_a_stats": stats_a,
        "agent_b_stats": stats_b
    }


def main():
    """Main entry point with command line arguments."""
    parser = argparse.ArgumentParser(
        description='Packet Game - Two-agent negotiation simulation'
    )
    
    parser.add_argument('--turns', '-t',
                       type=int,
                       default=20,
                       help='Number of turns to play (default: 20)')
    
    parser.add_argument('--model', '-m',
                       default='gpt-5-mini',
                       help='LLM model to use (default: gpt-5-mini)')
    
    parser.add_argument('--quiet', '-q',
                       action='store_true',
                       help='Run without pausing between turns')
    
    args = parser.parse_args()
    
    # Run game
    results = run_game(
        num_turns=args.turns,
        model=args.model,
        verbose=not args.quiet
    )
    
    # Show final summary
    print(f"\n🎯 Key Metric: {results['avg_value_per_turn']:.2f} average value per turn")


if __name__ == "__main__":
    main()