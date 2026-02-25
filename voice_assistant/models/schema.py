from sqlalchemy import select, Text, String, update
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

class Base(DeclarativeBase):
    pass


class VoiceMessage(Base):
    __tablename__ = "voice_messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    file_path: Mapped[str] = mapped_column(String(500))  # Путь к .ogg
    transcription: Mapped[str] = mapped_column(Text)
    result_post: Mapped[str] = mapped_column(Text, nullable=True)  # Готовый пост от Gemini
    style_tag: Mapped[str] = mapped_column(String(50), default="default")


class DBSpeakingObject:
    def __init__(self, connection: Session):
        self.connection = connection

    def get_origin_data(self, message_id: int):

        query = select(VoiceMessage).where(VoiceMessage.id == message_id)
        result = self.connection.execute(query).scalar_one_or_none()

        if not result:
            raise ValueError(f"Сообщение с id {message_id} не найдено")

        return {
            "text": result.transcription,
            "path": result.file_path
        }

    def get_style_reference(self, limit: int = 3):
        """Достает эталонные тексты для Few-shot промптинга (EDD подход)"""
        query = (
            select(VoiceMessage.transcription)
            .where(VoiceMessage.style_tag == "gold")
            .limit(limit)
        )
        return self.connection.execute(query).scalars().all()

    def close(self):
        self.connection.close()

    def update_voice_post(self, message_id: int, post_text: str):
        """Обновляет запись в БД, вставляя готовый текст поста."""
        # Пример для SQLAlchemy:
        statement = update(VoiceMessage).where(VoiceMessage.id == message_id).values(result_post=post_text)
        self.connection.execute(statement)
        self.connection.commit()

    def __del__(self):
        self.close()
