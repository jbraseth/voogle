# Copyright (c) 2022-2023 Pablo González Carrizo (unmonoqueteclea)
# All rights reserved.

"""Analytics related models to store things such us queries performed
by users.

"""
import ormar

from voogle.models import base


class Query(base.CoreModel):
    """A query performed by a user. Table queries"""

    class Meta(ormar.ModelMeta):
        tablename = "queries"

    text = ormar.String(max_length=150)
