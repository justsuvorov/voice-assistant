from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_read_main_endpoint():
    # Проверяем, что роут возвращает 422, если отправить пустой JSON (валидация Pydantic)
    response = client.post("/api/update", json={})
    assert response.status_code == 422


def test_api_with_mock_logic(mocker):
    # Мокаем весь сервис целиком, чтобы не трогать БД и ИИ
    mocker.patch("voice_assistant.services.assistant.AIAssistantService.result",
                 return_value={"status": "success"})

    response = client.post("/api/update", json={"message_id": 1})
    assert response.status_code == 200