import pika

# Conexión a RabbitMQ
credentials = pika.PlainCredentials('centinela', 'centinela')
parameters = pika.ConnectionParameters(host='rabbitmq', credentials=credentials)
connection = pika.BlockingConnection(parameters)

channel = connection.channel()

# Declarar la cola (por si no existe)
channel.queue_declare(queue='publish_queue', durable=True)


def publish(content: str, target: str = "social"):
    """
    Simula la publicación de contenido verificado en una red social.
    En el proyecto real, aquí irían las llamadas a APIs de Mastodon/Twitter/Reddit.
    """
    print(f"[publishing] Publicando en {target}: {content[:80]}...")


# Función que procesa cada mensaje
def callback(ch, method, properties, body):
    content = body.decode()
    print(f"Procesando mensaje para publicar: {content}")
    publish(content)


# Escuchar la cola
channel.basic_consume(queue='publish_queue', on_message_callback=callback, auto_ack=True)

print("Esperando mensajes en publish_queue...")
channel.start_consuming()
