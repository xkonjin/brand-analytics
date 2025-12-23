# =============================================================================
# Payment Authorization Dependency
# =============================================================================
# Checks for valid payment before allowing access to premium features.
# =============================================================================

from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status, Header, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.database import get_db
from app.models.db_models import PaymentInvoice, PaymentStatusEnum


async def require_payment(
    x_invoice_id: Optional[str] = Header(None, alias="X-Invoice-ID"),
    db: AsyncSession = Depends(get_db),
) -> PaymentInvoice:
    """
    Require a completed payment for the request.
    
    Args:
        x_invoice_id: The ID of the paid invoice (from header)
        db: Database session
        
    Returns:
        PaymentInvoice: The validated invoice record
        
    Raises:
        HTTPException: 402 Payment Required if no valid payment found
    """
    if not settings.REQUIRE_PAYMENT:
        return None

    if not x_invoice_id:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Payment required to access this resource",
        )

    try:
        invoice_uuid = UUID(x_invoice_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid invoice ID format",
        )

    result = await db.execute(select(PaymentInvoice).where(PaymentInvoice.id == invoice_uuid))
    invoice = result.scalar_one_or_none()

    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found",
        )

    if invoice.status != PaymentStatusEnum.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Payment not completed",
            headers={"X-Invoice-Status": invoice.status.value},
        )

    return invoice

