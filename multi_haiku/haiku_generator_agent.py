#!/usr/bin/env python3
"""HaikuGeneratorAgent - Generates haiku based on assigned theme"""

import sys
from pathlib import Path

# Add parent directory to path for NLM system imports

from agent_base import BaseAgent


class HaikuGeneratorAgent(BaseAgent):
    """Agent that generates haiku based on a specific theme"""
    
    def __init__(self, agent_id, theme_number, model=None, reasoning_effort="low"):
        super().__init__(agent_id, model=model, reasoning_effort=reasoning_effort)
        self.theme_number = theme_number
    
    def run(self):
        """Generate haiku based on assigned theme"""
        haiku_prompt = f"""
        # Haiku Generation Task
        
        Create a beautiful haiku poem based on the theme in {{@theme_{self.theme_number}}}.

        ## Traditional Haiku Principles
        - 5-7-5 syllable structure
        - Focus on a single moment or image
        - Include vivid, concrete imagery
        - Capture an emotion or feeling
        - Use simple, elegant language

        ## Instructions
        Create an authentic haiku that captures the essence and mood of the theme.

        ## Output
        Save the completed haiku to {{@haiku_{self.theme_number}}}
        """.strip()
        
        self.execute_macro(haiku_prompt)
        return True