# Copyright (c) 2022 Pablo González Carrizo (unmonoqueteclea)
# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Pytest configuration, hooks, and plugin registration."""

pytest_plugins = [
    "tests.fixtures.database",
    "tests.fixtures.net",
    "tests.fixtures.models",
    "tests.fixtures.data",
]
