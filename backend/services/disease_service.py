# backend/services/disease_service.py
from backend.models.inference import model
from backend.agents.rag_pipeline import get_treatment_advice
from PIL import Image
import io

async def analyze_leaf(
    image_bytes: bytes,
    use_agents: bool = True,
    lat: float = None,
    lng: float = None,
    lang: str = "en"
) -> dict:
    """
    Central service that combines model inference + RAG advice.
    Routers call this instead of calling model/agents directly.
    """
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    result = model.predict(image)

    if use_agents and not result["is_healthy"]:
        location = f"{lat},{lng}" if lat else "India"
        result["treatment_advice"] = await get_treatment_advice(
            disease=result["disease"],
            plant=result["plant"],
            confidence=result["confidence"],
            location=location
        )

    return result