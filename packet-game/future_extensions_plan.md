# Packet Game Future Extensions Design Document

## Overview

Design for extending the current fixed 3-slot system to an advanced packet scheduling system with variable slot counts and future prediction capabilities. This will develop the system into a research platform where LLMs perform temporal reasoning and strategic planning.

## Current System Status

### Current Constraints
- **Fixed 3 slots/turn**: Same resource constraints every turn
- **Single-turn optimization**: Decisions considering only current state
- **Deterministic environment**: Predictable system behavior

### Motivation for Extensions
- **Improved realism**: Reflecting wireless channel variations
- **Strategic thinking**: Decision-making considering future states
- **Increased complexity**: Evaluation of more advanced AI reasoning

## Extension Design Details

### 1. Variable Slot System

#### 1.1 Channel Condition Modeling
```python
class ChannelCondition:
    """Models wireless channel conditions"""
    
    def __init__(self):
        self.quality = 0.5        # Channel quality (0.0-1.0)
        self.noise_level = 0.3    # Noise level (0.0-1.0)
        self.congestion = 0.4     # Congestion level (0.0-1.0)
        self.weather_factor = 1.0 # Weather impact (0.5-1.5)
    
    def update_markov_chain(self):
        """State transitions using Markov chain"""
        # Time-series changes in quality (trend + random)
        trend = random.uniform(-0.1, 0.1)
        noise = random.uniform(-0.05, 0.05)
        self.quality = max(0.0, min(1.0, self.quality + trend + noise))
        
        # Daily congestion variation patterns
        time_factor = math.sin(turn * 0.1) * 0.2  # Periodic variation
        self.congestion = max(0.0, min(1.0, 0.5 + time_factor + noise))
    
    def get_available_slots(self) -> int:
        """Determine slot count based on channel conditions"""
        base_slots = 3
        
        # Quality-based increase/decrease (0-2 slot bonus)
        quality_bonus = int(self.quality * 2)
        
        # Congestion-based reduction (0-2 slot penalty)
        congestion_penalty = int(self.congestion * 2)
        
        # Noise-based random variation
        noise_variation = random.randint(-1, 1) if self.noise_level > 0.7 else 0
        
        total_slots = base_slots + quality_bonus - congestion_penalty + noise_variation
        return max(1, min(6, total_slots))  # Constrained to 1-6 slots
```

#### 1.2 Dynamic Slot Allocation
- **Minimum guarantee**: 1 slot (system continuity)
- **Maximum limit**: 6 slots (computational complexity management)
- **Probability distribution**: 70% for 2-4 slots, 30% for 1,5,6 slots

### 2. Future Prediction System

#### 2.1 Types of Prediction Information
```python
class FuturePrediction:
    """Future situation prediction information"""
    
    def __init__(self, horizon: int = 3):
        self.horizon = horizon  # Prediction range (number of turns)
        self.slot_predictions = []    # Slot count predictions
        self.confidence_levels = []   # Prediction confidence
        self.trend_analysis = ""      # Trend analysis
    
    def generate_predictions(self, current_channel: ChannelCondition):
        """Generate future predictions from current situation"""
        predictions = []
        
        for t in range(1, self.horizon + 1):
            # Probabilistic prediction using Markov chain
            prob_dist = self._calculate_slot_probabilities(current_channel, t)
            predictions.append({
                'turn': t,
                'slot_distribution': prob_dist,
                'most_likely': max(prob_dist, key=prob_dist.get),
                'confidence': self._calculate_confidence(t)
            })
        
        return predictions
    
    def _calculate_slot_probabilities(self, channel, turns_ahead):
        """Probability distribution of slot counts for specified turns ahead"""
        # Probabilistic transition from current quality
        base_quality = channel.quality
        uncertainty = 0.1 * turns_ahead  # Uncertainty increases with time
        
        probabilities = {}
        for slots in range(1, 7):
            # Quality-based probability calculation
            optimal_quality = (slots - 1) / 5.0  # Ideal quality corresponding to slot count
            distance = abs(base_quality - optimal_quality)
            prob = math.exp(-distance / uncertainty)
            probabilities[slots] = prob
        
        # Normalization
        total = sum(probabilities.values())
        return {k: v/total for k, v in probabilities.items()}
```

#### 2.2 Prediction Information Presentation to LLM
```
=== FUTURE PREDICTION INFORMATION ===

Current Channel Status:
  Quality: 0.75 (Good)
  Congestion: 0.40 (Moderate)
  Available Slots: 4

Next Turn Prediction (Confidence: 85%):
  2 slots: 15%
  3 slots: 40%
  4 slots: 35%
  5 slots: 10%

2 Turns Ahead Prediction (Confidence: 65%):
  1 slot: 10%
  2 slots: 25%
  3 slots: 35%
  4 slots: 25%
  5 slots: 5%

Channel Trend: Quality declining, congestion increasing
```

### 3. Phased Implementation Plan

#### Phase 1: Simple Variable Slots ✅ **COMPLETED** (August 2024)
**Goal**: Introduction of basic variability
```python
# Completed Items
1. SlotManager class implementation ✓
2. VariableSlotScheduler class creation ✓  
3. Variable slot-compatible LLM prompt implementation ✓
4. 1-turn lookahead prediction feature ✓
5. Custom probability distribution support ✓

# Implementation Files
- variable_slot_scheduler.py (Complete)
- SlotManager: Probability-based slot management
- VariableSlotScheduler: Inherits from LLMDirectScheduler

# Confirmed Changes
- LLM adapts to available slot counts
- Strategic decisions using next-turn predictions
- Reasoning like "With only 2 slots now and 4 slots next turn..."
```

#### Phase 2: Prediction System Integration (Implementation period: 2-3 days)
**Goal**: Decision-making considering future information
```python
# Implementation Items
1. Complete FuturePrediction class implementation
2. Markov chain-based prediction algorithms
3. Integration of prediction information into LLM prompts
4. Time-series data management system

# Expected Changes
- Emergence of strategic decisions (wait vs immediate execution)
- Response patterns to uncertainty
- Observation of risk management behaviors
```

#### Phase 3: Advanced Strategic Analysis (Implementation period: 3-4 days)
**Goal**: Evaluation of complex temporal reasoning
```python
# Implementation Items
1. Multi-period performance evaluation system
2. Correlation analysis between prediction accuracy and decision quality
3. Multi-scenario comparison functionality
4. Automatic detection of strategy patterns

# Expected Changes
- Establishment of long-term optimization strategies
- Quantification of prediction information utilization
- Discovery of adaptive learning patterns
```

### 4. Technical Implementation Details

#### 4.1 New Class Structure
```python
# Extended main class
class AdvancedLLMScheduler(LLMDirectScheduler):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.channel = ChannelCondition()
        self.predictor = FuturePrediction(horizon=3)
        self.strategy_history = []  # Strategy decision history
    
    def get_dynamic_context(self):
        """Generate dynamic context information"""
        current_slots = self.channel.get_available_slots()
        predictions = self.predictor.generate_predictions(self.channel)
        return {
            'current_slots': current_slots,
            'predictions': predictions,
            'trend': self.channel.get_trend_analysis()
        }
```

#### 4.2 Extended LLM Prompt Design
```python
def create_strategic_prompt(self, context):
    return f"""
=== Strategic Packet Selection Task ===

Current Situation:
Available Slots: {context['current_slots']}
{self.format_state_for_llm()}

Future Predictions:
{self.format_predictions(context['predictions'])}

Strategic Considerations:
1. Current transmission vs waiting for better future conditions
2. Certainty vs optimality trade-off
3. Risk management under deadline constraints

Your Task:
Select packets for the current {context['current_slots']} slots.
Consider future predictions and make optimal decisions from both short-term and long-term perspectives.

Include the following in your reasoning:
- Why you made this choice
- How you utilized future predictions
- Comparison with alternative options
"""
```

#### 4.3 New Evaluation Metrics
```python
class AdvancedMetrics:
    """Extended evaluation metrics"""
    
    def calculate_adaptation_score(self, decisions, slot_variations):
        """Adaptation score to variable conditions"""
        # Evaluate flexibility of decisions to slot variations
        pass
    
    def calculate_prediction_utilization(self, decisions, predictions):
        """Prediction information utilization score"""
        # How much future predictions were reflected in actual decisions
        pass
    
    def calculate_risk_management_score(self, decisions, uncertainties):
        """Risk management quality score"""
        # Validity of decisions under uncertainty
        pass
    
    def calculate_temporal_optimization(self, multi_turn_performance):
        """Temporal optimization score"""
        # Effectiveness of strategic decisions across multiple turns
        pass
```

### 5. Expected Effects

#### 5.1 Evolution of LLM Behavior Patterns
**Current Behavior**:
- Deadline priority (deadline ≤ 3)
- Overflow management
- Single-shot value maximization

**Expected Post-Extension Behavior**:
- **Conditional postponement**: "Hold high-value packets until 6-slot turn"
- **Risk hedging**: "Choose safe and certain options due to high uncertainty"
- **Timing optimization**: "Aim for good conditions 3 turns ahead, be conservative now"
- **Composite strategies**: "Build portfolio of certain and speculative portions"

#### 5.2 Research Value
- **Temporal reasoning ability**: Analysis of LLM future prediction utilization patterns
- **Uncertainty handling**: Evaluation of decision quality based on probabilistic information
- **Adaptive learning**: Observation of strategy modification processes in dynamic environments
- **Explainability**: Maintaining interpretability of complex decisions

#### 5.3 Technical Challenges
**Complexity Management**:
- Limits on information amount understandable by LLM
- Balance between computational cost and prediction accuracy
- Real-time processing requirements

**Evaluation Systems**:
- Transition from single metrics to multi-dimensional evaluation
- Methods for short-term evaluation of long-term strategies
- Separation of prediction accuracy and decision quality

## Implementation Status

### ✅ Completed Items (Phase 1)
1. **SlotManager implementation**: Variable slot management complete
2. **VariableSlotScheduler**: Variable slots with prediction complete
3. **LLM prompt adaptation**: Next-turn prediction information integration complete
4. **Operation testing**: Normal operation confirmed

### Usage
```bash
# Default uniform distribution (25% each)
uv run variable_slot_scheduler.py

# Custom distribution examples
uv run variable_slot_scheduler.py -p 0.1 0.2 0.5 0.2  # 3-slot centered
uv run variable_slot_scheduler.py -p 0.4 0.1 0.1 0.4  # Extreme variation
```

### Natural Language Strategy Integration
```bash
# Strategy instruction examples
uv run variable_slot_scheduler.py -s "Deadline priority, never let packets expire!"
uv run llm_direct_scheduler.py -s "High-value packets first, maximize total value"
uv run variable_slot_scheduler.py -s "Balance all queues, avoid penalties"
```

### Gradual Development Items
1. **Prediction algorithm implementation**: 2-3 hours
2. **Strategy analysis system**: 4-5 hours
3. **Comprehensive evaluation framework**: 6-8 hours

## Summary

This extension transforms the packet game system from simple scheduling to an advanced strategic AI decision platform. It provides a valuable research environment for comprehensive evaluation of LLM temporal reasoning, risk management, and adaptive learning capabilities.

Through phased implementation, new insights can be gained at each phase, ultimately enabling observation of highly interesting AI behavior patterns.

The addition of natural language strategy instructions further enhances the system's flexibility and research value, allowing users to guide LLM behavior through intuitive commands while observing how the AI interprets and adapts human intent to system constraints.

---
*Created: August 17, 2025*  
*Ready for immediate implementation upon next session*