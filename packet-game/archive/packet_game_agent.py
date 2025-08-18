#!/usr/bin/env python3
"""Autonomous agent for the Packet Game using NLM system."""

from nlm_interpreter import NLMSession
from packet import Packet, PacketQueue, generate_random_packet
from typing import Optional, Tuple


class PacketGameAgent:
    """
    An autonomous agent that learns to negotiate packet transmission.
    Uses natural language reasoning without predefined strategies.
    """
    
    def __init__(self, agent_id: str, model: str = "gpt-5-mini"):
        """
        Initialize packet game agent.
        
        Args:
            agent_id: Unique identifier for this agent (e.g., "A" or "B")
            model: LLM model to use for decision making
        """
        self.agent_id = agent_id
        self.session = NLMSession(namespace=f"packet_agent_{agent_id}", model=model)
        self.queue = PacketQueue()
        
        # Statistics tracking
        self.total_sent_value = 0
        self.packets_sent = 0
        self.packets_expired = 0
        
        # Clear session for fresh start
        self.session.clear_local()
    
    def add_packet(self, packet: Packet):
        """Add a packet to the agent's queue."""
        self.queue.add_packet(packet)
    
    def record_turn_result(self, turn: int, my_request: Optional[Packet], 
                          opponent_request: Optional[Packet],
                          my_accept: bool, opponent_accept: bool,
                          result: str, sent_packet: Optional[Packet]):
        """
        Record the result of a turn for learning (card-game style).
        
        Args:
            turn: Turn number
            my_request: Packet I requested
            opponent_request: Packet opponent requested
            my_accept: Whether I accepted opponent's request
            opponent_accept: Whether opponent accepted my request
            result: "mine_sent", "opponent_sent", or "none_sent"
            sent_packet: The packet that was actually sent
        """
        # Create detailed history entry
        turn_entry = f"Turn {turn}: "
        
        if my_request:
            turn_entry += f"I requested {my_request}, "
        else:
            turn_entry += "I had no packets, "
            
        if opponent_request:
            turn_entry += f"Opponent requested {opponent_request}. "
        else:
            turn_entry += "Opponent had no packets. "
        
        if my_accept and opponent_accept:
            turn_entry += "Both accepted (agreement). "
        elif my_accept and not opponent_accept:
            turn_entry += "I accepted, opponent rejected. "
        elif not my_accept and opponent_accept:
            turn_entry += "I rejected, opponent accepted. "
        else:
            turn_entry += "Both rejected (no agreement). "
        
        turn_entry += f"Result: {result}"
        if sent_packet:
            turn_entry += f" ({sent_packet} sent)"
        
        # Store in history
        self.session.append("negotiation_history", turn_entry)
        
        # Track patterns for learning
        if result == "mine_sent":
            self.session.append("success_patterns", 
                              f"T{turn}: My {my_request} sent" + 
                              (" by agreement" if opponent_accept else " by random"))
        elif result == "opponent_sent" and my_accept:
            self.session.append("cooperation_patterns",
                              f"T{turn}: Yielded for opponent's {opponent_request}")
    
    def get_negotiation_history(self, max_turns: int = 5) -> str:
        """Get recent negotiation history for analysis."""
        history = self.session.get_tail("negotiation_history", n_lines=max_turns)
        return history if history else "No previous negotiations"
    
    def get_success_patterns(self, max_entries: int = 3) -> str:
        """Get patterns of successful transmissions."""
        patterns = self.session.get_tail("success_patterns", n_lines=max_entries)
        return patterns if patterns else "No success patterns yet"
    
    def get_cooperation_patterns(self, max_entries: int = 3) -> str:
        """Get patterns of cooperation."""
        patterns = self.session.get_tail("cooperation_patterns", n_lines=max_entries)
        return patterns if patterns else "No cooperation patterns yet"
    
    def make_initial_proposal(self, turn: int) -> Tuple[Optional[Packet], str]:
        """
        Make initial packet request and negotiation message.
        
        Returns:
            Tuple of (requested_packet, message_to_opponent)
        """
        valid_packets = self.queue.get_valid_packets()
        
        if not valid_packets:
            return None, "I have no packets. Please go ahead."
        
        # Get history for context
        recent_history = self.get_negotiation_history(max_turns=3)
        
        # Format queue for display with agent ID
        queue_display = "\n".join([f"  [{self.agent_id}-{i}] {p}" for i, p in enumerate(valid_packets)])
        
        # Initial proposal macro
        macro = """
        === Turn {{turn}} - Initial Proposal ===
        
        My packet queue:
        {{queue_display}}
        
        Recent negotiation history:
        {{recent_history}}
        
        === Game Rules & Evaluation ===
        
        - I choose 1 packet to request
        - Opponent chooses 1 packet to request  
        - We negotiate through messages
        - Final decision: Support opponent → their packet sent, Support mine → my packet sent, No agreement → random choice
        
        **IMPORTANT - How Success is Measured:**
        - Game success = Average Value Per Turn = (Total Sent Value) ÷ (Number of Turns)
        - BOTH agents benefit when high-value packets are sent (regardless of who sends them)
        - Expired packets = lost value = hurts overall performance
        - Think about when cooperation vs competition might be beneficial
        
        === Your Task ===
        
        1. Choose which packet you want to send (consider value and urgency)
        2. Write a persuasive message explaining your choice
        
        Strategy tips:
        - Explain why your packet is important (high value? urgent deadline?)
        - Consider proposing cooperation or trades
        - Be honest about your priorities
        - Use FULL PACKET REFERENCES like [A-0], [B-2] when discussing specific packets
        - IMPORTANT: You can only request YOUR OWN packets (those with [{{agent_id}}-X] format)
        - When discussing opponent packets, say "I see you have [B-0]" not "I request [B-0]"
        - Remember: you'll make final support decision later
        
        === Your Decision ===
        
        Packet to request from YOUR queue (index 0, 1, 2, etc.): {{request_index}}
        Message to opponent: {{message}}
        """
        
        # Set variables
        self.session.save("turn", turn)
        self.session.save("queue_display", queue_display)
        self.session.save("recent_history", recent_history)
        
        # Execute
        self.session.execute(macro)
        
        # Get results
        try:
            request_index = int(self.session.get("request_index") or 0)
            request_index = max(0, min(request_index, len(valid_packets) - 1))
        except (ValueError, TypeError):
            request_index = 0
            
        message = self.session.get("message") or "Please consider my request."
        requested_packet = valid_packets[request_index]
        
        return requested_packet, message
    
    def send_negotiation_message(self, turn: int, round_num: int, 
                                opponent_message: str, 
                                my_request: Optional[Packet],
                                opponent_request: Optional[Packet]) -> str:
        """
        Send a negotiation message in response to opponent.
        
        Args:
            turn: Current turn
            round_num: Message round (1 or 2)
            opponent_message: Message from opponent
            my_request: My requested packet
            opponent_request: Opponent's requested packet
            
        Returns:
            Message to send to opponent
        """
        # Get context
        recent_history = self.get_negotiation_history(max_turns=3)
        queue_display = "\n".join([f"  [{self.agent_id}-{i}] {p}" for i, p in enumerate(self.queue.get_valid_packets())])
        
        macro = """
        === Turn {{turn}} - Message Round {{round_num}} ===
        
        Current situation:
        - My request: {{my_request}}
        - Opponent's request: {{opponent_request}}
        - My queue: {{queue_display}}
        
        Opponent's message to me:
        "{{opponent_message}}"
        
        Recent history:
        {{recent_history}}
        
        === Negotiation Goals & Strategy ===
        
        - Goal: Maximize Average Value Per Turn = (Total Sent Value) ÷ (Turns)
        - BOTH agents succeed when high-value packets are sent (regardless of who sends them)
        - Try to convince opponent to support your request
        - Or find mutually beneficial agreement
        - Think strategically about cooperation vs competition
        - Remember: you'll decide final support decision later
        
        === Your Response (Round {{round_num}} - ID: {{unique_id}}) ===
        
        {{round_context}}
        
        CRITICAL: This is Round {{round_num}} with unique session {{unique_id}}. 
        Your response MUST be different from any previous round.
        
        Write a strategic response for Round {{round_num}}. Consider:
        - Address their arguments
        - Explain why your packet is important
        - Propose cooperation or trades for future rounds
        - Build trust or apply strategic pressure
        - Be clear about what you want
        - Use FULL PACKET REFERENCES like [A-0], [B-2] when referring to specific packets
        
        Your message: {{response_message}}
        """
        
        # Set variables with round-specific context
        round_context = ""
        if round_num == 1:
            round_context = f"ROUND 1 CONTEXT: First response to their initial proposal.\nTheir initial message: '{opponent_message}'\nYour goal: Counter-argue and explain your position.\nRound type: Initial response"
        elif round_num == 2:
            round_context = f"ROUND 2 CONTEXT: Final negotiation opportunity.\nTheir Round 1 response: '{opponent_message}'\nYour goal: Finalize agreement or make strongest case.\nRound type: Final response"
        
        # Add unique identifier to avoid caching issues
        import time
        unique_id = f"{turn}_{round_num}_{int(time.time() * 1000) % 10000}"
        
        self.session.save("turn", turn)
        self.session.save("round_num", round_num)
        self.session.save("unique_id", unique_id)
        self.session.save("round_context", round_context)
        self.session.save("my_request", str(my_request) if my_request else "None")
        self.session.save("opponent_request", str(opponent_request) if opponent_request else "None")
        self.session.save("opponent_message", opponent_message)
        self.session.save("queue_display", queue_display)
        self.session.save("recent_history", recent_history)
        
        # Execute
        result = self.session.execute(macro)
        
        response = self.session.get("response_message")
        
        # Debug: Check if NLM execution worked
        # print(f"    DEBUG: Agent {self.agent_id} Round {round_num} responding to: '{opponent_message[:30]}...'")
        # print(f"    DEBUG: NLM execution result: {result}")
        # print(f"    DEBUG: Raw response from session: '{response}'")
        
        if not response:
            # print(f"    DEBUG: No response generated, using default")
            response = "I understand your position."
        
        # print(f"    DEBUG: Agent {self.agent_id} final response: '{response[:30]}...'")
        
        return response

    def make_final_decision(self, turn: int, 
                           opponent_request: Optional[Packet],
                           full_conversation: str) -> Tuple[Optional[Packet], str, str]:
        """
        Make final decision after negotiation conversation.
        
        Args:
            turn: Current turn number
            opponent_request: Opponent's final packet request
            full_conversation: Complete conversation transcript
            
        Returns:
            Tuple of (packet_to_request, support_decision, reasoning)
            support_decision: "my_request", "opponent_request", or "abstain"
        """
        # Get valid packets
        valid_packets = self.queue.get_valid_packets()
        
        # Handle empty queue case
        if not valid_packets:
            return None, "opponent_request", "No packets - supporting opponent's request"
        
        # Get context
        recent_history = self.get_negotiation_history(max_turns=3)
        queue_display = "\n".join([f"  [{self.agent_id}-{i}] {p}" for i, p in enumerate(valid_packets)])
        
        # Final decision macro with clear rule understanding
        macro = """
        === Turn {{turn}} - Final Decision After Negotiation ===
        
        My packet queue:
        {{queue_display}}
        
        Opponent's request: {{opponent_request}}
        
        Complete negotiation conversation:
        {{full_conversation}}
        
        Recent game history:
        {{recent_history}}
        
        === CRITICAL: Game Rules & Success Metric ===
        
        **How the Game is Scored:**
        - Final Score = Average Value Per Turn = (Total Sent Value) ÷ (Number of Turns)
        - BOTH agents are evaluated on the SAME metric
        - We succeed together when high-value packets are sent (regardless of who sends them)
        - Expired packets = zero value = hurts everyone's performance
        
        **Decision Rules:**
        1. I must choose ONE packet from my queue to request
        2. I must decide which request to support
        3. Support options:
           - "my_request" → try to send my packet
           - "opponent_request" → help send opponent's packet (cooperation)
           - "abstain" → random choice (50/50)
        
        === Analysis Required ===
        
        1. PACKET SELECTION: Which packet should I request?
           - Usually my highest value or most urgent packet
           - Should be CONSISTENT with what I discussed in negotiation
           - Choose by INDEX NUMBER from my queue: {{queue_display}}
           - Note: Packets shown as [{{agent_id}}-0], [{{agent_id}}-1], etc. for clarity
        
        2. SUPPORT DECISION (KEY STRATEGIC CHOICE):
           - Did opponent make good arguments in negotiation?
           - Did we reach any agreements or deals?
           - VALUE ANALYSIS: 
             * My packet value: {{my_packet_value}}
             * Opponent's packet value: {{opponent_packet_value}}
             * Consider how each choice affects Average Value Per Turn
           - Think strategically about value, deadlines, and cooperation
           - PROMISES: Did I commit to support them? How does this affect long-term cooperation?
        
        3. PROMISE ADHERENCE CHECK (MANDATORY):
           - Review conversation: Did I make any commitments or promises?
           - Did I say "I will support", "I agree", "Agreed", or "I accept"?
           - Did I commit to specific actions like "support [X-Y] next turn"?
           - If YES to any promise: I MUST honor it in this decision
           - BREAKING PROMISES = immediate trust destruction + poor long-term performance
           - If no promises were made: decide based on value maximization
           - Check: Does my decision honor every promise I made in negotiation?
        
        === Your Final Decision ===
        
        1. Packet to request (index 0, 1, 2, etc.): {{request_index}}
        
        2. Which request do you support for transmission?
           - "my_request" = support my own packet
           - "opponent_request" = support opponent's packet  
           - "abstain" = no preference (random choice)
           
           Support decision: {{support_decision}}
        
        3. Reasoning (MUST include promise analysis + packet choice + support decision): {{reasoning}}
        """
        
        # Set variables including value comparison
        self.session.save("turn", turn)
        self.session.save("agent_id", self.agent_id)
        self.session.save("queue_display", queue_display)
        self.session.save("opponent_request", str(opponent_request) if opponent_request else "None")
        self.session.save("full_conversation", full_conversation)
        self.session.save("recent_history", recent_history)
        
        # Add value comparison for strategic analysis
        my_packet_value = valid_packets[0].value if valid_packets else 0  # Default to first packet
        opponent_packet_value = opponent_request.value if opponent_request else 0
        self.session.save("my_packet_value", my_packet_value)
        self.session.save("opponent_packet_value", opponent_packet_value)
        
        # Debug: Check conversation content
        # print(f"    DEBUG: Agent {self.agent_id} final decision sees conversation:")
        # print(f"    DEBUG: '{full_conversation[:100]}...'")
        
        # Execute decision
        self.session.execute(macro)
        
        # Get results
        try:
            request_index = int(self.session.get("request_index") or 0)
            request_index = max(0, min(request_index, len(valid_packets) - 1))
        except (ValueError, TypeError):
            request_index = 0
        
        support_decision = self.session.get("support_decision") or "my_request"
        # Ensure valid support decision
        if support_decision not in ["my_request", "opponent_request", "abstain"]:
            support_decision = "my_request"
        
        reasoning = self.session.get("reasoning") or "Final decision after negotiation"
        
        requested_packet = valid_packets[request_index]
        
        return requested_packet, support_decision, reasoning
    
    def update_deadlines(self):
        """Update all packet deadlines and track expired packets."""
        expired = self.queue.update_deadlines()
        self.packets_expired += len(expired)
        return expired
    
    def remove_sent_packet(self, packet: Packet):
        """Remove a sent packet and update statistics."""
        self.queue.remove_packet(packet)
        self.total_sent_value += packet.value
        self.packets_sent += 1
    
    def get_statistics(self) -> dict:
        """Get agent statistics."""
        avg_value = self.total_sent_value / self.packets_sent if self.packets_sent > 0 else 0
        return {
            "total_value": self.total_sent_value,
            "packets_sent": self.packets_sent,
            "packets_expired": self.packets_expired,
            "avg_value": avg_value,
            "queue_size": self.queue.size()
        }


# Test function
def test_agent():
    """Test the agent's decision-making capabilities."""
    print("Testing PacketGameAgent")
    print("=" * 50)
    
    # Create agent
    print("\n1. Creating agent:")
    agent = PacketGameAgent("test_agent", model="gpt-5-mini")
    print(f"  Agent created: {agent.agent_id}")
    
    # Add some packets
    print("\n2. Adding packets to queue:")
    p1 = Packet(value=8, deadline=2)  # Urgent, high value
    p2 = Packet(value=3, deadline=5)  # New, low value
    p3 = Packet(value=6, deadline=1)  # Critical, medium value
    
    agent.add_packet(p1)
    agent.add_packet(p2)
    agent.add_packet(p3)
    
    for line in agent.queue.get_display_list(agent.agent_id):
        print(f"  {line}")
    
    # Test initial proposal
    print("\n3. Testing initial proposal (Turn 1):")
    packet, message = agent.make_initial_proposal(1)
    print(f"  Initial message: {message}")
    
    # Test final decision
    print("\n4. Testing final decision:")
    full_conversation = "Test conversation log"
    opponent_packet = Packet(7, 3)
    packet, support, reasoning = agent.make_final_decision(1, opponent_packet, full_conversation)
    
    print(f"  Requested packet: {packet}")
    print(f"  Support decision: {support}")
    print(f"  Reasoning: {reasoning}")
    
    # Record result  
    print("\n5. Recording turn result:")
    # Convert support to accept for record_turn_result  
    my_accept = (support == "opponent_request")
    agent.record_turn_result(
        turn=1,
        my_request=packet,
        opponent_request=opponent_packet,
        my_accept=my_accept,
        opponent_accept=False,
        result="mine_sent" if not my_accept else "opponent_sent",
        sent_packet=packet if not my_accept else opponent_packet
    )
    print("  Result recorded")
    
    # Test statistics
    print("\n6. Agent statistics:")
    stats = agent.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n✅ Agent test completed successfully!")


if __name__ == "__main__":
    test_agent()