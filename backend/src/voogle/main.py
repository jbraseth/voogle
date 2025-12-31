# Copyright (c) 2022-2023 Pablo González Carrizo (unmonoqueteclea)
# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Main module that will be always executed on startup."""
import logging
from typing import Callable

import fastapi
from fastapi.middleware import cors
from fastapi_pagination import add_pagination

import voogle
from voogle import db, routers

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")

app = fastapi.FastAPI(title="voogle", version=voogle.__version__, lifespan=db.lifespan)

app.add_middleware(
    cors.CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_private_network_access_headers(
    request: fastapi.Request,
    call_next: Callable[[fastapi.Request], fastapi.Response],
) -> fastapi.Response:
    """Allow Chrome Private Network Access (requests from external hosts to localhost)."""
    response = await call_next(request)
    # Always add PNA header for dev - Chrome requires it for localhost access from external hosts
    response.headers["Access-Control-Allow-Private-Network"] = "true"
    return response

app.include_router(routers.app.router)
app.include_router(routers.users.router)
app.include_router(routers.media.router)
app.include_router(routers.analytics.router)
app.include_router(routers.local.router)
app.include_router(routers.assistant.router)

add_pagination(app)
