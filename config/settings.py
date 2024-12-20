# -*- coding: utf-8 -*-

import os
from pathlib import Path
from typing import Union

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load environment variables from the specified path
env_path = Path('./config') / '.env'
load_dotenv(dotenv_path=env_path)


class Settings(BaseSettings):
    """
    Configuration settings for the aoe3de project.
    """
    
    PROJECT_NAME: str = "aoe3de project"
    PROJECT_VERSION: str = "1.0"
    PROJECT_EMAIL: str = "jonathan.diazm5@gmail.com"

    SHOW_ADMIN_ROUTES: bool = True

    # PostgreSQL database configuration
    POSTGRES_DB: str = os.getenv("POSTGRES_DB")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD: Union[str, None] = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT")

    POSTGRES_SOCKET_PATH: str = "/var/run/postgresql"

    DATABASE_URL: str = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"

# Create an instance of the Settings class
settings = Settings()