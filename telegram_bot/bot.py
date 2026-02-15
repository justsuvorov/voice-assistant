import asyncio
import os
import requests
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message
from sqlalchemy.orm import Session

# Импортируем твои настройки и модели
from voice_assistant.core.config import settings
from voice_assistant.core.database import get_db_connection
from voice_assistant.models.schema import VoiceMessage

# Инициализация бота
API_TOKEN = 'ТВОЙ_ТЕЛЕГРАМ_ТОКЕН'
FASTAPI_URL = "http://localhost:8000/api/update"
bot = Bot(token=API_TOKEN)
dp = Dispatcher()


@dp.message(F.voice)
async def handle_voice(message: Message):
    # 1. Информируем пользователя
    status_msg = await message.answer("🎙 Голос получен. Начинаю обработку...")

    # Создаем сессию БД
    db: Session = get_db_connection()

    try:
        # 2. Скачивание файла
        file_id = message.voice.file_id
        file = await bot.get_file(file_id)
        file_path = f"uploads/{file_id}.ogg"
        os.makedirs("uploads", exist_ok=True)
        await bot.download_file(file.file_path, file_path)

        # 3. Создаем запись в БД (Initial state)
        # Нам нужно получить ID для передачи в API
        new_voice = VoiceMessage(
            file_path=file_path,
            transcription="pending",  # Будет обновлено позже внутри API
            style_tag="default"
        )
        db.add(new_voice)
        db.commit()
        db.refresh(new_voice)

        message_id = new_voice.id

        # 4. Запрос к твоему FastAPI сервису
        await status_msg.edit_text("⏳ Нейросеть думает...")

        payload = {"message_id": message_id}
        response = requests.post(FASTAPI_URL, json=payload)

        if response.status_code == 200:
            result = response.json()
            final_text = result["payload"]["text"]

            # 5. Отправляем результат пользователю
            await status_msg.edit_text(final_text, parse_mode="Markdown")
        else:
            await status_msg.edit_text(f"❌ Ошибка сервера: {response.text}")

    except Exception as e:
        await status_msg.edit_text(f"💥 Произошла ошибка: {str(e)}")
    finally:
        db.close()


async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())