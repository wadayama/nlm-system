#!/usr/bin/env python3
"""Game Orchestrator for High Card 5 - Manages two-player card game matches."""

import random
import argparse
from card_game_agent import CardGameAgent

# Strategy definitions
STRATEGIES = {
    'aggressive': """
    Round {{round_num}}/5. Score: Me {{my_score}}, Opponent {{opponent_score}}
    My hand: {{my_hand}}
    
    Previous rounds:
    {{round_history}}
    
    STRATEGY: Always play your HIGHEST card! Dominate early rounds.
    Look at the history - are you winning with this strategy?
    From {{my_hand}}, select the HIGHEST value card.
    
    Save the chosen card number to {{selected_card}}.
    Save reasoning like "Playing highest card X to maintain aggression" to {{reasoning}}.
    """,
    
    'conservative': """
    Round {{round_num}}/5. Score: Me {{my_score}}, Opponent {{opponent_score}}
    My hand: {{my_hand}}
    
    Previous rounds:
    {{round_history}}
    
    STRATEGY: Always play your LOWEST card! Save high cards for later.
    Look at the history - is opponent playing aggressively or conservatively?
    From {{my_hand}}, select the LOWEST value card.
    
    Save the chosen card number to {{selected_card}}.
    Save reasoning like "Conserving high cards, playing lowest X" to {{reasoning}}.
    """,
    
    'default': None  # Use agent's default strategy
}


def deal_cards():
    """Shuffle and deal cards 1-10 to two players."""
    cards = list(range(1, 11))
    random.shuffle(cards)
    player_a_hand = sorted(cards[:5])
    player_b_hand = sorted(cards[5:])
    return player_a_hand, player_b_hand


def display_round_header(round_num, agent_a, agent_b, score_a, score_b):
    """Display round header with current game state."""
    print(f"\n{'='*60}")
    print(f"Round {round_num}/5")
    print(f"{'='*60}")
    print(f"Player A - Hand: {agent_a.hand}  Score: {score_a}")
    print(f"Player B - Hand: {agent_b.hand}  Score: {score_b}")
    

def play_game(model="gpt-5-mini", verbose=True, strategy_a=None, strategy_b=None):
    """
    Play a complete game of High Card 5.
    
    Args:
        model: LLM model to use for both agents
        verbose: Whether to show detailed output
        strategy_a: Custom strategy macro for Player A (None = default)
        strategy_b: Custom strategy macro for Player B (None = default)
        
    Returns:
        dict: Game results
    """
    print("\n🎮 High Card 5 - Game Start")
    print("="*60)
    
    # Deal cards
    hand_a, hand_b = deal_cards()
    
    # Create agents with optional strategies
    agent_a = CardGameAgent("player_a", model=model, strategy_macro=strategy_a)
    agent_b = CardGameAgent("player_b", model=model, strategy_macro=strategy_b)
    
    # Set initial hands
    agent_a.set_hand(hand_a)
    agent_b.set_hand(hand_b)
    
    print(f"Player A dealt: {hand_a}")
    print(f"Player B dealt: {hand_b}")
    
    # Game state
    score_a = 0
    score_b = 0
    history = []
    
    # Play 5 rounds
    for round_num in range(1, 6):
        display_round_header(round_num, agent_a, agent_b, score_a, score_b)
        
        # Both players select cards
        print("\n[Player A thinking...]")
        card_a, reasoning_a = agent_a.select_card(
            round_num, score_a, score_b, agent_b.played_cards
        )
        if verbose:
            print(f"💭 {reasoning_a}")
        
        print("\n[Player B thinking...]")
        card_b, reasoning_b = agent_b.select_card(
            round_num, score_b, score_a, agent_a.played_cards
        )
        if verbose:
            print(f"💭 {reasoning_b}")
        
        # Show cards played
        print(f"\n⚔️  Player A plays: {card_a}")
        print(f"⚔️  Player B plays: {card_b}")
        
        # Determine winner
        if card_a > card_b:
            score_a += 1
            winner_name = "A"
            print(f"🏆 Player A wins this round! ({card_a} > {card_b})")
        else:
            score_b += 1
            winner_name = "B"
            print(f"🏆 Player B wins this round! ({card_b} > {card_a})")
        
        # Update hands
        agent_a.play_card(card_a)
        agent_b.play_card(card_b)
        
        # Record round results in both agents' history
        agent_a.record_round_result(
            round_num, card_a, card_b, 
            "me" if winner_name == "A" else "opponent",
            score_a, score_b
        )
        agent_b.record_round_result(
            round_num, card_b, card_a,
            "me" if winner_name == "B" else "opponent", 
            score_b, score_a
        )
        
        # Record history
        history.append({
            "round": round_num,
            "card_a": card_a,
            "card_b": card_b,
            "winner": winner_name,
            "reasoning_a": reasoning_a,
            "reasoning_b": reasoning_b
        })
        
        print(f"\nCurrent Score - A: {score_a}, B: {score_b}")
    
    # Final results
    print("\n" + "="*60)
    print("🏁 GAME OVER!")
    print("="*60)
    
    if score_a > score_b:
        print(f"🥇 Player A WINS {score_a}-{score_b}!")
        game_winner = "A"
    elif score_b > score_a:
        print(f"🥇 Player B WINS {score_b}-{score_a}!")
        game_winner = "B"
    else:
        print(f"🤝 DRAW {score_a}-{score_b}!")
        game_winner = "Draw"
    
    # Summary
    print(f"\nRound Summary:")
    for h in history:
        print(f"  Round {h['round']}: A({h['card_a']}) vs B({h['card_b']}) → {h['winner']} wins")
    
    return {
        "winner": game_winner,
        "score_a": score_a,
        "score_b": score_b,
        "history": history
    }


def main():
    """Main entry point with command line arguments."""
    parser = argparse.ArgumentParser(
        description='High Card 5 - Two-player strategic card game'
    )
    
    parser.add_argument('--model', '-m',
                       default='gpt-5-mini',
                       help='LLM model to use (default: gpt-5-mini)')
    
    parser.add_argument('--games', '-g',
                       type=int,
                       default=1,
                       help='Number of games to play (default: 1)')
    
    parser.add_argument('--quiet', '-q',
                       action='store_true',
                       help='Reduce output verbosity')
    
    parser.add_argument('--strategy-a', '-sa',
                       choices=['default', 'aggressive', 'conservative'],
                       default='default',
                       help='Strategy for Player A (default: default)')
    
    parser.add_argument('--strategy-b', '-sb',
                       choices=['default', 'aggressive', 'conservative'],
                       default='default',
                       help='Strategy for Player B (default: default)')
    
    args = parser.parse_args()
    
    # Get strategy macros
    strategy_a = STRATEGIES[args.strategy_a]
    strategy_b = STRATEGIES[args.strategy_b]
    
    # Show strategy info
    if args.strategy_a != 'default' or args.strategy_b != 'default':
        print(f"\n📋 Strategy Configuration:")
        print(f"  Player A: {args.strategy_a.upper()}")
        print(f"  Player B: {args.strategy_b.upper()}")
    
    # Statistics tracking
    stats = {"A": 0, "B": 0, "Draw": 0}
    
    # Play games
    for game_num in range(1, args.games + 1):
        if args.games > 1:
            print(f"\n{'#'*60}")
            print(f"GAME {game_num}/{args.games}")
            print('#'*60)
        
        result = play_game(
            model=args.model, 
            verbose=not args.quiet,
            strategy_a=strategy_a,
            strategy_b=strategy_b
        )
        stats[result["winner"]] += 1
    
    # Show statistics for multiple games
    if args.games > 1:
        print("\n" + "="*60)
        print("TOURNAMENT RESULTS")
        print("="*60)
        print(f"Games played: {args.games}")
        print(f"Player A wins: {stats['A']} ({100*stats['A']/args.games:.1f}%)")
        print(f"Player B wins: {stats['B']} ({100*stats['B']/args.games:.1f}%)")
        print(f"Draws: {stats['Draw']} ({100*stats['Draw']/args.games:.1f}%)")


if __name__ == "__main__":
    main()