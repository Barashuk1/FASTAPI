from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from photoshare.conf.config import settings

SQLALCHEMY_DATABASE_URL = settings.sqlalchemy_database_url
engine = create_engine(SQLALCHEMY_DATABASE_URL)

LocalSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Сесія для тестів моделей
# ПОТІМ ТРЕБА ПРИБРАТИ
test_session = LocalSession()

def get_db():
    db = LocalSession()
    try:
        yield db
    finally:
        db.close()
