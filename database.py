from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data.db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)

class Prompt(Base):
    __tablename__ = "prompt"
    id = Column(Integer, primary_key=True, default=1)
    content = Column(Text, nullable=False)

# Создание таблиц
Base.metadata.create_all(bind=engine)

def add_user(user_id: int):
    db = SessionLocal()
    if not db.query(User).filter(User.id == user_id).first():
        db.add(User(id=user_id))
        db.commit()
    db.close()

def get_users():
    db = SessionLocal()
    users = [user.id for user in db.query(User).all()]
    db.close()
    return users

def save_prompt(prompt_text: str):
    db = SessionLocal()
    prompt = db.query(Prompt).first()
    if prompt:
        prompt.content = prompt_text
    else:
        prompt = Prompt(id=1, content=prompt_text)
        db.add(prompt)
    db.commit()
    db.close()

def get_prompt():
    db = SessionLocal()
    prompt = db.query(Prompt).first()
    db.close()
    return prompt.content if prompt else "Ты — дружелюбный Telegram-ассистент."