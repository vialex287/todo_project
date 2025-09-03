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
        env_file = ".env"

    @property
    def DATABASE_URL(self):
        return (
            f"{self.DB_TYPE}://{self.DB_USER}:{self.DB_PASSWORD}@"
            f"{self.DB_HOST}/{self.DB_NAME}"
            f"?charset=utf8mb4"
        )


settings = Settings()
