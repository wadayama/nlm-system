#!/usr/bin/env python3
"""Card Game Agent for High Card 5 - Strategic card playing with natural language reasoning."""

from nlm_interpreter import NLMSession


class CardGameAgent:
    """
    Agent for playing High Card 5 card game.
    Uses natural language reasoning to select cards strategically.
    """
    
    def __init__(self, agent_id: str, model: str = "gpt-5-mini", strategy_macro: str = None):
        """
        Initialize card game agent.
        
        Args:
            agent_id: Unique identifier for this agent
            model: LLM model to use for decision making
            strategy_macro: Custom decision macro for card selection strategy
        """
        self.agent_id = agent_id
        self.session = NLMSession(namespace=f"card_game_{agent_id}", model=model)
        self.hand = []  # Current cards in hand
        self.played_cards = []  # Cards already played
        self.strategy_macro = strategy_macro  # Custom strategy if provided
        
    def set_hand(self, cards):
        """Set the agent's initial hand of cards."""
        self.hand = sorted(cards.copy())
        self.played_cards = []
        self.session.clear_local()  # Clear previous game state
        
    def select_card(self, round_num, my_score, opponent_score, opponent_played):
        """
        Select a card to play using LLM reasoning.
        
        Args:
            round_num: Current round number (1-5)
            my_score: Current score for this player
            opponent_score: Current score for opponent
            opponent_played: List of cards opponent has played
            
        Returns:
            tuple: (selected_card, reasoning)
        """
        if not self.hand:
            raise ValueError("No cards left in hand!")
            
        # Save current game state
        self.session.save("round_num", round_num)
        self.session.save("my_hand", self.hand)
        self.session.save("my_score", my_score) 
        self.session.save("opponent_score", opponent_score)
        self.session.save("opponent_played", opponent_played)
        self.session.save("my_played", self.played_cards)
        
        # Get round history for strategic analysis
        history = self.get_round_history(max_rounds=4)  # Last 4 rounds for context
        self.session.save("round_history", history)
        
        # Use custom strategy macro if provided, otherwise use default
        if self.strategy_macro:
            macro = self.strategy_macro
        else:
            # Default balanced strategy with history
            macro = """
            Round {{round_num}}/5. Score: Me {{my_score}}, Opponent {{opponent_score}}
            My hand: {{my_hand}}
            
            Previous rounds:
            {{round_history}}
            
            Analyze the game history and opponent's playing pattern.
            Consider:
            - What cards has opponent played (high/low pattern)?
            - Are they aggressive or conservative?
            - What strategy should I use based on current score?
            
            Choose exactly ONE card from {{my_hand}} to play.
            
            Save the chosen card number to {{selected_card}}.
            Save your strategic reasoning to {{reasoning}}.
            """
        
        # Execute decision
        self.session.execute(macro)
        
        # Get results
        selected_card = self.session.get("selected_card")
        reasoning = self.session.get("reasoning")
        
        # Validate and convert card
        try:
            card = int(selected_card)
            if card not in self.hand:
                # Fallback: play first available card
                print(f"Warning: Card {card} not in hand {self.hand}, using {self.hand[0]}")
                card = self.hand[0]
                reasoning = f"Fallback selection due to invalid card. {reasoning}"
        except (ValueError, TypeError):
            # Fallback: play first available card
            print(f"Warning: Could not parse '{selected_card}' as card, using {self.hand[0]}")
            card = self.hand[0]
            reasoning = "Fallback selection due to parsing error."
            
        # Ensure reasoning is not empty
        if not reasoning:
            reasoning = f"Playing {card} from hand {self.hand}."
            
        return card, reasoning
    
    def play_card(self, card):
        """Remove a card from hand and add to played cards."""
        if card in self.hand:
            self.hand.remove(card)
            self.played_cards.append(card)
        else:
            raise ValueError(f"Card {card} not in hand!")
    
    def record_round_result(self, round_num, my_card, opponent_card, winner, my_score, opponent_score):
        """
        Record the result of a round for historical analysis.
        
        Args:
            round_num: Round number (1-5)
            my_card: Card I played this round
            opponent_card: Card opponent played this round
            winner: "me" or "opponent"
            my_score: My score after this round
            opponent_score: Opponent's score after this round
        """
        # Create detailed round entry
        round_entry = f"Round {round_num}: I played {my_card}, Opponent played {opponent_card}, {winner} won, Score: {my_score}-{opponent_score}"
        
        # Store in session using append for history accumulation
        self.session.append("round_history", round_entry)
    
    def get_round_history(self, max_rounds=None):
        """
        Get the round history for strategic analysis.
        
        Args:
            max_rounds: Maximum number of recent rounds to return (None = all)
            
        Returns:
            str: Formatted round history
        """
        if max_rounds:
            history = self.session.get_tail("round_history", n_lines=max_rounds)
        else:
            history = self.session.get("round_history") or ""
        
        if not history:
            return "No previous rounds"
        
        return history
            
    def get_status(self):
        """Get current agent status."""
        return {
            "agent_id": self.agent_id,
            "hand": self.hand,
            "played": self.played_cards
        }


# Simple test function
def test_agent():
    """Test the agent with a sample scenario."""
    print("Testing CardGameAgent...")
    
    # Create agent
    agent = CardGameAgent("test_player")
    
    # Set initial hand
    agent.set_hand([2, 4, 6, 8, 10])
    print(f"Agent hand: {agent.hand}")
    
    # Test card selection
    print("\nTesting card selection for Round 1...")
    card, reasoning = agent.select_card(
        round_num=1,
        my_score=0,
        opponent_score=0,
        opponent_played=[]
    )
    
    print(f"Selected card: {card}")
    print(f"Reasoning: {reasoning}")
    
    # Play the card
    agent.play_card(card)
    print(f"Hand after playing: {agent.hand}")
    print(f"Played cards: {agent.played_cards}")
    
    # Test another round
    print("\nTesting card selection for Round 2...")
    card, reasoning = agent.select_card(
        round_num=2,
        my_score=0,
        opponent_score=1,
        opponent_played=[3]
    )
    
    print(f"Selected card: {card}")
    print(f"Reasoning: {reasoning}")
    
    print("\nAgent test completed!")


if __name__ == "__main__":
    test_agent()