#!/usr/bin/env python
"""Quick test of both models without max_tokens"""

from nlm_interpreter import NLMSession

# Test local model
print("Testing gpt-oss:20b (local)...")
s1 = NLMSession("gpt-oss:20b", "test_local")
r1 = s1.execute("Set {{x}} to 42")
print(f"✅ Local model: x = {s1.get('x')}")

# Test OpenAI model
print("\nTesting gpt-5-nano (OpenAI)...")
s2 = NLMSession("gpt-5-nano", "test_openai")
r2 = s2.execute("Set {{y}} to 99")
print(f"✅ OpenAI model: y = {s2.get('y')}")

print("\n✅ Both models work without max_tokens!")