import pytest
from unittest.mock import patch, AsyncMock, MagicMock

@pytest.fixture(autouse=True)
def mock_model_load():
    mock_result = {
        "plant": "Tomato",
        "disease": "Late_blight",
        # FIX: removed "label" key — PredictionResponse has no label field
        # and the real ModelService.predict() doesn't return it either
        "confidence": 0.95,
        "uncertainty": 0.02,
        "confidence_range": [0.91, 0.99],
        "top3": [
            {"class_name": "Tomato___Late_blight", "confidence": 0.95},
            {"class_name": "Tomato___Early_blight", "confidence": 0.03},
            {"class_name": "Tomato___healthy", "confidence": 0.02},
        ],
        "is_healthy": False
    }

    with patch("backend.models.inference.ModelService.load", return_value=None), \
         patch("backend.models.inference.ModelService.predict", return_value=mock_result):
        yield


@pytest.fixture(autouse=True)
def mock_db():
    with patch("backend.routers.predict.save_prediction", return_value=None):
        yield

@pytest.fixture(autouse=True)
def mock_redis():
    # FIX: get_redis is an async def so it MUST be mocked with AsyncMock.
    # Using a regular MagicMock caused `await get_redis()` to raise TypeError,
    # which was silently swallowed by the try/except in RedisCache — meaning
    # cache calls never actually worked in tests.
    mock_r = AsyncMock()
    mock_r.get.return_value = None          # simulate cache miss
    mock_r.setex.return_value = True        # simulate successful set

    with patch(
        "backend.database.redis_cache.get_redis",
        new_callable=AsyncMock,
        return_value=mock_r
    ):
        yield
