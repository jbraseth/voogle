# Copyright (c) 2022 Pablo González Carrizo (unmonoqueteclea)
# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Pytest configuration, hooks, and plugin registration."""

pytest_plugins = [
    "fixtures.database",
    "fixtures.net",
    "fixtures.models",
    "fixtures.test_files",
    "fixtures.manifest",
    "fixtures.playwright",
    "fixtures.voogle",
]
