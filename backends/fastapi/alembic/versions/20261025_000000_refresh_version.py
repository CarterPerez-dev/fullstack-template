"""
©AngelaMos | 2026
20261025_000000_refresh_version.py
"""

from alembic import op
import sqlalchemy as sa


revision = "c62a9f108d31"
down_revision = "801b86be184b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "refresh_tokens",
        sa.Column(
            "token_version",
            sa.Integer(),
            nullable = False,
            server_default = "0"
        )
    )


def downgrade() -> None:
    op.drop_column("refresh_tokens", "token_version")
