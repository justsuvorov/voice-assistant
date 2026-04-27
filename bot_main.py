import asyncio
import os
import httpx
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message
from aiogram.client.session.aiohttp import AiohttpSession
from sqlalchemy.orm import Session

# Используем твои настройки
from voice_assistant.core.config import settings
from voice_assistant.core.database import get_db_connection
from voice_assistant.models.schema import VoiceMessage

# Инициализация бота из конфига — явно передаём прокси, т.к. aiohttp не читает env автоматически
_proxy_url = os.getenv("HTTPS_PROXY") or os.getenv("HTTP_PROXY")
_session = AiohttpSession(proxy=_proxy_url) if _proxy_url else None
bot = Bot(token=settings.telegram_bot_token.get_secret_value(), session=_session)
dp = Dispatcher()

# ВАЖНО: 'api' — это имя сервиса из docker-compose.yaml
FASTAPI_URL = os.getenv("FASTAPI_URL", "http://api:80/api/update")


@dp.message(F.voice)
async def handle_voice(message: Message):
    status_msg = await message.answer("🎙 Сообщение получено. Начинаю обработку...")

    # Используем контекстный менеджер для БД, чтобы сессия точно закрылась
    db: Session = get_db_connection()

    try:
        # 1. Скачивание файла
        file_id = message.voice.file_id
        file = await bot.get_file(file_id)

        # Сохраняем в общую папку /app/uploads
        file_path = f"uploads/{file_id}.ogg"
        os.makedirs("uploads", exist_ok=True)
        await bot.download_file(file.file_path, file_path)

        # 2. Создаем запись в БД
        new_voice = VoiceMessage(
            file_path=file_path,
            transcription="pending",
            style_tag="default"
        )
        db.add(new_voice)
        db.commit()
        db.refresh(new_voice)

        await status_msg.edit_text("⏳ Модель Whisper и Gemini работают...")

        # 3. Асинхронный запрос к FastAPI
        async with httpx.AsyncClient(timeout=300.0) as client:
            payload = {"message_id": new_voice.id}
            response = await client.post(FASTAPI_URL, json=payload)

        if response.status_code == 200:
            result = response.json()
            # Убедись, что структура JSON совпадает с ответом твоего API
            final_text = result.get("payload", {}).get("text", "Текст не получен")
            await status_msg.edit_text(f"✅ **Результат:**\n\n{final_text}", parse_mode="Markdown")
        else:
            await status_msg.edit_text(f"❌ Ошибка API ({response.status_code}): {response.text}")

    except Exception as e:
        await status_msg.edit_text(f"💥 Произошла ошибка: {str(e)}")
    finally:
        db.close()


async def main():
    print("🚀 Бот запущен и готов к работе...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())