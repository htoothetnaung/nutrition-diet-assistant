# Nutrition Voice Assistant Training Guide

This guide will help you train the voice assistant with your nutrition dataset.

## 🚀 Quick Start

### 1. Set up the environment
```bash
# Install dependencies
pip install -r requirements.txt

# Set up directories and create sample datasets
python train_nutrition_assistant.py --setup
```

### 2. Train with your dataset
```bash
# Train with your nutrition dataset
python train_nutrition_assistant.py --dataset your_nutrition_data.csv --output models/nutrition_kb.json
```

### 3. Run the nutrition assistant
```bash
# Run the nutrition voice assistant
python nutrition_app.py --model vosk-model-small-en-us-0.15/vosk-model-small-en-us-0.15 --nutrition-kb models/nutrition_kb.json --device 0
```

## 📊 Dataset Formats

The training system supports two formats for your nutrition dataset:

### CSV Format
Create a CSV file with the following columns:

**Required columns:**
- `name`: Food name (e.g., "apple", "chicken breast")
- `calories`: Calories per 100g
- `protein`: Protein content in grams
- `carbs`: Carbohydrates in grams
- `fat`: Fat content in grams

**Optional columns:**
- `fiber`: Fiber content in grams
- `sugar`: Sugar content in grams
- `synonyms`: Comma-separated synonyms (e.g., "red apple,green apple")
- `description`: Food description

**Example CSV:**
```csv
name,calories,protein,carbs,fat,fiber,sugar,synonyms,description
apple,52,0.3,14,0.2,2.4,10.4,"red apple,green apple,gala apple",A crisp and sweet fruit
chicken breast,165,31,0,3.6,0,0,"chicken,grilled chicken",Lean protein source
```

### JSON Format
Create a JSON file with an array of nutrition objects:

**Example JSON:**
```json
[
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
    "name": "chicken breast",
    "calories": 165,
    "protein": 31,
    "carbs": 0,
    "fat": 3.6,
    "fiber": 0,
    "sugar": 0,
    "synonyms": ["chicken", "grilled chicken"],
    "description": "Lean protein source"
  }
]
```

## 🛠️ Training Commands

### Basic Training
```bash
# Train with your dataset
python train_nutrition_assistant.py --dataset data/your_nutrition_data.csv

# Specify custom output path
python train_nutrition_assistant.py --dataset data/your_nutrition_data.json --output models/my_nutrition_kb.json
```

### Dataset Validation
```bash
# Validate your dataset format without training
python train_nutrition_assistant.py --dataset data/your_nutrition_data.csv --validate-only
```

### Create Sample Datasets
```bash
# Create sample datasets for testing
python train_nutrition_assistant.py --create-samples
```

## 🎤 Using the Nutrition Assistant

### Voice Commands
The assistant can understand various nutrition-related questions:

- **Calorie queries**: "What are the calories in an apple?"
- **Nutrition facts**: "Tell me about chicken nutrition"
- **Specific nutrients**: "How much protein is in salmon?"
- **General queries**: "What's in broccoli?"

### Example Interactions
```
You: "What are the calories in an apple?"
Assistant: "Here's the nutrition information for apple:
• Calories: 52 per 100g
• Protein: 0.3g
• Carbohydrates: 14g
• Fat: 0.2g
• Fiber: 2.4g
• Sugar: 10.4g

A crisp and sweet fruit"
```

## 📁 File Structure

After training, your project will have:
```
realtime_voice_assistant/
├── models/
│   └── nutrition_kb.json          # Trained nutrition knowledge base
├── data/
│   ├── sample_nutrition_dataset.csv
│   └── sample_nutrition_dataset.json
├── training/
│   └── nutrition_trainer.py       # Core training logic
├── nutrition_app.py               # Enhanced voice assistant
├── train_nutrition_assistant.py   # Training script
└── requirements.txt               # Dependencies
```

## 🔧 Troubleshooting

### Common Issues

1. **"Dataset not found"**
   - Check the file path is correct
   - Make sure the file exists

2. **"Missing required columns"**
   - Ensure your CSV has: name, calories, protein, carbs, fat
   - Check column names match exactly

3. **"No nutrition information available"**
   - Make sure the knowledge base was trained successfully
   - Check the nutrition_kb.json file exists

4. **Audio issues**
   - Use `--list-devices` to see available microphones
   - Try different device indices with `--device`

### Validation Tips

1. **Test your dataset format**:
   ```bash
   python train_nutrition_assistant.py --dataset your_data.csv --validate-only
   ```

2. **Check the knowledge base**:
   ```bash
   python -c "
   import json
   with open('models/nutrition_kb.json') as f:
       data = json.load(f)
   print(f'Loaded {len(data)} items')
   print('Sample item:', data[0])
   "
   ```

## 🎯 Tips for Better Results

1. **Include synonyms**: Add common alternative names for foods
2. **Use consistent units**: All nutritional values should be per 100g
3. **Add descriptions**: Help the assistant understand context
4. **Test with sample data**: Start with the provided sample datasets
5. **Validate before training**: Always validate your dataset format first

## 📈 Advanced Usage

### Custom Training Parameters
You can modify the training parameters in `training/nutrition_trainer.py`:

- `max_features`: Number of TF-IDF features (default: 1000)
- `similarity_threshold`: Minimum similarity for matches (default: 0.1)

### Adding More Food Items
Simply add more rows to your dataset and retrain:

```bash
python train_nutrition_assistant.py --dataset updated_nutrition_data.csv
```

The assistant will automatically learn about new foods!

## 🆘 Getting Help

If you encounter issues:

1. Check the troubleshooting section above
2. Validate your dataset format
3. Test with the sample datasets first
4. Check the console output for error messages

The system is designed to be robust and provide helpful error messages to guide you through any issues.
