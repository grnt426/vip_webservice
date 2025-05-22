import secrets
from typing import Literal


class Settings:
    # Eventually get a bunch of this from a .env file when running inside a Docker container

    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8

    BACKEND_PORT: int = 8080

    FRONTEND_HOST: str = "http://localhost:5173"
    FRONTEND_ORIGIN: list[str] = [
        "http://localhost:5173",
        "localhost:5173"
    ]
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"


class Constants:
    pass