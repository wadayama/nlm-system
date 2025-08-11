#!/usr/bin/env python3
"""Dice Game Agent for NLM System - Strategic betting agent with natural language decision making."""

import random
import logging

from agent_base import BaseAgent


class DiceGameAgent(BaseAgent):
    """
    A strategic dice game agent that uses natural language macros to make betting decisions.
    
    Game Rules:
    - Start with 20 chips, goal: reach 30+ chips in 10 rounds
    - Betting options:
      * even_bet: Win on even numbers (2,4,6) - 2x payout (4x final round)
      * specific_number_bet: Win on exact number - 5x payout (10x final round) 
      * pass: Skip betting
    """
    
    def __init__(self, agent_id: str = "dice_player"):
        super().__init__(agent_id)
        
        # Suppress noisy HTTP logs for cleaner game output
        logging.getLogger('httpx').setLevel(logging.WARNING)
        logging.getLogger('openai').setLevel(logging.WARNING)
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        
        self.initial_chips = 20
        self.target_chips = 30
        self.total_rounds = 10
        self.current_round = 0
        self.logger.info(f"Initialized DiceGameAgent: {agent_id}")
        
    def initialize_game(self):
        """Initialize game variables (clear previous state first)"""
        # Clear all local variables to start fresh
        self.session.clear_local()
        self.logger.info("Cleared previous game state")
        
        # Initialize new game variables
        self.session.save("assets", self.initial_chips)
        self.session.save("round", 0)
        self.session.save("game_status", "initialized")
        self.session.save("target_chips", self.target_chips)
        self.session.save("total_rounds", self.total_rounds)
        self.logger.info("Game initialized: 20 chips, 10 rounds, target 30+ chips")
        
    def roll_dice(self):
        """Roll a fair 6-sided dice"""
        return random.randint(1, 6)
    
    def validate_agent_action(self):
        """Validate agent's action and return parsed values"""
        action = self.session.get("action")
        bet_amount_str = str(self.session.get("bet_amount") or "0")
        target_number_str = str(self.session.get("target_number") or "0")
        current_assets = int(self.session.get("assets") or 0)
        
        # Validate action
        if action not in ["even_bet", "specific_number_bet", "pass"]:
            self.session.save("game_status", f"ERROR: Invalid action '{action}'")
            return None
        
        # Parse and validate bet_amount
        try:
            bet_amount = int(bet_amount_str) if bet_amount_str else 0
        except ValueError:
            self.session.save("game_status", f"ERROR: Invalid bet_amount '{bet_amount_str}'")
            return None
        
        # Validate bet_amount range
        if action != "pass" and (bet_amount < 1 or bet_amount > current_assets):
            self.session.save("game_status", f"ERROR: Invalid bet_amount {bet_amount} (assets: {current_assets})")
            return None
        
        # Parse and validate target_number
        target_number = None
        if action == "specific_number_bet":
            try:
                target_number = int(target_number_str) if target_number_str else 0
            except ValueError:
                self.session.save("game_status", f"ERROR: Invalid target_number '{target_number_str}'")
                return None
                
            if target_number < 1 or target_number > 6:
                self.session.save("game_status", f"ERROR: Invalid target_number {target_number} (must be 1-6)")
                return None
        
        return {
            "action": action,
            "bet_amount": bet_amount,
            "target_number": target_number,
            "current_assets": current_assets
        }
    
    def calculate_payout(self, action, bet_amount, target_number, dice_result, is_final_round=False):
        """Calculate payout based on betting action and dice result"""
        multiplier = 2 if is_final_round else 1
        
        if action == "pass":
            return 0
        elif action == "even_bet":
            if dice_result % 2 == 0:  # Even numbers: 2, 4, 6
                # Win: get 2x payout, but lose original bet, so net = bet_amount * (2-1) = bet_amount
                return bet_amount * 1 * multiplier
            else:
                return -bet_amount
        elif action == "specific_number_bet":
            if dice_result == target_number:
                # Win: get 5x payout, but lose original bet, so net = bet_amount * (5-1) = bet_amount * 4
                return bet_amount * 4 * multiplier
            else:
                return -bet_amount
        
        return 0
    
    def _format_action_description(self, action, bet_amount, target_number):
        """Format action description for round summary"""
        if action == "pass":
            return "PASS"
        elif action == "even_bet":
            return f"EVEN({bet_amount})"
        elif action == "specific_number_bet":
            return f"NUM{target_number}({bet_amount})"
        else:
            return f"{action.upper()}({bet_amount})"
    
    def make_decision(self):
        """Use natural language macros to make betting decisions"""
        import time
        start_time = time.time()
        
        current_round = int(self.session.get("round") or 0)
        current_assets = int(self.session.get("assets") or 0)
        target = int(self.session.get("target_chips") or 30)
        remaining_rounds = self.total_rounds - current_round
        
        # Set current values in session for macro to access
        self.session.save("current_round", current_round)
        self.session.save("current_assets", current_assets)
        self.session.save("target_chips", target)
        self.session.save("remaining_rounds", remaining_rounds)
        
        prep_time = time.time() - start_time
        self.logger.debug(f"Decision prep time: {prep_time:.2f}s")
        
        # Natural language macro for decision making
        decision_prompt = """
        You are playing a dice betting game. Your mission is critical.
        
        WIN CONDITION: You MUST have 30+ chips after round 10 to WIN.
        Current status:
        - Round: {{current_round}}/10
        - Assets: {{current_assets}} chips (CURRENT)
        - Target: 30 chips (REQUIRED TO WIN)
        - Need: {{target_chips}} - {{current_assets}} = MORE CHIPS NEEDED
        - Remaining rounds: {{remaining_rounds}}
        
        Game rules:
        - Even bet: Win on dice 2,4,6 - pays 2x (4x in final round)
        - Specific number bet: Win on exact number - pays 5x (10x in final round)  
        - Pass: Skip betting - no risk, no reward
        - Final round (round 10) has double payouts
        - Bankruptcy (0 chips) = immediate game over
        
        Remember: The goal is to REACH 30+ chips, not to maximize chips.
        Analyze the situation and decide:
        - Action: even_bet, specific_number_bet, or pass
        - Bet amount: 1 to {{current_assets}} chips
        - Target number: 1-6 (if specific_number_bet)
        - Decision reason: Brief explanation
        
        Save your decisions to:
        - {{action}} - your chosen action
        - {{bet_amount}} - amount to bet
        - {{target_number}} - target number if specific bet
        - {{decision_reason}} - brief explanation of your reasoning
        """
        
        # Execute decision-making macro
        llm_start = time.time()
        print(f"  🔄 Calling LLM for decision...")
        result = self.execute_macro(decision_prompt)
        llm_time = time.time() - llm_start
        
        total_time = time.time() - start_time
        print(f"  ⏱️  Decision timing: LLM={llm_time:.1f}s, Total={total_time:.1f}s")
        
        return result
    
    def play_round(self):
        """Play a single round of the dice game"""
        current_round = int(self.session.get("round") or 0) + 1
        self.session.save("round", current_round)
        current_assets = int(self.session.get("assets") or 0)
        
        # Round separator for readability
        print("─" * 60)
        
        # Check for bankruptcy
        if current_assets <= 0:
            bankruptcy_msg = f"R{current_round} | BANKRUPTCY | Assets: 0 | GAME_OVER"
            print(bankruptcy_msg)
            self.session.save("game_status", bankruptcy_msg)
            return False
        
        # Show current situation
        remaining_rounds = self.total_rounds - current_round + 1
        chips_needed = max(0, self.target_chips - current_assets)
        print(f"  📊 Round {current_round}/{self.total_rounds} | Assets: {current_assets} chips | Need: {chips_needed} more | Rounds left: {remaining_rounds}")
        
        # Make decision using natural language
        self.make_decision()
        
        # Validate the decision
        validation = self.validate_agent_action()
        if not validation:
            error_msg = f"R{current_round} | ERROR: Invalid action | GAME_OVER"
            print(error_msg)
            self.session.save("game_status", error_msg)
            return False
        
        action = validation["action"]
        bet_amount = validation["bet_amount"]
        target_number = validation["target_number"]
        
        # Display agent's reasoning
        decision_reason = self.session.get("decision_reason") or "No reasoning provided"
        print(f"  💭 Agent thinking: {decision_reason}")
        
        # Show the decision made
        if action == "pass":
            print(f"  🤔 Decision: PASS (skip betting)")
        elif action == "even_bet":
            print(f"  🎯 Decision: Bet {bet_amount} chips on EVEN numbers (2,4,6)")
        elif action == "specific_number_bet":
            print(f"  🎯 Decision: Bet {bet_amount} chips on NUMBER {target_number}")
        
        print(f"  🎲 Rolling dice...")  # Create suspense
        
        # Roll dice
        dice_result = self.roll_dice()
        self.session.save("dice_result", dice_result)
        
        # Calculate payout
        is_final_round = (current_round == self.total_rounds)
        payout = self.calculate_payout(action, bet_amount, target_number, dice_result, is_final_round)
        
        # Update assets
        new_assets = current_assets + payout
        self.session.save("assets", new_assets)
        
        # Create round summary in original format
        action_desc = self._format_action_description(action, bet_amount, target_number)
        result_desc = "WIN" if payout > 0 else "LOSE" if payout < 0 else "PASS"
        final_flag = " (FINAL ROUND)" if current_round == self.total_rounds else ""
        
        round_summary = f"R{current_round} | {action_desc} | Dice:{dice_result} | {result_desc} | Assets:{current_assets}→{new_assets}{final_flag}"
        print(round_summary)
        self.session.save("game_status", round_summary)
        
        # Check for bankruptcy
        if new_assets <= 0:
            bankruptcy_msg = f"R{current_round} | BANKRUPTCY | Assets: 0 | GAME_OVER"
            print(bankruptcy_msg)
            self.session.save("game_status", bankruptcy_msg)
            return False
        
        # Check win condition
        if current_round == self.total_rounds:
            if new_assets >= self.target_chips:
                victory_msg = f"GAME END: VICTORY! Final: {new_assets} chips"
                print(victory_msg)
                self.session.save("game_status", victory_msg)
            else:
                shortage = self.target_chips - new_assets
                defeat_msg = f"GAME END: DEFEAT. Final: {new_assets} chips (short by {shortage})"
                print(defeat_msg)
                self.session.save("game_status", defeat_msg)
        
        return True
    
    def run(self):
        """Main game execution"""
        self.set_status("starting")
        
        # Initialize game
        self.initialize_game()
        
        # Game start summary
        print(f"GAME START: {self.initial_chips} chips, Goal: {self.target_chips}+ chips")
        self.session.save("game_status", f"GAME START: {self.initial_chips} chips, Goal: {self.target_chips}+ chips")
        self.set_status("playing")
        
        # Play all rounds
        for round_num in range(1, self.total_rounds + 1):
            success = self.play_round()
            if not success:
                break
                
            # Brief pause for readability (optional)
            # import time
            # time.sleep(0.5)
        
        # Final status
        final_assets = int(self.session.get("assets") or 0)
        game_status = self.session.get("game_status") or "unknown"
        
        self.set_status("completed")
        
        return {
            "final_assets": final_assets,
            "game_status": game_status,
            "target_reached": final_assets >= self.target_chips
        }


if __name__ == "__main__":
    # Quick test run with local model
    agent = DiceGameAgent("test_player")
    agent.session.model = "gpt-oss:20b"  # Use local model for faster testing
    result = agent.run()
    print(f"Game result: {result}")