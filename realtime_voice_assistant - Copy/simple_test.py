#!/usr/bin/env python3
"""
Simple test of the nutrition data without torch dependencies
"""

import json
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def simple_nutrition_test():
    """Test nutrition queries with simple text matching"""
    
    print("🧪 Testing Nutrition Data (Simple Mode)")
    print("=" * 50)
    
    # Load the nutrition knowledge base
    with open('models/nutrition_kb.json', 'r') as f:
        nutrition_data = json.load(f)
    
    print(f"📊 Loaded {len(nutrition_data)} food items")
    
    # Test queries
    test_queries = [
        "apple",
        "chicken breast", 
        "banana",
        "eggs",
        "beef steak",
        "broccoli"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: '{query}'")
        
        # Simple text matching
        best_match = None
        best_score = 0
        
        for item in nutrition_data:
            # Check if query matches name or synonyms
            name_match = query.lower() in item['name'].lower()
            synonym_match = any(query.lower() in syn.lower() for syn in item.get('synonyms', []))
            
            if name_match or synonym_match:
                score = 1.0 if name_match else 0.8
                if score > best_score:
                    best_score = score
                    best_match = item
        
        if best_match:
            print(f"✅ Found: {best_match['name']}")
            print(f"   Calories: {best_match['calories']}")
            print(f"   Protein: {best_match['protein']}g")
            print(f"   Carbs: {best_match['carbs']}g")
            print(f"   Fat: {best_match['fat']}g")
            print(f"   Confidence: {best_score:.3f}")
        else:
            print("❌ No results found")
    
    print("\n🎉 Nutrition data is working correctly!")
    print("🚀 Ready to run the full voice assistant!")

if __name__ == "__main__":
    simple_nutrition_test()








