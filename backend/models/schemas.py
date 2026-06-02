from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class SeverityLevel(str, Enum):
    HEALTHY = "healthy"
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"

class TopPrediction(BaseModel):
    class_name: str
    confidence: float

class PredictionResponse(BaseModel):
    prediction_id: str
    plant: str
    disease: str
    confidence: float
    uncertainty: float
    confidence_range: List[float]
    is_healthy: bool
    severity: SeverityLevel
    top3: List[TopPrediction]
    treatment_advice: Optional[str] = None
    agent_report: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)