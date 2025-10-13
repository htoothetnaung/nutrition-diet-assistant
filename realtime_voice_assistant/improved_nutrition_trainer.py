#!/usr/bin/env python3
"""
Improved Nutrition Trainer with Better Accuracy
This will train your AI to understand questions much better
"""

import json
import pandas as pd
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from typing import List, Dict, Tuple

class ImprovedNutritionTrainer:
    """Improved trainer for better nutrition question understanding"""
    
    def __init__(self, dataset_path: str):
        self.dataset_path = dataset_path
        self.nutrition_data = []
        self.question_patterns = []
        self.vectorizer = None
        self.question_vectors = None
        
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
        
        # Process each food item with better synonyms and descriptions
        for _, row in unique_foods.iterrows():
            food_name = str(row['Food_Item']).strip()
            category = str(row['Category']).strip()
            
            # Create comprehensive synonyms
            synonyms = self.create_smart_synonyms(food_name, category)
            
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
                'category': category
            }
            
            self.nutrition_data.append(nutrition_item)
        
        print(f"✅ Processed {len(self.nutrition_data)} food items")
        
    def create_smart_synonyms(self, food_name: str, category: str) -> List[str]:
        """Create smart synonyms for better matching"""
        synonyms = []
        
        # Add category-based synonyms
        if category.lower() == 'fruits':
            synonyms.extend([f"{food_name} fruit", f"fresh {food_name}"])
        elif category.lower() == 'meat':
            synonyms.extend([f"{food_name} meat", f"cooked {food_name}"])
        elif category.lower() == 'vegetables':
            synonyms.extend([f"{food_name} vegetable", f"fresh {food_name}"])
        
        # Add common variations
        if ' ' in food_name:
            synonyms.append(food_name.replace(' ', ''))
            synonyms.append(food_name.replace(' ', '_'))
        
        # Add singular/plural forms
        if food_name.endswith('s'):
            synonyms.append(food_name[:-1])  # Remove 's'
        else:
            synonyms.append(f"{food_name}s")  # Add 's'
        
        # Add common misspellings and variations
        common_variations = {
            'chicken breast': ['chicken', 'chicken meat', 'breast'],
            'beef steak': ['beef', 'steak', 'beef meat'],
            'chicken breast': ['chicken', 'chicken meat', 'breast'],
            'apple': ['apples', 'red apple', 'green apple'],
            'banana': ['bananas', 'yellow banana'],
            'eggs': ['egg', 'chicken eggs'],
            'bread': ['white bread', 'whole wheat bread'],
            'cheese': ['cheddar cheese', 'cheese slice'],
            'butter': ['salted butter', 'unsalted butter'],
            'broccoli': ['fresh broccoli', 'green broccoli'],
            'carrot': ['carrots', 'orange carrot'],
            'grapes': ['grape', 'red grapes', 'green grapes']
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
            description += " - High protein"
        elif protein > 10:
            description += " - Good protein source"
        
        if calories > 300:
            description += " - High calorie"
        elif calories < 100:
            description += " - Low calorie"
        
        return description
    
    def create_question_patterns(self):
        """Create comprehensive question patterns for training"""
        print("🧠 Creating question patterns for better understanding...")
        
        # Common question patterns
        patterns = [
            # Calorie questions
            "how many calories in {food}",
            "what are the calories in {food}",
            "calories in {food}",
            "how many calories does {food} have",
            "calorie content of {food}",
            
            # Protein questions
            "how much protein in {food}",
            "protein content of {food}",
            "protein in {food}",
            "how much protein does {food} have",
            
            # General nutrition questions
            "nutrition facts for {food}",
            "nutritional value of {food}",
            "what's in {food}",
            "tell me about {food} nutrition",
            "nutrition information for {food}",
            "what nutrients are in {food}",
            
            # Carbs questions
            "how many carbs in {food}",
            "carbohydrates in {food}",
            "carbs in {food}",
            
            # Fat questions
            "how much fat in {food}",
            "fat content of {food}",
            "fat in {food}",
            
            # General questions
            "tell me about {food}",
            "what is {food}",
            "information about {food}",
            "details about {food}"
        ]
        
        # Generate patterns for each food
        self.question_patterns = []
        for food in self.nutrition_data:
            food_name = food['name'].lower()
            for pattern in patterns:
                question = pattern.format(food=food_name)
                self.question_patterns.append({
                    'question': question,
                    'food_name': food_name,
                    'food_item': food
                })
        
        print(f"✅ Created {len(self.question_patterns)} question patterns")
    
    def train_similarity_model(self):
        """Train a similarity model for better question understanding"""
        print("🤖 Training similarity model for better accuracy...")
        
        # Prepare text data for training
        all_texts = []
        for pattern in self.question_patterns:
            all_texts.append(pattern['question'])
        
        # Add food names and synonyms
        for food in self.nutrition_data:
            all_texts.append(food['name'])
            all_texts.extend(food['synonyms'])
            all_texts.append(food['description'])
        
        # Train TF-IDF vectorizer
        self.vectorizer = TfidfVectorizer(
            max_features=2000,
            stop_words='english',
            ngram_range=(1, 2),  # Use unigrams and bigrams
            min_df=1
        )
        
        self.question_vectors = self.vectorizer.fit_transform(all_texts)
        print("✅ Similarity model trained successfully")
    
    def save_improved_model(self, output_path: str):
        """Save the improved model"""
        print(f"💾 Saving improved model to {output_path}")
        
        # Save nutrition data
        with open(output_path, 'w') as f:
            json.dump(self.nutrition_data, f, indent=2)
        
        # Save question patterns
        patterns_path = output_path.replace('.json', '_patterns.json')
        with open(patterns_path, 'w') as f:
            json.dump(self.question_patterns, f, indent=2)
        
        # Save vectorizer (simplified version)
        vectorizer_path = output_path.replace('.json', '_vectorizer.json')
        vectorizer_data = {
            'vocabulary': self.vectorizer.vocabulary_,
            'idf': self.vectorizer.idf_.tolist(),
            'feature_names': self.vectorizer.get_feature_names_out().tolist()
        }
        with open(vectorizer_path, 'w') as f:
            json.dump(vectorizer_data, f, indent=2)
        
        print(f"✅ Improved model saved successfully!")
        print(f"📁 Files created:")
        print(f"   - {output_path}")
        print(f"   - {patterns_path}")
        print(f"   - {vectorizer_path}")
    
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
            "calories in cheese"
        ]
        
        for question in test_questions:
            print(f"\n❓ Question: '{question}'")
            
            # Find best match using similarity
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
        """Find best match for a question using similarity"""
        if not self.vectorizer or self.question_vectors is None:
            return None
        
        # Vectorize the question
        question_vector = self.vectorizer.transform([question])
        
        # Calculate similarities
        similarities = cosine_similarity(question_vector, self.question_vectors)[0]
        
        # Find best match
        best_idx = np.argmax(similarities)
        best_similarity = similarities[best_idx]
        
        if best_similarity > 0.1:  # Threshold for confidence
            return {
                'food_item': self.question_patterns[best_idx]['food_item'],
                'confidence': best_similarity,
                'matched_pattern': self.question_patterns[best_idx]['question']
            }
        
        return None

def main():
    print("🚀 Improved Nutrition Assistant Training")
    print("=" * 50)
    
    # Path to your dataset
    dataset_path = "daily_food_nutrition_dataset.csv"
    output_path = "models/improved_nutrition_kb.json"
    
    # Initialize trainer
    trainer = ImprovedNutritionTrainer(dataset_path)
    
    # Train the model
    trainer.load_and_process_dataset()
    trainer.create_question_patterns()
    trainer.train_similarity_model()
    
    # Save improved model
    trainer.save_improved_model(output_path)
    
    # Test the model
    trainer.test_improved_model()
    
    print("\n🎉 Training completed successfully!")
    print("🎯 Your AI assistant is now much more accurate!")
    print(f"📁 Use the improved model: {output_path}")

if __name__ == "__main__":
    main()








