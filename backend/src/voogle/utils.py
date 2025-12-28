# Copyright (c) 2022-2023 Pablo González Carrizo (unmonoqueteclea)
# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Mixed utilities

Everything can be considered an utility, so let's try to keep this as
small as possible.

"""
import typing
import re
import time
import unicodedata

from voogle import settings


def slugify(value: str) -> str:
    value = (
        unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    )
    value = re.sub(r"[^\w\s-]", "", value).strip().lower()
    return re.sub(r"[-\s]+", "-", value)


def log_event(key: str, info: str) -> None:
    redis = settings.settings.redis_cache
    redis.set(key, f"{time.time()}|{info}")


def get_event(key: str) -> typing.Optional[dict]:
    redis = settings.settings.redis_cache
    event = redis.get(key)
    if event:
        event_str: str = event.decode("utf-8") if isinstance(event, bytes) else event  # type: ignore[assignment]
        parts = event_str.split("|")
        return {"time": parts[0], "info": parts[1]}
    return None
