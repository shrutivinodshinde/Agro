# backend/database/postgres.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, String, Float, Boolean, DateTime, JSON
from datetime import datetime
from backend.config import get_settings

settings = get_settings()

engine = create_async_engine(settings.POSTGRES_URL, echo=False)
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)
Base = declarative_base()

class PredictionRecord(Base):
    __tablename__ = "predictions"
    id          = Column(String, primary_key=True)
    plant       = Column(String, nullable=False, index=True)
    disease     = Column(String, nullable=False, index=True)
    confidence  = Column(Float)
    uncertainty = Column(Float)
    severity    = Column(String)
    is_healthy  = Column(Boolean)
    latitude    = Column(Float, nullable=True)
    longitude   = Column(Float, nullable=True)
    top3        = Column(JSON)
    created_at  = Column(DateTime, default=datetime.utcnow, index=True)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def save_prediction(pred, lat=None, lng=None):
    async with AsyncSessionLocal() as session:
        record = PredictionRecord(
            id=pred.prediction_id,
            plant=pred.plant,
            disease=pred.disease,
            confidence=pred.confidence,
            uncertainty=pred.uncertainty,
            severity=pred.severity,
            is_healthy=pred.is_healthy,
            latitude=lat,
            longitude=lng,
            top3=[t.model_dump() for t in pred.top3]  # FIXED: was .dict()
        )
        session.add(record)
        await session.commit()