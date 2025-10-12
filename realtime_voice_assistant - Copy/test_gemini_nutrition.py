#!/usr/bin/env python3
"""
Test the Gemini AI nutrition assistant without voice
"""

import json
import os
import google.generativeai as genai

def test_gemini_nutrition():
    """Test Gemini AI nutrition assistant functionality"""
    
    print("🧪 Testing Gemini AI Nutrition Assistant")
    print("=" * 50)
    
    # Check if nutrition knowledge base exists
    if not os.path.exists("models/accurate_nutrition_kb.json"):
        print("❌ Nutrition knowledge base not found!")
        print("💡 Run 'py simple_accurate_trainer.py' first")
        return
    
    # Load nutrition data
    with open("models/accurate_nutrition_kb.json", 'r') as f:
        nutrition_data = json.load(f)
    
    print(f"📊 Loaded {len(nutrition_data)} food items")
    
    # Get Gemini AI API key
    api_key = input("\nEnter your Gemini AI API key (or press Enter to skip Gemini tests): ").strip()
    
    if not api_key:
        print("⚠️  Skipping Gemini tests. Testing local functionality only.")
        test_local_functionality(nutrition_data)
        return
    
    # Test Gemini AI integration
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        print("✅ Gemini AI client initialized successfully")
        
        # Test nutrition questions
        test_questions = [
            "How many calories are in an apple?",
            "What's the protein content of chicken breast?",
            "Tell me about banana nutrition",
            "What's the weather today?",  # Should be blocked
            "What time is it?",  # Should be blocked
            "How many calories in eggs?",
            "What's the fat content of beef steak?"
        ]
        
        print("\n🔍 Testing questions:")
        print("-" * 30)
        
        for question in test_questions:
            print(f"\n❓ Question: '{question}'")
            
            # Check if it's a nutrition query
            is_nutrition = is_nutrition_query(question)
            is_blocked = is_blocked_query(question)
            
            if is_blocked:
                print("🚫 BLOCKED: Non-nutrition question")
                response = "I'm a nutrition assistant and can only help with food and nutrition questions. Please ask me about calories, protein, vitamins, or other nutrition topics."
            elif is_nutrition:
                print("✅ ALLOWED: Nutrition question")
                
                # Find food data
                food_data = find_food_in_query(nutrition_data, question)
                
                # Get Gemini AI response
                response = get_gemini_response(model, question, food_data)
            else:
                print("⚠️  UNCLEAR: Redirecting to nutrition")
                response = "I'm a nutrition assistant and can only help with food and nutrition questions. Please ask me about calories, protein, vitamins, or other nutrition topics."
            
            print(f"🤖 Response: {response}")
        
        print("\n🎉 Gemini AI integration test completed!")
        
    except Exception as e:
        print(f"❌ Gemini AI Error: {e}")
        print("💡 Check your API key and internet connection")
        test_local_functionality(nutrition_data)

def test_local_functionality(nutrition_data):
    """Test local functionality without Gemini AI"""
    print("\n🔍 Testing local functionality:")
    print("-" * 30)
    
    test_questions = [
        "How many calories are in an apple?",
        "What's the protein content of chicken breast?",
        "What's the weather today?",  # Should be blocked
        "What time is it?",  # Should be blocked
    ]
    
    for question in test_questions:
        print(f"\n❓ Question: '{question}'")
        
        is_nutrition = is_nutrition_query(question)
        is_blocked = is_blocked_query(question)
        
        if is_blocked:
            print("🚫 BLOCKED: Non-nutrition question")
        elif is_nutrition:
            print("✅ ALLOWED: Nutrition question")
            food_data = find_food_in_query(nutrition_data, question)
            if food_data:
                print(f"🍎 Found: {food_data['food_item']['name']}")
            else:
                print("❌ No food found in query")
        else:
            print("⚠️  UNCLEAR: Would redirect to nutrition")

def is_nutrition_query(text: str) -> bool:
    """Check if the query is nutrition-related"""
    text_lower = text.lower()
    
    nutrition_keywords = [
        "calories", "calorie", "nutrition", "nutrients", "protein", "carbs", "carbohydrates",
        "fat", "fiber", "sugar", "vitamin", "mineral", "healthy", "diet", "food",
        "how many", "how much", "what are", "tell me", "information", "facts",
        "content", "value", "amount", "quantity", "eating", "meal", "breakfast",
        "lunch", "dinner", "snack", "ingredient", "recipe", "cooking", "baking"
    ]
    
    return any(keyword in text_lower for keyword in nutrition_keywords)

def is_blocked_query(text: str) -> bool:
    """Check if the query should be blocked"""
    text_lower = text.lower()
    
    blocked_topics = [
        "weather", "time", "date", "news", "politics", "sports", "entertainment",
        "technology", "programming", "coding", "games", "movies", "music",
        "travel", "shopping", "money", "finance", "business", "work", "job",
        "school", "education", "science", "history", "geography", "math",
        "personal", "relationship", "family", "friends", "health", "medical",
        "doctor", "hospital", "medicine", "drug", "alcohol", "smoking"
    ]
    
    return any(topic in text_lower for topic in blocked_topics)

def find_food_in_query(nutrition_data, text: str):
    """Find food item in the query"""
    text_lower = text.lower()
    best_match = None
    best_score = 0
    
    for food in nutrition_data:
        score = 0
        
        # Check search terms
        for term in food.get('search_terms', []):
            if term in text_lower:
                score += 1
        
        # Check direct name match
        if food['name'].lower() in text_lower:
            score += 2
        
        # Check synonyms
        for synonym in food.get('synonyms', []):
            if synonym.lower() in text_lower:
                score += 1.5
        
        if score > best_score:
            best_score = score
            best_match = {
                'food_item': food,
                'confidence': min(score / 3, 1.0)
            }
    
    return best_match if best_score > 0 else None

def get_gemini_response(model, question: str, food_data=None):
    """Get response from Gemini AI"""
    try:
        system_prompt = """You are a nutrition expert assistant. You ONLY answer questions about food, nutrition, calories, protein, carbohydrates, fat, vitamins, minerals, and healthy eating. 

Rules:
1. ONLY answer nutrition-related questions
2. If asked about non-nutrition topics, politely decline and redirect to nutrition
3. Be helpful and informative about nutrition
4. Use the provided nutrition data when available
5. Keep responses concise and clear
6. Always mention "per 100g" when giving nutritional values

If the user asks about topics other than nutrition, respond with: "I'm a nutrition assistant and can only help with food and nutrition questions. Please ask me about calories, protein, vitamins, or other nutrition topics.""""
        
        user_prompt = question
        
        if food_data:
            food_item = food_data['food_item']
            user_prompt += f"\n\nNutrition data for {food_item['name']} (per 100g):\n"
            user_prompt += f"- Calories: {food_item['calories']}\n"
            user_prompt += f"- Protein: {food_item['protein']}g\n"
            user_prompt += f"- Carbohydrates: {food_item['carbs']}g\n"
            user_prompt += f"- Fat: {food_item['fat']}g\n"
            user_prompt += f"- Fiber: {food_item['fiber']}g\n"
            user_prompt += f"- Sugar: {food_item['sugar']}g\n"
        
        full_prompt = f"{system_prompt}\n\nUser Question: {user_prompt}"
        response = model.generate_content(full_prompt)
        
        return response.text.strip()
        
    except Exception as e:
        return f"Gemini AI Error: {e}"

if __name__ == "__main__":
    test_gemini_nutrition()







