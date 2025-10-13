import argparse
import json
import os
import pickle
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

@dataclass
class NutritionItem:
    """Represents a nutrition item with its properties"""
    name: str
    calories: float
    protein: float
    carbs: float
    fat: float
    fiber: float
    sugar: float
    synonyms: List[str] = None
    description: str = ""

class NutritionDataset(Dataset):
    """Dataset for nutrition knowledge"""
    def __init__(self, nutrition_data: List[NutritionItem]):
        self.data = nutrition_data
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        
        # Prepare text data for vectorization
        all_texts = []
        for item in nutrition_data:
            text = f"{item.name} {item.description}"
            if item.synonyms:
                text += " " + " ".join(item.synonyms)
            all_texts.append(text)
        
        self.text_vectors = self.vectorizer.fit_transform(all_texts).toarray()
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        return {
            'name': self.data[idx].name,
            'text_vector': torch.FloatTensor(self.text_vectors[idx]),
            'nutrition': torch.FloatTensor([
                self.data[idx].calories,
                self.data[idx].protein,
                self.data[idx].carbs,
                self.data[idx].fat,
                self.data[idx].fiber,
                self.data[idx].sugar
            ])
        }
    
    def find_similar(self, query: str, top_k: int = 5) -> List[Tuple[NutritionItem, float]]:
        """Find similar nutrition items based on text query"""
        query_vector = self.vectorizer.transform([query]).toarray()
        similarities = cosine_similarity(query_vector, self.text_vectors)[0]
        
        # Get top-k most similar items
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        results = []
        for idx in top_indices:
            if similarities[idx] > 0.1:  # Only include if similarity > 0.1
                results.append((self.data[idx], similarities[idx]))
        return results

class NutritionKnowledgeBase:
    """Knowledge base for nutrition information"""
    
    def __init__(self, dataset_path: Optional[str] = None):
        self.nutrition_data = []
        self.dataset = None
        self.load_default_data()  # Load some default nutrition data
        
        if dataset_path:
            self.load_custom_dataset(dataset_path)
    
    def load_default_data(self):
        """Load default nutrition data for common foods"""
        default_foods = [
            NutritionItem("apple", 52, 0.3, 14, 0.2, 2.4, 10.4, 
                         ["red apple", "green apple", "gala apple"], 
                         "A crisp and sweet fruit"),
            NutritionItem("banana", 89, 1.1, 23, 0.3, 2.6, 12.2,
                         ["yellow banana", "ripe banana"],
                         "A yellow tropical fruit"),
            NutritionItem("chicken breast", 165, 31, 0, 3.6, 0, 0,
                         ["chicken", "grilled chicken", "chicken meat"],
                         "Lean protein source"),
            NutritionItem("brown rice", 111, 2.6, 23, 0.9, 1.8, 0.4,
                         ["rice", "whole grain rice"],
                         "Whole grain carbohydrate"),
            NutritionItem("broccoli", 34, 2.8, 7, 0.4, 2.6, 1.5,
                         ["green broccoli", "fresh broccoli"],
                         "Green cruciferous vegetable"),
            NutritionItem("salmon", 208, 20, 0, 12, 0, 0,
                         ["fish", "salmon fillet", "pink salmon"],
                         "Fatty fish rich in omega-3"),
            NutritionItem("avocado", 160, 2, 9, 15, 7, 0.7,
                         ["avocado fruit", "green avocado"],
                         "Creamy fruit high in healthy fats"),
            NutritionItem("eggs", 155, 13, 1.1, 11, 0, 1.1,
                         ["chicken eggs", "fresh eggs"],
                         "Protein-rich breakfast food"),
            NutritionItem("spinach", 23, 2.9, 3.6, 0.4, 2.2, 0.4,
                         ["leafy greens", "fresh spinach"],
                         "Dark leafy green vegetable"),
            NutritionItem("almonds", 579, 21, 22, 50, 12, 4.4,
                         ["nuts", "almond nuts"],
                         "Nutritious tree nuts")
        ]
        self.nutrition_data.extend(default_foods)
    
    def load_custom_dataset(self, dataset_path: str):
        """Load custom nutrition dataset from file"""
        if dataset_path.endswith('.csv'):
            self.load_csv_dataset(dataset_path)
        elif dataset_path.endswith('.json'):
            self.load_json_dataset(dataset_path)
        else:
            print(f"Unsupported file format: {dataset_path}")
            return
        
        # Create dataset for similarity search
        self.dataset = NutritionDataset(self.nutrition_data)
        print(f"Loaded {len(self.nutrition_data)} nutrition items")
    
    def load_csv_dataset(self, csv_path: str):
        """Load nutrition data from CSV file"""
        try:
            df = pd.read_csv(csv_path)
            required_columns = ['name', 'calories', 'protein', 'carbs', 'fat']
            
            # Check if required columns exist
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                print(f"Missing required columns: {missing_columns}")
                print(f"Available columns: {list(df.columns)}")
                return
            
            for _, row in df.iterrows():
                item = NutritionItem(
                    name=str(row['name']),
                    calories=float(row.get('calories', 0)),
                    protein=float(row.get('protein', 0)),
                    carbs=float(row.get('carbs', 0)),
                    fat=float(row.get('fat', 0)),
                    fiber=float(row.get('fiber', 0)),
                    sugar=float(row.get('sugar', 0)),
                    synonyms=row.get('synonyms', '').split(',') if pd.notna(row.get('synonyms', '')) else [],
                    description=str(row.get('description', ''))
                )
                self.nutrition_data.append(item)
                
        except Exception as e:
            print(f"Error loading CSV dataset: {e}")
    
    def load_json_dataset(self, json_path: str):
        """Load nutrition data from JSON file"""
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            for item_data in data:
                item = NutritionItem(
                    name=item_data['name'],
                    calories=item_data.get('calories', 0),
                    protein=item_data.get('protein', 0),
                    carbs=item_data.get('carbs', 0),
                    fat=item_data.get('fat', 0),
                    fiber=item_data.get('fiber', 0),
                    sugar=item_data.get('sugar', 0),
                    synonyms=item_data.get('synonyms', []),
                    description=item_data.get('description', '')
                )
                self.nutrition_data.append(item)
                
        except Exception as e:
            print(f"Error loading JSON dataset: {e}")
    
    def search_food(self, query: str) -> List[Tuple[NutritionItem, float]]:
        """Search for food items based on query"""
        if not self.dataset:
            self.dataset = NutritionDataset(self.nutrition_data)
        return self.dataset.find_similar(query)
    
    def get_nutrition_info(self, food_name: str) -> Optional[NutritionItem]:
        """Get nutrition information for a specific food"""
        for item in self.nutrition_data:
            if food_name.lower() in item.name.lower() or any(food_name.lower() in syn.lower() for syn in item.synonyms):
                return item
        return None
    
    def save_knowledge_base(self, output_path: str):
        """Save the knowledge base to file"""
        data = []
        for item in self.nutrition_data:
            data.append({
                'name': item.name,
                'calories': item.calories,
                'protein': item.protein,
                'carbs': item.carbs,
                'fat': item.fat,
                'fiber': item.fiber,
                'sugar': item.sugar,
                'synonyms': item.synonyms,
                'description': item.description
            })
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Knowledge base saved to {output_path}")

def create_sample_dataset(output_path: str):
    """Create a sample nutrition dataset for testing"""
    sample_data = [
        {
            "name": "apple",
            "calories": 52,
            "protein": 0.3,
            "carbs": 14,
            "fat": 0.2,
            "fiber": 2.4,
            "sugar": 10.4,
            "synonyms": ["red apple", "green apple", "gala apple"],
            "description": "A crisp and sweet fruit"
        },
        {
            "name": "banana",
            "calories": 89,
            "protein": 1.1,
            "carbs": 23,
            "fat": 0.3,
            "fiber": 2.6,
            "sugar": 12.2,
            "synonyms": ["yellow banana", "ripe banana"],
            "description": "A yellow tropical fruit"
        },
        {
            "name": "chicken breast",
            "calories": 165,
            "protein": 31,
            "carbs": 0,
            "fat": 3.6,
            "fiber": 0,
            "sugar": 0,
            "synonyms": ["chicken", "grilled chicken", "chicken meat"],
            "description": "Lean protein source"
        }
    ]
    
    with open(output_path, 'w') as f:
        json.dump(sample_data, f, indent=2)
    print(f"Sample dataset created at {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Train nutrition knowledge base")
    parser.add_argument("--dataset", type=str, help="Path to nutrition dataset (CSV or JSON)")
    parser.add_argument("--output", type=str, default="models/nutrition_kb.json", 
                       help="Output path for trained knowledge base")
    parser.add_argument("--create-sample", action="store_true", 
                       help="Create a sample dataset for testing")
    
    args = parser.parse_args()
    
    if args.create_sample:
        create_sample_dataset("sample_nutrition_dataset.json")
        return
    
    # Initialize knowledge base
    kb = NutritionKnowledgeBase(args.dataset)
    
    # Save the knowledge base
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    kb.save_knowledge_base(args.output)
    
    # Test the knowledge base
    print("\nTesting knowledge base:")
    test_queries = ["apple", "chicken", "healthy food", "protein"]
    for query in test_queries:
        results = kb.search_food(query)
        print(f"\nQuery: '{query}'")
        for item, score in results[:3]:  # Show top 3 results
            print(f"  {item.name}: {item.calories} cal, {item.protein}g protein (score: {score:.3f})")

if __name__ == "__main__":
    main()
