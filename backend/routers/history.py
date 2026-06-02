from fastapi import APIRouter, Query
from backend.database.postgres import AsyncSessionLocal, PredictionRecord
from sqlalchemy import select, desc

router = APIRouter(prefix="/api/v1", tags=["history"])

@router.get("/history")
async def get_history(limit: int = Query(100, le=1000)):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(PredictionRecord)
            .order_by(desc(PredictionRecord.created_at))
            .limit(limit)
        )
        records = result.scalars().all()
        return [
            {
                "prediction_id": r.id,
                "plant": r.plant,
                "disease": r.disease,
                "confidence": r.confidence,
                "severity": r.severity,
                "is_healthy": r.is_healthy,
                "latitude": r.latitude,
                "longitude": r.longitude,
                "created_at": r.created_at.isoformat()
            }
            for r in records
        ]