from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    APP_NAME: str = "whatsapp-backend"
    ENV: str = "production"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    DATABASE_URL: str = Field(..., description="Async URL e.g. postgresql+asyncpg://user:pass@host:5432/db")

    WABA_PHONE_NUMBER_ID: str = Field(..., description="Phone number ID")
    WABA_ACCESS_TOKEN: str = Field(..., description="Bearer token for Graph API")
    WABA_VERIFY_TOKEN: str = Field(..., description="Verify token for webhook GET")
    META_APP_SECRET: str | None = Field(default=None, description="App secret to verify X-Hub-Signature-256")

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
