#!/usr/bin/env python3
"""
LLM-driven optimization agent
Using LLM to make point selection decisions
"""

from nlm_interpreter import NLMSession


class OptimizationAgent:
    """LLM-driven optimization agent"""
    
    def __init__(self, model="gpt-5-mini"):
        self.session = NLMSession(namespace="simple_opt", model=model)
    
    def decide_next_point(self, evaluation_history):
        """Use LLM to decide next point based on accumulated experience context"""
        
        if len(evaluation_history) == 0:
            # First point: let LLM decide where to start
            macro = """
            Choose the first point to evaluate an unknown function f(x,y).
            Search range is [-5, 5] for both x and y.
            
            Save your x-coordinate to {{x_coord}}.
            Save your y-coordinate to {{y_coord}}.
            Save your reasoning to {{reasoning}}.
            """
        else:
            # Use recent experience (last 8 entries to provide richer context)
            recent_experience = self.session.get_tail("experience_context", n_lines=8)
            
            macro = """
            Recent experience:
            {{recent_experience}}
            
            Choose next point to minimize function. Range: [-5, 5].
            IMPORTANT: Explore new areas! Avoid repeating the same point unless you have strong evidence it's optimal.
            Try different regions to find the global minimum.
            
            Save x to {{x_coord}}.
            Save y to {{y_coord}}.
            Save reason to {{reasoning}}.
            """
            
            # Set the recent experience in session
            self.session.save("recent_experience", recent_experience)
        
        # Execute the macro
        result = self.session.execute(macro)
        
        # Get LLM's decision
        x = float(self.session.get("x_coord"))
        y = float(self.session.get("y_coord"))
        reasoning = self.session.get("reasoning")
        
        return [x, y], reasoning
    
    def record_experience(self, point, value, reasoning):
        """Record the experience (point, value, reasoning) to context"""
        experience_entry = f"Tried ({point[0]:.2f}, {point[1]:.2f}) → Value: {value:.4f}. Reasoning: {reasoning}"
        self.session.append("experience_context", experience_entry)


# Test the LLM decision agent with experience accumulation
if __name__ == "__main__":
    print("Testing LLM-driven optimization agent with experience context...")
    
    agent = OptimizationAgent()
    
    # Test 1: First point decision
    print("\n=== Test 1: First Point Decision ===")
    point, reasoning = agent.decide_next_point([])
    print(f"Point: ({point[0]:.3f}, {point[1]:.3f})")
    print(f"Reasoning: {reasoning}")
    
    # Record first experience
    agent.record_experience(point, 2.5, reasoning)
    
    # Test 2: Second point with accumulated experience
    print("\n=== Test 2: Second Point Decision (using experience) ===")
    point2, reasoning2 = agent.decide_next_point([{'point': point, 'value': 2.5}])
    print(f"Point: ({point2[0]:.3f}, {point2[1]:.3f})")
    print(f"Reasoning: {reasoning2}")
    
    # Record second experience
    agent.record_experience(point2, 0.8, reasoning2)
    
    # Test 3: Third point with more experience
    print("\n=== Test 3: Third Point Decision (richer experience) ===")
    point3, reasoning3 = agent.decide_next_point([
        {'point': point, 'value': 2.5},
        {'point': point2, 'value': 0.8}
    ])
    print(f"Point: ({point3[0]:.3f}, {point3[1]:.3f})")
    print(f"Reasoning: {reasoning3}")
    
    # Show accumulated experience
    print("\n=== Accumulated Experience Context ===")
    experience = agent.session.get("experience_context")
    print(experience)
    
    print("\nTest completed!")