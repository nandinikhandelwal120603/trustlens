"""TrustLens settings configuration using Pydantic Settings."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment or .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # General
    app_name: str = "TrustLens"
    app_env: str = "development"
    log_level: str = "INFO"
    pipeline_version: str = "0.1.0"
    schema_version: str = "1.0.0"

    # Database
    database_url: str = Field(
        default="sqlite:///./trustlens.db",
        description="Database connection URL (SQLite or PostgreSQL)",
    )

    # Storage paths
    data_dir: Path = Path("./data")
    raw_data_dir: Path = Path("./data/raw")
    normalized_data_dir: Path = Path("./data/normalized")
    processed_data_dir: Path = Path("./data/processed")
    labels_data_dir: Path = Path("./data/labels")

    # Privacy & Security
    hash_salt: str = Field(
        default="trustlens_default_dev_salt_change_in_production",
        description="Secret salt used for HMAC-SHA256 hashing of sensitive seller identifiers",
    )

    # Media settings
    media_max_file_size_mb: int = 50
    media_download_timeout_sec: int = 15
    media_max_concurrent_downloads: int = 5

    # Crawl4AI / Web Extraction
    crawl4ai_headless: bool = True
    crawl4ai_timeout_ms: int = 30000

    def ensure_directories(self) -> None:
        """Ensure all storage directories exist."""
        for path in [
            self.data_dir,
            self.raw_data_dir,
            self.normalized_data_dir,
            self.processed_data_dir,
            self.labels_data_dir,
        ]:
            path.mkdir(parents=True, exist_ok=True)


# Global singleton instance
settings = Settings()
