#!/usr/bin/env python3
"""Test different card playing strategies."""

import random
from card_game_agent import CardGameAgent

# Define different strategy macros
AGGRESSIVE_STRATEGY = """
Round {{round_num}}/5. Score: Me {{my_score}}, Opponent {{opponent_score}}
My hand: {{my_hand}}
Opponent has played: {{opponent_played}}

STRATEGY: Play aggressively! Always play your HIGHEST available card.
This dominates early rounds and forces opponent to waste their high cards.

From {{my_hand}}, select the HIGHEST value card.

Save the chosen card number to {{selected_card}}.
Save reasoning like "Playing highest card X to dominate early" to {{reasoning}}.
"""

CONSERVATIVE_STRATEGY = """
Round {{round_num}}/5. Score: Me {{my_score}}, Opponent {{opponent_score}}
My hand: {{my_hand}}
Opponent has played: {{opponent_played}}

STRATEGY: Play conservatively! Always play your LOWEST available card.
Save high cards for crucial later rounds.

From {{my_hand}}, select the LOWEST value card.

Save the chosen card number to {{selected_card}}.
Save reasoning like "Conserving high cards, playing lowest X" to {{reasoning}}.
"""

ADAPTIVE_STRATEGY = """
Round {{round_num}}/5. Score: Me {{my_score}}, Opponent {{opponent_score}}
My hand: {{my_hand}}
Opponent has played: {{opponent_played}}

STRATEGY: Adapt to the game state!
- If ahead in score: play conservatively (lower cards)
- If behind: play aggressively (higher cards)
- If tied: play medium cards

Choose a card from {{my_hand}} based on the current score situation.

Save the chosen card number to {{selected_card}}.
Save your adaptive reasoning to {{reasoning}}.
"""


def play_strategy_game(strategy_a=None, strategy_b=None, strategy_names=("Default", "Default")):
    """
    Play a game with specified strategies.
    
    Args:
        strategy_a: Strategy macro for Player A (None = default)
        strategy_b: Strategy macro for Player B (None = default)
        strategy_names: Tuple of strategy names for display
    """
    print(f"\n🎮 High Card 5 - Strategy Test")
    print(f"Player A Strategy: {strategy_names[0]}")
    print(f"Player B Strategy: {strategy_names[1]}")
    print("="*60)
    
    # Deal cards
    cards = list(range(1, 11))
    random.shuffle(cards)
    hand_a = sorted(cards[:5])
    hand_b = sorted(cards[5:])
    
    # Create agents with strategies
    agent_a = CardGameAgent("player_a", strategy_macro=strategy_a)
    agent_b = CardGameAgent("player_b", strategy_macro=strategy_b)
    
    # Set initial hands
    agent_a.set_hand(hand_a)
    agent_b.set_hand(hand_b)
    
    print(f"Player A dealt: {hand_a}")
    print(f"Player B dealt: {hand_b}")
    
    # Game state
    score_a = 0
    score_b = 0
    
    # Play 5 rounds
    for round_num in range(1, 6):
        print(f"\n=== Round {round_num}/5 ===")
        print(f"Score: A:{score_a}, B:{score_b}")
        
        # Both players select cards
        card_a, reasoning_a = agent_a.select_card(
            round_num, score_a, score_b, agent_b.played_cards
        )
        print(f"[A - {strategy_names[0]}] {reasoning_a}")
        
        card_b, reasoning_b = agent_b.select_card(
            round_num, score_b, score_a, agent_a.played_cards
        )
        print(f"[B - {strategy_names[1]}] {reasoning_b}")
        
        # Show cards played
        print(f"Cards: A plays {card_a}, B plays {card_b}")
        
        # Determine winner
        if card_a > card_b:
            score_a += 1
            print(f"→ Round winner: A")
        else:
            score_b += 1
            print(f"→ Round winner: B")
        
        # Update hands
        agent_a.play_card(card_a)
        agent_b.play_card(card_b)
    
    # Final results
    print("\n" + "="*60)
    if score_a > score_b:
        print(f"🏆 PLAYER A ({strategy_names[0]}) WINS {score_a}-{score_b}!")
    elif score_b > score_a:
        print(f"🏆 PLAYER B ({strategy_names[1]}) WINS {score_b}-{score_a}!")
    else:
        print(f"🤝 DRAW {score_a}-{score_b}!")
    
    return score_a, score_b


def main():
    """Test different strategy combinations."""
    
    # Test 1: Aggressive vs Default
    print("\n" + "#"*60)
    print("# TEST 1: Aggressive vs Default")
    print("#"*60)
    play_strategy_game(
        strategy_a=AGGRESSIVE_STRATEGY,
        strategy_b=None,  # Default strategy
        strategy_names=("Aggressive", "Default")
    )
    
    # Test 2: Conservative vs Default
    print("\n" + "#"*60)
    print("# TEST 2: Conservative vs Default")
    print("#"*60)
    play_strategy_game(
        strategy_a=CONSERVATIVE_STRATEGY,
        strategy_b=None,  # Default strategy
        strategy_names=("Conservative", "Default")
    )
    
    # Test 3: Aggressive vs Conservative
    print("\n" + "#"*60)
    print("# TEST 3: Aggressive vs Conservative")
    print("#"*60)
    play_strategy_game(
        strategy_a=AGGRESSIVE_STRATEGY,
        strategy_b=CONSERVATIVE_STRATEGY,
        strategy_names=("Aggressive", "Conservative")
    )
    
    # Test 4: Adaptive vs Aggressive
    print("\n" + "#"*60)
    print("# TEST 4: Adaptive vs Aggressive")
    print("#"*60)
    play_strategy_game(
        strategy_a=ADAPTIVE_STRATEGY,
        strategy_b=AGGRESSIVE_STRATEGY,
        strategy_names=("Adaptive", "Aggressive")
    )


if __name__ == "__main__":
    main()