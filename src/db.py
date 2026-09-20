import os
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from dotenv import load_dotenv

load_dotenv()


def get_engine():

    host = os.getenv("APP_DB_HOST", os.getenv("POSTGRES_HOST", "localhost"))
    port = os.getenv("APP_DB_PORT", os.getenv("POSTGRES_PORT", "5432"))
    db = os.getenv("APP_DB_NAME", os.getenv("POSTGRES_DB", "datastore360"))
    user = os.getenv("APP_DB_USER", os.getenv("POSTGRES_USER", "ds360_user"))
    password = os.getenv("APP_DB_PASSWORD", os.getenv("POSTGRES_PASSWORD", "ds360_password"))

    url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"

    engine = create_engine(url)
    return engine


