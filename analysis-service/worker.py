import pika

connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
channel = connection.channel()
channel.queue_declare(queue='analysis_queue', durable=True)

def callback(ch, method, properties, body):
    url = body.decode()
    print(f"[ANALYSIS WORKER] Procesando URL desde cola: {url}")
    # Aquí puedes llamar funciones de análisis o insertar en BD

channel.basic_consume(queue='analysis_queue', on_message_callback=callback, auto_ack=True)

print("Esperando mensajes en analysis_queue...")
channel.start_consuming()
