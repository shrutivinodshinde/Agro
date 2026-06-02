# test_model.py
import sys
sys.path.insert(0, ".")

def test_model():
    print("\n" + "="*50)
    print("  TESTING PYTORCH MODEL")
    print("="*50 + "\n")

    import os
    # FIX: path now matches config.py MODEL_PATH (was plant_disease_model.pth)
    model_path   = "data/models/best_model.pth"
    classes_path = "data/models/classes.json"

    print("Checking files...")
    if not os.path.exists(model_path):
        print(f"❌ Model file not found: {model_path}")
        print("   → Copy your .pth file to data/models/best_model.pth")
        return
    print(f"✅ Model file found: {os.path.getsize(model_path) / 1024 / 1024:.1f} MB")

    if not os.path.exists(classes_path):
        print(f"❌ classes.json not found: {classes_path}")
        print("   → Create data/models/classes.json with your class names")
        return

    import json
    with open(classes_path) as f:
        classes = json.load(f)
    print(f"✅ classes.json found: {len(classes)} disease classes")
    print(f"   Sample classes: {list(classes.values())[:3]}")

    # Load model
    print("\nLoading model...")
    try:
        from backend.models.inference import model
        model.load()
        print("✅ Model loaded successfully!")
        print(f"   Device: {model._device}")
        # FIX: ModelService has _disease_classes and _plant_classes, not _classes
        print(f"   Disease classes : {len(model._disease_classes)}")
        print(f"   Plant classes   : {len(model._plant_classes)}")
    except Exception as e:
        print(f"❌ Model load failed: {e}")
        print("\nCommon fixes:")
        print("  → Wrong architecture: adjust PlantModel in inference.py")
        print("  → Wrong save format: check checkpoint loading in inference.py")
        import traceback
        traceback.print_exc()
        return

    # Test prediction
    print("\nTesting prediction...")
    try:
        from PIL import Image
        import numpy as np
        fake_img = Image.fromarray(
            np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        )
        result = model.predict(fake_img)

        print("✅ Prediction works!\n")
        print("  Result:")
        print(f"    Plant:            {result['plant']}")
        print(f"    Disease:          {result['disease']}")
        print(f"    Confidence:       {result['confidence']:.1%}")
        print(f"    Uncertainty:      ±{result['uncertainty']:.4f}")
        print(f"    Range:            {result['confidence_range']}")
        print(f"    Is Healthy:       {result['is_healthy']}")
        print(f"    Top 3:")
        for i, t in enumerate(result['top3']):
            print(f"      {i+1}. {t['class_name']}: {t['confidence']:.1%}")

    except Exception as e:
        print(f"❌ Prediction failed: {e}")
        import traceback
        traceback.print_exc()

test_model()
