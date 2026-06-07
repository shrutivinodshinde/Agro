<div align="center">

<img src="https://img.icons8.com/material-rounded/96/c1ecd4/leaf.png" width="80" alt="Agro Logo"/>

# Agro

### AI-Powered Plant Disease Detection & Agricultural Advisory Platform

**Deep Learning · RAG Pipeline · Multi-Agent AI · Mobile-First**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=flat-square&logo=react)](https://react.dev)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.3-EE4C2C?style=flat-square&logo=pytorch)](https://pytorch.org)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python)](https://python.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

</div>

---

## Overview

Agro is a production-ready full-stack platform that helps farmers detect plant diseases and receive actionable treatment recommendations — simply by uploading a photo.

A custom dual-head **EfficientNet-B3** model classifies the plant and disease simultaneously. The result then flows through a **LangChain + ChromaDB RAG pipeline** (powered by Ollama locally) to retrieve research-backed agricultural knowledge, and a **CrewAI multi-agent system** (powered by Groq LLMs) to generate a structured, farmer-friendly treatment report — all within a single API call.

The frontend is a **React 19 + TypeScript** mobile-first app, also deployable as a native **Android application** via Capacitor.

---

## Table of Contents

- [Features](#features)
- [System Architecture](#system-architecture)
- [End-to-End Request Flow](#end-to-end-request-flow)
- [Frontend](#frontend)
- [Backend](#backend)
- [ML Pipeline](#ml-pipeline)
- [RAG Pipeline](#rag-pipeline)
- [Multi-Agent System](#multi-agent-system)
- [Database Design](#database-design)
- [API Reference](#api-reference)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Docker Deployment](#docker-deployment)
- [Environment Variables](#environment-variables)
- [Testing](#testing)
- [Roadmap](#roadmap)

---

## Features

| Category | Capability |
|---|---|
| **Disease Detection** | 150+ disease classes across 30+ crops |
| **Model** | Custom dual-head EfficientNet-B3 (plant + disease simultaneously) |
| **Confidence** | Top-3 predictions with confidence scores and uncertainty range |
| **Severity** | Automatic classification — HEALTHY / MILD / MODERATE / SEVERE |
| **RAG** | ChromaDB vector store + Ollama LLM for research-grounded treatment plans |
| **Agents** | 4 specialized CrewAI agents powered by Groq (Llama 3.1 8B + 3.3 70B) |
| **Weather** | Real-time weather fetch for spray window scheduling |
| **Language** | Multilingual report output via translation agent |
| **Mobile** | Capacitor Android app with native camera access |
| **Auth** | JWT-based authentication (24h expiry) |
| **Caching** | Redis MD5-hash caching for repeated predictions |
| **Monitoring** | Prometheus metrics via `prometheus-fastapi-instrumentator` |
| **CI/CD** | GitHub Actions → Azure deployment |

---

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│              React 19 + TypeScript (Vite)               │
│         Tailwind CSS  ·  Motion  ·  Lucide React        │
│              Capacitor (Android Deployment)             │
└────────────────────────┬────────────────────────────────┘
                         │  HTTP / REST
                         ▼
┌─────────────────────────────────────────────────────────┐
│                    FastAPI Backend                      │
│        JWT Auth  ·  CORS  ·  Prometheus Metrics        │
│           Routers  →  Services  →  Response            │
└──────────────────┬──────────────────┬───────────────────┘
                   │                  │
         ┌─────────▼──────┐  ┌────────▼────────────────┐
         │ EfficientNet-B3│  │   CrewAI Agent System   │
         │  Dual-Head     │  │   Groq LLMs (Cloud)     │
         │  plant_head    │  └────────┬────────────────┘
         │  disease_head  │           │
         └────────────────┘  ┌────────▼────────────────┐
                             │   RAG Pipeline          │
                             │   LangChain + Ollama    │
                             │   ChromaDB Vector Store │
                             └────────┬────────────────┘
                                      │
              ┌───────────────────────┼──────────────────┐
              ▼                       ▼                  ▼
       PostgreSQL                  Redis           Weather API
    (Predictions DB)             (Cache)         (Spray Planner)
```

---

## End-to-End Request Flow

```
1.  User opens app  →  JWT Login  →  Dashboard

2.  Upload image / camera capture
        │
        ▼
3.  POST /api/v1/predict  (multipart/form-data)
        │
        ▼
4.  File validation  →  JPEG/PNG check  →  MD5 Redis cache lookup
        │
        ▼ (cache miss)
5.  Image preprocessing
        Resize 256×256  →  ToTensor  →  Normalize (ImageNet stats)
        │
        ▼
6.  EfficientNet-B3 dual-head inference
        ├── plant_head    →  Plant species
        └── disease_head  →  Disease · Confidence · Top-3 · Severity
        │
        ▼
7.  RAG Pipeline  (if disease detected)
        ChromaDB retrieval (k=5 documents)
        →  LangChain prompt  →  Ollama LLM
        →  ICAR-structured treatment context
        │
        ▼
8.  CrewAI multi-agent workflow  (sequential)
        Agent 1:  Disease Analyst      (Llama 3.1 8B  via Groq)
        Agent 2:  Treatment Advisor    (Llama 3.3 70B via Groq)
        Agent 3:  Weather Advisor      (Llama 3.3 70B via Groq)
        Agent 4:  Communication Agent  (Llama 3.3 70B via Groq)
        │
        ▼
9.  PredictionResponse built  →  saved to PostgreSQL
        →  cached in Redis (TTL 3600s)
        │
        ▼
10. JSON response  →  Results screen
        Plant · Disease · Confidence · Severity · Top-3 · Agent Report
```

---

## Frontend

**Stack:** React 19 · TypeScript · Vite 6 · Tailwind CSS v4 · Motion v12 · Capacitor v8

### Screen Flow

```
Login  ──►  Home (Dashboard)  ──►  Result
  ▲                │
  └────────────────┘ (back navigation)
```

### Screens

**`Login.tsx`**
- Email/password form with show/hide password toggle
- Calls `POST /api/v1/auth/login`, stores JWT in app state
- Animated UI using Framer Motion

**`Home.tsx` (Dashboard)**
- File picker upload + live camera capture
- Sends image to `POST /api/v1/predict` with optional `lat`, `lng`, `lang` params
- Multi-stage animated loading feedback tied to real processing steps:

```
0s    →  🔍 Analysing leaf image...
3s    →  🧠 Detecting disease with EfficientNet-B3...
8s    →  🤖 Running AI Disease Specialist...
60s   →  💊 Generating treatment plan...
120s  →  🌤️  Checking weather for spray schedule...
180s  →  📋 Finalising report... almost done!
```

- Recent scan activity feed (local state)

**`Result.tsx`**
- Displays plant species, disease name, confidence %, severity badge
- Top-3 prediction breakdown
- Full AI-generated agent report (markdown rendered)
- Back to dashboard

### Component Tree

```
App.tsx                   ← Screen router: login | dashboard | result
├── Login.tsx
├── Home.tsx
│   ├── TopAppBar.tsx
│   └── BottomNav.tsx
└── Result.tsx
```

### Android Deployment (Capacitor)

```
App ID:    com.lab.agroai
App Name:  AgroAI
Web Dir:   dist
```

```bash
npm run build
npx cap sync android
npx cap open android
```

---

## Backend

**Stack:** FastAPI 0.111 · SQLAlchemy 2.0 (async) · Pydantic v2 · Uvicorn · python-jose

### Module Structure

```
backend/
├── main.py              ← App factory, lifespan, CORS, Prometheus, auth endpoints
├── config.py            ← Pydantic-settings, .env loading
├── routers/
│   ├── predict.py       ← POST /api/v1/predict  (7-step pipeline)
│   └── history.py       ← GET  /api/v1/history
├── services/            ← Business logic, orchestration
├── models/
│   ├── inference.py     ← ModelService: lazy load, predict()
│   ├── schemas.py       ← Pydantic: PredictionResponse, SeverityLevel, TopPrediction
│   └── mock_model.py    ← Dev fallback (no GPU required)
├── agents/
│   ├── crew_agents.py   ← CrewAI agents + Groq LLM config
│   ├── rag_pipeline.py  ← LangChain + Ollama RAG chain + SSE streaming
│   └── tools.py         ← WeatherTool, TranslateTool, PesticidePriceTool
└── database/
    ├── postgres.py      ← SQLAlchemy async engine, PredictionRecord ORM model
    ├── redis_cache.py   ← MD5-keyed response caching (TTL 3600s)
    └── vector_store.py  ← ChromaDB + HuggingFace embeddings + PDF ingestion
```

### Predict Endpoint — Step-by-Step

```python
POST /api/v1/predict
```

| Step | Action |
|------|--------|
| 1 | Validate file type (JPEG/PNG only) |
| 2 | MD5 hash → Redis cache lookup |
| 3 | Model guard (503 if not loaded) |
| 4 | EfficientNet-B3 inference |
| 5 | CrewAI agent report (async, skipped if healthy) |
| 6 | Build `PredictionResponse` via Pydantic |
| 7 | Background task: write result to Redis cache |

---

## ML Pipeline

### Model Architecture

- One forward pass → two outputs (plant + disease) simultaneously
- Lazy loading — model loads on first request, not at startup
- Auto-downloads from `MODEL_URL` (Azure Storage) if not present locally
- CUDA / CPU auto-detection

### Preprocessing

```python
transforms.Resize((256, 256))
transforms.ToTensor()
transforms.Normalize(
    mean=[0.485, 0.456, 0.406],   # ImageNet mean
    std=[0.229, 0.224, 0.225]     # ImageNet std
)
```

### Inference Output

```python
{
    "plant":            "Tomato",
    "disease":          "Early_Blight",
    "confidence":       0.95,             # float 0–1
    "uncertainty":      0.05,
    "confidence_range": [0.90, 1.00],
    "is_healthy":       False,
    "top3": [
        {"class_name": "Early_Blight", "confidence": 0.95},
        {"class_name": "Late_Blight",  "confidence": 0.03},
        {"class_name": "Healthy",      "confidence": 0.02}
    ]
}
```

### Severity Mapping

| Confidence | is_healthy | Severity |
|---|---|---|
| any | `True` | `HEALTHY` |
| > 0.90 | `False` | `SEVERE` |
| > 0.70 | `False` | `MODERATE` |
| ≤ 0.70 | `False` | `MILD` |

### Supported Crops

150+ disease classes across 30+ crops:

`Apple` · `Banana` · `Cabbage` · `Cauliflower` · `Chili` · `Coffee` · `Corn` · `Eggplant` · `Gourd` · `Grape` · `Hibiscus` · `Jasmine` · `Lettuce` · `Lemon` · `Mango` · `Orange` · `Papaya` · `Pea` · `Peach` · `Pepper` · `Plum` · `Potato` · `Pumpkin` · `Rice` · `Rose` · `Soybean` · `Strawberry` · `Sugarcane` · `Tea` · `Tomato` · `Wheat`

---

## RAG Pipeline

**Stack:** LangChain · LangChain-Ollama · ChromaDB · HuggingFace Embeddings

The RAG pipeline ensures treatment recommendations are grounded in actual agricultural research — not hallucinated by the LLM.

```
Disease + Plant + Confidence + Location (India)
        │
        ▼
ChromaDB semantic retrieval
    collection: "plant_disease_knowledge"
    embeddings: HuggingFace (sentence-transformers, CPU)
    k = 5 documents retrieved
        │
        ▼
LangChain TREATMENT_PROMPT
    Context: retrieved research chunks
    Format:  ICAR-aligned, Indian farming context
        │
        ▼
Ollama LLM  (local · no API key required)
    model:    OLLAMA_MODEL  (default: llama3)
    base_url: OLLAMA_BASE_URL (default: http://localhost:11434)
        │
        ▼
Structured treatment plan:
    1. IMMEDIATE ACTION     (next 24 hours)
    2. CHEMICAL TREATMENT   (ICAR-approved pesticide, exact dosage)
    3. ORGANIC ALTERNATIVE  (neem oil, copper sulfate, etc.)
    4. PREVENTIVE MEASURES
    5. ESTIMATED RECOVERY TIME
```

### SSE Streaming

The endpoint `GET /api/v1/predict/stream/{disease}` streams RAG output as Server-Sent Events for real-time frontend rendering.

### Building the Knowledge Base

```bash
# Add plant disease PDFs to data/disease_docs/
python -m backend.database.vector_store
# Chunks PDFs (size=1000, overlap=200) and ingests into ChromaDB
```

---

## Multi-Agent System

**Stack:** CrewAI ≥ 0.51 · Groq API · Sequential process

All four agents run sequentially — each task receives context from the previous one.

### Agent 1 — Disease Analyst

| Property | Value |
|---|---|
| **Model** | `groq/llama-3.1-8b-instant` |
| **Tools** | None (expert knowledge only) |
| **Output** | Disease stage, spread speed, crop loss %, worsening conditions |

### Agent 2 — Treatment Advisor

| Property | Value |
|---|---|
| **Model** | `groq/llama-3.3-70b-versatile` |
| **Tools** | `PesticidePriceTool` (pre-fetched, no ReAct loop) |
| **Output** | Chemical name, dosage, frequency, cost (₹), organic alternative |

### Agent 3 — Weather Advisor

| Property | Value |
|---|---|
| **Model** | `groq/llama-3.3-70b-versatile` |
| **Tools** | `WeatherTool` (called once) |
| **Output** | 7-day spray schedule with ✅ safe / ❌ unsafe days |

### Agent 4 — Farmer Communication Agent

| Property | Value |
|---|---|
| **Model** | `groq/llama-3.3-70b-versatile` |
| **Tools** | `TranslateTool` (only if `lang != "en"`) |
| **Output** | Final bullet-point farmer report starting with "Most Important Action Today:" |

### Crew Configuration

```python
crew = Crew(
    agents=[disease_analyst, treatment_advisor, weather_agent, report_writer],
    tasks=[task1, task2, task3, task4],
    process=Process.sequential,
    memory=False,
)
```

### Rate Limit Handling

The crew retries up to 3 times on Groq `429` errors, with progressive backoff (60s · 120s · 180s). On final failure, a structured fallback report is returned — the prediction response is never blocked.

---

## Database Design

### PostgreSQL — `predictions` table

| Column | Type | Notes |
|---|---|---|
| `id` | String (PK) | UUID |
| `plant` | String | indexed |
| `disease` | String | indexed |
| `confidence` | Float | |
| `uncertainty` | Float | |
| `severity` | String | HEALTHY/MILD/MODERATE/SEVERE |
| `is_healthy` | Boolean | |
| `latitude` | Float | nullable |
| `longitude` | Float | nullable |
| `top3` | JSON | list of `{class_name, confidence}` |
| `created_at` | DateTime | indexed, UTC |

### Redis — Response Cache

- **Key:** MD5 hash of image bytes
- **Value:** Serialized `PredictionResponse`
- **TTL:** 3600 seconds
- Written as a background task (non-blocking)

### ChromaDB — Vector Store

- **Collection:** `plant_disease_knowledge`
- **Embeddings:** HuggingFace sentence-transformers (CPU)
- **Persist path:** `./data/chroma_db`
- **Chunk size:** 1000 tokens · overlap: 200

---

## API Reference

### Authentication

```http
POST /api/v1/auth/login
Content-Type: application/json

{ "email": "admin@agro.com", "password": "admin" }
```

```json
{ "token": "<JWT>", "name": "AgriGuard Admin", "email": "admin@agro.com" }
```

---

### Disease Prediction

```http
POST /api/v1/predict
Content-Type: multipart/form-data

file=<image>          # JPEG or PNG
use_agents=true       # run CrewAI (default: true)
lat=18.5204           # optional, for weather
lng=73.8567           # optional
lang=en               # optional, for translation
```

**Response:**

```json
{
  "prediction_id": "550e8400-e29b-41d4-a716-446655440000",
  "plant":         "Tomato",
  "disease":       "Early_Blight",
  "confidence":    0.95,
  "uncertainty":   0.05,
  "confidence_range": [0.90, 1.00],
  "is_healthy":    false,
  "severity":      "severe",
  "top3": [
    { "class_name": "Early_Blight", "confidence": 0.95 },
    { "class_name": "Late_Blight",  "confidence": 0.03 },
    { "class_name": "Healthy",      "confidence": 0.02 }
  ],
  "treatment_advice": null,
  "agent_report":  "**Most Important Action Today:** ...",
  "timestamp":     "2026-06-02T09:53:00Z"
}
```

---

### Prediction History

```http
GET /api/v1/history?limit=100
```

---

### Agent Report (Standalone)

```http
POST /api/v1/agent-report
Content-Type: application/json

{ "plant": "Tomato", "disease": "Early Blight", "is_healthy": false }
```

Uses Ollama locally — no API key required.

---

### RAG Stream (SSE)

```http
GET /api/v1/predict/stream/{disease}?plant=Tomato
```

Returns `text/event-stream` — real-time RAG output chunks.

---

### Health Checks

```http
GET /health       →  { "status": "healthy", "model_loaded": true, "ollama_url": "..." }
GET /api/v1/health →  { "status": "ok", "version": "1.0.0" }
```

---

## Tech Stack

### Frontend

| Package | Version | Purpose |
|---|---|---|
| React | 19.0.1 | UI framework |
| TypeScript | 5.8 | Type safety |
| Vite | 6.2 | Build tool (dev port: 3001) |
| Tailwind CSS | 4.1 | Utility-first styling |
| Motion | 12.x | Animations (Framer Motion) |
| Lucide React | 0.546 | Icon library |
| Capacitor | 8.3 | Android packaging |

### Backend

| Package | Version | Purpose |
|---|---|---|
| FastAPI | 0.111 | API framework |
| Uvicorn | 0.30 | ASGI server |
| Pydantic | 2.7 | Request/response validation |
| SQLAlchemy | 2.0 | Async ORM |
| asyncpg | 0.29 | PostgreSQL async driver |
| redis | 5.0 | Caching |
| python-jose | 3.3 | JWT |
| httpx | 0.27 | Async HTTP client |
| gunicorn | 21.2 | Production process manager |

### AI / ML

| Package | Purpose |
|---|---|
| PyTorch 2.3 (CPU) | Model inference |
| torchvision 0.18 | EfficientNet-B3 backbone + transforms |
| Pillow 10.3 | Image loading |
| CrewAI ≥ 0.51 | Multi-agent orchestration |
| LangChain 0.2 | RAG chain |
| langchain-ollama | Local LLM integration |
| langchain-groq | Groq cloud LLM integration |
| chromadb | Vector database |
| HuggingFace Embeddings | Document embeddings (CPU) |
| duckduckgo-search | Web search tool for agents |

### Infrastructure

| Tool | Purpose |
|---|---|
| Docker + Docker Compose | Containerization |
| Nginx | Reverse proxy |
| Prometheus | Metrics collection |
| GitHub Actions | CI/CD → Azure |

---

## Project Structure

```
Agro/
│
├── Frontend/
│   ├── src/
│   │   ├── App.tsx               ← Screen router + shared types
│   │   ├── types.ts              ← CropResult, RecentScan interfaces
│   │   ├── index.css
│   │   ├── main.tsx
│   │   └── components/
│   │       ├── Login.tsx
│   │       ├── Home.tsx
│   │       ├── Result.tsx
│   │       ├── BottomNav.tsx
│   │       └── TopAppBar.tsx
│   ├── public/
│   ├── android/                  ← Capacitor Android project
│   ├── capacitor.config.ts
│   ├── vite.config.ts
│   └── package.json
│
├── backend/
│   ├── main.py
│   ├── config.py
│   ├── routers/
│   │   ├── predict.py
│   │   └── history.py
│   ├── services/
│   ├── models/
│   │   ├── inference.py
│   │   ├── schemas.py
│   │   └── mock_model.py
│   ├── agents/
│   │   ├── crew_agents.py
│   │   ├── rag_pipeline.py
│   │   └── tools.py
│   └── database/
│       ├── postgres.py
│       ├── redis_cache.py
│       └── vector_store.py
│
├── data/
│   ├── models/                   ← best_model.pth, classes.json
│   ├── chroma_db/                ← ChromaDB vector store
│   └── disease_docs/             ← Source PDFs for RAG ingestion
│
├── ml/                           ← Training pipeline
├── infrastructure/
│   ├── docker-compose.yml
│   └── .github/workflows/ci-cd.yml
│
├── .github/
│   └── workflows/
│       └── main_florascope-api.yml   ← Azure deployment
│
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL
- Redis
- Ollama (`ollama pull llama3`)
- Groq API key ([console.groq.com](https://console.groq.com))

### Backend Setup

```bash
# Clone the repo
git clone https://github.com/shrutivinodshinde/Agro.git
cd Agro

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env — set POSTGRES_URL, GROQ_API_KEY, OLLAMA_BASE_URL, MODEL_URL

# Start Ollama locally
ollama pull llama3
ollama serve

# Build the RAG knowledge base (add PDFs to data/disease_docs/ first)
python -m backend.database.vector_store

# Run the backend
uvicorn backend.main:app --reload --port 8000
# API available at http://localhost:8000
```

### Frontend Setup

```bash
cd Frontend

npm install

# Set backend URL
echo "VITE_API_URL=http://localhost:8000" > .env

npm run dev
# App available at http://localhost:3001
```

### Android Build

```bash
cd Frontend
npm run build
npx cap sync android
npx cap open android   # Opens in Android Studio
```

---

## Docker Deployment

```bash
# Build and start all services (API + PostgreSQL + Redis + Nginx)
docker compose -f infrastructure/docker-compose.yml up --build -d

# View logs
docker compose -f infrastructure/docker-compose.yml logs -f

# Stop
docker compose -f infrastructure/docker-compose.yml down
```

---

## Environment Variables

```env
# Database
POSTGRES_URL=
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=

# Redis
REDIS_HOST=localhost
REDIS_PORT=

# AI — Groq (for CrewAI agents)
GROQ_API_KEY=

# AI — Ollama (for RAG pipeline, local)
OLLAMA_BASE_URL=
OLLAMA_MODEL=llama3

# HuggingFace (for ChromaDB embeddings)
HF_MODEL_NAME=

# Model
MODEL_URL=           # Azure Blob Storage URL to download best_model.pth

# Auth
SECRET_KEY=change-me-in-production
DEMO_EMAIL=admin@agro.com
DEMO_PASSWORD=admin
DEMO_NAME=AgriGuard Admin
```

---

## Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=backend
```

Coverage includes:
- API endpoint tests (predict, history, auth, health)
- Model inference (EfficientNet-B3 forward pass)
- RAG pipeline (retrieval + chain)
- CrewAI agent workflows
- Redis cache read/write
- PostgreSQL CRUD

---

## Roadmap

- [ ] Offline mobile inference (TFLite / ONNX export)
- [ ] Voice-based advisory in regional languages
- [ ] Real-time IoT sensor integration
- [ ] Satellite-assisted crop health monitoring
- [ ] Drone-based field scanning support
- [ ] Market price intelligence per crop
- [ ] Farmer-specific history and personalization
- [ ] Precision farming recommendations
- [ ] PWA support (installable web app)

---

<div align="center">

Built with ❤️ using Deep Learning, RAG, and Multi-Agent AI

**Agro — Empowering Agriculture Through Artificial Intelligence**

</div>
