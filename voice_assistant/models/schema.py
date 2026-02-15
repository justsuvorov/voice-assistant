from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Text, String


class Base(DeclarativeBase):
    pass


class VoiceMessage(Base):
    __tablename__ = "voice_messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    file_path: Mapped[str] = mapped_column(String(500))  # Путь к .ogg
    transcription: Mapped[str] = mapped_column(Text)
    style_tag: Mapped[str] = mapped_column(String(50), default="default")


from sqlalchemy.orm import Session
from sqlalchemy import select
from voice_assistant.core.database import SessionLocal


class DBSpeakingObject:
    def __init__(self, session: Session = None):
        # Если сессия не передана (например, в скриптах), создаем свою
        self.session = session or SessionLocal()

    def get_origin_data(self, message_id: int):
        """Достает транскрипцию конкретного сообщения"""
        query = select(VoiceMessage).where(VoiceMessage.id == message_id)
        result = self.session.execute(query).scalar_one_or_none()

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
        return self.session.execute(query).scalars().all()

    def close(self):
        self.session.close()