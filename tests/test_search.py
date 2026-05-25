# Quick test for Week 2 search pipeline
import sys
sys.path.append('.')
from src.search.vector_store import build_catalogue_index, find_similar_products

# Simulate attributes Gemini would extract from a black formal shoe image
test_attributes = {
    "category": "shoes",
    "colour": "black",
    "style": "formal",
    "material": "patent leather",
    "gender": "men",
    "brand": "unknown"
}

# Build the index (embeds all 20 products)
index = build_catalogue_index()

# Find similar products
results = find_similar_products(test_attributes, index)

print("\nTop 5 similar products:")
for i, product in enumerate(results, 1):
    print(f"{i}. {product['name']} — ₹{product['price']}")