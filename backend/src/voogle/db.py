# Copyright (c) 2022-2023 Pablo González Carrizo (unmonoqueteclea)
# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Database configuration. In this module, the lifespan context manager
handles database connection on app startup and disconnection on shutdown.

"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import databases
import sqlalchemy
from fastapi import FastAPI

from voogle import settings


def get_db_url() -> str:
    """Obtain the url of the running database. It will be different
    depending on the environment (development, test, production).

    """
    curset = settings.settings
    base = f"sqlite:///{settings.settings.data_dir!s}"

    ""
    if curset.environment == settings.Environment.development.value:
        return f"{base}/db-dev.sqlite"
    elif curset.environment == settings.Environment.test.value:
        return f"{base}/db-test.sqlite"
    elif curset.environment == settings.Environment.production.value:
        return f"{base}/db-prod.sqlite"
    raise ValueError(f"invalid environment value {curset.environment}")


database = databases.Database(get_db_url())
metadata = sqlalchemy.MetaData()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan context manager for database connection management."""
    app.state.database = database
    if not database.is_connected:
        await database.connect()
    yield
    if database.is_connected:
        await database.disconnect()
