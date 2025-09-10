#!/usr/bin/env python3
"""
Interactive testing for your nutrition assistant
Type questions and get answers without microphone
"""

import json
import sys

def interactive_nutrition_test():
    """Interactive test where you type questions"""
    
    print("🧪 Interactive Nutrition Assistant Test")
    print("=" * 50)
    print("Type nutrition questions and get answers!")
    print("Type 'quit' to exit")
    print()
    
    # Load nutrition data
    with open('models/nutrition_kb.json', 'r') as f:
        nutrition_data = json.load(f)
    
    print(f"📊 Loaded {len(nutrition_data)} food items")
    print("💡 Try: 'apple', 'chicken breast', 'banana', 'eggs'")
    print()
    
    while True:
        try:
            # Get user input
            question = input("❓ Your question: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not question:
                continue
            
            # Process the question
            answer = process_nutrition_question(nutrition_data, question)
            print(f"🤖 Answer: {answer}")
            print()
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def process_nutrition_question(nutrition_data, question):
    """Process a nutrition question and return answer"""
    
    question_lower = question.lower()
    
    # Check if it's a nutrition question
    nutrition_keywords = [
        "calories", "calorie", "nutrition", "nutrients", "protein", "carbs", 
        "carbohydrates", "fat", "fiber", "sugar", "healthy", "diet", "food"
    ]
    
    is_nutrition = any(keyword in question_lower for keyword in nutrition_keywords)
    
    if not is_nutrition:
        return "I'm a nutrition assistant. Try asking about food nutrition facts!"
    
    # Extract food name
    food_name = extract_food_name(question)
    
    if not food_name:
        return "I didn't catch the food name. Try asking about a specific food item."
    
    # Find the food
    food_item = find_food(nutrition_data, food_name)
    
    if not food_item:
        return f"I don't have nutrition information for '{food_name}'. Try asking about a different food."
    
    # Generate answer
    answer = f"Here's the nutrition information for {food_item['name']}:\n"
    answer += f"• Calories: {food_item['calories']} per 100g\n"
    answer += f"• Protein: {food_item['protein']}g\n"
    answer += f"• Carbohydrates: {food_item['carbs']}g\n"
    answer += f"• Fat: {food_item['fat']}g\n"
    
    if food_item.get('fiber', 0) > 0:
        answer += f"• Fiber: {food_item['fiber']}g\n"
    if food_item.get('sugar', 0) > 0:
        answer += f"• Sugar: {food_item['sugar']}g\n"
    
    return answer

def extract_food_name(question):
    """Extract food name from question"""
    question_lower = question.lower()
    
    # Remove common question patterns
    patterns = [
        "what are the calories in", "calories in", "how many calories in",
        "tell me about", "nutrition", "nutrition facts for", "what's in",
        "how much protein is in", "protein in", "carbs in", "fat in"
    ]
    
    for pattern in patterns:
        question_lower = question_lower.replace(pattern, "").strip()
    
    # Remove common words
    common_words = ["an", "a", "the", "of", "for", "about", "in"]
    words = [word for word in question_lower.split() if word not in common_words]
    
    return " ".join(words) if words else None

def find_food(nutrition_data, query):
    """Find food item in dataset"""
    query_lower = query.lower()
    
    # Direct name match
    for item in nutrition_data:
        if query_lower in item['name'].lower():
            return item
    
    # Synonym match
    for item in nutrition_data:
        for synonym in item.get('synonyms', []):
            if query_lower in synonym.lower():
                return item
    
    # Partial match
    for item in nutrition_data:
        if any(word in item['name'].lower() for word in query_lower.split()):
            return item
    
    return None

if __name__ == "__main__":
    interactive_nutrition_test()








