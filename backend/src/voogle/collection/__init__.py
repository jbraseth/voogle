# Copyright (c) 2022-2023 Pablo González Carrizo (unmonoqueteclea)
# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Functions to collect channels and episodes.

- Module crawler is the module that will retrieve podcast channels and
  episodes and create the corresponding app models.

- Module feed contains some functions to deal with RSS podcasts feeds
  and return channel or episode objects (not stored yet in db)
"""

from .crawler import default_channels
from .crawler import get_or_create_channel
from .crawler import get_or_create_local_channel
from .crawler import update_channel
from .crawler import add_default_channels, add_local_channels
from .feed import read_channel, read_episodes
from .local import read_local_channel, read_local_episodes
