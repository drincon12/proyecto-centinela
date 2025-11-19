import os
import time


def publish(content: str, target: str = "social"):
    """
    Simula la publicación de contenido verificado en una red social.
    En el proyecto real, aquí irían las llamadas a APIs de Mastodon/Twitter/Reddit.
    """
    print(f"[publishing] Publicando en {target}: {content[:80]}...")


if __name__ == "__main__":
    publish("Ejemplo de contenido verificado del Proyecto Centinela.")
    time.sleep(1)
    print("[publishing] Publicación simulada completada.")
