from pathlib import Path

from pydantic import BaseSettings, Field

PROJECT_ROOT = Path(__file__).parent.parent.parent


class Environment(BaseSettings):
    db_username: str = Field(env="DB_USERNAME", default="postgres")
    db_password: str = Field(env="DB_PASSWORD", default="postgres")
    db_database: str = Field(env="DB_DATABASE", default="postgres")
    db_host: str = Field(env="DB_HOST", default="localhost")
    db_port: int = Field(env="DB_PORT", default=5432)

    class Config:
        env_file = PROJECT_ROOT.joinpath(".env")
        env_file_encoding = "utf-8"
