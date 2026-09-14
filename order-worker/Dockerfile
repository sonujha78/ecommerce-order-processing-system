# ---- Build stage ----
FROM python:3.12-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ---- Final stage ----
FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

COPY . .

RUN rm -rf venv .env __pycache__

# Liveness/readiness handled via `celery inspect ping` in K8s probes (see k8s manifests)

CMD ["celery", "-A", "order_worker", "worker", "--loglevel=info", "-Q", "order_processing"]
