# Multi-Haiku Generator

A sophisticated multi-agent haiku generation system showcasing natural language macro orchestration with the NLM system.

## Overview

This example demonstrates advanced NLM patterns through a collaborative haiku generation workflow:

1. **Theme Generation**: AI creates an inspiring haiku theme
2. **Multiple Haiku Creation**: Three different haiku variations are generated
3. **Intelligent Selection**: AI evaluates and selects the best haiku based on imagery and emotion

## Architecture

### Agent Coordination
- **Theme Generator Agent**: Creates compelling themes for haiku inspiration
- **Haiku Generator Agent**: Produces multiple haiku variations from themes
- **Haiku Selector Agent**: Evaluates and selects the highest quality haiku

### Key NLM Features Demonstrated
- **Multi-agent coordination** through shared global variables
- **Natural language variable operations** using `{{@variable}}` syntax  
- **Sequential workflow orchestration** with intelligent handoffs
- **Model flexibility** supporting both OpenAI and local LLMs

## Quick Start

### Prerequisites
- Ensure you have the NLM system installed (see main README.md)
- OpenAI API key (for OpenAI models) or local LLM setup

### Running the Multi-Haiku System

```bash
# Navigate to multi-haiku directory
cd multi_haiku

# Quick test with local model (no API key needed)
uv run simple_orchestrator.py --model local

# With OpenAI models (requires API key)
uv run simple_orchestrator.py --model gpt-5-mini
uv run simple_orchestrator.py --model gpt-5

# View generation progress
uv run simple_orchestrator.py --model gpt-5-mini --verbose
```

## Expected Output

```
🎨 Generated theme: "Morning dew on cherry blossoms"
📝 Generated 3 haiku variations:
   1. Cherry petals fall / Morning dew catches first light / Spring's gentle whisper
   2. Dew drops hold sunrise / On pink blossoms, nature's tears / Dawn's delicate gift  
   3. Blossoms wear diamonds / Each dewdrop reflects new day / Silent beauty speaks
🏆 Selected best haiku: #2 - "Exceptional imagery combining visual and emotional elements"
```

## Model Support

### OpenAI Models
- `gpt-5` - Premium quality, rich creativity
- `gpt-5-mini` - Balanced performance and cost
- `gpt-5-nano` - Fast and economical

### Local Models  
- `local` or `gpt-oss:20b` - Standard local LLM
- `gpt-oss:120b` - Enhanced local LLM (requires capable hardware)

## Technical Implementation

### Variable Flow
```python
# Theme generation
{{@theme_1}}, {{@theme_2}}, {{@theme_3}} = generated themes

# Haiku creation  
{{@haiku_1}}, {{@haiku_2}}, {{@haiku_3}} = haiku variations

# Selection process
{{@selected_haiku}} = best haiku
{{@selection_reason}} = evaluation reasoning
```

### Agent Communication Pattern
1. **Theme Generator** → Saves themes to global variables
2. **Haiku Generators** → Read themes, create haiku variations
3. **Selector Agent** → Evaluates all haiku, selects winner
4. **Orchestrator** → Coordinates workflow and presents results

## Customization

### Adding More Themes
```python
# Modify simple_orchestrator.py
theme_count = 5  # Generate 5 themes instead of 3
```

### Custom Haiku Styles
```python
# Edit haiku_generator_agent.py
style_instruction = "Create a haiku in traditional 5-7-5 syllable format about {{@theme}}"
```

### Different Selection Criteria
```python
# Modify haiku_selector_agent.py 
selection_criteria = "humor and wit" # Instead of imagery and emotion
```

## Learning Opportunities

This example illustrates several advanced NLM concepts:

- **Multi-agent orchestration**: How agents can work together seamlessly
- **Global variable sharing**: Cross-agent communication patterns
- **Natural language programming**: Replacing traditional APIs with intuitive instructions
- **Flexible model integration**: Same code works with different LLM backends
- **Workflow automation**: Complex creative processes automated through NLM

## Troubleshooting

### No Output Generated
- Check your API key setup (for OpenAI models)
- Verify local LLM is running (for local models)
- Ensure all dependencies are installed with `uv sync`

### Low Quality Results
- Try a more capable model (gpt-5 instead of gpt-5-nano)
- Increase reasoning effort in agent configurations
- Check that themes are being generated successfully

### Performance Issues  
- Use local models for faster iteration
- Reduce the number of haiku variations generated
- Check system resources for large models

## Related Examples

- **[Dice Game](../dice-game/)** - Interactive game mechanics with NLM
- **[Agent Examples](../src/agent_examples.py)** - Additional agent patterns

## Contributing

This example serves as a template for building your own multi-agent NLM applications. Feel free to:

- Extend with additional agent types
- Implement different creative workflows  
- Add new evaluation criteria
- Create variations for other creative tasks

---

*This example showcases the power of natural language programming for creative AI applications.*