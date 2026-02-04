from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    app_name: str = "Dynamic Cell Culture Drive"
    version: str = "1.0.0"
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True

    # CORS
    allowed_origins: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:8080",
    ]

    # JWT
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_weeks: int = 4

    # Database
    postgres_user: str = "dynamic-cell-culture-drive_user"
    postgres_password: str = "password"
    postgres_db: str = "dynamic-cell-culture-drive_db"
    postgres_host: str = "0.0.0.0"
    postgres_port: int = 5432

    @property
    def database_url(self) -> str:
        """Get database connection URL."""
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    class Config:
        """Configuration for the settings class."""

        env_file = ".env"


settings = Settings()
