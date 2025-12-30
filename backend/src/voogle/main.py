# Copyright (c) 2022-2023 Pablo González Carrizo (unmonoqueteclea)
# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Main module that will be always executed on startup."""
import logging

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

app.include_router(routers.app.router)
app.include_router(routers.users.router)
app.include_router(routers.media.router)
app.include_router(routers.analytics.router)
app.include_router(routers.local.router)

add_pagination(app)
