#!/usr/bin/env python3
"""
Quick test to verify AssemblyAI setup
"""

import os
import json

print("🧪 Quick Test - AssemblyAI Nutrition Assistant Setup")
print("=" * 60)

# Test 1: Check if nutrition data exists
if os.path.exists("models/accurate_nutrition_kb.json"):
    print("✅ Nutrition knowledge base found")
else:
    print("❌ Nutrition knowledge base not found")
    print("💡 Run: py simple_accurate_trainer.py")

# Test 2: Check if AssemblyAI SDK is installed
try:
    import assemblyai as aai
    print("✅ AssemblyAI package installed")
except ImportError:
    print("❌ AssemblyAI package not installed")
    print("💡 Run: py -m pip install assemblyai")

# Test 3: Load KB count
try:
    with open("models/accurate_nutrition_kb.json", 'r') as f:
        data = json.load(f)
    print(f"✅ Loaded {len(data)} food items")
except Exception as e:
    print(f"❌ Error loading nutrition data: {e}")

print("\n🚀 To run the assistant:")
print("1. Get AssemblyAI API key from: https://www.assemblyai.com")
print("2. Run: .\\run_assembly_nutrition.bat")
print("3. Enter your API key when prompted")

print("\n💡 Test questions to try:")
print("- 'How many calories in an apple?'")
print("- 'What's the protein content of chicken breast?'")
print("- 'Make me a 7-day diet plan for weight loss'")

print("\n🎉 AssemblyAI integration ready!")



