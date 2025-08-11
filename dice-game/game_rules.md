# Dice Game Rules

## 🎯 Game Objective

Start with **20 chips** and reach **30 or more chips** by the end of **10 rounds** through betting on dice rolls.

## 🎲 Game Mechanics

### Basic Setup
- **Starting chips**: 20
- **Target chips**: 30+ 
- **Total rounds**: 10
- **Dice**: Standard 6-sided die (1-6)

### Betting Options

Each round, players can choose one of three actions:

#### 1. Even Bet (`even_bet`)
- **Bet on**: Even numbers (2, 4, 6)
- **Payout**: 
  - Rounds 1-9: **2x** your bet
  - Round 10: **4x** your bet

#### 2. Specific Number Bet (`specific_number_bet`)  
- **Bet on**: Exact number (1, 2, 3, 4, 5, or 6)
- **Payout**:
  - Rounds 1-9: **5x** your bet
  - Round 10: **10x** your bet

#### 3. Pass (`pass`)
- **Action**: Skip betting this round
- **Result**: No chips lost or gained

## 💰 Payout Examples

### Regular Rounds (1-9)
| Bet Type | Bet Amount | Win Condition | Payout | Net Result |
|----------|------------|---------------|---------|------------|
| Even bet | 5 chips | Dice shows 2,4,6 | 10 chips | +5 chips |
| Even bet | 5 chips | Dice shows 1,3,5 | 0 chips | -5 chips |
| Specific (3) | 2 chips | Dice shows 3 | 10 chips | +8 chips |
| Specific (3) | 2 chips | Dice shows 1,2,4,5,6 | 0 chips | -2 chips |

### Final Round (10)
| Bet Type | Bet Amount | Win Condition | Payout | Net Result |
|----------|------------|---------------|---------|------------|
| Even bet | 5 chips | Dice shows 2,4,6 | 20 chips | +15 chips |
| Specific (6) | 2 chips | Dice shows 6 | 20 chips | +18 chips |

## 🎮 Game Flow

1. **Round Start**: Display current assets and round number
2. **Decision Phase**: Choose action (even_bet, specific_number_bet, or pass)
3. **Betting Phase**: If betting, specify bet amount and target number
4. **Dice Roll**: Random 1-6 result determines outcome
5. **Payout**: Calculate winnings/losses and update assets
6. **Next Round**: Continue until 10 rounds complete or bankruptcy

## 🏆 Victory Conditions

### Victory ✅
- Complete all 10 rounds with **30 or more chips**

### Defeat ❌  
- Complete all 10 rounds with **less than 30 chips**
- **Bankruptcy**: Assets reach 0 at any point (game ends immediately)

## ⚠️ Important Rules

- Players must bet at least 1 chip and cannot bet more than their current assets
- For specific number bets, target number must be between 1 and 6
- Final round (round 10) offers double payouts for all bet types
- Game ends immediately if assets reach 0