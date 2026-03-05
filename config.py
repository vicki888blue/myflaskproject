import os
from pathlib import Path

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-insecure-change-me")
    PROJECT_DIR = Path(__file__).parent.resolve()
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{(PROJECT_DIR / 'mydatabase.db').as_posix()}"
    )