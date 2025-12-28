# Copyright (c) 2022-2023 Pablo González Carrizo (unmonoqueteclea)
# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Authentication related models

"""
from typing import ClassVar

import ormar

from voogle.models.base import CoreModel


class User(CoreModel):
    """Basic information about an application user. Table user

    Fields email and username are unique.  Admin field is not
    postable, it is automatically set if a user signs up with the same
    name as the admin_username defined in app settings.

    """

    class Meta:
        tablename = "user"
        constraints: ClassVar = [
            ormar.UniqueColumns("email"),
            ormar.UniqueColumns("username"),
        ]

    email = ormar.String(max_length=400)
    username = ormar.String(max_length=40)
    hashed_password = ormar.String(max_length=65)
    admin = ormar.Boolean(default=False)
