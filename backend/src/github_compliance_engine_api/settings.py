from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
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
    ingestion_metadata_timeout_seconds: int = Field(
        default=30,
        ge=1,
        alias="INGESTION_METADATA_TIMEOUT_SECONDS",
    )
    ingestion_file_tree_max_depth: int = Field(
        default=20,
        ge=1,
        alias="INGESTION_FILE_TREE_MAX_DEPTH",
    )
    ingestion_file_tree_max_files: int = Field(
        default=5000,
        ge=1,
        alias="INGESTION_FILE_TREE_MAX_FILES",
    )
    ingestion_max_text_file_bytes: int = Field(
        default=1048576,
        ge=1,
        alias="INGESTION_MAX_TEXT_FILE_BYTES",
    )
    github_token: str | None = Field(default=None, alias="GITHUB_TOKEN")

    @field_validator("github_token", mode="before")
    @classmethod
    def empty_github_token_is_none(cls, value: str | None) -> str | None:
        if value == "":
            return None
        return value

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.backend_cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
