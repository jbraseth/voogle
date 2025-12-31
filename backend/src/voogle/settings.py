# Copyright (c) 2022-2023 Pablo González Carrizo (unmonoqueteclea)
# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""App configuration values.

Settings class will try to obtain, from environment variables, the
value for each configuration parameter, using the default value
defined in the class if a specific value is not found.

If you are running everything through the provided Docker and Docker
Compose configuration, all the needed parameters are provided as
environment variables.

"""
import enum
import pathlib
from typing import Optional

import pydantic
import redis
from pydantic_settings import BaseSettings
from rq import Queue

CODE_DIR = pathlib.Path(__file__).parent
BACKEND_DIR = CODE_DIR.parent.parent
REPO_DIR = BACKEND_DIR.parent
REDIS_CACHE_DB_NUMBER = 1


class Environment(enum.Enum):
    test = "test"
    development = "development"
    production = "production"


class Settings(BaseSettings):

    # this default variables will be used when running the system
    # without any additional env var (usually, we will want them to be
    # synchronized with the ones in infra/dev/.env.dev)
    environment: str = Environment.production.value
    code_dir: pydantic.DirectoryPath = CODE_DIR
    repo_dir: pydantic.DirectoryPath = REPO_DIR
    media_folder_name: str = "media"
    redis_host: str = "redis"
    qdrant_host: str = "qdrant"
    qdrant_port: int = 6333
    admin_username: str = "voogle-admin"
    admin_password: str = "*audio*search*engine"
    admin_email: str = "placeholder@voogle.com"
    # you can generate it with: openssl rand -hex 32
    secret_key: str = "917b2755cafdb6456cc718a5d6b25d0ac25a4f12a288dbc8941f39861a86ab06"

    # OpenAI Embeddings Configuration (optional)
    # If OPENAI_API_KEY is set, uses OpenAI API instead of local models
    openai_api_key: Optional[str] = None
    openai_model: str = "text-embedding-3-small"

    @property
    def data_dir(self) -> pathlib.Path:
        # In Docker (both dev and prod), data is always mounted at /data
        # For native development or test, use repo_dir-based paths
        if self.environment == Environment.test.value:
            return self.repo_dir / "data-test"
        elif pathlib.Path("/data").exists():
            # Running in Docker - use mounted volume
            return pathlib.Path("/data")
        else:
            # Running natively - use repo-relative path
            return self.repo_dir / "data"

    @property
    def media_folder(self) -> pathlib.Path:
        return self.data_dir / self.media_folder_name

    @property
    def qdrant_use_file(self) -> bool:
        return self.environment == Environment.test.value

    @property
    def redis_cache(self) -> redis.Redis:
        return redis.Redis(
            host=self.redis_host, db=REDIS_CACHE_DB_NUMBER, decode_responses=True
        )

    @property
    def embeddings_provider(self) -> str:
        """Auto-detect embeddings provider based on API key presence.

        Returns 'openai' if OPENAI_API_KEY is set, otherwise 'local'.
        """
        return "openai" if self.openai_api_key else "local"


def create_queue(settings: Settings) -> Queue:
    """Return the main app rq queue"""
    redis_conn = redis.Redis(settings.redis_host)
    return Queue(connection=redis_conn)


settings = Settings()
queue = create_queue(settings)
settings.data_dir.mkdir(exist_ok=True)
