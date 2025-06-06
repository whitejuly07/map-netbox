#database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite — путь к БД
SQLALCHEMY_DATABASE_URL = "sqlite:///./network.db"

# Создание движка
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Сессия
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовая модель
Base = declarative_base()
