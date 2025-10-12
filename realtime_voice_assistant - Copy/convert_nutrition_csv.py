#!/usr/bin/env python3
"""
Convert the daily food nutrition dataset to the training format
"""

import pandas as pd
import json
import os

def convert_nutrition_dataset(input_csv, output_json):
    """Convert the daily food nutrition dataset to training format"""
    
    print(f"🔄 Converting {input_csv} to training format...")
    
    # Read the CSV
    df = pd.read_csv(input_csv)
    print(f"📊 Loaded {len(df)} rows from CSV")
    
    # Get unique food items (remove duplicates)
    unique_foods = df.groupby('Food_Item').agg({
        'Calories (kcal)': 'mean',
        'Protein (g)': 'mean', 
        'Carbohydrates (g)': 'mean',
        'Fat (g)': 'mean',
        'Fiber (g)': 'mean',
        'Sugars (g)': 'mean',
        'Category': 'first'
    }).reset_index()
    
    print(f"🍎 Found {len(unique_foods)} unique food items")
    
    # Convert to training format
    nutrition_data = []
    
    for _, row in unique_foods.iterrows():
        food_name = str(row['Food_Item']).strip()
        category = str(row['Category']).strip()
        
        # Create synonyms based on category
        synonyms = []
        if category.lower() == 'fruits':
            synonyms.append(f"{food_name} fruit")
        elif category.lower() == 'meat':
            synonyms.append(f"{food_name} meat")
        elif category.lower() == 'vegetables':
            synonyms.append(f"{food_name} vegetable")
        
        # Add common variations
        if ' ' in food_name:
            synonyms.append(food_name.replace(' ', ''))
        
        nutrition_item = {
            'name': food_name,
            'calories': round(float(row['Calories (kcal)']), 1),
            'protein': round(float(row['Protein (g)']), 1),
            'carbs': round(float(row['Carbohydrates (g)']), 1),
            'fat': round(float(row['Fat (g)']), 1),
            'fiber': round(float(row['Fiber (g)']), 1),
            'sugar': round(float(row['Sugars (g)']), 1),
            'synonyms': synonyms,
            'description': f"{food_name} ({category})"
        }
        
        nutrition_data.append(nutrition_item)
    
    # Save as JSON
    os.makedirs(os.path.dirname(output_json), exist_ok=True)
    with open(output_json, 'w') as f:
        json.dump(nutrition_data, f, indent=2)
    
    print(f"✅ Converted dataset saved to: {output_json}")
    print(f"📊 Converted {len(nutrition_data)} unique food items")
    
    # Show sample
    print("\n📝 Sample of converted data:")
    for i, item in enumerate(nutrition_data[:3]):
        print(f"  {i+1}. {item['name']}: {item['calories']} cal, {item['protein']}g protein")
    
    return True

def main():
    input_csv = "daily_food_nutrition_dataset.csv"
    output_json = "models/nutrition_kb.json"
    
    if not os.path.exists(input_csv):
        print(f"❌ Input file not found: {input_csv}")
        return
    
    success = convert_nutrition_dataset(input_csv, output_json)
    
    if success:
        print("\n🎉 Conversion completed successfully!")
        print("🚀 You can now run the nutrition assistant:")
        print("   python nutrition_app.py --model vosk-model-small-en-us-0.15/vosk-model-small-en-us-0.15 --nutrition-kb models/nutrition_kb.json --device 0")
    else:
        print("❌ Conversion failed!")

if __name__ == "__main__":
    main()



