#!/usr/bin/env python3
"""
Training script for the Nutrition Voice Assistant

This script helps you train the voice assistant with your nutrition dataset.
It supports multiple data formats and provides comprehensive training options.
"""

import argparse
import json
import os
import sys
from pathlib import Path

# Add training directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'training'))
from nutrition_trainer import NutritionKnowledgeBase, create_sample_dataset

def setup_directories():
    """Create necessary directories"""
    directories = ['models', 'data', 'training_output']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def create_sample_datasets():
    """Create sample datasets in different formats"""
    print("📊 Creating sample datasets...")
    
    # Create JSON sample
    create_sample_dataset("data/sample_nutrition_dataset.json")
    
    # Create CSV sample
    import pandas as pd
    sample_data = [
        {
            "name": "apple",
            "calories": 52,
            "protein": 0.3,
            "carbs": 14,
            "fat": 0.2,
            "fiber": 2.4,
            "sugar": 10.4,
            "synonyms": "red apple,green apple,gala apple",
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
            "synonyms": "yellow banana,ripe banana",
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
            "synonyms": "chicken,grilled chicken,chicken meat",
            "description": "Lean protein source"
        },
        {
            "name": "brown rice",
            "calories": 111,
            "protein": 2.6,
            "carbs": 23,
            "fat": 0.9,
            "fiber": 1.8,
            "sugar": 0.4,
            "synonyms": "rice,whole grain rice",
            "description": "Whole grain carbohydrate"
        },
        {
            "name": "broccoli",
            "calories": 34,
            "protein": 2.8,
            "carbs": 7,
            "fat": 0.4,
            "fiber": 2.6,
            "sugar": 1.5,
            "synonyms": "green broccoli,fresh broccoli",
            "description": "Green cruciferous vegetable"
        }
    ]
    
    df = pd.DataFrame(sample_data)
    df.to_csv("data/sample_nutrition_dataset.csv", index=False)
    print("✅ Created sample datasets:")
    print("   - data/sample_nutrition_dataset.json")
    print("   - data/sample_nutrition_dataset.csv")

def train_with_dataset(dataset_path: str, output_path: str = "models/nutrition_kb.json"):
    """Train the nutrition knowledge base with a dataset"""
    print(f"🔬 Training with dataset: {dataset_path}")
    
    if not os.path.exists(dataset_path):
        print(f"❌ Dataset not found: {dataset_path}")
        return False
    
    try:
        # Load and train the knowledge base
        kb = NutritionKnowledgeBase(dataset_path)
        
        # Save the trained model
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        kb.save_knowledge_base(output_path)
        
        print(f"✅ Training completed! Knowledge base saved to: {output_path}")
        print(f"📊 Loaded {len(kb.nutrition_data)} nutrition items")
        
        # Test the knowledge base
        print("\n🧪 Testing the knowledge base:")
        test_queries = ["apple", "chicken", "healthy food", "protein"]
        for query in test_queries:
            results = kb.search_food(query)
            if results:
                best_match, score = results[0]
                print(f"   '{query}' → {best_match.name} (confidence: {score:.3f})")
        
        return True
        
    except Exception as e:
        print(f"❌ Training failed: {e}")
        return False

def validate_dataset_format(dataset_path: str):
    """Validate dataset format and provide guidance"""
    print(f"🔍 Validating dataset: {dataset_path}")
    
    if not os.path.exists(dataset_path):
        print(f"❌ File not found: {dataset_path}")
        return False
    
    file_ext = os.path.splitext(dataset_path)[1].lower()
    
    if file_ext == '.csv':
        try:
            import pandas as pd
            df = pd.read_csv(dataset_path)
            required_columns = ['name', 'calories', 'protein', 'carbs', 'fat']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                print(f"❌ Missing required columns: {missing_columns}")
                print(f"📋 Available columns: {list(df.columns)}")
                print("💡 Required columns: name, calories, protein, carbs, fat")
                print("💡 Optional columns: fiber, sugar, synonyms, description")
                return False
            else:
                print("✅ CSV format is valid")
                return True
                
        except Exception as e:
            print(f"❌ CSV validation failed: {e}")
            return False
    
    elif file_ext == '.json':
        try:
            with open(dataset_path, 'r') as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                print("❌ JSON should contain a list of nutrition items")
                return False
            
            if not data:
                print("❌ JSON file is empty")
                return False
            
            # Check first item structure
            first_item = data[0]
            required_fields = ['name', 'calories', 'protein', 'carbs', 'fat']
            missing_fields = [field for field in required_fields if field not in first_item]
            
            if missing_fields:
                print(f"❌ Missing required fields: {missing_fields}")
                print("💡 Required fields: name, calories, protein, carbs, fat")
                print("💡 Optional fields: fiber, sugar, synonyms, description")
                return False
            else:
                print("✅ JSON format is valid")
                return True
                
        except Exception as e:
            print(f"❌ JSON validation failed: {e}")
            return False
    
    else:
        print(f"❌ Unsupported file format: {file_ext}")
        print("💡 Supported formats: .csv, .json")
        return False

def main():
    parser = argparse.ArgumentParser(description="Train Nutrition Voice Assistant")
    parser.add_argument("--dataset", type=str, help="Path to your nutrition dataset (CSV or JSON)")
    parser.add_argument("--output", type=str, default="models/nutrition_kb.json",
                       help="Output path for trained knowledge base")
    parser.add_argument("--create-samples", action="store_true",
                       help="Create sample datasets for testing")
    parser.add_argument("--validate-only", action="store_true",
                       help="Only validate dataset format without training")
    parser.add_argument("--setup", action="store_true",
                       help="Set up directories and create sample datasets")
    
    args = parser.parse_args()
    
    print("🥗 Nutrition Voice Assistant Training")
    print("=" * 50)
    
    # Setup mode
    if args.setup:
        setup_directories()
        create_sample_datasets()
        print("\n✅ Setup completed!")
        print("📁 Check the 'data' folder for sample datasets")
        print("🚀 Run with --dataset data/sample_nutrition_dataset.json to train")
        return
    
    # Create samples mode
    if args.create_samples:
        setup_directories()
        create_sample_datasets()
        return
    
    # Validate only mode
    if args.validate_only:
        if not args.dataset:
            print("❌ Please provide --dataset path for validation")
            return
        validate_dataset_format(args.dataset)
        return
    
    # Training mode
    if not args.dataset:
        print("❌ Please provide --dataset path for training")
        print("💡 Use --setup to create sample datasets")
        print("💡 Use --create-samples to generate sample data")
        return
    
    # Validate dataset first
    if not validate_dataset_format(args.dataset):
        print("\n❌ Dataset validation failed. Please fix the format and try again.")
        return
    
    # Train the model
    success = train_with_dataset(args.dataset, args.output)
    
    if success:
        print("\n🎉 Training completed successfully!")
        print(f"📁 Knowledge base saved to: {args.output}")
        print("\n🚀 To run the nutrition assistant:")
        print(f"   python nutrition_app.py --model vosk-model-small-en-us-0.15/vosk-model-small-en-us-0.15 --nutrition-kb {args.output} --device 0")
    else:
        print("\n❌ Training failed. Please check the error messages above.")

if __name__ == "__main__":
    main()
