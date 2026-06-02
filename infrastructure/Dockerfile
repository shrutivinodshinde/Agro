# Multi-stage build
FROM python:3.10-slim AS builder

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl

COPY --from=builder /root/.local /root/.local

ENV PATH=/root/.local/bin:$PATH

COPY backend/ ./backend/
COPY frontend/ ./frontend/
COPY data/models/ ./data/models/

RUN adduser --disabled-password --gecos '' appuser

# USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl -f http://localhost:8000/ || exit 1

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]