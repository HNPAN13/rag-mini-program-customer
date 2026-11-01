# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import DATABASE_URL

# 数据库引擎
engine = create_engine(DATABASE_URL, echo=True)

# 会话工厂
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# 模型基类
Base = declarative_base()


def get_db():
    """给接口用的数据库会话，用完自动关闭"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()