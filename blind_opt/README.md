# 🔍 Blind Optimization - LLM-Driven Function Minimization

An advanced NLM (Natural Language Macro) agent that performs blind optimization using natural language decision-making to find the minimum of unknown functions.

## 🎯 Optimization Overview

**Objective**: Find the global minimum of an unknown function f(x,y) using only function evaluations, with no gradient information or function structure knowledge.

### Available Test Functions
- **Sphere**: Simple convex function with minimum at (4, -3)
- **Rosenbrock**: Classic "banana" function with narrow valley at (1, 1)  
- **Himmelblau**: Multi-modal function with 4 global minima
- **Complex**: Oscillating function with interactions at (1.5, -0.8)

## 🚀 Quick Start

```bash
# Navigate to blind optimization directory
cd blind_opt

# Run basic sphere function optimization
uv run optimizer.py

# Run with different test function
uv run optimizer.py --function rosenbrock

# Use faster model with more evaluations
uv run optimizer.py --model gpt-5-mini --evaluations 15

# Test challenging complex function
uv run optimizer.py --function complex --evaluations 20
```

## 🧠 LLM-Driven Optimization Features

### 🔍 Natural Language Reasoning
The agent uses sophisticated natural language reasoning for point selection:

```
"Previous points show the function value decreases as we move toward 
(4, -3). The gradient seems to point in that direction. I should try 
a point closer to (4, -3) but slightly offset to confirm the pattern 
and avoid getting stuck in a local minimum."
```

### 📊 Experience-Based Learning
- **Context Accumulation**: Builds experience from previous evaluations
- **Pattern Recognition**: Identifies trends in function behavior
- **Adaptive Exploration**: Balances exploitation vs exploration
- **Historical Memory**: Uses 8-line rolling context window

### 🎯 Search Strategy
- **Initial Exploration**: Random starting point selection
- **Gradient Estimation**: Infers function slope from samples
- **Local Search**: Fine-tunes around promising regions  
- **Global Awareness**: Avoids premature convergence

## 🛠️ Usage Examples

### Basic Optimization
```bash
# Sphere function with 10 evaluations
uv run optimizer.py --function sphere --evaluations 10
```

### Advanced Testing
```bash
# Complex multi-modal function with more evaluations
uv run optimizer.py --function himmelblau --model gpt-5-mini --evaluations 20
```

### Model Comparison
```bash
# Test with different LLM models
uv run optimizer.py --model gpt-oss:20b --function rosenbrock
uv run optimizer.py --model gpt-5-mini --function rosenbrock
```

## 📋 Command Line Options

```
usage: optimizer.py [-h] [--function {sphere,rosenbrock,himmelblau,complex}]
                    [--model MODEL] [--evaluations EVALUATIONS]

Options:
  --function, -f   Test function to optimize (default: sphere)
  --model, -m      LLM model for decision making (default: gpt-5-mini)  
  --evaluations, -e Number of function evaluations (default: 10)
```

## 🎯 Test Functions

### Function Characteristics
| Function | Minimum | Value | Difficulty | Properties |
|----------|---------|-------|------------|------------|
| Sphere | (4, -3) | 0.0 | Easy | Convex, single minimum |
| Rosenbrock | (1, 1) | 0.0 | Hard | Narrow valley, slow convergence |
| Himmelblau | (3, 2) | 0.0 | Medium | Multiple global minima |
| Complex | (1.5, -0.8) | 0.0 | Hard | Oscillations, interactions |

### Expected Performance
- **Sphere**: Should converge quickly (5-8 evaluations)
- **Rosenbrock**: Requires patience due to narrow valley  
- **Himmelblau**: May find any of the 4 global minima
- **Complex**: Challenging due to local minima from oscillations

## 🏗️ Architecture

### Core Components

**OptimizationAgent** (`optimization_agent.py`)
- Inherits from NLM session management
- Natural language point selection
- Experience context accumulation
- Adaptive reasoning prompts

**Optimizer Orchestrator** (`optimizer.py`)  
- Function evaluation controller
- Performance tracking and reporting
- Command-line interface
- Results visualization

**Test Functions** (`test_functions.py`)
- Mathematical function implementations
- True minimum specifications
- Evaluation interface
- Performance benchmarking

### Integration with NLM System
- Uses `NLMSession` for variable management
- Leverages `append()` for experience accumulation
- Uses `get_tail()` for context retrieval
- Follows NLM macro syntax `{{variable}}`

## 📊 Example Optimization Run

```
🎯 Blind Optimization
Function: sphere
Model: gpt-5-mini
Evaluations: 10
📊 Target (unknown to agent):
   Optimal point: (4.000, -3.000)
   Optimal value: 0.000000
--------------------------------------------------

--- Evaluation 1/10 ---
Point: (2.300, -1.500)
Value: 5.140000
Reasoning: Starting with a central point to explore the function landscape

--- Evaluation 2/10 ---  
Point: (4.200, -2.800)
Value: 0.080000
Reasoning: Moving toward lower values, this direction looks promising

--- Evaluation 3/10 ---
Point: (3.950, -3.100)
Value: 0.012500
Reasoning: Very close! Fine-tuning around the minimum region

...

==================================================
🏁 Optimization Results:
📈 Best found: (4.010, -2.985) → 0.000325
🎯 True optimum: (4.000, -3.000) → 0.000000  
📏 Distance to optimum: 0.018385
🌟 Excellent! Very close to true optimum!
```

## 🧪 Testing

### Agent Testing
```bash
# Test optimization agent directly
uv run optimization_agent.py

# Test individual test functions
uv run test_functions.py
```

### Performance Benchmarking
```bash
# Compare different functions
for func in sphere rosenbrock himmelblau complex; do
    echo "Testing $func..."
    uv run optimizer.py --function $func --evaluations 15
done
```

## 📈 Optimization Strategies

### LLM Decision Patterns

#### Exploration Phase
> "First evaluation - I'll try a point near the center of the search 
> space to get initial information about the function landscape."

#### Exploitation Phase  
> "Previous points show the minimum is likely around (4, -3). I'll 
> search more precisely in that neighborhood to find the exact optimum."

#### Balanced Strategy
> "Found a good region but should verify it's global minimum. Testing 
> a distant point to confirm I haven't missed a better region."

### Adaptive Behavior
- **Conservative**: Small steps around best known point
- **Explorative**: Large jumps to unexplored regions
- **Gradient-Following**: Movement based on inferred slope
- **Pattern-Based**: Using experience to predict good directions

## 🔬 Advanced Features

### Experience Context Management
The agent maintains rolling context of recent evaluations:

```python
experience_entry = f"Tried ({point[0]:.2f}, {point[1]:.2f}) → Value: {value:.4f}. Reasoning: {reasoning}"
self.session.append("experience_context", experience_entry)
```

### Prompt Engineering for Exploration
```python
"IMPORTANT: Explore new areas! Avoid repeating the same point unless 
you have strong evidence it's optimal. Try different regions to find 
the global minimum."
```

### Multi-Function Capability
Easy switching between optimization challenges:
- Mathematical benchmarks (Rosenbrock, Himmelblau)
- Custom objective functions
- Real-world optimization problems (with function interface)

## 🎓 Educational Value

### Learning Objectives
1. **LLM Reasoning**: See how language models approach optimization
2. **Blind Search**: Understand gradient-free optimization challenges  
3. **Experience Learning**: Observe how context improves decisions
4. **Strategy Adaptation**: Watch agents adapt to different functions

### Key Concepts Demonstrated
- **Natural Language Programming**: Using English for algorithm logic
- **Meta-Learning**: Learning to learn from limited function evaluations
- **Exploration vs Exploitation**: Balancing search strategies
- **Context Window Management**: Handling limited memory effectively

## 📚 Further Reading

- [NLM System Documentation](../docs/) - Core NLM system documentation
- [Multi-Agent Guide](../docs/multi_agent_guide.md) - Building agent systems
- [API Reference](../docs/api_reference.md) - NLM API documentation

---

This blind optimization tutorial demonstrates the power of natural language macro systems for creating intelligent optimization agents that can reason about unknown functions and adapt their search strategies dynamically!