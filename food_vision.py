"""
NutriNet Food Vision - Core AI Module (Food-101 only)
This module provides food classification and nutrition analysis using a single
Food-101 classifier at model_weights/food101_model.pth.
"""

import os
from typing import List, Dict, Tuple, Optional

import torch
import torchvision.transforms as T
import torchvision.models as models
from PIL import Image

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
        """Initialize NutriNet Vision with Food-101 classifier only"""
        self.load_info = {}
        self.suspect_weights = False
        self.weight_overlap = 0.0
        self.arch = "resnet50"  # default
        self.setup_models()

    def _load_class_names(self) -> List[str]:
        """Optionally load class names for Food-101 from a text file or checkpoint.
        Fallback to generic labels if unavailable.
        """
        class_names: List[str] = []
        # Try external class list
        txt_path = os.path.join("model_weights", "food101_classes.txt")
        if os.path.exists(txt_path):
            try:
                with open(txt_path, "r", encoding="utf-8") as f:
                    class_names = [ln.strip() for ln in f if ln.strip()]
            except Exception:
                class_names = []
        # Fallback generic mapping if not provided
        if not class_names or len(class_names) < 101:
            class_names = [f"class_{i}" for i in range(101)]
        return class_names

    def _clean_state_key(self, k: str) -> str:
        """Strip common prefixes like 'module.' or 'model.' or 'backbone.'
        from state_dict keys so they match torchvision resnet naming.
        """
        for prefix in ("module.", "model.", "backbone."):
            if k.startswith(prefix):
                return k[len(prefix) :]
        return k

    def _try_load_class_names_from_ckpt(self, ckpt: Dict) -> None:
        """Attempt to derive class name ordering from checkpoint metadata if available."""
        def set_if_valid(names: List[str]):
            if isinstance(names, list) and len(names) == 101 and all(isinstance(x, str) for x in names):
                self.class_names = names
                return True
            return False

        # Direct list
        for key in ("classes", "class_names", "labels", "labels_map"):
            if key in ckpt and isinstance(ckpt[key], list):
                if set_if_valid(ckpt[key]):
                    return
        # Nested metadata
        for meta_key in ("meta", "args", "hparams", "config"):
            meta = ckpt.get(meta_key)
            if isinstance(meta, dict):
                for key in ("classes", "class_names", "labels", "labels_map"):
                    if key in meta and isinstance(meta[key], list):
                        if set_if_valid(meta[key]):
                            return
        # idx_to_class dict
        for key in ("idx_to_class", "index_to_class", "itoc"):
            mapping = ckpt.get(key)
            if isinstance(mapping, dict):
                try:
                    # keys may be str or int
                    pairs = []
                    for k, v in mapping.items():
                        try:
                            idx = int(k)
                        except Exception:
                            idx = int(k) if isinstance(k, (int, str)) else None
                        if idx is None:
                            continue
                        pairs.append((idx, v))
                    if pairs:
                        pairs.sort(key=lambda x: x[0])
                        names = [str(v) for _, v in pairs]
                        if set_if_valid(names):
                            return
                except Exception:
                    pass
        # class_to_idx dict
        for key in ("class_to_idx", "cto", "class2idx"):
            mapping = ckpt.get(key)
            if isinstance(mapping, dict):
                try:
                    size = max(int(v) for v in mapping.values()) + 1
                    names = [None] * size
                    for cls, idx in mapping.items():
                        names[int(idx)] = str(cls)
                    if None not in names and set_if_valid(names):
                        return
                except Exception:
                    pass

    def _load_meta(self) -> Dict:
        """Load sidecar metadata if present: model_weights/food101_meta.json
        Expected fields: {"arch": "tf_efficientnet_b4_ns", "class_names": [..101..]}
        """
        import json
        meta_path = os.path.join("model_weights", "food101_meta.json")
        if os.path.exists(meta_path):
            try:
                with open(meta_path, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                return meta if isinstance(meta, dict) else {}
            except Exception:
                return {}
        return {}

    def setup_models(self):
        """Initialize Food-101 classifier from model_weights/food101_model.pth"""
        try:
            model_path = os.path.join("model_weights", "food101_model.pth")
            if not os.path.exists(model_path):
                raise FileNotFoundError(
                    f"Food-101 weights not found at {model_path}. Please add the file."
                )

            # Load meta (arch, classes) if available
            meta = self._load_meta()
            if isinstance(meta, dict):
                arch_from_meta = meta.get("arch")
                if isinstance(arch_from_meta, str) and arch_from_meta.strip():
                    self.arch = arch_from_meta.strip()

            self.class_names = self._load_class_names()
            # If meta carried class_names, prefer it
            if isinstance(meta.get("class_names"), list) and len(meta["class_names"]) == 101:
                self.class_names = [str(x) for x in meta["class_names"]]

            self.load_info = {"path": model_path, "arch": self.arch}

            # Option to disable TorchScript path via env
            disable_ts = os.getenv("NUTRINET_DISABLE_TORCHSCRIPT", "0") == "1"

            # Try to load as TorchScript first (if the file is scripted/traced)
            self.model = None
            if not disable_ts:
                try:
                    self.model = torch.jit.load(model_path, map_location="cpu")
                    _ = self.model.eval()
                    self.is_scripted = True
                    self.load_info.update({"mode": "torchscript"})
                    print("Loaded TorchScript Food-101 model")
                except Exception as e_js:
                    self.is_scripted = False
                    self.load_info.update({"torchscript_error": str(e_js)})
            else:
                self.is_scripted = False
                self.load_info.update({"torchscript_skipped": True})

            # If not TorchScript, try an architecture-aware load
            if self.model is None:
                ckpt = torch.load(model_path, map_location="cpu")
                # Try to discover arch in checkpoint
                for meta_key in ("arch", "model_name"):
                    if isinstance(ckpt, dict) and meta_key in ckpt and isinstance(ckpt[meta_key], str):
                        self.arch = ckpt[meta_key]
                        self.load_info["arch"] = self.arch
                        break
                # Also try nested
                for nest_key in ("meta", "hparams", "args", "config"):
                    blob = ckpt.get(nest_key) if isinstance(ckpt, dict) else None
                    if isinstance(blob, dict):
                        for meta_key in ("arch", "model_name"):
                            if isinstance(blob.get(meta_key), str):
                                self.arch = blob[meta_key]
                                self.load_info["arch"] = self.arch
                                break

                # Prefer common keys for weights, including notebook's 'model_state_dict'
                state_dict = None
                if isinstance(ckpt, dict):
                    for k in ("state_dict", "model_state_dict", "model", "net"):
                        sd = ckpt.get(k)
                        if isinstance(sd, dict):
                            state_dict = sd
                            break
                if state_dict is None:
                    state_dict = ckpt

                # If we have timm and arch is not resnet50, use timm backbone
                used_timm = False
                if _TIMM_AVAILABLE and self.arch and self.arch.lower() != "resnet50":
                    try:
                        model = timm.create_model(self.arch, pretrained=False, num_classes=101)
                        # Clean prefixes
                        cleaned = {self._clean_state_key(k): v for k, v in state_dict.items()} if isinstance(state_dict, dict) else state_dict
                        missing, unexpected = model.load_state_dict(cleaned, strict=False)
                        self.model = model.eval()
                        used_timm = True
                        # Compute overlap stats
                        target_sd = model.state_dict()
                        overlap = sum(1 for k in cleaned.keys() if k in target_sd) if isinstance(cleaned, dict) else 0
                        shape_match = 0
                        if isinstance(cleaned, dict):
                            for k, v in cleaned.items():
                                if k in target_sd and tuple(target_sd[k].shape) == tuple(v.shape):
                                    shape_match += 1
                        total = len(target_sd)
                        self.weight_overlap = shape_match / max(total, 1)
                        self.load_info.update({
                            "mode": "state_dict+timm",
                            "keys_in_common": overlap,
                            "shape_match_ratio": round(self.weight_overlap, 3),
                            "total_params_keys": total,
                            "missing_keys_count": len(missing),
                            "unexpected_keys_count": len(unexpected),
                        })
                        # Transforms from timm config
                        data_cfg = resolve_model_data_config(model)
                        self.transform = timm_create_transform(**data_cfg, is_training=False)
                    except Exception as e_timm:
                        self.load_info["timm_error"] = str(e_timm)

                if not used_timm:
                    # Fallback to torchvision resnet50
                    backbone = models.resnet50(weights=None)
                    backbone.fc = torch.nn.Linear(backbone.fc.in_features, 101)
                    # Try to override class names from checkpoint if available
                    try:
                        if isinstance(ckpt, dict):
                            self._try_load_class_names_from_ckpt(ckpt)
                    except Exception:
                        pass
                    cleaned_state_dict = {self._clean_state_key(k): v for k, v in state_dict.items()} if isinstance(state_dict, dict) else {}
                    # Remap Sequential FC keys (fc.1.*) -> fc.* as notebook saved Dropout+Linear
                    remapped_state_dict = {}
                    for k, v in cleaned_state_dict.items():
                        if k.startswith("fc.1."):
                            new_k = "fc." + k[len("fc.1."):]
                            remapped_state_dict[new_k] = v
                        else:
                            remapped_state_dict[k] = v
                    if any(k.startswith("classifier.") for k in remapped_state_dict.keys()):
                        if "classifier.weight" in remapped_state_dict and "classifier.bias" in remapped_state_dict:
                            remapped_state_dict["fc.weight"] = remapped_state_dict["classifier.weight"]
                            remapped_state_dict["fc.bias"] = remapped_state_dict["classifier.bias"]
                    target_sd = backbone.state_dict()
                    overlap = 0
                    shape_match = 0
                    for k, v in remapped_state_dict.items():
                        if k in target_sd:
                            overlap += 1
                            if tuple(target_sd[k].shape) == tuple(v.shape):
                                shape_match += 1
                    total = len(target_sd)
                    self.weight_overlap = shape_match / max(total, 1)
                    self.load_info.update({
                        "mode": "state_dict",
                        "keys_in_common": overlap,
                        "shape_match_ratio": round(self.weight_overlap, 3),
                        "total_params_keys": total,
                    })
                    missing, unexpected = backbone.load_state_dict(remapped_state_dict, strict=False)
                    self.model = backbone.eval()
                    self.load_info.update({
                        "missing_keys_count": len(missing),
                        "unexpected_keys_count": len(unexpected),
                    })
                    if self.weight_overlap < 0.5:
                        self.suspect_weights = True

                # If transform not set by timm path, use torchvision default
                if not hasattr(self, "transform"):
                    self.transform = T.Compose(
                        [
                            T.Resize(256),
                            T.CenterCrop(224),
                            T.ToTensor(),
                            T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
                        ]
                    )

        except Exception as e:
            print(f"Error setting up Food-101 model: {str(e)}")
            raise

    def diagnostics(self) -> Dict:
        info = {
            "is_scripted": getattr(self, "is_scripted", False),
            "weight_overlap": round(self.weight_overlap, 3),
            "suspect_weights": self.suspect_weights,
        }
        info.update(self.load_info or {})
        return info

    def classify_food(self, food_image: Image.Image) -> Tuple[str, float]:
        """Classify food using the Food-101 model"""
        try:
            img_tensor = self.transform(food_image).unsqueeze(0)
            with torch.no_grad():
                outputs = self.model(img_tensor)
                # Validate output shape
                if outputs.ndim == 1:
                    outputs = outputs.unsqueeze(0)
                if outputs.shape[1] != len(self.class_names):
                    # Attempt to adapt if off-by-one; else warn
                    print(f"Model output classes {outputs.shape[1]} != class_names {len(self.class_names)}")
                probs = torch.softmax(outputs, dim=1)
                conf, idx = torch.max(probs, 1)
                pred_idx = idx.item()
                if 0 <= pred_idx < len(self.class_names):
                    food_name = self.class_names[pred_idx]
                else:
                    food_name = f"class_{pred_idx}"
                return food_name, float(conf.item())
        except Exception as e:
            print(f"Error in food classification: {str(e)}")
            return "unknown_food", 0.0

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

    def analyze_image(self, image: Image.Image) -> List[Dict]:
        """Analyze a single food image using Food-101 classifier only."""
        try:
            food_name, confidence = self.classify_food(image)
            portion = self.estimate_portion(image)
            nutrition = self.get_nutrition_info(food_name, portion)
            advice = self.get_health_recommendations(food_name, nutrition)
            return [
                {
                    "name": food_name,
                    "confidence": confidence,
                    "portion": portion,
                    "nutrition": nutrition,
                    "health_advice": advice,
                }
            ]
        except Exception as e:
            print(f"Error in image analysis: {str(e)}")
            return []

    def output_variability(self, food_image: Image.Image) -> float:
        """Return the standard deviation of logits as a quick variability sanity check.
        Very low values across different images may indicate a broken or constant model.
        """
        try:
            img_tensor = self.transform(food_image).unsqueeze(0)
            with torch.no_grad():
                outputs = self.model(img_tensor)
                if outputs.ndim == 1:
                    outputs = outputs.unsqueeze(0)
                logits = outputs[0].float().cpu()
                return float(torch.std(logits).item())
        except Exception:
            return 0.0


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
