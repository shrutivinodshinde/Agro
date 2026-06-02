import uuid, io, hashlib, logging, traceback, sys
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from PIL import Image
from backend.models.inference import model
from backend.models.schemas import PredictionResponse, SeverityLevel
from backend.database.redis_cache import RedisCache
from backend.database.postgres import save_prediction
from backend.agents.crew_agents import run_agriguard_crew
import inspect

# ── Configure logging so it actually prints ─────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# ── Log whether crew is async at import time ─────────────────────────────────
logger.info(f"run_agriguard_crew is coroutine: {inspect.iscoroutinefunction(run_agriguard_crew)}")

router = APIRouter(prefix="/api/v1", tags=["prediction"])


def get_severity(confidence: float, is_healthy: bool) -> SeverityLevel:
    if is_healthy:
        return SeverityLevel.HEALTHY
    if confidence > 0.9:
        return SeverityLevel.SEVERE
    if confidence > 0.7:
        return SeverityLevel.MODERATE
    return SeverityLevel.MILD


@router.post("/predict")
async def predict_disease(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    use_agents: bool = True,
    lat: float = None,
    lng: float = None,
    lang: str = "en"
):
    print("🔥 PREDICT ENDPOINT HIT", flush=True)
    logger.info(f"📥 File: {file.filename} | content_type: {file.content_type}")

    try:
        # ── Step 1: Validate ─────────────────────────────────────────────────
        print("Step 1: validating file type", flush=True)
        if file.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
            raise HTTPException(400, f"Only JPEG/PNG accepted. Got: {file.content_type}")

        img_bytes = await file.read()
        if not img_bytes:
            raise HTTPException(400, "Uploaded file is empty")
        print(f"Step 1 OK: {len(img_bytes)} bytes", flush=True)

        # ── Step 2: Redis cache (optional) ───────────────────────────────────
        print("Step 2: checking Redis cache", flush=True)
        img_hash = hashlib.md5(img_bytes).hexdigest()
        try:
            cached = await RedisCache.get(img_hash)
            if cached:
                print("Step 2: cache hit", flush=True)
                return cached
        except Exception as redis_err:
            print(f"Step 2: Redis unavailable ({redis_err}), skipping", flush=True)
        print("Step 2 OK: no cache hit", flush=True)

        # ── Step 3: Model guard ──────────────────────────────────────────────
        print("Step 3: checking model", flush=True)
        if model is None:
            raise HTTPException(503, "Model not loaded")
        print("Step 3 OK: model exists", flush=True)

        # ── Step 4: Inference ────────────────────────────────────────────────
        print("Step 4: running inference", flush=True)
        try:
            image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
            result = model.predict(image)
            print(f"Step 4 OK: {result}", flush=True)
        except Exception as model_err:
            tb = traceback.format_exc()
            print(f"Step 4 FAILED:\n{tb}", flush=True)
            raise HTTPException(500, detail=f"Model inference failed: {model_err}")

        prediction_id = str(uuid.uuid4())
        severity = get_severity(result["confidence"], result["is_healthy"])
        print(f"Step 4: plant={result.get('plant')} disease={result.get('disease')} healthy={result.get('is_healthy')}", flush=True)

        # ── Step 5: Agent report ─────────────────────────────────────────────
        agent_report = None
        if use_agents and not result["is_healthy"]:
            print("Step 5: running CrewAI agent...", flush=True)
            try:
                if inspect.iscoroutinefunction(run_agriguard_crew):
                    print("Step 5: crew is async, awaiting...", flush=True)
                    agent_report = await run_agriguard_crew(
                        disease=result["disease"],
                        plant=result["plant"],
                        confidence=result["confidence"],
                        lat=lat, lng=lng, lang=lang,
                    )
                else:
                    print("Step 5: crew is SYNC, running in executor...", flush=True)
                    import asyncio
                    loop = asyncio.get_event_loop()
                    agent_report = await loop.run_in_executor(
                        None,
                        lambda: run_agriguard_crew(
                            disease=result["disease"],
                            plant=result["plant"],
                            confidence=result["confidence"],
                            lat=lat, lng=lng, lang=lang,
                        )
                    )
                print(f"Step 5 OK: agent_report length={len(str(agent_report))}", flush=True)
            except Exception as crew_err:
                tb = traceback.format_exc()
                print(f"Step 5 FAILED (using fallback):\n{tb}", flush=True)
                agent_report = _fallback_agent_report(result["plant"], result["disease"])
        else:
            print("Step 5: skipped (healthy or use_agents=False)", flush=True)

        # ── Step 6: Build response ───────────────────────────────────────────
        print("Step 6: building PredictionResponse", flush=True)
        try:
            response = PredictionResponse(
                prediction_id=prediction_id,
                severity=severity,
                agent_report=agent_report,
                plant=result.get("plant", "Unknown"),
                disease=result.get("disease", "Unknown"),
                confidence=result.get("confidence", 0.0),
                is_healthy=result.get("is_healthy", True),
                uncertainty=result.get("uncertainty", 0.0),
                confidence_range=result.get("confidence_range", [0.0, 1.0]),
                top3=result.get("top3", []),
                treatment_advice=result.get("treatment_advice", None),
            )
            print(f"Step 6 OK: response built", flush=True)
        except Exception as schema_err:
            tb = traceback.format_exc()
            print(f"Step 6 FAILED (schema error):\n{tb}", flush=True)
            raise HTTPException(500, detail=f"Response schema error: {schema_err}")

        # ── Step 7: Background cache write ───────────────────────────────────
        try:
            background_tasks.add_task(
                RedisCache.set, img_hash, response.model_dump(), 3600
            )
        except Exception as cache_err:
            print(f"Step 7: cache write scheduling failed: {cache_err}", flush=True)

        print("✅ PREDICT SUCCESS — returning response", flush=True)
        return response

    except HTTPException:
        raise

    except Exception as exc:
        tb = traceback.format_exc()
        print(f"💥 UNHANDLED EXCEPTION IN /predict:\n{tb}", flush=True)
        return JSONResponse(
            status_code=500,
            content={"detail": f"Internal server error: {exc}"}
        )


def _fallback_agent_report(plant: str, disease: str) -> str:
    return (
        f"## {plant} — {disease}\n\n"
        "**Treatment steps:**\n"
        "1. Remove and dispose of all visibly infected leaves immediately.\n"
        "2. Apply a copper-based fungicide or neem oil every 7-10 days.\n"
        "3. Improve air circulation — space plants adequately.\n"
        "4. Avoid overhead watering; water at the base in the morning.\n"
        "5. Monitor closely for two weeks; repeat treatment if needed.\n\n"
        "**Prevention:**\n"
        "- Rotate crops each season.\n"
        "- Keep tools clean and disinfected between plants.\n\n"
        "> AI report unavailable — showing standard treatment guide."
    )


@router.get("/predict/stream/{disease}")
async def stream_treatment(disease: str, plant: str = "Unknown"):
    from backend.agents.rag_pipeline import stream_treatment_advice
    return StreamingResponse(
        stream_treatment_advice(disease, plant),
        media_type="text/event-stream"
    )