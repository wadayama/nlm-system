#!/usr/bin/env python3
"""Demo script showing nlm_interpreter.py usage patterns"""

import os
import sys

from nlm_interpreter import NLMSession, nlm_execute


def demo_basic_usage():
    """Demonstrate basic variable operations"""
    print("=== Demo: Basic Variable Operations ===")
    
    session = NLMSession(namespace="demo")
    
    # Simple save and retrieve
    print("1. Save and retrieve a greeting")
    result = session.execute("Save 'Hello World' to variable 'greeting'")
    print(f"Save result: {result}")
    
    result = session.execute("Get the greeting variable")
    print(f"Get result: {result}")
    print()
    
    # User information
    print("2. Store user information")
    result = session.execute("Save my name 'Alice Johnson' to 'user_name'")
    print(f"Name save: {result}")
    
    result = session.execute("Save my age '30' to variable 'age'")
    print(f"Age save: {result}")
    print()
    
    # List variables
    print("3. List all variables")
    result = session.execute("Show me all the variables")
    print(f"Variables: {result}")
    print()


def demo_global_variables():
    """Demonstrate global variable usage"""
    print("=== Demo: Global Variables ===")
    
    session1 = NLMSession(namespace="session_a")
    session2 = NLMSession(namespace="session_b")
    
    # Set global configuration
    print("1. Set global configuration from session A")
    result = session1.execute("Save 'production' to global variable 'environment'")
    print(f"Global save: {result}")
    
    result = session1.execute("Save 'https://api.prod.com' to global variable 'api_url'")
    print(f"API URL save: {result}")
    print()
    
    # Access from different session
    print("2. Access global variables from session B")
    result = session2.execute("Get the global environment setting")
    print(f"Environment from B: {result}")
    
    result = session2.execute("Get the global API URL")
    print(f"API URL from B: {result}")
    print()


def demo_data_processing():
    """Demonstrate data processing workflow"""
    print("=== Demo: Data Processing Workflow ===")
    
    analytics_session = NLMSession(namespace="analytics")
    
    # Setup processing parameters
    print("1. Setup data processing parameters")
    result = analytics_session.execute("Save input file path '/data/sales_2024.csv' to 'input_file'")
    print(f"Input file: {result}")
    
    result = analytics_session.execute("Save output directory '/tmp/results' to 'output_dir'")
    print(f"Output dir: {result}")
    
    result = analytics_session.execute("Save analysis type 'regression' to 'model_type'")
    print(f"Model type: {result}")
    print()
    
    # Simulate processing steps
    print("2. Process data and save intermediate results")
    result = analytics_session.execute("Save preprocessing status 'completed' to 'prep_status'")
    print(f"Prep status: {result}")
    
    result = analytics_session.execute("Save model accuracy '0.92' to 'model_score'")
    print(f"Model score: {result}")
    print()
    
    # Check final status
    print("3. Check processing results")
    result = analytics_session.execute("List all variables to see processing results")
    print(f"Final status: {result}")
    print()


def demo_simple_function_interface():
    """Demonstrate simple function interface"""
    print("=== Demo: Simple Function Interface ===")
    
    # Using nlm_execute function
    print("1. Using nlm_execute function")
    result = nlm_execute("Save today's date '2025-08-07' to 'current_date'", namespace="simple")
    print(f"Date save: {result}")
    
    result = nlm_execute("Get the current date", namespace="simple")
    print(f"Date get: {result}")
    print()
    
    # Configuration example
    print("2. Configuration management")
    result = nlm_execute("Save debug level 'INFO' to global 'log_level'", namespace="config")
    print(f"Log level: {result}")
    
    result = nlm_execute("Save max connections '100' to global 'max_conn'", namespace="config")
    print(f"Max conn: {result}")
    print()


def demo_error_handling():
    """Demonstrate error handling"""
    print("=== Demo: Error Handling ===")
    
    session = NLMSession(namespace="error_demo")
    
    # Try to get non-existent variable
    print("1. Try to get non-existent variable")
    result = session.execute("Get the value of variable 'nonexistent'")
    print(f"Non-existent: {result}")
    print()
    
    # Delete and try to access
    print("2. Delete variable and try to access")
    session.execute("Save 'temporary' to variable 'temp'")
    result = session.execute("Delete the 'temp' variable")
    print(f"Delete result: {result}")
    
    result = session.execute("Get the temp variable")
    print(f"Deleted variable: {result}")
    print()


def demo_file_processing():
    """Demonstrate processing files"""
    print("=== Demo: File Processing Simulation ===")
    
    processor = NLMSession(namespace="file_processor")
    
    # Read macro from file
    print("1. Process basic usage macro file")
    try:
        with open("examples/basic_usage.md", "r") as f:
            macro_content = f.read()
        
        # Extract first few lines as a simple macro
        lines = macro_content.split('\n')
        simple_macro = None
        for line in lines:
            if line.strip() and not line.startswith('#') and not line.startswith('This'):
                simple_macro = line.strip()
                break
        
        if simple_macro:
            print(f"Executing: {simple_macro}")
            result = processor.execute(simple_macro)
            print(f"Result: {result}")
        else:
            print("No suitable macro found in file")
            
    except Exception as e:
        print(f"File processing error: {e}")
    
    print()


def run_all_demos():
    """Run all demonstration functions"""
    print("🚀 NLM System Demonstration\n")
    print("This demo shows various usage patterns of the Natural Language Macro system.")
    print("Each demo section shows how to use different features.\n")
    print("=" * 80)
    
    demos = [
        demo_basic_usage,
        demo_global_variables,
        demo_data_processing,
        demo_simple_function_interface,
        demo_error_handling,
        demo_file_processing
    ]
    
    for i, demo in enumerate(demos, 1):
        try:
            demo()
            print("=" * 80)
            if i < len(demos):
                input("Press Enter to continue to next demo...")
                print()
        except Exception as e:
            print(f"❌ Demo failed: {e}")
            import traceback
            traceback.print_exc()
            print("=" * 80)
    
    print("🎉 Demo completed!")
    print("\nTo explore more:")
    print("  uv run nlm_interpreter.py 'Save hello to greeting'")
    print("  uv run nlm_interpreter.py -f examples/basic_usage.md")
    print("  uv run history_viewer.py history")


if __name__ == "__main__":
    # Check if Ollama is available
    try:
        session = NLMSession(namespace="test")
        session.execute("Save 'test' to 'connection_test'")
        print("✅ Ollama connection verified")
        print()
        run_all_demos()
    except Exception as e:
        print("❌ Ollama connection failed")
        print("Please make sure:")
        print("1. Ollama is running: ollama serve")
        print("2. Model is available: ollama pull gpt-oss:20b")
        print(f"Error: {e}")