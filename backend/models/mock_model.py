class MockModelService:

    def load(self):
        pass

    def predict(self, image):
        confidence = 0.95

        return {
            "plant": "Tomato",
            "disease": "Late_blight",
            "label": "Tomato___Late_blight",
            "confidence": confidence,
            "uncertainty": 0.05,
            "confidence_range": [confidence - 0.05, confidence + 0.05],
            "top3": [
                {"class_name": "Tomato___Late_blight", "confidence": 0.95},
                {"class_name": "Tomato___Early_blight", "confidence": 0.03},
                {"class_name": "Tomato___healthy", "confidence": 0.02},
            ],
            "is_healthy": False
        }