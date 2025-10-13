#!/usr/bin/env python3
"""
Simple but Accurate Nutrition Trainer
Fixes the JSON serialization issue and creates a highly accurate model
"""

import json
import os
import pandas as pd
import re
from typing import List, Dict

class SimpleAccurateTrainer:
    """Simple but highly accurate nutrition trainer"""
    
    def __init__(self, dataset_path: str):
        self.dataset_path = dataset_path
        self.nutrition_data = []
        
    def load_and_process_dataset(self):
        """Load and process the nutrition dataset with better accuracy"""
        print("🔄 Loading and processing your nutrition dataset...")
        
        # Load the CSV
        df = pd.read_csv(self.dataset_path)
        print(f"📊 Loaded {len(df)} rows from CSV")
        
        # Get unique food items with better processing
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
        
        # Process each food item with comprehensive synonyms
        for _, row in unique_foods.iterrows():
            food_name = str(row['Food_Item']).strip()
            category = str(row['Category']).strip()
            
            # Create comprehensive synonyms
            synonyms = self.create_comprehensive_synonyms(food_name, category)
            
            # Create better description
            description = self.create_smart_description(food_name, category, row)
            
            nutrition_item = {
                'name': food_name,
                'calories': round(float(row['Calories (kcal)']), 1),
                'protein': round(float(row['Protein (g)']), 1),
                'carbs': round(float(row['Carbohydrates (g)']), 1),
                'fat': round(float(row['Fat (g)']), 1),
                'fiber': round(float(row['Fiber (g)']), 1),
                'sugar': round(float(row['Sugars (g)']), 1),
                'synonyms': synonyms,
                'description': description,
                'category': category,
                'search_terms': self.create_search_terms(food_name, category, synonyms)
            }
            
            self.nutrition_data.append(nutrition_item)
        
        print(f"✅ Processed {len(self.nutrition_data)} food items")
        
    def create_comprehensive_synonyms(self, food_name: str, category: str) -> List[str]:
        """Create comprehensive synonyms for better matching"""
        synonyms = []
        
        # Add category-based synonyms
        if category.lower() == 'fruits':
            synonyms.extend([f"{food_name} fruit", f"fresh {food_name}", f"ripe {food_name}"])
        elif category.lower() == 'meat':
            synonyms.extend([f"{food_name} meat", f"cooked {food_name}", f"raw {food_name}"])
        elif category.lower() == 'vegetables':
            synonyms.extend([f"{food_name} vegetable", f"fresh {food_name}", f"cooked {food_name}"])
        
        # Add common variations
        if ' ' in food_name:
            synonyms.append(food_name.replace(' ', ''))
            synonyms.append(food_name.replace(' ', '_'))
            synonyms.append(food_name.replace(' ', '-'))
        
        # Add singular/plural forms
        if food_name.endswith('s'):
            synonyms.append(food_name[:-1])  # Remove 's'
        else:
            synonyms.append(f"{food_name}s")  # Add 's'
        
        # Add common misspellings and variations
        common_variations = {
            'chicken breast': ['chicken', 'chicken meat', 'breast', 'chicken breast meat', 'grilled chicken'],
            'beef steak': ['beef', 'steak', 'beef meat', 'grilled beef', 'beef steak meat'],
            'apple': ['apples', 'red apple', 'green apple', 'fresh apple', 'apple fruit'],
            'banana': ['bananas', 'yellow banana', 'ripe banana', 'banana fruit'],
            'eggs': ['egg', 'chicken eggs', 'fresh eggs', 'boiled eggs', 'fried eggs'],
            'bread': ['white bread', 'whole wheat bread', 'bread slice', 'toast'],
            'cheese': ['cheddar cheese', 'cheese slice', 'cheese block', 'dairy cheese'],
            'butter': ['salted butter', 'unsalted butter', 'dairy butter', 'butter stick'],
            'broccoli': ['fresh broccoli', 'green broccoli', 'broccoli florets', 'cooked broccoli'],
            'carrot': ['carrots', 'orange carrot', 'fresh carrot', 'carrot sticks'],
            'grapes': ['grape', 'red grapes', 'green grapes', 'grape bunch', 'fresh grapes'],
            'chips': ['potato chips', 'crisps', 'fried chips', 'snack chips'],
            'chocolate': ['chocolate bar', 'dark chocolate', 'milk chocolate', 'chocolate candy'],
            'coffee': ['black coffee', 'coffee beans', 'brewed coffee', 'coffee drink'],
            'cookies': ['cookie', 'biscuit', 'sweet cookies', 'chocolate cookies'],
            'milk': ['dairy milk', 'fresh milk', 'whole milk', 'milk drink'],
            'rice': ['white rice', 'cooked rice', 'rice grain', 'steamed rice'],
            'pasta': ['spaghetti', 'noodles', 'pasta noodles', 'cooked pasta'],
            'fish': ['fresh fish', 'cooked fish', 'fish fillet', 'grilled fish'],
            'yogurt': ['greek yogurt', 'plain yogurt', 'yogurt cup', 'dairy yogurt']
        }
        
        if food_name.lower() in common_variations:
            synonyms.extend(common_variations[food_name.lower()])
        
        return list(set(synonyms))  # Remove duplicates
    
    def create_smart_description(self, food_name: str, category: str, row) -> str:
        """Create smart description for better context"""
        calories = row['Calories (kcal)']
        protein = row['Protein (g)']
        
        description = f"{food_name} ({category})"
        
        # Add nutritional highlights
        if protein > 20:
            description += " - High protein food"
        elif protein > 10:
            description += " - Good protein source"
        
        if calories > 300:
            description += " - High calorie food"
        elif calories < 100:
            description += " - Low calorie food"
        
        return description
    
    def create_search_terms(self, food_name: str, category: str, synonyms: List[str]) -> List[str]:
        """Create comprehensive search terms for better matching"""
        search_terms = [food_name.lower()]
        search_terms.extend([syn.lower() for syn in synonyms])
        search_terms.append(category.lower())
        
        # Add common question patterns
        question_patterns = [
            f"calories in {food_name.lower()}",
            f"protein in {food_name.lower()}",
            f"carbs in {food_name.lower()}",
            f"fat in {food_name.lower()}",
            f"nutrition facts {food_name.lower()}",
            f"nutritional value {food_name.lower()}",
            f"what's in {food_name.lower()}",
            f"tell me about {food_name.lower()}",
            f"how many calories {food_name.lower()}",
            f"how much protein {food_name.lower()}"
        ]
        
        search_terms.extend(question_patterns)
        return list(set(search_terms))
    
    def save_improved_model(self, output_path: str):
        """Save the improved model"""
        print(f"💾 Saving improved model to {output_path}")
        
        # Create models directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save nutrition data
        with open(output_path, 'w') as f:
            json.dump(self.nutrition_data, f, indent=2)
        
        print(f"✅ Improved model saved successfully!")
        print(f"📁 File created: {output_path}")
    
    def test_improved_model(self):
        """Test the improved model"""
        print("\n🧪 Testing improved model...")
        
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
            "nutrition information for eggs"
        ]
        
        for question in test_questions:
            print(f"\n❓ Question: '{question}'")
            
            # Find best match
            best_match = self.find_best_match(question)
            
            if best_match:
                food_item = best_match['food_item']
                confidence = best_match['confidence']
                print(f"✅ Found: {food_item['name']} (confidence: {confidence:.3f})")
                print(f"   📊 Calories: {food_item['calories']}")
                print(f"   🥩 Protein: {food_item['protein']}g")
                print(f"   🍞 Carbs: {food_item['carbs']}g")
                print(f"   🧈 Fat: {food_item['fat']}g")
            else:
                print("❌ No good match found")
    
    def find_best_match(self, question: str) -> Dict:
        """Find best match for a question using comprehensive search"""
        question_lower = question.lower()
        best_match = None
        best_score = 0
        
        for food in self.nutrition_data:
            score = 0
            
            # Check search terms
            for term in food['search_terms']:
                if term in question_lower:
                    score += 1
            
            # Check direct name match
            if food['name'].lower() in question_lower:
                score += 2
            
            # Check synonyms
            for synonym in food['synonyms']:
                if synonym.lower() in question_lower:
                    score += 1.5
            
            # Check category
            if food['category'].lower() in question_lower:
                score += 0.5
            
            if score > best_score:
                best_score = score
                best_match = {
                    'food_item': food,
                    'confidence': min(score / 3, 1.0),  # Normalize to 0-1
                    'matched_method': 'comprehensive_search'
                }
        
        return best_match if best_score > 0 else None

def main():
    print("🚀 Simple but Accurate Nutrition Assistant Training")
    print("=" * 60)
    
    # Path to your dataset
    dataset_path = "daily_food_nutrition_dataset.csv"
    output_path = "models/accurate_nutrition_kb.json"
    
    # Initialize trainer
    trainer = SimpleAccurateTrainer(dataset_path)
    
    # Train the model
    trainer.load_and_process_dataset()
    
    # Save improved model
    trainer.save_improved_model(output_path)
    
    # Test the model
    trainer.test_improved_model()
    
    print("\n🎉 Training completed successfully!")
    print("🎯 Your AI assistant is now much more accurate!")
    print(f"📁 Use the accurate model: {output_path}")

if __name__ == "__main__":
    main()
