import torch
import torch.nn as nn
from torchvision.models import efficientnet_b3
from torchvision import transforms
from PIL import Image
import json
import os
import urllib.request

from backend.config import get_settings

settings = get_settings()

# ===============================
# MODEL (MATCHES TRAINING EXACTLY)
# ===============================
class PlantModel(nn.Module):
    def __init__(self, n_plants, n_diseases):
        super().__init__()
        backbone = efficientnet_b3(weights=None)
        self.features = backbone.features
        self.pool = nn.AdaptiveAvgPool2d(1)
        feature_dim = 1536
        self.plant_head = nn.Linear(feature_dim, n_plants)
        self.disease_head = nn.Sequential(
            nn.Linear(feature_dim, 1024),
            nn.ReLU(),
            nn.Dropout(0.4),
            nn.Linear(1024, n_diseases)
        )

    def forward(self, x):
        feat = self.features(x)
        feat = self.pool(feat).flatten(1)
        plant_out = self.plant_head(feat)
        disease_out = self.disease_head(feat)
        return plant_out, disease_out


# ===============================
# INFERENCE CLASS
# ===============================
class ModelService:
    def __init__(self):
        self._model = None
        self._device = "cuda" if torch.cuda.is_available() else "cpu"
        self._disease_classes = None
        self._plant_classes = None
        self._loaded = False
        self._transform = transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])

    def _download_model_if_needed(self):
        model_path = settings.MODEL_PATH
        model_url = os.getenv("MODEL_URL", "")
        if not os.path.exists(model_path) and model_url:
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            print("Downloading model from Azure Storage...")
            urllib.request.urlretrieve(model_url, model_path)
            print("Model downloaded successfully!")

    def load(self):
        if self._loaded:
            return
        self._download_model_if_needed()
        with open(settings.MODEL_CLASSES_PATH) as f:
            self._disease_classes = json.load(f)
        raw_plant_names = sorted(set(
            v.split("_")[0] for v in self._disease_classes.values()
        ))
        self._plant_classes = {str(i): p for i, p in enumerate(raw_plant_names)}
        n_diseases = len(self._disease_classes)
        n_plants = len(self._plant_classes)
        self._model = PlantModel(n_plants, n_diseases).to(self._device)
        checkpoint = torch.load(settings.MODEL_PATH, map_location=self._device)
        self._model.load_state_dict(checkpoint)
        self._model.eval()
        self._loaded = True
        print(f"✅ Model loaded on {self._device}")
        print(f"✅ Disease classes: {n_diseases}")
        print(f"✅ Plant classes: {n_plants}")

    def predict(self, image: Image.Image):
        if not self._loaded:
            self.load()
        tensor = self._transform(image).unsqueeze(0).to(self._device)
        with torch.no_grad():
            plant_logits, disease_logits = self._model(tensor)
            disease_probs = torch.softmax(disease_logits, dim=1)
            disease_conf, disease_idx = torch.max(disease_probs, dim=1)
            disease_conf = float(disease_conf.item())
            disease_idx = int(disease_idx.item())
            disease_name = self._disease_classes[str(disease_idx)]
            plant_probs = torch.softmax(plant_logits, dim=1)
            plant_idx = int(torch.argmax(plant_probs, dim=1).item())
            plant_name = self._plant_classes[str(plant_idx)]
            top3_probs, top3_indices = torch.topk(
                disease_probs[0], k=min(3, disease_probs.size(1))
            )
            top3 = [
                {
                    "class_name": self._disease_classes[str(int(idx.item()))],
                    "confidence": float(prob.item())
                }
                for prob, idx in zip(top3_probs, top3_indices)
            ]
        confidence_range = [
            float(max(0.0, disease_conf - 0.05)),
            float(min(1.0, disease_conf + 0.05))
        ]
        return {
            "plant": plant_name,
            "disease": disease_name,
            "confidence": disease_conf,
            "uncertainty": 0.05,
            "confidence_range": confidence_range,
            "is_healthy": "healthy" in disease_name.lower(),
            "top3": top3
        }


# ===============================
# GLOBAL INSTANCE
# ===============================
model = ModelService()