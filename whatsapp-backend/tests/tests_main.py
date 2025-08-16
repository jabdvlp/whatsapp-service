from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    """Prueba que la API responde en /health"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_list_messages_empty(monkeypatch):
    """Prueba que /messages devuelve lista vacía inicialmente"""

    # Mock de la función get_messages para no depender de la DB real
    def fake_get_messages(db, limit=100):
        return []

    # Inyectar el mock
    from app import crud
    monkeypatch.setattr(crud, "get_messages", fake_get_messages)

    response = client.get("/messages")
    assert response.status_code == 200
    assert response.json() == []
