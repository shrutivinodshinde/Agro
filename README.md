# 🌿 Agro — AI-Powered Plant Disease Detection & Agricultural Advisory Platform

<div align="center">

### Intelligent Agriculture Powered by Deep Learning, RAG, and Multi-Agent AI

Upload a plant image, detect diseases instantly, retrieve agricultural knowledge, and receive actionable treatment recommendations through specialized AI agents.

</div>

---

# 📖 Overview

Agro is an AI-driven agricultural decision support platform designed to help farmers, agronomists, and agricultural organizations identify plant diseases and receive scientifically grounded treatment recommendations.

The platform combines:

* Deep Learning for disease detection
* Retrieval-Augmented Generation (RAG)
* Multi-Agent AI collaboration
* Agricultural knowledge retrieval
* Weather-aware recommendations
* Mobile-friendly deployment

Unlike traditional plant disease classifiers, Agro not only predicts diseases but also explains them, assesses severity, retrieves relevant agricultural knowledge, and generates farmer-friendly treatment plans.

---

# 🚀 Key Features

## 🌱 Plant Disease Detection

* Image-based disease diagnosis
* Multi-crop support
* Healthy vs Diseased classification
* Confidence scoring
* Top predictions ranking
* Severity assessment

## 🤖 AI Agricultural Advisory

* Treatment recommendations
* Pesticide suggestions
* Organic alternatives
* Preventive measures
* Recovery guidance
* Risk assessment

## 📚 Retrieval-Augmented Generation (RAG)

* Agricultural knowledge retrieval
* Research-backed recommendations
* Context-aware reasoning
* Reduced hallucinations
* Grounded treatment generation

## 🧠 Multi-Agent Intelligence

Specialized AI agents collaborate to:

* Analyze disease conditions
* Assess environmental impact
* Generate treatment plans
* Simplify recommendations
* Produce farmer-friendly reports

## 📱 Mobile Ready

* Camera capture support
* Gallery image upload
* Android deployment through Capacitor
* Responsive user experience

---

# 🏗️ System Architecture

```text
┌───────────────────────────────────────────────┐
│                React Frontend                 │
│        React + TypeScript + Vite             │
└─────────────────────┬─────────────────────────┘
                      │
                      ▼
┌───────────────────────────────────────────────┐
│                FastAPI Backend                │
└─────────────────────┬─────────────────────────┘
                      │
        ┌─────────────┴─────────────┐
        ▼                           ▼

┌──────────────────┐     ┌──────────────────────┐
│ EfficientNet-B3  │     │ CrewAI Agent System  │
│ Disease Model    │     │ + RAG Pipeline       │
└──────────────────┘     └──────────────────────┘
        │                           │
        ▼                           ▼

┌──────────────────┐     ┌──────────────────────┐
│ Vector Database  │     │ Weather & Tools      │
│ Knowledge Store  │     │ Translation Services │
└──────────────────┘     └──────────────────────┘
        │                           │
        └─────────────┬─────────────┘
                      ▼

             Recommendation Engine
                      │
                      ▼

              Farmer-Friendly Report
```

---

# 🔄 End-to-End Workflow

```text
Farmer Uploads Image
          │
          ▼
Frontend Application
          │
          ▼
FastAPI Backend
          │
          ▼
Image Processing
          │
          ▼
EfficientNet-B3 Inference
          │
          ▼
Disease Prediction
          │
          ▼
Knowledge Retrieval (RAG)
          │
          ▼
CrewAI Multi-Agent Analysis
          │
          ▼
Treatment Recommendation
          │
          ▼
Database Storage
          │
          ▼
Frontend Dashboard
          │
          ▼
Farmer Receives Report
```

---

# 🖥️ Frontend Architecture

The frontend is developed using **React 19**, **TypeScript**, and **Vite** to provide a fast, responsive, and mobile-friendly experience.

## Responsibilities

The frontend serves as the primary interaction layer between users and AI services.

### Features

* Authentication
* Image uploads
* Camera capture
* Disease scan initiation
* Report visualization
* Historical scan tracking
* Mobile application support

---

## Frontend Flow

```text
User
 │
 ▼
Upload Image
 │
 ▼
React Components
 │
 ▼
API Request
 │
 ▼
Backend Response
 │
 ▼
Results Dashboard
```

---

## Core Screens

### `Login.tsx`
- Email/password form with show/hide password toggle
- Calls `POST /api/v1/auth/login`, stores JWT in app state
- Animated UI using Framer Motion

### `Home.tsx` (Dashboard)
- File picker upload + live camera capture
- Sends image to `POST /api/v1/predict` with optional `lat`, `lng`, `lang` params
- Multi-stage animated loading feedback tied to real processing steps:

0s    →  🔍 Analysing leaf image...
3s    →  🧠 Detecting disease with EfficientNet-B3...
8s    →  🤖 Running AI Disease Specialist...
60s   →  💊 Generating treatment plan...
120s  →  🌤️  Checking weather for spray schedule...
180s  →  📋 Finalising report... almost done!

- Recent scan activity feed (local state)

### `Result.tsx`
- Displays plant species, disease name, confidence %, severity badge
- Top-3 prediction breakdown
- Full AI-generated agent report (markdown rendered)
- Back to dashboard

---

## Mobile Deployment

Using Capacitor, the web application can be deployed as a native Android application.

Benefits:

* Native camera support
* Better performance
* Mobile-first experience
* Future offline capabilities

---

# ⚙️ Backend Architecture

The backend is implemented using **FastAPI** and follows a modular service-oriented architecture.

Its primary responsibilities include:

* Image processing
* Disease prediction
* AI orchestration
* Knowledge retrieval
* Report generation
* Data persistence

---

## Backend Request Lifecycle

```text
Client Request
      │
      ▼
FastAPI Router
      │
      ▼
Service Layer
      │
      ▼
Inference Engine
      │
      ▼
RAG Pipeline
      │
      ▼
CrewAI Agents
      │
      ▼
Recommendation Engine
      │
      ▼
Database Layer
      │
      ▼
JSON Response
```

---

## API Layer

Located in:

```text
backend/routers/
```

Responsibilities:

* Route handling
* Request validation
* File uploads
* Response generation

---

## Service Layer

Located in:

```text
backend/services/
```

Responsibilities:

* Business logic
* Prediction orchestration
* Agent coordination
* Data transformation

---

## Model Layer

Located in:

```text
backend/models/
```

Responsibilities:

* Image preprocessing
* Disease classification
* Confidence estimation
* Prediction generation

---

## Agent Layer

Located in:

```text
backend/agents/
```

Responsibilities:

* CrewAI workflows
* RAG integration
* Tool execution
* Recommendation generation

---

# 🤖 AI & Machine Learning Pipeline

## Image Processing

Uploaded images undergo:

* Resizing
* Normalization
* Tensor conversion

Configuration:

```python
Resize = 256x256

mean = [0.485, 0.456, 0.406]
std  = [0.229, 0.224, 0.225]
```

---

## Deep Learning Model

Agro uses a custom EfficientNet-B3 based architecture.

### Outputs

* Plant species
* Disease category
* Confidence score
* Healthy status
* Severity estimation
* Top predictions

---

## Retrieval-Augmented Generation (RAG)

The RAG pipeline enriches recommendations using agricultural knowledge sources.

### Workflow

```text
Prediction
    │
    ▼
Retrieve Context
    │
    ▼
Rank Documents
    │
    ▼
Provide Context to LLM
    │
    ▼
Generate Recommendation
```

Benefits:

* Research-backed responses
* Reduced hallucinations
* Explainable recommendations

---

# 🧠 Multi-Agent System

The platform uses CrewAI to orchestrate specialized agricultural agents.

---

## Disease Analyst Agent

**Role:** Plant Disease Specialist

Responsibilities:

* Interpret disease predictions
* Assess severity
* Validate diagnoses
* Risk analysis

**Model:** Llama 3.1 8B

---

## Weather Advisor Agent

**Role:** Weather & Spray Planner

Responsibilities:

* Weather assessment
* Spray scheduling
* Environmental analysis

Tools:

* Weather Tool

**Model:** Llama 3.3 70B

---

## Treatment Advisor Agent

**Role:** Agricultural Treatment Expert

Responsibilities:

* Treatment planning
* Pesticide recommendations
* Preventive strategies
* Cost-aware guidance

**Model:** Llama 3.3 70B

---

## Farmer Communication Agent

**Role:** Communication Specialist

Responsibilities:

* Simplify recommendations
* Generate farmer-friendly reports
* Support multilingual output

Tools:

* Translation Tool

---

# 🗄️ Database Architecture

## PostgreSQL

Stores:

* Users
* Prediction history
* Reports
* Metadata

---

## Redis

Used for:

* Response caching
* Session acceleration
* Faster repeated predictions

---

## Vector Database

Stores:

* Agricultural embeddings
* Research documents
* Disease knowledge
* Treatment references

Used by the RAG pipeline for semantic retrieval.

---

# 🌾 Supported Crops

The current model supports over **150+ disease classes** across multiple crops.

### Crop Categories

* Apple
* Banana
* Cabbage
* Cauliflower
* Chili
* Coffee
* Corn
* Eggplant
* Gourd
* Grape
* Hibiscus
* Jasmine
* Lettuce
* Lemon
* Mango
* Orange
* Papaya
* Pea
* Peach
* Pepper
* Plum
* Potato
* Pumpkin
* Rice
* Rose
* Soybean
* Strawberry
* Sugarcane
* Tea
* Tomato
* Wheat

---

# 🔌 API Design

## Disease Prediction Endpoint

```http
POST /api/v1/predict
```

### Supported Formats

* JPG
* JPEG
* PNG

### Example Response

```json
{
  "prediction_id": "uuid",
  "plant": "Tomato",
  "disease": "Early Blight",
  "confidence": 0.95,
  "severity": "SEVERE",
  "is_healthy": false,
  "treatment_advice": "...",
  "agent_report": "..."
}
```

---

# 🛠️ Technology Stack

## Frontend

* React 19
* TypeScript
* Vite
* Tailwind CSS
* Framer Motion
* Capacitor

## Backend

* FastAPI
* SQLAlchemy
* Pydantic
* Uvicorn

## AI / ML

* PyTorch
* EfficientNet-B3
* CrewAI
* LangChain
* Ollama
* Groq LLMs

## Databases

* PostgreSQL
* Redis
* Vector Database

## Infrastructure

* Docker
* Docker Compose
* Nginx
* Prometheus

---

# 📁 Project Structure

```text
Agro/
│
├── Frontend/
│   ├── src/
│   ├── public/
│   ├── android/
│   └── components/
│
├── backend/
│   ├── agents/
│   ├── database/
│   ├── models/
│   ├── routers/
│   ├── services/
│   ├── schemas/
│   └── tests/
│
├── data/
│
├── ml/
│
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

---

# 🚀 Local Development

## Backend Setup

```bash
cd backend

pip install -r requirements.txt

uvicorn main:app --reload
```

Backend:

```text
http://localhost:8000
```

---

## Frontend Setup

```bash
cd Frontend

npm install

npm run dev
```

Frontend:

```text
http://localhost:5173
```

---

# 🐳 Docker Deployment

## Build

```bash
docker compose build
```

## Start

```bash
docker compose up -d
```

## Logs

```bash
docker compose logs -f
```

## Stop

```bash
docker compose down
```

---

# 📊 Monitoring & Observability

Prometheus integration provides:

* Request metrics
* Response latency
* API health monitoring
* Error tracking
* Service performance analytics

This enables production-grade observability and monitoring.

---

# 🔐 Environment Variables

```env
POSTGRES_URL=

POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=

REDIS_HOST=
REDIS_PORT=

GROQ_API_KEY=

OLLAMA_BASE_URL=
OLLAMA_MODEL=

MODEL_URL=

SECRET_KEY=
```

---

# 🧪 Testing

Run all tests:

```bash
pytest
```

Covered areas:

* API testing
* Model inference
* Agent workflows
* Service integrations

---

# 🎯 Design Principles

* Modular Architecture
* Separation of Concerns
* Scalable Design
* AI-First Development
* Agent-Driven Intelligence
* Retrieval-Grounded Responses
* Production-Ready Monitoring
* Containerized Deployment
* Mobile-First Experience
* Maintainable Codebase

---

# 🔮 Future Roadmap

* Real-time weather integration
* Voice-based advisory
* Offline mobile inference
* Precision farming recommendations
* Farmer-specific personalization
* Market price intelligence
* Regional language expansion
* Satellite-assisted crop monitoring
* IoT sensor integration
* Drone-based crop health assessment

---

to build an intelligent agricultural decision-support platform focused on improving disease diagnosis, treatment planning, and farmer accessibility.

---

# 📄 License

This project is licensed under the terms specified by the repository owner.

---

<div align="center">

### 🌿 Agro — Empowering Agriculture Through Artificial Intelligence

Built with ❤️ using Deep Learning, RAG, and Multi-Agent AI.

</div>
