from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base,sessionmaker
from . import settings

# 配置引擎
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    echo=settings.DEBUG
)

# 定义基类
Base = declarative_base()

# 创建会话工厂
SessionLocal = sessionmaker(bind=engine)

# --- 依赖注入用的函数 ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



