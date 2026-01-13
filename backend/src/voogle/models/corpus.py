# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Corpus database model.

Defines the Corpus table for persistent storage of corpus metadata.
"""
from datetime import datetime
from typing import Any

import ormar

from voogle.models import base


class Corpus(base.CoreModel):
    """Database model for a searchable content collection.

    A Corpus represents a logical grouping of documents that can be
    searched together, stored in the 'corpora' table.
    """

    ormar_config = ormar.OrmarConfig(
        tablename="corpora",
    )

    name = ormar.String(max_length=250)
    description = ormar.Text(default="")
    content_types = ormar.JSON(default=[])
    settings: Any = ormar.JSON(default={})
    document_count = ormar.Integer(default=0)
    updated_at = ormar.DateTime(default=datetime.now, timezone=True)
