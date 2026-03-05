from sqlalchemy import create_engine
from contextlib import contextmanager

_engine = None

def init_engine(database_url: str):
    global _engine
    _engine = create_engine(database_url, echo=False)

def get_engine():
    if _engine is None:
        raise RuntimeError("DB engine not initialised; call init_engine() first.")
    return _engine

@contextmanager
def connect():
    with get_engine().connect() as conn:
        yield conn

@contextmanager
def transaction():
    with get_engine().begin() as conn:
        yield conn