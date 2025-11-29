from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel, HttpUrl

import os
from typing import List

import pika
import requests
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

app = FastAPI(title="Centinela API Gateway")

# --------------------- Modelos ---------------------


class ScrapeRequest(BaseModel):
    url: HttpUrl


class AnalyzeRequest(BaseModel):
    url: HttpUrl


class AnalyzeResult(BaseModel):
    url: HttpUrl
    title: str
    summary: str
    score: float
    label: str


# --------------------- CORS ------------------------

origins: List[str] = [
    "http://localhost:5173",      # Vite en tu máquina
    # "http://192.168.254.128",   # si algún día sirves el frontend desde la VM
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------- Configuración -------------------

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE", "scraping_requests")

ANALYSIS_HOST = os.getenv("ANALYSIS_HOST", "analysis-service")
ANALYSIS_PORT = int(os.getenv("ANALYSIS_PORT", "9000"))

# ------------------ Métricas -----------------------

REQUEST_COUNT = Counter(
    "centinela_http_requests_total",
    "Total de peticiones HTTP recibidas por el API Gateway",
    ["endpoint", "method"],
)
ANALYZE_LATENCY = Histogram(
    "centinela_analyze_seconds",
    "Tiempo de respuesta del endpoint /analyze",
)


def send_to_queue(queue_name: str, payload: str) -> None:
    """Envía un mensaje a RabbitMQ (cola de scraping)."""
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=queue_name, durable=True)
    channel.basic_publish(exchange="", routing_key=queue_name, body=payload.encode("utf-8"))
    connection.close()


# ------------------ Endpoints ----------------------


@app.get("/health")
def health():
    REQUEST_COUNT.labels(endpoint="/health", method="GET").inc()
    return {"status": "ok"}


@app.post("/scrape")
def scrape(request: ScrapeRequest):
    """
    Modo asíncrono: manda la URL a la cola de RabbitMQ.
    Lo dejamos como soporte al requerimiento de broker de mensajes.
    """
    REQUEST_COUNT.labels(endpoint="/scrape", method="POST").inc()

    url = str(request.url)

    if not url.startswith("http"):
        raise HTTPException(status_code=400, detail="URL inválida")

    try:
        send_to_queue(RABBITMQ_QUEUE, url)
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail="No se pudo enviar la tarea de scraping (RabbitMQ no disponible)",
        ) from e

    return {"message": "URL recibida para scraping", "url": url}


@app.post("/analyze", response_model=AnalyzeResult)
def analyze(req: AnalyzeRequest):
    """
    Modo síncrono: llama al microservicio analysis-service,
    que hace scraping + análisis básico y guarda el resultado en PostgreSQL.
    """
    REQUEST_COUNT.labels(endpoint="/analyze", method="POST").inc()
    url = str(req.url)

    with ANALYZE_LATENCY.time():
        try:
            resp = requests.post(
                f"http://{ANALYSIS_HOST}:{ANALYSIS_PORT}/analyze",
                json={"url": url},
                timeout=60,
            )
        except requests.RequestException as exc:
            raise HTTPException(
                status_code=502,
                detail=f"Error llamando a analysis-service: {exc}",
            )

        if resp.status_code != 200:
            raise HTTPException(
                status_code=resp.status_code,
                detail=f"analysis-service devolvió error: {resp.text}",
            )

        data = resp.json()

    return data  # FastAPI lo valida contra AnalyzeResult


@app.get("/metrics")
def metrics():
    """Endpoint para Prometheus."""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
