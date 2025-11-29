import os
import pika
import time

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://centinela:centinela@rabbitmq:5672/")
QUEUE_NAME = os.getenv("QUEUE_NAME", "analysis.jobs")

def connect_with_retry(url, retries=30, delay=2):
    params = pika.URLParameters(url)
    for i in range(retries):
        try:
            return pika.BlockingConnection(params)
        except Exception as e:
            print(f"[worker] Intento {i+1}/{retries} conectando a RabbitMQ: {e}")
            time.sleep(delay)
    raise RuntimeError("No se pudo conectar a RabbitMQ después de varios intentos.")

def main():
    print("[worker] Analysis worker iniciado correctamente.")
    conn = connect_with_retry(RABBITMQ_URL)
    channel = conn.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)

    def handle_message(ch, method, properties, body):
        print(f"[worker] Mensaje recibido: {body.decode('utf-8')}")
        # Aquí implementarías tu lógica de análisis
        time.sleep(1)
        ch.basic_ack(delivery_tag=method.delivery_tag)
        print("[worker] Procesado y ACK enviado.")

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=handle_message)

    print(f"[worker] Esperando mensajes en la cola '{QUEUE_NAME}'...")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("[worker] Interrumpido por usuario.")
    finally:
        conn.close()
        print("[worker] Conexión cerrada.")

if __name__ == "__main__":
    main()
