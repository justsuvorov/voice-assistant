from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from voice_assistant.core.config import settings
from voice_assistant.models.schema import Base

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10
)

# 2. Называем фабрику Connection (как ты и хотел)
# Это класс, который при вызове Connection() создает новую сессию
Connection = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_db_connection() -> Session:

    db = Connection()
    try:
        return db
    finally:
        # В FastAPI мы закроем это в блоке finally или через Depends
        pass

def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()