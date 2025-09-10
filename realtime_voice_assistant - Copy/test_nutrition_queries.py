#!/usr/bin/env python3
"""
Test nutrition queries without microphone - perfect for testing your dataset
"""

import json
import re

def test_nutrition_queries():
    """Test various nutrition queries to verify your dataset works"""
    
    print("🧪 Testing Nutrition Assistant Queries")
    print("=" * 50)
    
    # Load the nutrition knowledge base
    with open('models/nutrition_kb.json', 'r') as f:
        nutrition_data = json.load(f)
    
    print(f"📊 Loaded {len(nutrition_data)} food items from your dataset")
    print()
    
    # Test queries that should work
    test_queries = [
        "apple",
        "banana", 
        "chicken breast",
        "eggs",
        "beef steak",
        "broccoli",
        "bread",
        "cheese",
        "butter",
        "carrot"
    ]
    
    print("🔍 Testing food recognition:")
    print("-" * 30)
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        
        # Find the food
        food_item = None
        for item in nutrition_data:
            if query.lower() in item['name'].lower():
                food_item = item
                break
        
        if food_item:
            print(f"✅ Found: {food_item['name']}")
            print(f"   📊 Calories: {food_item['calories']}")
            print(f"   🥩 Protein: {food_item['protein']}g")
            print(f"   🍞 Carbs: {food_item['carbs']}g")
            print(f"   🧈 Fat: {food_item['fat']}g")
        else:
            print("❌ Not found")
    
    print("\n" + "=" * 50)
    print("🎯 Testing nutrition question patterns:")
    print("-" * 40)
    
    # Test different question patterns
    question_patterns = [
        "What are the calories in an apple?",
        "Tell me about banana nutrition",
        "How much protein is in chicken breast?",
        "What's in eggs?",
        "Calories in beef steak",
        "Nutrition facts for broccoli"
    ]
    
    for question in question_patterns:
        print(f"\nQuestion: '{question}'")
        
        # Extract food name (simple method)
        food_name = extract_food_from_question(question)
        print(f"Extracted food: '{food_name}'")
        
        if food_name:
            food_item = find_food(nutrition_data, food_name)
            if food_item:
                print(f"✅ Answer: {food_item['name']} has {food_item['calories']} calories")
            else:
                print("❌ Food not found in dataset")
        else:
            print("❌ Could not extract food name")
    
    print("\n" + "=" * 50)
    print("📋 Your dataset contains these foods:")
    print("-" * 30)
    for i, item in enumerate(nutrition_data[:10]):
        print(f"{i+1:2d}. {item['name']:20s} - {item['calories']:6.1f} cal")
    if len(nutrition_data) > 10:
        print(f"... and {len(nutrition_data) - 10} more items")
    
    print("\n🎉 Testing completed!")
    print("💡 Your nutrition assistant should work with these foods!")

def extract_food_from_question(question):
    """Extract food name from nutrition question"""
    question_lower = question.lower()
    
    # Remove common question words
    question_words = [
        "what are the calories in", "calories in", "how many calories in",
        "tell me about", "nutrition", "nutrition facts for", "what's in",
        "how much protein is in", "protein in", "carbs in", "fat in"
    ]
    
    for word in question_words:
        question_lower = question_lower.replace(word, "").strip()
    
    # Remove common words
    common_words = ["an", "a", "the", "of", "for", "about"]
    words = [word for word in question_lower.split() if word not in common_words]
    
    return " ".join(words) if words else None

def find_food(nutrition_data, query):
    """Find food item in dataset"""
    query_lower = query.lower()
    
    for item in nutrition_data:
        if query_lower in item['name'].lower():
            return item
        # Check synonyms
        for synonym in item.get('synonyms', []):
            if query_lower in synonym.lower():
                return item
    
    return None

if __name__ == "__main__":
    test_nutrition_queries()








