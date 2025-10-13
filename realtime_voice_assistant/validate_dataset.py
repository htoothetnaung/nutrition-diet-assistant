#!/usr/bin/env python3
"""
Validate your nutrition dataset and show statistics
"""

import json

def validate_dataset():
    """Validate and analyze the nutrition dataset"""
    
    print("📊 Nutrition Dataset Validation")
    print("=" * 50)
    
    # Load dataset
    with open('models/nutrition_kb.json', 'r') as f:
        data = json.load(f)
    
    print(f"✅ Dataset loaded successfully")
    print(f"📈 Total food items: {len(data)}")
    print()
    
    # Check data quality
    print("🔍 Data Quality Check:")
    print("-" * 25)
    
    missing_data = 0
    zero_calories = 0
    high_calories = 0
    
    for item in data:
        if not item.get('name'):
            missing_data += 1
        if item.get('calories', 0) == 0:
            zero_calories += 1
        if item.get('calories', 0) > 1000:
            high_calories += 1
    
    print(f"✅ Items with names: {len(data) - missing_data}/{len(data)}")
    print(f"⚠️  Items with zero calories: {zero_calories}")
    print(f"⚠️  Items with >1000 calories: {high_calories}")
    print()
    
    # Show statistics
    print("📈 Nutrition Statistics:")
    print("-" * 25)
    
    calories = [item.get('calories', 0) for item in data]
    proteins = [item.get('protein', 0) for item in data]
    carbs = [item.get('carbs', 0) for item in data]
    fats = [item.get('fat', 0) for item in data]
    
    print(f"Calories - Min: {min(calories):.1f}, Max: {max(calories):.1f}, Avg: {sum(calories)/len(calories):.1f}")
    print(f"Protein  - Min: {min(proteins):.1f}, Max: {max(proteins):.1f}, Avg: {sum(proteins)/len(proteins):.1f}")
    print(f"Carbs    - Min: {min(carbs):.1f}, Max: {max(carbs):.1f}, Avg: {sum(carbs)/len(carbs):.1f}")
    print(f"Fat      - Min: {min(fats):.1f}, Max: {max(fats):.1f}, Avg: {sum(fats)/len(fats):.1f}")
    print()
    
    # Show sample items
    print("🍎 Sample Food Items:")
    print("-" * 20)
    for i, item in enumerate(data[:10]):
        print(f"{i+1:2d}. {item['name']:20s} - {item['calories']:6.1f} cal")
    
    if len(data) > 10:
        print(f"... and {len(data) - 10} more items")
    
    print()
    print("✅ Dataset validation completed!")
    print("🎯 Your nutrition assistant is ready to use!")

if __name__ == "__main__":
    validate_dataset()








