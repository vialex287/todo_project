from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    # databases
    DB_USER: str
    DB_TYPE: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    # auth
    SECRET_KEY: str
    PASSWORD_SALT: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    class Config:
        env_file = ".env.example"

    @property
    def DATABASE_URL(self):
        if self.DB_TYPE.startswith("sqlite"):
            return f"{settings.DB_TYPE}:///{settings.DB_NAME}"
        else:
            return (
                f"{self.DB_TYPE}://{self.DB_USER}:{self.DB_PASSWORD}@"
                f"{self.DB_HOST}/{self.DB_NAME}"
                f"?charset=utf8mb4"
            )


settings = Settings()


# config for DockerSecret
if Path("/.dockerenv").exists():
    settings.DB_HOST = "db"


def get_secret(name, default=None):
    import os

    value = os.getenv(name)
    if value:
        return value

    file_path = os.getenv(f"{name}_FILE")
    if file_path and Path(file_path).exists():
        return Path(file_path).read_text().strip()

    return default


DB_USER = get_secret("DB_USER", "adminToDo")
DB_PASSWORD = get_secret("DB_PASSWORD", "")
DB_HOST = get_secret("DB_HOST", "db")
DB_NAME = get_secret("DB_NAME", "ToDoProject")
