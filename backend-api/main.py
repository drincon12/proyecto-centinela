from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
import os
import pika
import requests

app = FastAPI(title="Centinela API Gateway")

# ======== MODELOS =========

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

# ======== CORS =========

origins = [
    "http://localhost:5173",      # Vite en tu máquina
    "http://192.168.254.128",     # Frontend en VM (si lo levantas en 80)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # para el proyecto dejamos todo abierto
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ======== CONFIG =========

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE", "scraping_requests")

ANALYSIS_HOST = os.getenv("ANALYSIS_HOST", "analysis-service")
ANALYSIS_PORT = int(os.getenv("ANALYSIS_PORT", "9000"))


def send_to_queue(queue_name: str, payload: str):
    """
    Envía un mensaje a la cola de RabbitMQ.
    """
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST)
    )
    channel = connection.channel()
    channel.queue_declare(queue=queue_name, durable=True)
    channel.basic_publish(
        exchange="",
        routing_key=queue_name,
        body=payload.encode("utf-8"),
    )
    connection.close()


# ======== ENDPOINTS =========

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/scrape")
def scrape(request: ScrapeRequest):
    """
    Recibe una URL y la envía a la cola de scraping (modo asíncrono).
    """
    url = str(request.url)

    if not url.startswith("http"):
        raise HTTPException(status_code=400, detail="URL inválida")

    try:
        send_to_queue(RABBITMQ_QUEUE, url)
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail="No se pudo enviar la tarea de scraping (cola no disponible)",
        ) from e

    return {"message": "URL recibida para scraping", "url": url}


@app.post("/analyze", response_model=AnalyzeResult)
def analyze(req: AnalyzeRequest):
    """
    Recibe la URL desde el frontend y delega el trabajo al microservicio
    analysis-service, que hace scraping + análisis básico.
    """
    try:
        resp = requests.post(
            f"http://{ANALYSIS_HOST}:{ANALYSIS_PORT}/analyze",
            json={"url": str(req.url)},
            timeout=30,
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

    return resp.json()
