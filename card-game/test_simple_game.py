#!/usr/bin/env python3
"""Simple test for debugging the card game."""

from card_game_agent import CardGameAgent
import random

def test_one_round():
    """Test just one round of the game."""
    print("Testing one round of High Card 5...")
    
    # Deal cards
    cards = list(range(1, 11))
    random.shuffle(cards)
    hand_a = sorted(cards[:5])
    hand_b = sorted(cards[5:])
    
    print(f"Player A hand: {hand_a}")
    print(f"Player B hand: {hand_b}")
    
    # Create agents
    print("\nCreating agents...")
    agent_a = CardGameAgent("player_a", model="gpt-5-mini")
    agent_b = CardGameAgent("player_b", model="gpt-5-mini")
    
    # Set hands
    agent_a.set_hand(hand_a)
    agent_b.set_hand(hand_b)
    
    # Play one round
    print("\n=== Round 1 ===")
    
    print("Player A selecting card...")
    card_a, reasoning_a = agent_a.select_card(1, 0, 0, [])
    print(f"Player A selected: {card_a}")
    print(f"Reasoning: {reasoning_a}")
    
    print("\nPlayer B selecting card...")
    card_b, reasoning_b = agent_b.select_card(1, 0, 0, [])
    print(f"Player B selected: {card_b}")
    print(f"Reasoning: {reasoning_b}")
    
    # Determine winner
    if card_a > card_b:
        print(f"\nPlayer A wins! ({card_a} > {card_b})")
    else:
        print(f"\nPlayer B wins! ({card_b} > {card_a})")
    
    print("\nTest completed!")

if __name__ == "__main__":
    test_one_round()