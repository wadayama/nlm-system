#!/usr/bin/env python3
"""Test history functionality with a simple game."""

from card_game_agent import CardGameAgent
import random

def test_history_simple():
    """Test history recording with 2 rounds."""
    print("Testing history functionality...")
    
    # Create agents
    agent_a = CardGameAgent("player_a")
    agent_b = CardGameAgent("player_b")
    
    # Set hands
    agent_a.set_hand([5, 7, 9])
    agent_b.set_hand([4, 6, 8])
    
    print(f"Player A hand: {agent_a.hand}")
    print(f"Player B hand: {agent_b.hand}")
    
    score_a = 0
    score_b = 0
    
    # Round 1
    print("\n=== Round 1 ===")
    
    card_a, reasoning_a = agent_a.select_card(1, score_a, score_b, agent_b.played_cards)
    print(f"A selects: {card_a} (Reasoning: {reasoning_a})")
    
    card_b, reasoning_b = agent_b.select_card(1, score_b, score_a, agent_a.played_cards)
    print(f"B selects: {card_b} (Reasoning: {reasoning_b})")
    
    # Determine winner
    if card_a > card_b:
        score_a += 1
        winner_name = "A"
        print(f"A wins ({card_a} > {card_b})")
    else:
        score_b += 1
        winner_name = "B"
        print(f"B wins ({card_b} > {card_a})")
    
    # Update hands and record history
    agent_a.play_card(card_a)
    agent_b.play_card(card_b)
    
    agent_a.record_round_result(1, card_a, card_b, "me" if winner_name == "A" else "opponent", score_a, score_b)
    agent_b.record_round_result(1, card_b, card_a, "me" if winner_name == "B" else "opponent", score_b, score_a)
    
    # Round 2 - with history
    print("\n=== Round 2 ===")
    print("A's history:", agent_a.get_round_history())
    print("B's history:", agent_b.get_round_history())
    
    card_a, reasoning_a = agent_a.select_card(2, score_a, score_b, agent_b.played_cards)
    print(f"A selects: {card_a} (Reasoning: {reasoning_a})")
    
    card_b, reasoning_b = agent_b.select_card(2, score_b, score_a, agent_a.played_cards)
    print(f"B selects: {card_b} (Reasoning: {reasoning_b})")
    
    print("\nHistory test completed!")

if __name__ == "__main__":
    test_history_simple()