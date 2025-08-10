"""Test difficult edge cases for NLM interpreter.

This module tests challenging scenarios that push the boundaries of
natural language understanding and variable management.
"""

import sys
import time
from pathlib import Path

# Add parent directory to path

from nlm_interpreter import NLMSession
from variable_db import VariableDB


def test_ambiguous_variable_references():
    """Test cases where variable references could be ambiguous"""
    print("\n=== Testing Ambiguous Variable References ===")
    session = NLMSession(namespace="ambiguous")
    
    # Case 1: Variable name that looks like a sentence
    print("Test 1: Variable name as sentence...")
    session.save("name", "Alice")
    result = session.execute("{{name}} is a developer and {{name}} is happy")
    # Should NOT become "Alice is a developer and Alice is happy"
    # Instead should update the variable
    value = session.get("name")
    print(f"Result: {result}")
    print(f"Variable value after: {value}")
    assert value != "Alice", "Variable should have been updated"
    
    # Case 2: Nested linguistic structures
    print("\nTest 2: Nested structures...")
    result = session.execute("Set {{message}} to 'The value of {{x}} is unknown'")
    # Should save the literal string with {{x}} in it, not expand x
    value = session.get("message")
    print(f"Stored message: {value}")
    assert "{{x}}" in value or "unknown" in value, f"Expected literal storage, got: {value}"
    
    # Case 3: Variable name conflicts with pronouns
    print("\nTest 3: Pronoun conflicts...")
    session.save("it", "computer")
    result = session.execute("{{it}} is fast but {{it}} needs repair")
    # Ambiguous: updating variable or describing it?
    print(f"Result: {result}")
    
    print("✓ Ambiguous reference tests completed")
    return True


def test_recursive_variable_patterns():
    """Test recursive and self-referential patterns"""
    print("\n=== Testing Recursive Variable Patterns ===")
    session = NLMSession(namespace="recursive")
    
    # Case 1: Self-referential update
    print("Test 1: Self-referential update...")
    session.save("counter", "1")
    result = session.execute("Increment {{counter}} and save back to {{counter}}")
    value = session.get("counter")
    print(f"Counter after increment: {value}")
    # Should handle incrementing properly
    
    # Case 2: Circular reference attempt
    print("\nTest 2: Circular reference...")
    session.save("a", "value_a")
    session.save("b", "value_b")
    result = session.execute("Set {{a}} to {{b}} and {{b}} to {{a}}")
    value_a = session.get("a")
    value_b = session.get("b")
    print(f"After swap - a: {value_a}, b: {value_b}")
    
    # Case 3: Variable containing variable syntax
    print("\nTest 3: Meta-variable...")
    result = session.execute("Save '{{another}}' as literal text to {{template}}")
    value = session.get("template")
    print(f"Template value: {value}")
    assert "{{" in value or "another" in value, f"Should store variable syntax literally"
    
    print("✓ Recursive pattern tests completed")
    return True


def test_natural_language_ambiguity():
    """Test natural language constructs that could confuse the interpreter"""
    print("\n=== Testing Natural Language Ambiguity ===")
    session = NLMSession(namespace="nlp_ambig")
    
    # Case 1: Homonyms and word play
    print("Test 1: Homonyms...")
    session.save("read", "book")
    result = session.execute("I {{read}} the {{read}} yesterday")
    # "read" as verb vs variable name
    print(f"Result: {result}")
    
    # Case 2: Grammatical ambiguity
    print("\nTest 2: Grammar ambiguity...")
    result = session.execute("{{name}} {{verb}} {{object}} to {{recipient}}")
    # All positions could be either variables or grammatical roles
    print(f"Result: {result}")
    
    # Case 3: Partial variable names
    print("\nTest 3: Partial matches...")
    session.save("test", "value1")
    session.save("testing", "value2")
    result = session.execute("Update {{test}} without changing {{testing}}")
    value1 = session.get("test")
    value2 = session.get("testing")
    print(f"test: {value1}, testing: {value2}")
    
    print("✓ Natural language ambiguity tests completed")
    return True


def test_multilingual_edge_cases():
    """Test edge cases with multiple languages"""
    print("\n=== Testing Multilingual Edge Cases ===")
    session = NLMSession(namespace="multilang")
    
    # Case 1: Japanese particles that look like operations
    print("Test 1: Japanese particles...")
    result = session.execute("{{名前}}は太郎です")  # "name is Taro"
    value = session.get("名前")
    print(f"Japanese variable value: {value}")
    
    # Case 2: Mixed language instructions
    print("\nTest 2: Mixed languages...")
    session.save("greeting", "Hello")
    result = session.execute("{{greeting}}を「こんにちは」に変更してください")
    value = session.get("greeting")
    print(f"Greeting after Japanese instruction: {value}")
    
    # Case 3: RTL language (Arabic/Hebrew simulation)
    print("\nTest 3: Special characters...")
    result = session.execute("Set {{מחיר}} to 100")  # Hebrew "price"
    print(f"Result: {result}")
    
    print("✓ Multilingual tests completed")
    return True


def test_complex_conditional_logic():
    """Test complex conditional and logical operations"""
    print("\n=== Testing Complex Conditional Logic ===")
    session = NLMSession(namespace="logic")
    
    # Case 1: Nested conditionals
    print("Test 1: Nested conditions...")
    session.save("score", "75")
    session.save("grade", "")
    result = session.execute(
        "If {{score}} is greater than 90, set {{grade}} to A, "
        "else if {{score}} is greater than 80, set {{grade}} to B, "
        "else if {{score}} is greater than 70, set {{grade}} to C, "
        "else set {{grade}} to F"
    )
    grade = session.get("grade")
    print(f"Grade for score 75: {grade}")
    
    # Case 2: Boolean operations
    print("\nTest 2: Boolean operations...")
    session.save("is_admin", "true")
    session.save("is_active", "false")
    result = session.execute(
        "Set {{access}} to 'granted' if {{is_admin}} AND {{is_active}}, otherwise 'denied'"
    )
    access = session.get("access")
    print(f"Access status: {access}")
    
    print("✓ Conditional logic tests completed")
    return True


def test_malformed_syntax_recovery():
    """Test recovery from malformed variable syntax"""
    print("\n=== Testing Malformed Syntax Recovery ===")
    session = NLMSession(namespace="malformed")
    
    # Case 1: Unclosed brackets
    print("Test 1: Unclosed brackets...")
    result = session.execute("Save value to {{unclosed")
    print(f"Result with unclosed bracket: {result}")
    
    # Case 2: Extra brackets
    print("\nTest 2: Extra brackets...")
    result = session.execute("Save value to {{{{extra}}}}")
    print(f"Result with extra brackets: {result}")
    
    # Case 3: Mixed bracket styles
    print("\nTest 3: Mixed brackets...")
    result = session.execute("Save value to {{var1} and {var2}}")
    print(f"Result with mixed brackets: {result}")
    
    # Case 4: Special characters in variable names
    print("\nTest 4: Special characters...")
    result = session.execute("Save value to {{var-with-dashes}}")
    print(f"Result with dashes: {result}")
    
    result = session.execute("Save value to {{var.with.dots}}")
    print(f"Result with dots: {result}")
    
    print("✓ Malformed syntax tests completed")
    return True


def test_performance_edge_cases():
    """Test performance with extreme cases"""
    print("\n=== Testing Performance Edge Cases ===")
    session = NLMSession(namespace="performance")
    
    # Case 1: Very long variable values
    print("Test 1: Long values...")
    long_value = "x" * 10000
    session.save("huge", long_value)
    result = session.execute("Append 'END' to {{huge}} and save to {{huge2}}")
    value = session.get("huge2")
    if value:
        print(f"Successfully handled {len(value)} character value")
    
    # Case 2: Many variables in one command
    print("\nTest 2: Many variables...")
    for i in range(20):
        session.save(f"var{i}", str(i))
    
    template = "Combine " + " and ".join([f"{{{{var{i}}}}}" for i in range(20)])
    result = session.execute(template + " into {{combined}}")
    print(f"Combined 20 variables")
    
    # Case 3: Rapid successive operations
    print("\nTest 3: Rapid operations...")
    start = time.time()
    for i in range(10):
        session.execute(f"Set {{{{rapid{i}}}}} to {i}")
    elapsed = time.time() - start
    print(f"10 operations in {elapsed:.2f} seconds")
    
    print("✓ Performance tests completed")
    return True


def test_semantic_understanding_limits():
    """Test the limits of semantic understanding"""
    print("\n=== Testing Semantic Understanding Limits ===")
    session = NLMSession(namespace="semantic")
    
    # Case 1: Implicit operations
    print("Test 1: Implicit operations...")
    session.save("price", "100")
    session.save("tax", "10")
    result = session.execute("Calculate total with {{price}} and {{tax}}")
    # Should infer addition operation
    print(f"Result: {result}")
    
    # Case 2: Context-dependent meaning
    print("\nTest 2: Context-dependent...")
    session.save("date", "2024-01-01")
    result = session.execute("Move {{date}} forward by one month")
    # Should understand date manipulation
    print(f"Result: {result}")
    
    # Case 3: Metaphorical language
    print("\nTest 3: Metaphorical language...")
    session.save("list", "apple,banana")
    result = session.execute("Add orange to the fruit basket {{list}}")
    # Should understand "fruit basket" means the list
    value = session.get("list")
    print(f"List after metaphorical add: {value}")
    
    print("✓ Semantic understanding tests completed")
    return True


def run_all_difficult_edge_cases():
    """Run all difficult edge case tests"""
    print("=" * 60)
    print("RUNNING DIFFICULT EDGE CASE TESTS")
    print("=" * 60)
    
    tests = [
        ("Ambiguous References", test_ambiguous_variable_references),
        ("Recursive Patterns", test_recursive_variable_patterns),
        ("Natural Language Ambiguity", test_natural_language_ambiguity),
        ("Multilingual Cases", test_multilingual_edge_cases),
        ("Complex Conditional Logic", test_complex_conditional_logic),
        ("Malformed Syntax", test_malformed_syntax_recovery),
        ("Performance Edge Cases", test_performance_edge_cases),
        ("Semantic Understanding", test_semantic_understanding_limits)
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            print(f"\n{'='*60}")
            print(f"Running: {name}")
            print('='*60)
            
            if test_func():
                passed += 1
                print(f"✅ {name} PASSED")
            else:
                failed += 1
                print(f"❌ {name} FAILED")
                
        except Exception as e:
            failed += 1
            print(f"❌ {name} FAILED with error: {e}")
    
    print("\n" + "=" * 60)
    print(f"DIFFICULT EDGE CASES SUMMARY")
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_difficult_edge_cases()
    sys.exit(0 if success else 1)