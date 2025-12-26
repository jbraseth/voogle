# Copyright (c) 2022-2023 Pablo González Carrizo (unmonoqueteclea)
# All rights reserved.

import fastapi

import voogle

router = fastapi.APIRouter(prefix="/app", tags=["app"])


@router.get("/version", summary="Return application version")
async def version() -> dict:
    """Return voilib back-end version.

    It is the version of the Voilib Python package.
    """
    return {"version": voilib.__version__}
