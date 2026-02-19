import pytest
from unittest.mock import MagicMock
from voice_assistant.services.assistant import AIAssistantService


def test_ai_assistant_full_cycle(mocker):
    # 1. Создаем моки для всех компонентов
    mock_preprocessor = MagicMock()
    mock_preprocessor.query.return_value = "Текст из аудио"

    mock_postprocessor = MagicMock()
    mock_postprocessor.report.return_value = "Готовый пост"

    mock_model = MagicMock()
    mock_model.response.return_value = "Сырой ответ ИИ"

    mock_export = MagicMock()
    mock_export.response.return_value = {"status": "success", "payload": {"text": "Готовый пост"}}

    # 2. Инициализируем сервис с моками
    service = AIAssistantService(
        preprocessor=mock_preprocessor,
        postprocessor=mock_postprocessor,
        ai_model=mock_model,
        report_export=mock_export
    )

    # 3. Выполняем метод
    result = service.result()

    # 4. Проверки (Assertions)
    assert result["status"] == "success"
    assert result["payload"]["text"] == "Готовый пост"

    # Проверяем, что методы вызывались в нужном порядке
    mock_preprocessor.query.assert_called_once()
    mock_model.response.assert_called_with("Текст из аудио")
    mock_postprocessor.report.assert_called_with("Сырой ответ ИИ")


from voice_assistant.ai.postprocessor import PostProcessor


def test_post_processor_cleaning():
    processor = PostProcessor()
    raw_text = "```markdown\nВот ваш пост\n```"

    clean_text = processor.report(raw_text)

    # Проверяем, что лишние теги разметки удалены
    assert "```markdown" not in clean_text
    assert "Вот ваш пост" in clean_text


from voice_assistant.models.schema import VoiceMessage, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def test_db_update():
    # Создаем временную БД в памяти
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # 1. Создаем запись
    msg = VoiceMessage(file_path="test.ogg", transcription="test", style_tag="default")
    session.add(msg)
    session.commit()

    # 2. Имитируем обновление через твой DBSpeakingObject
    msg.result_post = "Обновленный пост"
    session.commit()

    # 3. Проверяем
    updated_msg = session.query(VoiceMessage).first()
    assert updated_msg.result_post == "Обновленный пост"