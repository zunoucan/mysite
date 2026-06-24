from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./housing.db"
    debug: bool = False
    scrape_interval_hours: int = 6   # スクレイピング実行間隔
    cors_origins: list[str] = ["*"]

    class Config:
        env_file = ".env"


settings = Settings()
