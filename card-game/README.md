# 🃏 High Card 5 - Strategic Card Battle Game

An advanced NLM (Natural Language Macro) system showcasing intelligent two-player card battles with history-enhanced strategic decision making.

## 🎯 Game Overview

**Objective**: Win the majority of 5 rounds by playing cards strategically against an opponent using natural language reasoning and historical analysis.

### Game Rules
- **Players**: 2 players (A and B)
- **Deck**: Cards numbered 1-10 (no duplicates)
- **Hand Size**: 5 cards per player
- **Rounds**: 5 simultaneous card battles
- **Scoring**: Higher card wins the round, best 3 out of 5 wins the game

## 🚀 Quick Start

```bash
# Navigate to card-game directory
cd card-game

# Run a basic game with default strategies
uv run game_orchestrator.py

# Test aggressive vs conservative strategies
uv run game_orchestrator.py --strategy-a aggressive --strategy-b conservative

# Run multiple games for statistical analysis
uv run game_orchestrator.py --strategy-a aggressive --games 10

# Use different LLM model
uv run game_orchestrator.py --model gpt-5-nano
```

## 🎮 Game Features

### 🧠 History-Enhanced Decision Making
Agents analyze previous rounds to predict opponent behavior:

```
"Round 3: Looking at history, opponent played 6 then 9 - seems aggressive early.
I'll play 4 to conserve my high cards (8,10) for rounds 4-5 when they 
might have used up their strongest cards."
```

### 📊 Strategic Intelligence
- **Pattern Recognition**: Analyzes opponent's high/low card preferences
- **Adaptive Planning**: Adjusts strategy based on current score and remaining rounds
- **Risk Assessment**: Balances card conservation vs. immediate wins
- **Counter-Strategy**: Develops responses to opponent's playing patterns

### 🎯 Multiple Strategy Types
- **Aggressive**: Always plays highest available card to dominate early
- **Conservative**: Always plays lowest card to save high cards for later
- **Default**: Balanced approach with historical analysis and adaptive planning

## 🛠️ Usage Examples

### Strategy Comparison
```bash
# Aggressive domination strategy vs balanced analysis
uv run game_orchestrator.py --strategy-a aggressive --strategy-b default

# Conservative patience vs aggressive pressure
uv run game_orchestrator.py --strategy-a conservative --strategy-b aggressive

# Multiple games to test strategy effectiveness
uv run game_orchestrator.py --strategy-a aggressive --strategy-b conservative --games 20
```

### Tournament Analysis
```bash
# Run statistical comparison
uv run game_orchestrator.py --games 50 --strategy-a aggressive --strategy-b default

# Expected output:
# TOURNAMENT RESULTS
# ==================
# Games played: 50
# Player A wins: 32 (64.0%)
# Player B wins: 18 (36.0%)
# Draws: 0 (0.0%)
```

## 📋 Command Line Options

```
usage: game_orchestrator.py [-h] [--model MODEL] [--games GAMES] [--quiet]
                             [--strategy-a {default,aggressive,conservative}]
                             [--strategy-b {default,aggressive,conservative}]

Options:
  --model, -m       LLM model for decision making (default: gpt-5-mini)
  --games, -g       Number of games to play (default: 1)
  --quiet, -q       Reduce output verbosity
  --strategy-a, -sa Strategy for Player A (default: default)
  --strategy-b, -sb Strategy for Player B (default: default)
```

## 🎯 Strategy Analysis

### Aggressive Strategy
- **Philosophy**: "Strike first, strike hard"
- **Tactics**: Always plays highest card to win early rounds
- **Strengths**: Dominates weak opponents, builds psychological pressure
- **Weaknesses**: Vulnerable to card counting and late-game reversals

### Conservative Strategy  
- **Philosophy**: "Patience wins wars"
- **Tactics**: Always plays lowest card to preserve high cards
- **Strengths**: Strong finish, unpredictable hand strength
- **Weaknesses**: May fall too far behind early to recover

### Default Strategy (Adaptive)
- **Philosophy**: "Know your enemy and know yourself"
- **Tactics**: Uses history analysis and situation-aware planning
- **Strengths**: Learns opponent patterns, adapts to circumstances
- **Weaknesses**: More complex, may overthink simple situations

## 📊 Example Game Output

```
🎮 High Card 5 - Game Start
============================================================
Player A dealt: [2, 4, 7, 9, 10]
Player B dealt: [1, 3, 5, 6, 8]

============================================================
Round 1/5
============================================================
Player A - Hand: [2, 4, 7, 9, 10]  Score: 0
Player B - Hand: [1, 3, 5, 6, 8]   Score: 0

[Player A thinking...]
💭 Playing highest card 10 to maintain aggression

[Player B thinking...]
💭 No previous rounds. Playing 3 conservatively to test opponent while saving high cards.

⚔️  Player A plays: 10
⚔️  Player B plays: 3
🏆 Player A wins this round! (10 > 3)

Current Score - A: 1, B: 0

============================================================
Round 2/5
============================================================
[Player A thinking...]
💭 Playing highest card 9 to maintain aggression

[Player B thinking...]
💭 Opponent played 10 in round 1 - very aggressive. I need to counter with higher cards now.

⚔️  Player A plays: 9
⚔️  Player B plays: 8
🏆 Player A wins this round! (9 > 8)

...
```

## 🏗️ Architecture

### Core Components

**CardGameAgent** (`card_game_agent.py`)
- History-enhanced decision making using `record_round_result()`
- Strategic pattern analysis with `get_round_history()`
- Configurable strategy macros for different playing styles
- Natural language reasoning with game state awareness

**Game Orchestrator** (`game_orchestrator.py`)
- Two-player battle management and coordination
- Strategy selection and configuration
- Round progression and scoring
- Statistical analysis for multiple games

**Strategy System**
- Pluggable strategy architecture using custom macros
- Built-in aggressive, conservative, and adaptive strategies
- History-aware decision making for all strategies

### Integration with NLM System
- Uses `NLMSession` for variable management and state persistence
- Leverages `append()` for history accumulation and pattern analysis
- Employs natural language macros for strategic reasoning
- Follows NLM agent architecture with configurable strategies

## 🧪 Testing and Development

### Quick Test
```bash
# Test strategy system with sample comparison
uv run strategy_test.py

# Single game validation
uv run game_orchestrator.py --strategy-a aggressive --strategy-b conservative
```

### Performance Analysis
```bash
# Statistical validation over multiple games
uv run game_orchestrator.py --games 100 --strategy-a aggressive --strategy-b default

# Model comparison
uv run game_orchestrator.py --model gpt-5-nano --games 50
uv run game_orchestrator.py --model gpt-5-mini --games 50
```

## 🎓 Educational Value

### Learning Objectives
1. **Game Theory**: Understanding strategic interactions and opponent modeling
2. **History Analysis**: How past information informs future decisions
3. **Natural Language Strategy**: Expressing complex game logic in plain English
4. **Adaptive AI**: Building agents that learn and counter opponent patterns

### Key Concepts Demonstrated
- **Strategic Thinking**: Multi-round planning and resource management
- **Pattern Recognition**: Identifying and exploiting opponent weaknesses
- **Risk Management**: Balancing immediate gains vs. long-term positioning
- **Natural Language Programming**: Using English for complex game logic

## 📈 Strategy Effectiveness Research

Early testing suggests:
- **Aggressive vs Conservative**: Aggressive typically wins 60-70% (quick decisive victories)
- **Default vs Aggressive**: Default adapts and wins 55-65% (learns aggressive patterns)
- **Default vs Conservative**: Default wins 70-80% (exploits predictable low-card plays)

## 📚 Further Reading

- [Game Rules](rule.md) - Detailed game mechanics and examples
- [NLM System Documentation](../docs/) - Core NLM system documentation
- [Multi-Agent Guide](../docs/multi_agent_guide.md) - Building agent systems

---

This card game demonstrates the power of history-enhanced natural language agents for strategic gameplay, pattern recognition, and adaptive decision making in competitive environments!