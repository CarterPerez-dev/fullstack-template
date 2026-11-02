"""
©AngelaMos | 2026
20261025_010000_portfolio_integrity.py
"""

from alembic import op
import sqlalchemy as sa

revision = "d74b10ce893f"
down_revision = "c62a9f108d31"
branch_labels = None
depends_on = None

MEDIA_REFERENCES = (
    ("portfolio_profile", "avatar_media_id"),
    ("portfolio_settings", "favicon_media_id"),
    ("portfolio_certifications", "badge_media_id"),
    ("portfolio_projects", "image_media_id"),
    ("portfolio_links", "media_id"),
)


def upgrade() -> None:
    for table in ("portfolio_profile", "portfolio_settings"):
        op.add_column(
            table,
            sa.Column("singleton_key", sa.Boolean(), nullable=False, server_default=sa.true()),
        )
        op.create_check_constraint(
            op.f(f"ck_{table}_singleton_key_true"), table, "singleton_key = true",
        )
        op.create_unique_constraint(
            op.f(f"uq_{table}_singleton_key"), table, ["singleton_key"],
        )
    for table, column in MEDIA_REFERENCES:
        op.create_foreign_key(
            op.f(f"fk_{table}_{column}_portfolio_media"), table, "portfolio_media",
            [column], ["id"], ondelete="SET NULL",
        )


def downgrade() -> None:
    for table, column in reversed(MEDIA_REFERENCES):
        op.drop_constraint(
            op.f(f"fk_{table}_{column}_portfolio_media"), table, type_="foreignkey",
        )
    for table in ("portfolio_settings", "portfolio_profile"):
        op.drop_constraint(op.f(f"uq_{table}_singleton_key"), table, type_="unique")
        op.drop_constraint(op.f(f"ck_{table}_singleton_key_true"), table, type_="check")
        op.drop_column(table, "singleton_key")
