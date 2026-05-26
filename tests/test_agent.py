# test_agent.py
# Tests the full LangGraph agent pipeline end to end.

import sys
sys.path.append('.')
from src.search.vector_store import build_catalogue_index
from src.agent.graph import run_agent

# Build catalogue index
print("Building index...")
index = build_catalogue_index()

# Simulate attributes from a black formal shoe image
attributes = {
    "category": "shoes",
    "colour": "black",
    "style": "formal",
    "material": "patent leather",
    "gender": "men",
    "brand": "unknown",
    "confidence": 95
}

# Run agent without price filter
print("\n--- Test 1: No price filter ---")
result = run_agent(attributes, index)
print(f"Recommendation:\n{result['recommendation']}")
print(f"\nSteps taken: {result['steps_taken']}")
print(f"Products found: {result['total_found']}")

# Run agent with price filter
print("\n--- Test 2: Max price ₹5000 ---")
result2 = run_agent(attributes, index, max_price=5000)
print(f"Recommendation:\n{result2['recommendation']}")
print(f"\nProducts found under ₹5000: {result2['total_found']}")
for p in result2['products']:
    print(f"  - {p['name']} ₹{p['price']}")