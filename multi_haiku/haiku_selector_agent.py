#!/usr/bin/env python3
"""HaikuSelectorAgent - Selects the best haiku from 4 candidates"""

import sys
from pathlib import Path

# Add parent directory to path for NLM system imports

from agent_base import BaseAgent


class HaikuSelectorAgent(BaseAgent):
    """Agent that selects the best haiku from 4 generated candidates"""
    
    def __init__(self, agent_id="haiku_selector", model=None, reasoning_effort="low"):
        super().__init__(agent_id, model=model, reasoning_effort=reasoning_effort)
    
    def run(self):
        """Select the best haiku from 4 candidates"""
        selector_prompt = """
        # Haiku Selection Task
        
        Evaluate and select the best haiku from the following 4 candidates based on their themes and quality.

        ## Evaluation Criteria
        Consider the following aspects when selecting the best haiku:
        - **Technical Excellence**: Adherence to 5-7-5 syllable structure
        - **Imagery Strength**: Vivid, concrete, and evocative imagery
        - **Emotional Resonance**: Depth of feeling and mood capture
        - **Originality**: Unique perspective and fresh approach
        - **Theme Integration**: How well the haiku captures its theme's essence
        - **Aesthetic Beauty**: Overall poetic elegance and flow

        ## Candidates to Evaluate
        
        **Candidate 1** (Theme: {{@theme_1}}):
        {{@haiku_1}}
        
        **Candidate 2** (Theme: {{@theme_2}}):
        {{@haiku_2}}
        
        **Candidate 3** (Theme: {{@theme_3}}):
        {{@haiku_3}}
        
        **Candidate 4** (Theme: {{@theme_4}}):
        {{@haiku_4}}

        ## Selection Process
        1. Analyze each haiku against the evaluation criteria
        2. Consider the strength of theme-haiku pairing
        3. Select the single best haiku that demonstrates the highest overall quality
        4. Provide brief reasoning for your selection

        ## Output Instructions
        - Save the selected best haiku to {{@best_haiku}}
        - Save the corresponding theme to {{@best_theme}}
        - Save the candidate number (1-4) to {{@best_haiku_number}}
        - Save your selection reasoning to {{@selection_reasoning}}
        """.strip()
        
        self.execute_macro(selector_prompt)
        return True