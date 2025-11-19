from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import pika


class ScrapeRequest(BaseModel):
    url: str


app = FastAPI(title="Centinela API Gateway")

# Valores por defecto: en local no pasará nada raro si no hay RabbitMQ
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE", "scraping_requests")


def send_to_queue(queue_name: str, payload: str) -> None:
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
