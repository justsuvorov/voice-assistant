import google.generativeai as genai
from abc import ABC, abstractmethod
from voice_assistant.core.config import settings


class AIModel(ABC):
    @abstractmethod
    def response(self, query: str) -> str:
        """
        Метод должен принимать промпт и возвращать текстовый ответ.
        """
        pass


class GeminiModel(AIModel):
    def __init__(self):

        genai.configure(api_key=settings.gemini_api_key.get_secret_value())

        self._model = genai.GenerativeModel(
            model_name='gemini-2.0-flash-lite'#'gemini-2.0-flash'#settings.model_name
        )


        self._generation_config = genai.types.GenerationConfig(
            temperature=settings.ai_temperature,
            top_p=0.95,
            top_k=64,
            max_output_tokens=8192,
        )

    def response(self, query: str) -> str:
        """
        Отправка запроса в Gemini и извлечение текста.
        """
        try:
            # Выполняем запрос
            response = self._model.generate_content(
                query,
                generation_config=self._generation_config
            )

            # Проверка на наличие текста (защита от блокировок Safety Settings)
            if not response or not response.text:
                raise ValueError("Gemini не вернула текст (возможно, сработал фильтр контента)")

            return response.text.strip()

        except Exception as e:
            # Пробрасываем ошибку выше для обработки в main.py
            raise RuntimeError(f"Ошибка Gemini API: {str(e)}")