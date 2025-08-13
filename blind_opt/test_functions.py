#!/usr/bin/env python3
"""
Test functions for blind optimization tutorial
Each function has a known minimum for evaluation purposes
"""

import math


class TestFunction:
    """Base class for test functions"""
    
    def __init__(self, name):
        self.name = name
    
    def __call__(self, x, y):
        """Evaluate function at point (x, y)"""
        raise NotImplementedError
    
    def get_minimum(self):
        """Return the true minimum point [x, y]"""
        raise NotImplementedError


class SphereFunction(TestFunction):
    """
    Sphere function: f(x,y) = (x-4)^2 + (y+3)^2
    Minimum: (4, -3) with value 0
    Simple convex function, good for testing basic optimization
    """
    
    def __init__(self):
        super().__init__("sphere")
    
    def __call__(self, x, y):
        return (x - 4)**2 + (y + 3)**2
    
    def get_minimum(self):
        return [4.0, -3.0]


class RosenbrockFunction(TestFunction):
    """
    Rosenbrock function: f(x,y) = (1-x)^2 + 100*(y-x^2)^2
    Minimum: (1, 1) with value 0
    Classic non-convex optimization benchmark with a narrow valley
    """
    
    def __init__(self):
        super().__init__("rosenbrock")
    
    def __call__(self, x, y):
        return (1 - x)**2 + 100 * (y - x**2)**2
    
    def get_minimum(self):
        return [1.0, 1.0]


class HimmelblauFunction(TestFunction):
    """
    Himmelblau's function: f(x,y) = (x^2 + y - 11)^2 + (x + y^2 - 7)^2
    Has 4 equal minima at:
    - (3.0, 2.0)
    - (-2.805118, 3.131312)
    - (-3.779310, -3.283186)
    - (3.584428, -1.848126)
    All with value 0
    """
    
    def __init__(self):
        super().__init__("himmelblau")
    
    def __call__(self, x, y):
        return (x**2 + y - 11)**2 + (x + y**2 - 7)**2
    
    def get_minimum(self):
        # Return the closest minimum to origin for simplicity
        return [3.0, 2.0]


class ComplexObjectiveFunction(TestFunction):
    """
    Complex 2D objective function with quadratic, oscillation, and interaction terms
    Based on claude-code-macro-programming example (without noise)
    Minimum at: (1.5, -0.8)
    """
    
    def __init__(self):
        super().__init__("complex")
        # Secret optimal solution
        self.X0 = 1.5
        self.Y0 = -0.8
        self.OSCILLATION_STRENGTH = 0.5
    
    def __call__(self, x, y):
        # Coordinate transformation
        dx = x - self.X0
        dy = y - self.Y0
        
        # Complex 2D function with quadratic, oscillation, and interaction terms
        quadratic_term = dx**2 + dy**2
        oscillation_term = self.OSCILLATION_STRENGTH * (math.sin(dx)**2 + math.sin(dy)**2)
        interaction_term = 5.0 * math.sin(dx) * math.sin(dy)
        
        base_value = quadratic_term + oscillation_term + interaction_term
        
        return base_value
    
    def get_minimum(self):
        return [self.X0, self.Y0]


def get_test_function(name):
    """Factory function to get test function by name"""
    functions = {
        'sphere': SphereFunction,
        'rosenbrock': RosenbrockFunction,
        'himmelblau': HimmelblauFunction,
        'complex': ComplexObjectiveFunction
    }
    
    if name not in functions:
        raise ValueError(f"Unknown function: {name}. Available: {list(functions.keys())}")
    
    return functions[name]()


# Simple test
if __name__ == "__main__":
    # Test sphere function
    sphere = get_test_function('sphere')
    print(f"Sphere at (0,0): {sphere(0, 0)}")
    print(f"Sphere at (1,1): {sphere(1, 1)}")
    print(f"Sphere minimum: {sphere.get_minimum()}")
    
    # Test Rosenbrock
    rosenbrock = get_test_function('rosenbrock')
    print(f"\nRosenbrock at (1,1): {rosenbrock(1, 1)}")
    print(f"Rosenbrock at (0,0): {rosenbrock(0, 0)}")
    print(f"Rosenbrock minimum: {rosenbrock.get_minimum()}")
    
    # Test Complex function
    complex_func = get_test_function('complex')
    print(f"\nComplex at (1.5,-0.8): {complex_func(1.5, -0.8):.6f}")
    print(f"Complex at (0,0): {complex_func(0, 0):.6f}")
    print(f"Complex minimum: {complex_func.get_minimum()}")