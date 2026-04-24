
import os
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv


def load_config_variables() -> None:
    """ Function will double check if there is a file called .env_local,
    if so variables defined in it will be loaded.
    """
    # root_path: ./app-library
    root_path = os.path.dirname(os.path.abspath(__file__))
    # env_path: ./app-library/.env_local
    env_path = os.path.join(root_path, '.env_local')
    if os.path.exists(env_path):
        load_dotenv(env_path)


load_config_variables()
config_data = dict(
    database_host=os.getenv("DATABASE_HOST") or "localhost",
    database_port=os.getenv("DATABASE_PORT") or "3306",
    database_name=os.getenv("DATABASE_NAME") or "dblibrary",
    database_user=os.getenv("DATABASE_USER") or "root",
    database_password=os.getenv("DATABASE_PASSWORD") or "18fddb0ce7f4",
    jwt_secret_key=os.getenv("JWT_SECRET_KEY") or "fakesecret",
    jwt_algorithm=os.getenv("JWT_ALGORITHM") or "HS256",
    jwt_expire_minutes=os.getenv("JWT_EXPIRE_MINUTES") or 5,
)


class Settings(BaseSettings):
    database_user: Optional[str]
    database_password: Optional[str]
    database_host: Optional[str]
    database_name: Optional[str]
    database_port: Optional[int]
    jwt_secret_key: Optional[str]
    jwt_algorithm: Optional[str]
    jwt_expire_minutes: Optional[int]


settings = Settings(**config_data)
