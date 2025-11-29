import requests
from bs4 import BeautifulSoup
import logging
from datetime import datetime
import pika

# Configurar logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Conexión a RabbitMQ
import pika

credentials = pika.PlainCredentials('centinela', 'centinela')
parameters = pika.ConnectionParameters(host='rabbitmq', credentials=credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()

channel = connection.channel()

# Declarar la cola (por si no existe)
channel.queue_declare(queue='scraping_queue', durable=True)


class ScrapingService:
    """Servicio de web scraping para análisis de contenido"""

    @staticmethod
    def scrape_url(url: str) -> dict:
        """Extrae contenido y metadata de una URL"""
        try:
            logger.info(f"Starting scraping for URL: {url}")
            headers = {
                'User-Agent': 'Mozilla/5.0'
            }
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            title = soup.title.string.strip() if soup.title and soup.title.string else 'No title'
            text = soup.get_text()[:1000]

            result = {
                'url': url,
                'status': 'success',
                'title': title,
                'text_length': len(text),
                'scraped_at': datetime.utcnow().isoformat()
            }
            return result
        except Exception as e:
            return {'url': url, 'status': 'error', 'error': str(e)}


# Función que procesa cada mensaje
def callback(ch, method, properties, body):
    url = body.decode()
    logger.info(f"Procesando URL: {url}")
    result = ScrapingService.scrape_url(url)
    logger.info(f"Resultado: {result}")


# Escuchar la cola
channel.basic_consume(queue='scraping_queue', on_message_callback=callback, auto_ack=True)

print("Esperando mensajes en scraping_queue...")
channel.start_consuming()
