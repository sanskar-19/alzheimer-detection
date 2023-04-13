import pymysql
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from config import setting
from contextvars import ContextVar

# url_pattern = 'mysql+mysqldb://{USERNAME}:{PASSWORD}@{HOST_NAME}/{DATABASE_NAME}'.format(
#     USERNAME = USERNAME , PASSWORD = PASSWORD , HOST_NAME = HOST_NAME , DATABASE_NAME = DATABASE_NAME
# )
# 'mysql+mysqldb://root:root@127.0.0.1:3306/auth'
pymysql.install_as_MySQLdb()
db_engine = create_engine(setting.DATABASE_URL)
SessionLocal = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
)

Base = declarative_base()


def get_session():
    with Session(db_engine) as session:
        yield session


def get_db():
    try:
        db = SessionLocal()
        yield db
    except Exception:
        db.rollback()

    finally:
        db.close()


db_session: ContextVar[Session] = ContextVar("db_session")
