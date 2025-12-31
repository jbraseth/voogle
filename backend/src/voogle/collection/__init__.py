# Copyright (c) 2022-2023 Pablo González Carrizo (unmonoqueteclea)
# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Functions to collect channels and episodes.

- Module crawler is the module that will retrieve podcast channels and
  episodes and create the corresponding app models.

- Module feed contains some functions to deal with RSS podcasts feeds
  and return channel or episode objects (not stored yet in db)
"""

from .crawler import add_default_channels as add_default_channels
from .crawler import add_generated_channels as add_generated_channels
from .crawler import add_local_channels as add_local_channels
from .crawler import default_channels as default_channels
from .crawler import get_or_create_channel as get_or_create_channel
from .crawler import get_or_create_generated_channel as get_or_create_generated_channel
from .crawler import get_or_create_local_channel as get_or_create_local_channel
from .crawler import update_channel as update_channel
from .feed import read_channel as read_channel
from .feed import read_episodes as read_episodes
from .local import read_local_channel as read_local_channel
from .local import read_local_episodes as read_local_episodes
