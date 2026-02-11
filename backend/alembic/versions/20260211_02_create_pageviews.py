"""create pageviews table

Revision ID: 20260211_02
Revises: 20260211_01
Create Date: 2026-02-11 13:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260211_02"
down_revision: Union[str, Sequence[str], None] = "20260211_01"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "pageviews",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("path", sa.String(length=2048), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("referrer", sa.String(length=2048), nullable=True),
        sa.Column("session_id", sa.String(length=128), nullable=True),
        sa.Column("user_agent", sa.String(length=512), nullable=True),
        sa.Column("ip_address", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("pageviews")
