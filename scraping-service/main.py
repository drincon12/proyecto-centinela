import pika
import os
import requests
from bs4 import BeautifulSoup
import json

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
REQUEST_QUEUE = os.getenv("REQUEST_QUEUE", "scraping_requests")


def process_url(url: str) -> dict:
    """
    Realiza un scraping muy básico: título y párrafos de la página.
    """
    resp = requests.get(url, timeout=10)
    soup = BeautifulSoup(resp.text, "html.parser")
    title = soup.title.string if soup.title else "Sin título"
    content = " ".join([p.get_text() for p in soup.find_all("p")])[:2000]

    return {
        "url": url,
        "title": title,
        "content": content,
    }


def callback(ch, method, properties, body):
    url = body.decode("utf-8")
    print(f"[scraping] Procesando {url}")
    try:
        result = process_url(url)
        print("[scraping] Resultado:", json.dumps(result)[:200])
        # Aquí más adelante mandaremos esto al Analysis Service o a la DB.
    except Exception as e:
        print(f"[scraping] Error procesando {url}: {e}")


def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST)
    )
    channel = connection.channel()
    channel.queue_declare(queue=REQUEST_QUEUE, durable=True)
    channel.basic_consume(
        queue=REQUEST_QUEUE,
        on_message_callback=callback,
        auto_ack=True,
    )
    print("[scraping] Esperando mensajes...")
    channel.start_consuming()


if __name__ == "__main__":
    main()
