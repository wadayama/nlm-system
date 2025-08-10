#!/usr/bin/env python3
"""ThemeGeneratorAgent - Generates 4 unusual themes for haiku poetry"""

import sys
from pathlib import Path

# Add parent directory to path for NLM system imports

from agent_base import BaseAgent


class ThemeGeneratorAgent(BaseAgent):
    """Agent that generates 4 unusual themes for haiku poetry"""
    
    def __init__(self, agent_id="theme_generator", model=None, reasoning_effort="low"):
        super().__init__(agent_id, model=model, reasoning_effort=reasoning_effort)
    
    def run(self):
        """Generate 4 unusual themes and store in own session"""
        theme_prompt = """
        # Theme Generation Task
        
        Generate 4 diverse and evocative themes for haiku poetry that will inspire exceptional verse.

        ## Theme Requirements
        Create themes that are:
        - Unusual and unexpected, avoiding clichéd topics
        - Rich in sensory potential (visual, auditory, tactile imagery)
        - 2-4 words that immediately evoke a specific scene or feeling
        - Varied across different categories: nature phenomena, human emotions, abstract concepts, seasonal elements
        - Capable of inspiring both traditional and contemporary haiku approaches

        ## Quality Guidelines
        Each theme should spark vivid imagery and emotional resonance. 
        Aim for themes that a master haiku poet would find compelling and worthy of exploration.

        ## Examples
        Excellent themes: "morning frost patterns", "distant thunder", "forgotten photograph", "candle's final moment"

        ## Output Instructions
        Save the themes as global variables:
        - Save the first theme (focus on nature/seasons) to {{@theme_1}}
        - Save the second theme (focus on human emotion/experience) to {{@theme_2}}  
        - Save the third theme (focus on abstract/philosophical) to {{@theme_3}}
        - Save the fourth theme (focus on everyday objects/moments) to {{@theme_4}}
        """.strip()
        
        self.execute_macro(theme_prompt)
        return True