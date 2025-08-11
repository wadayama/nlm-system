#!/usr/bin/env python3
"""Quick test for conditional logic with medium reasoning"""

from nlm_interpreter import NLMSession

# Test with medium reasoning
session = NLMSession(namespace="test_medium", model="gpt-5-mini", reasoning_effort="medium")

# Clear and test the problematic case
session.clear_local()
session.save("score", "70")

result = session.execute("""
{{score}}に基づいて評価を決定してください：
- 80点以上の場合は「優秀」
- 60点以上80点未満の場合は「良好」  
- 60点未満の場合は「要改善」
結果を{{evaluation}}に保存してください
""")

actual = session.get("evaluation")
print(f"Score: 70")
print(f"Expected: 良好")
print(f"Actual: {actual}")
print(f"Result: {'✅ PASS' if actual == '良好' else '❌ FAIL'}")