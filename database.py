from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import datetime

DATABASE_URL = "sqlite:///./chat_history.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False} # Required for SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class ConversationLog(Base):
    __tablename__ = "conversation_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    user_prompt = Column(String)
    bot_response = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

def create_db_and_tables():
    Base.metadata.create_all(bind=engine)
