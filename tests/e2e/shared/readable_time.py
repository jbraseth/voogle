# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Utilities for formatting time durations in human-readable format."""


def get_readable_seconds(seconds: float) -> str:
    """Given a seconds, return a human readable string of hours, minutes and seconds"""
    if seconds < 60:
        return f"{seconds:1.1f} seconds"

    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)

    sections = []
    d = int(d)
    h = int(h)
    m = int(m)
    s = int(s)

    if d > 1:
        sections.append(f"{d} days")
    elif d == 1:
        sections.append(f"{d} day")

    if h > 1:
        sections.append(f"{h} hours")
    elif h == 1:
        sections.append(f"{h} hour")

    if m > 1:
        sections.append(f"{m} minutes")
    elif m == 1:
        sections.append(f"{m} minute")

    if d < 1 and h < 1:
        if s > 1:
            sections.append(f"{s} seconds")
        else:
            sections.append(f"{s} second")

    return " ".join(sections)
