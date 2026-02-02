import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # DATABASE_URL : str = os.getenv('dburl', '')
    DATABASE_USERNAME: str = os.getenv('DATABASE_USERNAME', '')
    DATABASE_PASSWORD: str = os.getenv('DATABASE_PASSWORD', '')
    DATABASE_HOST: str = os.getenv('DATABASE_HOST', '')
    DATABASE_PORT: str = os.getenv('DATABASE_PORT', '')
    DATABASE_NAME: str = os.getenv('DATABASE_NAME', '')
    ROOT: str = os.getenv('root', '')

    KEYCLOAK_SERVER_URL = os.getenv("KEYCLOAK_SERVER_URL")
    KEYCLOAK_CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID")
    KEYCLOAK_REALM_NAME = os.getenv("KEYCLOAK_REALM_NAME")
    KEYCLOAK_CLIENT_SECRET_KEY = os.getenv("KEYCLOAK_CLIENT_SECRET_KEY")
    ROOT_PATH_PREFIX = os.getenv("ROOT_PATH_PREFIX")
