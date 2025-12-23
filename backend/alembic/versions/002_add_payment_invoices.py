"""Add payment invoices table

Revision ID: 002_add_payment_invoices
Revises: 001_initial
Create Date: 2025-12-23

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "002_add_payment_invoices"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create payment_invoices table
    op.create_table(
        "payment_invoices",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("payer_address", sa.String(42), nullable=False),
        sa.Column("amount_atomic", sa.BigInteger, nullable=False),
        sa.Column("nonce", sa.String(66), nullable=False),
        sa.Column("deadline", sa.DateTime, nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "pending",
                "completed",
                "expired",
                "failed",
                name="paymentstatusenum",
            ),
            nullable=False,
            default="pending",
            index=True,
        ),
        sa.Column("tx_hash", sa.String(66), nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, default=sa.func.now()),
    )

    op.create_index("ix_payment_invoices_nonce", "payment_invoices", ["nonce"], unique=True)
    op.create_index("ix_payment_invoices_tx_hash", "payment_invoices", ["tx_hash"])


def downgrade() -> None:
    op.drop_index("ix_payment_invoices_tx_hash", table_name="payment_invoices")
    op.drop_index("ix_payment_invoices_nonce", table_name="payment_invoices")
    op.drop_table("payment_invoices")
    op.execute("DROP TYPE IF EXISTS paymentstatusenum")

