from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

SQLALCHEMY_DATABASE_URL = 'postgresql+psycopg2://useradmin:supersecretpassword@localhost:5433/FastAPI_APP'
# SQLALCHEMY_DATABASE_URL = 'postgresql://useradmin:supersecretpassword@localhost:5432/FastAPI_APP'
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
