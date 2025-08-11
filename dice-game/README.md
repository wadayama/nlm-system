# 🎲 Dice Game - Strategic Betting Agent

An advanced NLM (Natural Language Macro) agent that plays a strategic dice betting game using natural language decision-making processes.

## 🎯 Game Overview

**Objective**: Start with 20 chips and reach 30+ chips in 10 rounds through strategic betting.

### Betting Options
- **Even Bet**: Bet on even numbers (2,4,6) - 50% chance, 2x payout (4x final round)
- **Specific Number Bet**: Bet on exact number (1-6) - 16.7% chance, 5x payout (10x final round)
- **Pass**: Skip betting - No risk, no reward

## 🚀 Quick Start

```bash
# Navigate to dice-game directory
cd dice-game

# Run a single game with default settings
uv run dice_orchestrator.py

# Run with specific model
uv run dice_orchestrator.py --model gpt-5-mini

# Run multiple parallel games
uv run dice_orchestrator.py --agents 5

# Enable variable watching for real-time monitoring
uv run dice_orchestrator.py --watch
```

## 🎮 Game Features

### 🧠 Natural Language Decision Making
The agent uses sophisticated natural language reasoning:

```
"Currently have 18 chips in round 7. Need 12 more chips in 4 rounds. 
Final round offers double payouts, so I should be conservative now 
and save bigger risks for round 10. Betting 3 chips on even numbers 
gives good odds while preserving most assets."
```

### 📊 Strategic Analysis
- **Risk Assessment**: Evaluates win probability vs. potential rewards
- **Resource Management**: Tracks chip count and remaining rounds
- **Adaptive Strategy**: Adjusts betting based on game situation
- **Final Round Optimization**: Leverages double payouts in round 10

### 🔍 Real-time Monitoring
- Watch game variables with `--watch` flag
- Monitor decision-making process
- Track agent reasoning and outcomes

## 🛠️ Usage Examples

### Single Game
```bash
# Basic game with reasoning explanation
uv run dice_orchestrator.py --model gpt-5-mini --reasoning medium --verbose
```

### Multiple Agent Tournament
```bash
# Parallel tournament with 5 agents
uv run dice_orchestrator.py --agents 5
```

### Development & Debugging
```bash
# Monitor variables with external watcher (run in separate terminal)
uv run watch_variables.py --format table

# Run game with verbose output
uv run dice_orchestrator.py --verbose
```

## 📋 Command Line Options

```
usage: dice_orchestrator.py [-h] [--model {gpt-5,gpt-5-mini,gpt-5-nano,local,gpt-oss:20b}]
                            [--reasoning {low,medium,high}] [--games GAMES]
                            [--agents AGENTS] [--verbose] [--watch]

Options:
  --model, -m      LLM model for decision making (default: gpt-5-mini)
  --reasoning, -r  Reasoning effort level (default: medium)
  --agents, -a     Number of parallel agents (default: 1)
  --verbose, -v    Enable detailed output
```

## 🎲 Game Mechanics

### Payout Structure
| Bet Type | Win Condition | Regular Rounds | Final Round |
|----------|---------------|----------------|-------------|
| Even bet | Dice shows 2,4,6 | 2x payout | 4x payout |
| Specific bet | Exact number match | 5x payout | 10x payout |
| Pass | N/A | No change | No change |

### Victory Conditions
- ✅ **Victory**: 30+ chips after 10 rounds
- ❌ **Defeat**: <30 chips after 10 rounds
- 💔 **Bankruptcy**: 0 chips at any point (immediate game over)

### Expected Value Analysis
- **Even bet regular**: 50% expected return
- **Even bet final**: 150% expected return
- **Specific bet regular**: -17% expected return
- **Specific bet final**: 67% expected return

## 🏗️ Architecture

### Core Components

**DiceGameAgent** (`dice_game_agent.py`)
- Inherits from NLM `BaseAgent`
- Natural language decision-making
- Strategic game logic
- Variable state management

**Dice Orchestrator** (`dice_orchestrator.py`)  
- Game execution controller
- Multi-agent coordination
- Performance analytics
- Real-time monitoring

### Integration with NLM System
- Uses `NLMSession` for variable management
- Leverages `MultiAgentSystem` for parallel execution
- Integrates with `watch_variables.py` for monitoring
- Follows NLM agent architecture patterns

## 📊 Example Game Output

```
🎲 Starting Dice Game with dice_player
==================================================
=== Round 1/10 ===
Current assets: 20 chips
Agent decision: even_bet
Bet amount: 4 chips
Reasoning: Conservative start, good odds with even bet
Dice result: 4
✅ Win! Payout: +8 chips
New asset total: 24 chips

=== Round 2/10 ===
...

🏁 Game Complete!
Final result: 32 chips
Status: victory
Victory: ✅ Yes
```

## 🧪 Testing

```bash
# Test basic agent functionality
uv run dice_game_agent.py

# Test orchestrator with local model
uv run dice_orchestrator.py --model local --verbose

# Performance testing with multiple runs
uv run dice_orchestrator.py --games 100 --model gpt-5-nano
```

## 📈 Performance Statistics

The system tracks comprehensive game statistics:
- Win rate across multiple games
- Average final chip count
- Best/worst performance
- Strategy effectiveness analysis

## 🎯 Strategic Insights

### Optimal Strategy Patterns
1. **Conservative Early Game**: Use even bets in rounds 1-7
2. **Calculated Mid-Game**: Assess chip position in rounds 8-9
3. **Final Round Aggression**: Leverage 2x payout multiplier in round 10
4. **Risk Management**: Never bet more than 50% of assets except in final round

### Common AI Decision Patterns
- **Risk Averse**: Prefers even bets, consistent small gains
- **Opportunistic**: Uses specific bets when far from target
- **Adaptive**: Changes strategy based on chip count and remaining rounds

## 🔧 Development

### Key Files
- `dice_game_agent.py` - Core game agent implementation
- `dice_orchestrator.py` - Game execution and coordination
- `game_rules.md` - Detailed game rules and mechanics
- `README.md` - This file

### Integration Points
- Extends NLM `BaseAgent` class
- Uses standard NLM variable management
- Compatible with NLM monitoring tools
- Follows NLM session architecture

## 🤖 Natural Language Examples

The agent makes decisions using natural language reasoning:

### Conservative Strategy
> "Round 3 with 22 chips. Target is achievable with steady even bets. 
> Betting 3 chips on even numbers for consistent growth."

### Aggressive Strategy  
> "Round 9 with only 25 chips. Need 5+ more chips and final round 
> offers double payouts. Betting 8 chips on specific number 6 for 
> 10x payout potential."

### Risk Management
> "Round 6 with 15 chips. Below starting amount, need to be careful. 
> Passing this round to preserve chips for better opportunities."

## 📚 Further Reading

- [Game Rules](game_rules.md) - Detailed mechanics and strategy analysis
- [NLM System Docs](../docs/) - Core NLM system documentation
- [API Reference](../docs/api_reference.md) - NLM API documentation

---

This dice game demonstrates the power of natural language macro systems for creating intelligent, reasoning-based agents that can adapt their strategies dynamically!