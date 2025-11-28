from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import pika


class ScrapeRequest(BaseModel):
    url: str


app = FastAPI(title="Centinela API Gateway")

#  Orígenes permitidos (frontend en dev y en VM)
origins = [
    "http://localhost:5173",        # Vite en tu máquina
    "http://192.168.254.128",       # Frontend en la VM (cuando lo levantemos en 80)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # en producción lo ideal es poner origen específico
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Valores por defecto: en local no pasará nada raro si no hay RabbitMQ
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE", "scraping_requests")


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


@app.get("/health")
def health():
    """
    Endpoint de salud del backend.
    """
    return {"status": "ok"}


@app.post("/scrape")
def scrape(request: ScrapeRequest):
    """
    Recibe una URL y la envía a la cola de scraping.
    """
    url = request.url

    if not url.startswith("http"):
        raise HTTPException(status_code=400, detail="URL inválida")

    try:
        send_to_queue(RABBITMQ_QUEUE, url)
    except Exception as e:
        # RabbitMQ puede no estar levantado en desarrollo.
        raise HTTPException(
            status_code=503,
            detail="No se pudo enviar la tarea de scraping (servicio de cola no disponible)",
        ) from e

    return {"message": "URL recibida para scraping", "url": url}
