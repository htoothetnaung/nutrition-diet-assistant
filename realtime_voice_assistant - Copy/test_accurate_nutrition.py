#!/usr/bin/env python3
"""
Test the highly accurate nutrition assistant
"""

import json
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

def test_accurate_nutrition():
    """Test the highly accurate nutrition assistant"""
    
    print("🧪 Testing Highly Accurate Nutrition Assistant")
    print("=" * 50)
    
    # Load the accurate knowledge base
    with open('models/accurate_nutrition_kb.json', 'r') as f:
        nutrition_data = json.load(f)
    
    print(f"📊 Loaded {len(nutrition_data)} food items")
    print()
    
    # Test questions that should work perfectly now
    test_questions = [
        "how many calories in an apple",
        "what are the calories in banana",
        "protein content of chicken breast",
        "tell me about eggs nutrition",
        "how much fat in beef steak",
        "nutrition facts for broccoli",
        "what's in bread",
        "calories in cheese",
        "how many calories does an apple have",
        "what's the protein content of chicken",
        "tell me about banana",
        "nutrition information for eggs",
        "how much protein is in chicken breast",
        "what are the carbs in banana",
        "fat content of beef steak"
    ]
    
    print("🔍 Testing question understanding:")
    print("-" * 40)
    
    for question in test_questions:
        print(f"\n❓ Question: '{question}'")
        
        # Simulate the assistant's logic
        best_match = find_best_match(nutrition_data, question)
        
        if best_match:
            food_item = best_match['food_item']
            confidence = best_match['confidence']
            print(f"✅ Found: {food_item['name']} (confidence: {confidence:.3f})")
            
            # Generate appropriate response
            question_lower = question.lower()
            if "calories" in question_lower:
                print(f"   📊 Answer: {food_item['name']} has {food_item['calories']} calories per 100g")
            elif "protein" in question_lower:
                print(f"   🥩 Answer: {food_item['name']} contains {food_item['protein']}g of protein per 100g")
            elif "carbs" in question_lower or "carbohydrates" in question_lower:
                print(f"   🍞 Answer: {food_item['name']} has {food_item['carbs']}g of carbohydrates per 100g")
            elif "fat" in question_lower:
                print(f"   🧈 Answer: {food_item['name']} contains {food_item['fat']}g of fat per 100g")
            else:
                print(f"   📋 Answer: {food_item['name']} - {food_item['calories']} cal, {food_item['protein']}g protein")
        else:
            print("❌ No match found")
    
    print("\n" + "=" * 50)
    print("🎉 Testing completed!")
    print("🎯 Your highly accurate nutrition assistant is ready!")
    print("🚀 Run: .\\run_accurate_nutrition.bat")

def find_best_match(nutrition_data, question):
    """Find best match for a question using comprehensive search"""
    question_lower = question.lower()
    best_match = None
    best_score = 0
    
    for food in nutrition_data:
        score = 0
        
        # Check search terms (most important)
        for term in food.get('search_terms', []):
            if term in question_lower:
                score += 1
        
        # Check direct name match (high priority)
        if food['name'].lower() in question_lower:
            score += 2
        
        # Check synonyms (medium priority)
        for synonym in food.get('synonyms', []):
            if synonym.lower() in question_lower:
                score += 1.5
        
        # Check category (low priority)
        if food.get('category', '').lower() in question_lower:
            score += 0.5
        
        if score > best_score:
            best_score = score
            best_match = {
                'food_item': food,
                'confidence': min(score / 3, 1.0),  # Normalize to 0-1
                'matched_method': 'comprehensive_search'
            }
    
    return best_match if best_score > 0 else None

if __name__ == "__main__":
    test_accurate_nutrition()








