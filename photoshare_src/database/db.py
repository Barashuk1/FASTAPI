from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session


from photoshare_src.conf.config import settings

SQLALCHEMY_DATABASE_URL = settings.sqlalchemy_database_url
engine = create_engine(SQLALCHEMY_DATABASE_URL)

LocalSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Сесія для тестів моделей
# ПОТІМ ТРЕБА ПРИБРАТИ
test_session = LocalSession()

def get_db():
    """
    The get_db function opens a new database connection if there is none yet
    for the current application context.
    It also binds the session to the current context so that you don’t have to
    use db.session in each view function.

    :return: A generator object
    """
    db = LocalSession()
    try:
        yield db
    finally:
        db.close()
