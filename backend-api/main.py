from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel, HttpUrl

import os
from typing import List
import psycopg2
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

class PublishRequest(BaseModel):
    message: str
    platform: str = "social"

# --------------------- CORS ------------------------

origins: List[str] = [
    "http://localhost:5173",      # Vite en tu máquina
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
SCRAPING_QUEUE = os.getenv("SCRAPING_QUEUE", "scraping_queue")
ANALYTICS_QUEUE = os.getenv("ANALYTICS_QUEUE", "analytics_queue")
PUBLISH_QUEUE = os.getenv("PUBLISH_QUEUE", "publish_queue")

ANALYSIS_HOST = os.getenv("ANALYSIS_HOST", "analysis-api")
ANALYSIS_PORT = int(os.getenv("ANALYSIS_PORT", "9000"))

DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "centinela_db")
DB_USER = os.getenv("DB_USER", "centinela")
DB_PASSWORD = os.getenv("DB_PASSWORD", "centinela")

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST, port=DB_PORT,
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD
    )

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
URLS_ADDED = Counter("centinela_urls_added_total", "Número de URLs añadidas")
URLS_PUBLISHED = Counter("centinela_urls_published_total", "Número de publicaciones enviadas")

def send_to_queue(queue_name: str, payload: str) -> None:
    """Envía un mensaje a RabbitMQ."""
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
    """Manda la URL a la cola de scraping."""
    REQUEST_COUNT.labels(endpoint="/scrape", method="POST").inc()
    url = str(request.url)

    if not url.startswith("http"):
        raise HTTPException(status_code=400, detail="URL inválida")

    try:
        send_to_queue(SCRAPING_QUEUE, url)
        URLS_ADDED.inc()
    except Exception as e:
        raise HTTPException(status_code=503, detail="RabbitMQ no disponible") from e

    return {"message": "URL recibida para scraping", "url": url}

@app.get("/urls")
def list_urls():
    """Listar todas las URLs registradas en la base de datos."""
    REQUEST_COUNT.labels(endpoint="/urls", method="GET").inc()
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, url, status, created_at FROM urls ORDER BY created_at DESC")
            rows = cur.fetchall()
    finally:
        conn.close()
    return [{"id": r[0], "url": r[1], "status": r[2], "created_at": r[3]} for r in rows]

@app.post("/analyze", response_model=AnalyzeResult)
def analyze(req: AnalyzeRequest):
    """Llama al microservicio analysis-api para analizar la URL."""
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
            raise HTTPException(status_code=502, detail=f"Error llamando a analysis-service: {exc}")

        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=f"analysis-service devolvió error: {resp.text}")

        data = resp.json()

    return data

@app.post("/publish")
def publish(req: PublishRequest):
    """Manda un mensaje a la cola de publicación."""
    REQUEST_COUNT.labels(endpoint="/publish", method="POST").inc()
    try:
        send_to_queue(PUBLISH_QUEUE, req.message)
        URLS_PUBLISHED.inc()
    except Exception as e:
        raise HTTPException(status_code=503, detail="RabbitMQ no disponible") from e

    return {"message": f"Mensaje enviado a {PUBLISH_QUEUE}", "platform": req.platform}

@app.get("/metrics")
def metrics():
    """Endpoint para Prometheus."""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
