"""Initial schema for brand analytics

Revision ID: 001_initial
Revises: 
Create Date: 2025-01-19

Creates the initial database schema:
- analyses: Main table for brand analysis jobs
- analysis_cache: Cache table for scraped data and API responses
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "analyses",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("url", sa.String(2048), nullable=False, index=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("industry", sa.String(255), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column(
            "status",
            sa.Enum("pending", "processing", "completed", "failed", name="analysisstatusenum"),
            nullable=False,
            default="pending",
            index=True,
        ),
        sa.Column("progress", sa.JSON, nullable=False, default=dict),
        sa.Column("scores", sa.JSON, nullable=True),
        sa.Column("overall_score", sa.Float, nullable=True),
        sa.Column("report", sa.JSON, nullable=True),
        sa.Column("pdf_url", sa.String(2048), nullable=True),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column("completed_at", sa.DateTime, nullable=True),
        sa.Column("processing_time_seconds", sa.Float, nullable=True),
    )

    op.create_index("ix_analyses_created_at", "analyses", [sa.text("created_at DESC")])
    op.create_index("ix_analyses_status_created", "analyses", ["status", sa.text("created_at DESC")])

    op.create_table(
        "analysis_cache",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("cache_key", sa.String(512), unique=True, nullable=False, index=True),
        sa.Column("url", sa.String(2048), nullable=False),
        sa.Column("data_type", sa.String(50), nullable=False),
        sa.Column("data", sa.JSON, nullable=False),
        sa.Column("expires_at", sa.DateTime, nullable=False, index=True),
        sa.Column("created_at", sa.DateTime, nullable=False, default=sa.func.now()),
    )

    op.create_index("ix_cache_url_type", "analysis_cache", ["url", "data_type"])


def downgrade() -> None:
    op.drop_index("ix_cache_url_type", table_name="analysis_cache")
    op.drop_table("analysis_cache")
    
    op.drop_index("ix_analyses_status_created", table_name="analyses")
    op.drop_index("ix_analyses_created_at", table_name="analyses")
    op.drop_table("analyses")
    
    op.execute("DROP TYPE IF EXISTS analysisstatusenum")
