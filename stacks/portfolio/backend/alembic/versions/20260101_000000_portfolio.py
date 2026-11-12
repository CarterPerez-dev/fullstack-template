"""portfolio content tables

Revision ID: b2f4a6c8d0e2
Revises: 801b86be184b
Create Date: 2026-01-01 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = 'b2f4a6c8d0e2'
down_revision: Union[str, None] = '801b86be184b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

item_status = postgresql.ENUM(
    'completed',
    'in_progress',
    'planned',
    name = 'itemstatus'
)


def upgrade() -> None:
    bind = op.get_bind()
    item_status.create(bind, checkfirst = True)
    status_type = postgresql.ENUM(
        'completed',
        'in_progress',
        'planned',
        name = 'itemstatus',
        create_type = False,
    )

    op.create_table(
        'portfolio_profile',
        sa.Column('name',
                  sa.String(length = 255),
                  nullable = False),
        sa.Column('headline',
                  sa.String(length = 1024),
                  nullable = False),
        sa.Column('subtitle',
                  sa.String(length = 255),
                  nullable = True),
        sa.Column('location',
                  sa.String(length = 255),
                  nullable = True),
        sa.Column('availability',
                  sa.String(length = 255),
                  nullable = True),
        sa.Column('bio',
                  sa.Text(),
                  nullable = True),
        sa.Column('email',
                  sa.String(length = 320),
                  nullable = True),
        sa.Column('avatar_media_id',
                  sa.Uuid(),
                  nullable = True),
        sa.Column('eyebrow_left',
                  sa.String(length = 255),
                  nullable = True),
        sa.Column('eyebrow_right',
                  sa.String(length = 255),
                  nullable = True),
        sa.Column(
            'meta_items',
            postgresql.JSONB(astext_type = sa.Text()),
            nullable = False
        ),
        sa.Column(
            'section_titles',
            postgresql.JSONB(astext_type = sa.Text()),
            nullable = False
        ),
        sa.Column('id',
                  sa.Uuid(),
                  nullable = False),
        sa.Column(
            'created_at',
            sa.DateTime(timezone = True),
            server_default = sa.text('now()'),
            nullable = False
        ),
        sa.Column('updated_at',
                  sa.DateTime(timezone = True),
                  nullable = True),
        sa.PrimaryKeyConstraint('id',
                                name = op.f('pk_portfolio_profile')),
    )

    op.create_table(
        'portfolio_settings',
        sa.Column('site_title',
                  sa.String(length = 255),
                  nullable = False),
        sa.Column('meta_description',
                  sa.String(length = 1024),
                  nullable = True),
        sa.Column('favicon_media_id',
                  sa.Uuid(),
                  nullable = True),
        sa.Column('color_bg',
                  sa.String(length = 32),
                  nullable = False),
        sa.Column('color_surface',
                  sa.String(length = 32),
                  nullable = False),
        sa.Column('color_text',
                  sa.String(length = 32),
                  nullable = False),
        sa.Column('color_text_muted',
                  sa.String(length = 32),
                  nullable = False),
        sa.Column('color_accent',
                  sa.String(length = 32),
                  nullable = False),
        sa.Column('color_dark_bg',
                  sa.String(length = 32),
                  nullable = False),
        sa.Column('color_dark_text',
                  sa.String(length = 32),
                  nullable = False),
        sa.Column('font_display',
                  sa.String(length = 128),
                  nullable = False),
        sa.Column('font_body',
                  sa.String(length = 128),
                  nullable = False),
        sa.Column('font_mono',
                  sa.String(length = 128),
                  nullable = False),
        sa.Column('dark_mode',
                  sa.Boolean(),
                  nullable = False),
        sa.Column(
            'theme_extra',
            postgresql.JSONB(astext_type = sa.Text()),
            nullable = False
        ),
        sa.Column('id',
                  sa.Uuid(),
                  nullable = False),
        sa.Column(
            'created_at',
            sa.DateTime(timezone = True),
            server_default = sa.text('now()'),
            nullable = False
        ),
        sa.Column('updated_at',
                  sa.DateTime(timezone = True),
                  nullable = True),
        sa.PrimaryKeyConstraint('id',
                                name = op.f('pk_portfolio_settings')),
    )

    op.create_table(
        'portfolio_certifications',
        sa.Column('name',
                  sa.String(length = 255),
                  nullable = False),
        sa.Column('code',
                  sa.String(length = 128),
                  nullable = True),
        sa.Column('issuer',
                  sa.String(length = 255),
                  nullable = True),
        sa.Column('status',
                  status_type,
                  nullable = False),
        sa.Column('issue_date',
                  sa.String(length = 64),
                  nullable = True),
        sa.Column('credential_url',
                  sa.String(length = 2048),
                  nullable = True),
        sa.Column('badge_media_id',
                  sa.Uuid(),
                  nullable = True),
        sa.Column('display_order',
                  sa.Integer(),
                  nullable = False),
        sa.Column('id',
                  sa.Uuid(),
                  nullable = False),
        sa.Column(
            'created_at',
            sa.DateTime(timezone = True),
            server_default = sa.text('now()'),
            nullable = False
        ),
        sa.Column('updated_at',
                  sa.DateTime(timezone = True),
                  nullable = True),
        sa.PrimaryKeyConstraint('id',
                                name = op.f('pk_portfolio_certifications')),
    )
    op.create_index(
        op.f('ix_portfolio_certifications_display_order'),
        'portfolio_certifications',
        ['display_order'],
        unique = False,
    )

    op.create_table(
        'portfolio_projects',
        sa.Column('title',
                  sa.String(length = 255),
                  nullable = False),
        sa.Column('description',
                  sa.Text(),
                  nullable = True),
        sa.Column('status',
                  status_type,
                  nullable = False),
        sa.Column('tags',
                  postgresql.JSONB(astext_type = sa.Text()),
                  nullable = False),
        sa.Column('repo_url',
                  sa.String(length = 2048),
                  nullable = True),
        sa.Column('live_url',
                  sa.String(length = 2048),
                  nullable = True),
        sa.Column('image_media_id',
                  sa.Uuid(),
                  nullable = True),
        sa.Column('display_order',
                  sa.Integer(),
                  nullable = False),
        sa.Column('id',
                  sa.Uuid(),
                  nullable = False),
        sa.Column(
            'created_at',
            sa.DateTime(timezone = True),
            server_default = sa.text('now()'),
            nullable = False
        ),
        sa.Column('updated_at',
                  sa.DateTime(timezone = True),
                  nullable = True),
        sa.PrimaryKeyConstraint('id',
                                name = op.f('pk_portfolio_projects')),
    )
    op.create_index(
        op.f('ix_portfolio_projects_display_order'),
        'portfolio_projects',
        ['display_order'],
        unique = False,
    )

    op.create_table(
        'portfolio_experience',
        sa.Column('role',
                  sa.String(length = 255),
                  nullable = False),
        sa.Column('company',
                  sa.String(length = 255),
                  nullable = True),
        sa.Column('dates',
                  sa.String(length = 128),
                  nullable = True),
        sa.Column(
            'bullets',
            postgresql.JSONB(astext_type = sa.Text()),
            nullable = False
        ),
        sa.Column('display_order',
                  sa.Integer(),
                  nullable = False),
        sa.Column('id',
                  sa.Uuid(),
                  nullable = False),
        sa.Column(
            'created_at',
            sa.DateTime(timezone = True),
            server_default = sa.text('now()'),
            nullable = False
        ),
        sa.Column('updated_at',
                  sa.DateTime(timezone = True),
                  nullable = True),
        sa.PrimaryKeyConstraint('id',
                                name = op.f('pk_portfolio_experience')),
    )
    op.create_index(
        op.f('ix_portfolio_experience_display_order'),
        'portfolio_experience',
        ['display_order'],
        unique = False,
    )

    op.create_table(
        'portfolio_skill_groups',
        sa.Column('label',
                  sa.String(length = 255),
                  nullable = False),
        sa.Column('items',
                  postgresql.JSONB(astext_type = sa.Text()),
                  nullable = False),
        sa.Column('display_order',
                  sa.Integer(),
                  nullable = False),
        sa.Column('id',
                  sa.Uuid(),
                  nullable = False),
        sa.Column(
            'created_at',
            sa.DateTime(timezone = True),
            server_default = sa.text('now()'),
            nullable = False
        ),
        sa.Column('updated_at',
                  sa.DateTime(timezone = True),
                  nullable = True),
        sa.PrimaryKeyConstraint('id',
                                name = op.f('pk_portfolio_skill_groups')),
    )
    op.create_index(
        op.f('ix_portfolio_skill_groups_display_order'),
        'portfolio_skill_groups',
        ['display_order'],
        unique = False,
    )

    op.create_table(
        'portfolio_links',
        sa.Column('label',
                  sa.String(length = 255),
                  nullable = False),
        sa.Column('url',
                  sa.String(length = 2048),
                  nullable = True),
        sa.Column('media_id',
                  sa.Uuid(),
                  nullable = True),
        sa.Column('icon',
                  sa.String(length = 64),
                  nullable = True),
        sa.Column('display_order',
                  sa.Integer(),
                  nullable = False),
        sa.Column('id',
                  sa.Uuid(),
                  nullable = False),
        sa.Column(
            'created_at',
            sa.DateTime(timezone = True),
            server_default = sa.text('now()'),
            nullable = False
        ),
        sa.Column('updated_at',
                  sa.DateTime(timezone = True),
                  nullable = True),
        sa.PrimaryKeyConstraint('id',
                                name = op.f('pk_portfolio_links')),
    )
    op.create_index(
        op.f('ix_portfolio_links_display_order'),
        'portfolio_links',
        ['display_order'],
        unique = False,
    )

    op.create_table(
        'portfolio_custom_sections',
        sa.Column('title',
                  sa.String(length = 255),
                  nullable = False),
        sa.Column('subtitle',
                  sa.String(length = 255),
                  nullable = True),
        sa.Column('body',
                  sa.Text(),
                  nullable = True),
        sa.Column('items',
                  postgresql.JSONB(astext_type = sa.Text()),
                  nullable = False),
        sa.Column('display_order',
                  sa.Integer(),
                  nullable = False),
        sa.Column('id',
                  sa.Uuid(),
                  nullable = False),
        sa.Column(
            'created_at',
            sa.DateTime(timezone = True),
            server_default = sa.text('now()'),
            nullable = False
        ),
        sa.Column('updated_at',
                  sa.DateTime(timezone = True),
                  nullable = True),
        sa.PrimaryKeyConstraint('id',
                                name = op.f('pk_portfolio_custom_sections')),
    )
    op.create_index(
        op.f('ix_portfolio_custom_sections_display_order'),
        'portfolio_custom_sections',
        ['display_order'],
        unique = False,
    )

    op.create_table(
        'portfolio_media',
        sa.Column('original_filename',
                  sa.String(length = 512),
                  nullable = False),
        sa.Column('content_type',
                  sa.String(length = 128),
                  nullable = False),
        sa.Column('byte_size',
                  sa.Integer(),
                  nullable = False),
        sa.Column('storage_filename',
                  sa.String(length = 512),
                  nullable = False),
        sa.Column('id',
                  sa.Uuid(),
                  nullable = False),
        sa.Column(
            'created_at',
            sa.DateTime(timezone = True),
            server_default = sa.text('now()'),
            nullable = False
        ),
        sa.Column('updated_at',
                  sa.DateTime(timezone = True),
                  nullable = True),
        sa.PrimaryKeyConstraint('id',
                                name = op.f('pk_portfolio_media')),
    )
    op.create_index(
        op.f('ix_portfolio_media_storage_filename'),
        'portfolio_media',
        ['storage_filename'],
        unique = True,
    )


def downgrade() -> None:
    op.drop_index(
        op.f('ix_portfolio_media_storage_filename'),
        table_name = 'portfolio_media'
    )
    op.drop_table('portfolio_media')
    op.drop_index(
        op.f('ix_portfolio_custom_sections_display_order'),
        table_name = 'portfolio_custom_sections'
    )
    op.drop_table('portfolio_custom_sections')
    op.drop_index(
        op.f('ix_portfolio_links_display_order'),
        table_name = 'portfolio_links'
    )
    op.drop_table('portfolio_links')
    op.drop_index(
        op.f('ix_portfolio_skill_groups_display_order'),
        table_name = 'portfolio_skill_groups'
    )
    op.drop_table('portfolio_skill_groups')
    op.drop_index(
        op.f('ix_portfolio_experience_display_order'),
        table_name = 'portfolio_experience'
    )
    op.drop_table('portfolio_experience')
    op.drop_index(
        op.f('ix_portfolio_projects_display_order'),
        table_name = 'portfolio_projects'
    )
    op.drop_table('portfolio_projects')
    op.drop_index(
        op.f('ix_portfolio_certifications_display_order'),
        table_name = 'portfolio_certifications'
    )
    op.drop_table('portfolio_certifications')
    op.drop_table('portfolio_settings')
    op.drop_table('portfolio_profile')
    item_status.drop(op.get_bind(), checkfirst = True)
