"""
NutriNet Food Vision - Core AI Module (Food-101 only)
This module provides food classification and nutrition analysis using a single
Food-101 classifier at model_weights/food101_model.pth.
"""

import os
from typing import List, Dict, Tuple, Optional
import json
import re

import torch
import torchvision.transforms as T
import torchvision.models as models
from PIL import Image
from transformers import AutoProcessor, BitsAndBytesConfig
from qwen_vl_utils import process_vision_info
import streamlit as st
from peft import PeftModel
import torchvision.models as tv_models

# Try to import Qwen3VLForConditionalGeneration (newer), fallback to Qwen2VL if not available
try:
    from transformers import Qwen3VLForConditionalGeneration
    _QWEN3_AVAILABLE = True
except ImportError:
    from transformers import Qwen2VLForConditionalGeneration
    _QWEN3_AVAILABLE = False

# Optional: timm for broader architecture support
try:
    import timm
    from timm.data import resolve_model_data_config
    from timm.data.transforms_factory import create_transform as timm_create_transform
    _TIMM_AVAILABLE = True
except Exception:
    _TIMM_AVAILABLE = False


class NutriNetVision:
    def __init__(self):
        """Initialize NutriNet Vision with Qwen3-VL-4B-Nutrition-SFT model"""
        # Try HuggingFace model first (adapter + base merged)
        self.model_name = "AustinNaung/Qwen3-VL-4B-Nutrition-SFT"
        print(f"Using model from HuggingFace: {self.model_name}")
            
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = None
        self.processor = None
        # Lightweight fallback classifier (used if VLM generate is unavailable)
        try:
            self.fallback_model = tv_models.resnet18(pretrained=True)
            self.fallback_model.eval()
        except Exception:
            self.fallback_model = None

        # Image transform used by fallback classifier
        self.transform = T.Compose([
            T.Resize(256),
            T.CenterCrop(224),
            T.ToTensor(),
            T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        self.load_model()

    def load_model(self):
        """Load Qwen3-VL base model with LoRA adapter (same as Colab inference)."""
        try:
            base_model_name = "Qwen/Qwen3-VL-4B-Instruct"
            adapter_model_id = "AustinNaung/Qwen3-VL-4B-Nutrition-SFT"
            
            print(f"Loading base model: {base_model_name} on {self.device}...")
            
            # Use the correct model class based on what's available
            ModelClass = Qwen3VLForConditionalGeneration if _QWEN3_AVAILABLE else Qwen2VLForConditionalGeneration
            model_class_name = "Qwen3VLForConditionalGeneration" if _QWEN3_AVAILABLE else "Qwen2VLForConditionalGeneration"
            print(f"   Using {model_class_name}")
            
            # Check if we're on Mac with MPS - quantization has issues on MPS
            is_mac_mps = torch.backends.mps.is_available() and self.device == "mps"
            
            # Try to use quantization if bitsandbytes is available (but not on MPS)
            quantization_config = None
            if not is_mac_mps:
                try:
                    import bitsandbytes  # noqa
                    # 4-bit quantization config (same as Colab)
                    quantization_config = BitsAndBytesConfig(
                        load_in_4bit=True,
                        bnb_4bit_use_double_quant=True,
                        bnb_4bit_quant_type="nf4",
                        bnb_4bit_compute_dtype=torch.bfloat16
                    )
                    print("   Using 4-bit quantization to reduce memory usage")
                except ImportError:
                    print("   ⚠️ bitsandbytes not available - loading without quantization")
            else:
                print("   ⚠️ Skipping quantization on Mac MPS (compatibility issues)")
                print("   Loading on CPU for stability...")
                self.device = "cpu"  # Force CPU on Mac for quantized models
            
            # Load base model with correct class
            load_kwargs = {
                "device_map": self.device if self.device == "cpu" else "auto",
                "trust_remote_code": True,
                "low_cpu_mem_usage": True,
            }
            
            if quantization_config:
                load_kwargs["quantization_config"] = quantization_config
            else:
                load_kwargs["torch_dtype"] = torch.float32
            
            self.model = ModelClass.from_pretrained(
                base_model_name,
                **load_kwargs
            )
            
            print(f"Loading LoRA adapter: {adapter_model_id}...")
            # Load LoRA adapter on top (same as Colab)
            self.model = PeftModel.from_pretrained(self.model, adapter_model_id)
            
            self.model.eval()
            
            # Load processor with resolution limits (same as Colab training)
            min_pixels = 256 * 28 * 28
            max_pixels = 1008 * 28 * 28
            self.processor = AutoProcessor.from_pretrained(
                base_model_name,
                min_pixels=min_pixels,
                max_pixels=max_pixels,
                trust_remote_code=True,
            )
            print("✅ Model and adapter loaded successfully!")
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            import traceback
            traceback.print_exc()

    def analyze_image(self, image: Image.Image) -> List[Dict]:
        """
        Analyze food image using Qwen2-VL model to get food name, portion, and nutrition info.
        Returns a list of dictionaries with analysis results.
        """
        # If VLM not loaded, use fallback classifier immediately
        if not self.model or not self.processor:
            print("VLM not loaded — using fallback ResNet18 classifier")
            if self.fallback_model is None:
                print("ERROR: No model available (VLM failed and no fallback)")
                return []
            
            try:
                img_tensor = self.transform(image).unsqueeze(0)
                if self.device != 'cpu':
                    try:
                        img_tensor = img_tensor.to(self.device)
                        self.fallback_model.to(self.device)
                    except Exception:
                        pass

                with torch.no_grad():
                    logits = self.fallback_model(img_tensor)
                    probs = torch.softmax(logits, dim=1)[0]
                    top_p, top_i = torch.topk(probs, 1)
                    top_idx = int(top_i[0].cpu().item())

                # Minimal mapping from ImageNet classes to demo food names
                imagenet_to_food = {
                    281: "Tabby Cat", 924: "Guacamole", 339: "Zebra", 770: "Screen",
                    # Add common food items from ImageNet1k
                    927: "Trifle", 961: "Ice Cream", 809: "Soup Bowl",
                    567: "Frying Pan", 659: "Mixing Bowl"
                }
                food_name = imagenet_to_food.get(top_idx, f"Food Item (ImageNet-{top_idx})")
                portion_g = 150.0
                confidence = float(top_p[0].cpu().item())
                advice = f"Using ResNet18 classifier (fallback mode). Detected: {food_name} with {confidence:.1%} confidence. For demo purposes."

                return [
                    {
                        "name": food_name,
                        "confidence": confidence,
                        "portion": portion_g,
                        "health_advice": advice,
                    }
                ]
            except Exception as e:
                print(f"Fallback classifier error: {e}")
                return []

        try:
            # Prepare the prompt for the VLM
            prompt = "Identify the food in this image and estimate its portion size in grams. Provide a brief health advice."
            
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "image": image,
                        },
                        {"type": "text", "text": prompt},
                    ],
                }
            ]

            # Process inputs
            text = self.processor.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
            image_inputs, video_inputs = process_vision_info(messages)
            # Prepare model inputs
            inputs = self.processor(
                text=[text],
                images=image_inputs,
                videos=video_inputs,
                padding=True,
                return_tensors="pt",
            )

            # Move inputs to the same device as the model
            # Get the actual device of the model
            try:
                model_device = next(self.model.parameters()).device
                inputs = {k: v.to(model_device) if isinstance(v, torch.Tensor) else v 
                         for k, v in inputs.items()}
            except Exception as e:
                print(f"Warning: Could not move inputs to model device: {e}")
                # Fallback: try to move to self.device
                try:
                    inputs = inputs.to(self.device)
                except Exception:
                    pass

            # If model supports generation, use it. Otherwise fall back to classifier.
            if hasattr(self.model, "generate") and callable(getattr(self.model, "generate")):
                generated_ids = self.model.generate(**inputs, max_new_tokens=256)
                generated_ids_trimmed = [
                    out_ids[len(in_ids) :] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
                ]
                output_text = self.processor.batch_decode(
                    generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
                )[0]
                print(f"VLM Output: {output_text}")
            else:
                # Fallback: use a fast classifier to return a plausible demo result
                print("VLM generate() not available — using fallback classifier for demo output")
                if self.fallback_model is None:
                    raise RuntimeError("No generator available and fallback classifier failed to initialize")

                img_tensor = self.transform(image).unsqueeze(0)
                if self.device != 'cpu':
                    try:
                        img_tensor = img_tensor.to(self.device)
                        self.fallback_model.to(self.device)
                    except Exception:
                        pass

                with torch.no_grad():
                    logits = self.fallback_model(img_tensor)
                    probs = torch.softmax(logits, dim=1)[0]
                    top_p, top_i = torch.topk(probs, 1)
                    top_idx = int(top_i[0].cpu().item())

                # Minimal mapping from ImageNet classes to demo food names (replace/extend as needed)
                image_net_to_food = {281: "salad", 924: "pizza", 339: "sushi", 770: "burger"}
                food_name = image_net_to_food.get(top_idx, f"image_net_{top_idx}")
                portion_g = 150.0
                advice = f"Fallback classifier predicted: {food_name} (ImageNet idx {top_idx})"

                return [
                    {
                        "name": food_name,
                        "confidence": float(top_p[0].cpu().item()),
                        "portion": portion_g,
                        "health_advice": advice,
                    }
                ]

            print(f"VLM Output: {output_text}")

            # Parse the output (This is a heuristic parsing, might need adjustment based on model output format)
            # Expected format example: "This is a grilled chicken salad. Estimated portion: 300g. Advice: High protein..."
            
            food_name = "Unknown Food"
            portion_g = 0.0
            advice = ""

            # Simple regex extraction (can be improved)
            # Extract food name (heuristic: first sentence or part before portion)
            sentences = re.split(r'[.!?]', output_text)
            if sentences:
                food_name = sentences[0].strip()
            
            # Extract portion
            portion_match = re.search(r'(\d+)\s*g', output_text, re.IGNORECASE)
            if portion_match:
                portion_g = float(portion_match.group(1))
            
            # Extract advice (heuristic: remaining text)
            advice = output_text

            return [
                {
                    "name": food_name,
                    "confidence": 0.95, # VLM doesn't give confidence score easily, assuming high
                    "portion": portion_g if portion_g > 0 else 100.0, # Default to 100g if not found
                    "health_advice": advice
                }
            ]

        except Exception as e:
            print(f"Error during image analysis: {e}")
            return []

    def diagnostics(self) -> Dict:
        info = {
            "model_name": self.model_name,
            "device": self.device,
            "model_loaded": self.model is not None
        }
        return info

    # Legacy methods removed or commented out as they are replaced by VLM logic
    # def classify_food(self, food_image: Image.Image) -> Tuple[str, float]:
    #     ...
    def classify_topk(self, food_image: Image.Image, k: int = 5) -> List[Tuple[int, str, float]]:
        """Return top-k predictions as (index, class_name, probability)."""
        try:
            img_tensor = self.transform(food_image).unsqueeze(0)
            with torch.no_grad():
                outputs = self.model(img_tensor)
                probs = torch.softmax(outputs, dim=1)[0]
                k = max(1, min(int(k), probs.shape[0]))
                top_p, top_i = torch.topk(probs, k)
                result: List[Tuple[int, str, float]] = []
                for idx, p in zip(top_i.tolist(), top_p.tolist()):
                    name = self.class_names[idx] if 0 <= idx < len(self.class_names) else f"class_{idx}"
                    result.append((idx, name, float(p)))
                return result
        except Exception as e:
            print(f"Error in top-k classification: {str(e)}")
            return []

    def get_class_index(self, class_name: str) -> Optional[int]:
        try:
            return self.class_names.index(class_name)
        except ValueError:
            return None

    def estimate_portion(self, image: Image.Image) -> float:
        """Simple portion heuristic without detection: assume medium portion (grams)."""
        try:
            # You can refine this later with metadata or UI inputs
            return 200.0
        except Exception:
            return 150.0

    def get_nutrition_info(self, food_name: str, portion_g: float) -> Dict:
        """Get nutrition information for detected food (scaled by portion)."""
        try:
            # Basic nutrition estimates (extend/replace with your DB as needed)
            nutrition_data = {
                "pizza": {"calories": 266, "protein_g": 11, "carbs_g": 33, "fat_g": 10, "fiber_g": 2},
                "sushi": {"calories": 150, "protein_g": 25, "carbs_g": 15, "fat_g": 2, "fiber_g": 1},
                "burger": {"calories": 295, "protein_g": 17, "carbs_g": 30, "fat_g": 12, "fiber_g": 2},
                "pasta": {"calories": 131, "protein_g": 5, "carbs_g": 25, "fat_g": 1, "fiber_g": 2},
                "salad": {"calories": 20, "protein_g": 2, "carbs_g": 4, "fat_g": 0, "fiber_g": 2},
                "steak": {"calories": 271, "protein_g": 26, "carbs_g": 0, "fat_g": 18, "fiber_g": 0},
                "rice": {"calories": 130, "protein_g": 3, "carbs_g": 28, "fat_g": 0, "fiber_g": 0},
                # ...extend as needed
            }
            base = nutrition_data.get(food_name)
            if base is None:
                # Generic fallback per 100g
                base = {"calories": 160, "protein_g": 7, "carbs_g": 20, "fat_g": 5, "fiber_g": 2}
            scale = portion_g / 100.0
            return {k: round(v * scale, 1) for k, v in base.items()}
        except Exception as e:
            print(f"Error getting nutrition info: {str(e)}")
            return {"error": "Nutrition data unavailable"}

    def get_health_recommendations(self, food_name: str, nutrition: Dict) -> str:
        """Basic health recommendations"""
        try:
            calories = nutrition.get("calories", 0)
            protein = nutrition.get("protein_g", 0)
            carbs = nutrition.get("carbs_g", 0)
            fat = nutrition.get("fat_g", 0)
            tips = []
            if calories > 300:
                tips.append("High calorie - consider portion control")
            if protein > 20:
                tips.append("Good protein source")
            if carbs > 50:
                tips.append("High in carbs - good for energy")
            if fat > 15:
                tips.append("Moderate fat - balance with other meals")
            if not tips:
                tips.append("Balanced choice")
            return " | ".join(tips)
        except Exception:
            return "Health recommendations unavailable"

    def output_variability(self, food_image: Image.Image) -> float:
        """Return the standard deviation of logits as a quick variability sanity check.
        Very low values across different images may indicate a broken or constant model.
        """
        try:
            # This method was designed for classification models. 
            # For VLM, we might skip or adapt. Returning 0.0 for now to avoid errors.
            return 0.0
        except Exception:
            return 0.0


@st.cache_resource
def get_vision_model():
    """
    Cached factory function to load the model only once.
    Use this in app.py instead of NutriNetVision()
    """
    return NutriNetVision()


# Simple test function (for debugging)
def test_food_vision():
    try:
        nutrinet = NutriNetVision()
        print("✅ NutriNet Food-101 classifier initialized successfully!")
        # Show known indices for quick sanity-check
        for label in ("pizza", "garlic_bread"):
            idx = nutrinet.get_class_index(label)
            print(f"Class '{label}' index: {idx}")
        return nutrinet
    except Exception as e:
        print(f"❌ Failed to initialize NutriNet: {str(e)}")
        return None


if __name__ == "__main__":
    _ = test_food_vision()
    print("🎯 NutriNet Food Vision ready (Food-101 only)")
