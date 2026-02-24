import whisper
import os
import torch
from abc import ABC, abstractmethod


class Encoder(ABC):
    @abstractmethod
    def prepared_data(self, source: str) -> str:
        pass


class VoiceEncoder(Encoder):
    def __init__(self, model_name: str = "base"):
        """
        """
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_name = model_name
        self._model = whisper.load_model(self.model_name, device=self.device)

    def prepared_data(self, file_path: str) -> str:
        """
        Распаковывает ogg/mp3/wav и конвертирует в текст.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Файл не найден: {file_path}")

        try:


            result = self._model.transcribe(
                audio=file_path,
                language="ru",
                fp16=(self.device == "cuda"),
            )

            return result["text"].strip()

        except Exception as e:
            raise RuntimeError(f"Ошибка при обработке аудио Whisper: {e}")
