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
from .url_health import URLHealthResult as URLHealthResult
from .url_health import URLRefreshResult as URLRefreshResult
from .url_health import URLStatus as URLStatus
from .url_health import apply_url_refresh as apply_url_refresh
from .url_health import check_all_broken_urls as check_all_broken_urls
from .url_health import check_channel_urls as check_channel_urls
from .url_health import check_episode_url as check_episode_url
from .url_health import check_url as check_url
from .url_health import preview_channel_refresh as preview_channel_refresh
from .url_health import refresh_broken_urls as refresh_broken_urls
