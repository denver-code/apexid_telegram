from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BOT_TOKEN: str
    API_URL: str

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
