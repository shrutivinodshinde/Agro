import pytest
import io
from httpx import AsyncClient
from PIL import Image
from backend.main import app

@pytest.fixture
def sample_image_bytes():
    """Create a minimal valid JPEG in memory — no file needed."""
    img = Image.new('RGB', (224, 224), color=(34, 139, 34))  # green leaf color
    buf = io.BytesIO()
    img.save(buf, format='JPEG')
    buf.seek(0)
    return buf.read()

@pytest.mark.asyncio
async def test_health_check():
    """API must respond with healthy status."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        resp = await client.get("/")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"

@pytest.mark.asyncio
async def test_predict_returns_valid_response(sample_image_bytes):
    """Prediction must return all required fields with valid ranges."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        resp = await client.post(
            "/api/v1/predict?use_agents=false",  # skip agents for speed
            files={"file": ("leaf.jpg", sample_image_bytes, "image/jpeg")}
        )
    assert resp.status_code == 200
    data = resp.json()

    # Check all required fields exist
    assert "plant" in data
    assert "disease" in data
    assert "confidence" in data
    assert "severity" in data
    assert "top3" in data
    assert "uncertainty" in data
    assert "confidence_range" in data

    # Check value ranges
    assert 0.0 <= data["confidence"] <= 1.0
    assert 0.0 <= data["uncertainty"] <= 1.0
    assert len(data["top3"]) == 3
    assert data["severity"] in ["healthy", "mild", "moderate", "severe"]

@pytest.mark.asyncio
async def test_confidence_range_is_valid(sample_image_bytes):
    """Confidence must fall within its own uncertainty range."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        resp = await client.post(
            "/api/v1/predict?use_agents=false",
            files={"file": ("leaf.jpg", sample_image_bytes, "image/jpeg")}
        )
    data = resp.json()
    low, high = data["confidence_range"]
    assert low <= data["confidence"] <= high

@pytest.mark.asyncio
async def test_rejects_non_image_files():
    """PDF files must be rejected with 400 error."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        resp = await client.post(
            "/api/v1/predict",
            files={"file": ("report.pdf", b"fake pdf content", "application/pdf")}
        )
    assert resp.status_code == 400

@pytest.mark.asyncio
async def test_healthy_plant_has_correct_severity(sample_image_bytes):
    """If model predicts 'healthy', severity must be 'healthy' not 'severe'."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        resp = await client.post(
            "/api/v1/predict?use_agents=false",
            files={"file": ("leaf.jpg", sample_image_bytes, "image/jpeg")}
        )
    data = resp.json()
    if data["is_healthy"]:
        assert data["severity"] == "healthy"