from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    backend_cors_origins: str = Field(default="http://localhost:3000", alias="BACKEND_CORS_ORIGINS")
    neo4j_uri: str = Field(default="bolt://neo4j:7687", alias="NEO4J_URI")
    neo4j_user: str = Field(default="neo4j", alias="NEO4J_USER")
    neo4j_password: str = Field(alias="NEO4J_PASSWORD")
    ingestion_workspace_root: Path = Field(
        default=Path("/tmp/github-compliance-engine/analyses"),
        alias="INGESTION_WORKSPACE_ROOT",
    )
    ingestion_clone_depth: int = Field(default=1, ge=1, alias="INGESTION_CLONE_DEPTH")
    ingestion_clone_timeout_seconds: int = Field(
        default=60,
        ge=1,
        alias="INGESTION_CLONE_TIMEOUT_SECONDS",
    )

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.backend_cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
