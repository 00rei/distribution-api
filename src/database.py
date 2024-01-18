from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from .config import DB_HOST, DB_PORT, DB_USER, DB_NAME, DB_PASS
from .config import DB_HOST_TEST, DB_PORT_TEST, DB_USER_TEST, DB_NAME_TEST, DB_PASS_TEST

SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SQLALCHEMY_DATABASE_URL_TEST = f"postgresql://{DB_USER_TEST}:{DB_PASS_TEST}@{DB_HOST_TEST}:{DB_PORT_TEST}/{DB_NAME_TEST}"
engine_test = create_engine(SQLALCHEMY_DATABASE_URL_TEST)


def get_session(mode: str = 'dev') -> Session:
    if mode == 'dev':
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    else:
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)

    return SessionLocal()


Base = declarative_base()


def drop_test_table() -> None:
    Base.metadata.drop_all(bind=engine_test)


def create_test_table() -> None:
    Base.metadata.create_all(bind=engine_test)
