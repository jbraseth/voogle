# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

# pyright: reportUndefinedVariable=false, reportGeneralTypeIssues=false

"""Add mux_playback_id to episodes and extend channel kind length

Revision ID: a3fdb61cc3d9
Revises: 6baff69d05b2
Create Date: 2026-01-11

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "a3fdb61cc3d9"
down_revision = "6baff69d05b2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("episodes", sa.Column("mux_playback_id", sa.String(100), nullable=True))
    # SQLite doesn't support ALTER COLUMN, but String(20) is compatible with String(10)
    # The model change is sufficient; existing data will work fine


def downgrade() -> None:
    op.drop_column("episodes", "mux_playback_id")
