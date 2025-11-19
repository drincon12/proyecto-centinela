import os
import sys

# Añadimos la carpeta raíz de backend-api al path de Python
CURRENT_DIR = os.path.dirname(__file__)
BACKEND_ROOT = os.path.dirname(CURRENT_DIR)
sys.path.append(BACKEND_ROOT)

from fastapi.testclient import TestClient
from main import app


client = TestClient(app)


def test_health_ok():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
