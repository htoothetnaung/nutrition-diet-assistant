#!/usr/bin/env python3
"""
Simple script to help prepare your CSV file for nutrition training
This script will check your CSV format and help convert it if needed
"""

import pandas as pd
import sys
import os

def check_csv_format(csv_path):
    """Check and display CSV format information"""
    try:
        print(f"📊 Analyzing CSV file: {csv_path}")
        print("=" * 50)
        
        # Read the CSV
        df = pd.read_csv(csv_path)
        
        print(f"✅ Successfully loaded CSV")
        print(f"📈 Number of rows: {len(df)}")
        print(f"📋 Number of columns: {len(df.columns)}")
        print()
        
        print("📝 Column names found:")
        for i, col in enumerate(df.columns):
            print(f"  {i+1}. '{col}'")
        print()
        
        print("🔍 First few rows:")
        print(df.head(3).to_string())
        print()
        
        # Check for required columns
        required_columns = ['food name', 'cal', 'nutrients']
        found_columns = []
        missing_columns = []
        
        for req_col in required_columns:
            if req_col in df.columns:
                found_columns.append(req_col)
            else:
                missing_columns.append(req_col)
        
        print("✅ Required columns found:")
        for col in found_columns:
            print(f"  - {col}")
        
        if missing_columns:
            print("❌ Missing required columns:")
            for col in missing_columns:
                print(f"  - {col}")
        
        # Check for similar column names
        print("\n🔍 Looking for similar column names...")
        all_columns = [col.lower().strip() for col in df.columns]
        
        # Look for calories column
        calorie_variants = ['cal', 'calories', 'kcal', 'energy']
        for variant in calorie_variants:
            for col in df.columns:
                if variant in col.lower():
                    print(f"  Found potential calories column: '{col}'")
        
        # Look for protein column
        protein_variants = ['protein', 'prot', 'g protein']
        for variant in protein_variants:
            for col in df.columns:
                if variant in col.lower():
                    print(f"  Found potential protein column: '{col}'")
        
        # Look for carbs column
        carb_variants = ['carbs', 'carbohydrates', 'carb', 'g carbs']
        for variant in carb_variants:
            for col in df.columns:
                if variant in col.lower():
                    print(f"  Found potential carbs column: '{col}'")
        
        # Look for fat column
        fat_variants = ['fat', 'g fat', 'total fat']
        for variant in fat_variants:
            for col in df.columns:
                if variant in col.lower():
                    print(f"  Found potential fat column: '{col}'")
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return False

def create_converted_csv(input_path, output_path):
    """Create a converted CSV with the correct format"""
    try:
        print(f"🔄 Converting CSV to training format...")
        
        df = pd.read_csv(input_path)
        
        # Create a new dataframe with the required format
        converted_data = []
        
        for _, row in df.iterrows():
            # Extract food name
            food_name = str(row.get('food name', row.get('name', ''))).strip()
            if not food_name:
                continue
            
            # Extract calories
            calories = 0
            for col in df.columns:
                if 'cal' in col.lower() and pd.notna(row[col]):
                    try:
                        calories = float(row[col])
                        break
                    except:
                        pass
            
            # Extract nutrients from the nutrients column
            nutrients_text = str(row.get('nutrients', '')).lower()
            
            # Try to extract protein, carbs, fat from nutrients text
            protein = 0
            carbs = 0
            fat = 0
            fiber = 0
            sugar = 0
            
            # Simple extraction (you might need to adjust based on your format)
            import re
            
            # Look for patterns like "protein: 10g" or "10g protein"
            protein_match = re.search(r'protein[:\s]*(\d+\.?\d*)\s*g', nutrients_text)
            if protein_match:
                protein = float(protein_match.group(1))
            
            carbs_match = re.search(r'(?:carbs|carbohydrates)[:\s]*(\d+\.?\d*)\s*g', nutrients_text)
            if carbs_match:
                carbs = float(carbs_match.group(1))
            
            fat_match = re.search(r'fat[:\s]*(\d+\.?\d*)\s*g', nutrients_text)
            if fat_match:
                fat = float(fat_match.group(1))
            
            fiber_match = re.search(r'fiber[:\s]*(\d+\.?\d*)\s*g', nutrients_text)
            if fiber_match:
                fiber = float(fiber_match.group(1))
            
            sugar_match = re.search(r'sugar[:\s]*(\d+\.?\d*)\s*g', nutrients_text)
            if sugar_match:
                sugar = float(sugar_match.group(1))
            
            converted_data.append({
                'name': food_name,
                'calories': calories,
                'protein': protein,
                'carbs': carbs,
                'fat': fat,
                'fiber': fiber,
                'sugar': sugar,
                'synonyms': '',
                'description': f"Nutrition information for {food_name}"
            })
        
        # Create new dataframe
        converted_df = pd.DataFrame(converted_data)
        
        # Save converted CSV
        converted_df.to_csv(output_path, index=False)
        
        print(f"✅ Converted CSV saved to: {output_path}")
        print(f"📊 Converted {len(converted_data)} food items")
        
        # Show sample of converted data
        print("\n📝 Sample of converted data:")
        print(converted_df.head(3).to_string())
        
        return True
        
    except Exception as e:
        print(f"❌ Error converting CSV: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python prepare_csv.py <your_csv_file.csv>")
        print("Example: python prepare_csv.py my_nutrition_data.csv")
        return
    
    csv_path = sys.argv[1]
    
    if not os.path.exists(csv_path):
        print(f"❌ File not found: {csv_path}")
        return
    
    # Check the CSV format
    if check_csv_format(csv_path):
        print("\n" + "=" * 50)
        print("🎯 Next steps:")
        print("1. If the format looks good, you can train with:")
        print(f"   python train_nutrition_assistant.py --dataset {csv_path}")
        print()
        print("2. If you need to convert the format, run:")
        print(f"   python prepare_csv.py {csv_path} --convert")
        print()
        print("3. The converted file will be saved as 'converted_nutrition_data.csv'")
    
    # Check if user wants to convert
    if len(sys.argv) > 2 and sys.argv[2] == '--convert':
        output_path = 'converted_nutrition_data.csv'
        create_converted_csv(csv_path, output_path)

if __name__ == "__main__":
    main()



