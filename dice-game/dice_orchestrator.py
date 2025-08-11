#!/usr/bin/env python3
"""Dice Game Orchestrator - Execute strategic dice betting game with NLM agents"""

import sys
import argparse
import logging

from dice_game_agent import DiceGameAgent
from multi_agent_system import MultiAgentSystem


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Dice Game - Strategic betting game with natural language decision making'
    )
    
    parser.add_argument('--model', '-m', 
                       choices=['gpt-5', 'gpt-5-mini', 'gpt-5-nano', 'local', 'gpt-oss:20b'],
                       default='gpt-5-mini',
                       help='LLM model to use for decision making (default: gpt-5-mini)')
    
    parser.add_argument('--reasoning', '-r',
                       choices=['low', 'medium', 'high'], 
                       default='medium',
                       help='Reasoning effort level (default: medium)')
    
    parser.add_argument('--agents', '-a',
                       type=int,
                       default=1,
                       help='Number of agents to run in parallel (default: 1)')
    
    parser.add_argument('--verbose', '-v',
                       action='store_true',
                       help='Enable verbose output')
    
    return parser.parse_args()


def setup_logging(verbose=False):
    """Setup logging configuration"""
    # Set root logger level
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Suppress noisy HTTP request logs from httpx and openai
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('openai').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    
    # Keep our game logs visible
    logging.getLogger('dice_game_agent').setLevel(level)
    logging.getLogger('multi_agent_system').setLevel(level)


def create_dice_agents(num_agents, model, reasoning):
    """Create dice game agents with specified configuration"""
    agents = []
    
    for i in range(num_agents):
        agent_id = f"dice_player_{i+1}" if num_agents > 1 else "dice_player"
        agent = DiceGameAgent(agent_id, model=model)
        
        # Configure reasoning
        agent.session.set_reasoning_effort(reasoning)
        
        agents.append(agent)
        
    return agents


def run_game(agents):
    """Run dice game(s) with specified agents"""
    if len(agents) == 1:
        # Single agent game
        agent = agents[0]
        print(f"🎲 Starting Dice Game with {agent.agent_id}")
        print("="*50)
        
        result = agent.run()
        
        print("="*50)
        print(f"🏁 Final Result: {result['final_assets']} chips")
        print(f"Victory: {'✅ Yes' if result['target_reached'] else '❌ No'}")
        
    else:
        # Multiple agents - use MultiAgentSystem for parallel execution
        print(f"🎲 Starting {len(agents)} Parallel Games")
        print("="*50)
        
        system = MultiAgentSystem("dice_tournament")
        for agent in agents:
            system.add_agent(agent)
        
        print("🚀 Running games in parallel...")
        results = system.run_parallel()
        
        print("="*50)
        print("📊 Tournament Results:")
        victories = 0
        for agent in agents:
            final_assets = int(agent.session.get("assets") or 0)
            target_reached = final_assets >= 30
            if target_reached:
                victories += 1
            print(f"🎯 {agent.agent_id}: {final_assets} chips {'✅' if target_reached else '❌'}")
        
        print(f"\nTournament Summary: {victories}/{len(agents)} victories ({victories/len(agents)*100:.1f}%)")


def main():
    """Main orchestrator function"""
    args = parse_arguments()
    
    # Setup
    setup_logging(args.verbose)
    
    print("🎲 Dice Game Orchestrator")
    print("Strategic betting game with natural language AI")
    print(f"Model: {args.model} | Reasoning: {args.reasoning}")
    print()
    
    # Create agents
    agents = create_dice_agents(args.agents, args.model, args.reasoning)
    
    try:
        run_game(agents)
    except KeyboardInterrupt:
        print("\n\n⚠️ Game interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during game execution: {e}")
        sys.exit(1)
    
    print("\n🎯 Thank you for playing!")


if __name__ == "__main__":
    main()