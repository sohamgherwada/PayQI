from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Merchant, Payment
from app.schemas import TransactionsResponse, PaymentOut
from app.deps import get_current_merchant

router = APIRouter()


@router.get("/transactions", response_model=TransactionsResponse)
def get_transactions(
    merchant: Merchant = Depends(get_current_merchant),
    db: Session = Depends(get_db),
):  # type: ignore[no-untyped-def]
    payments = db.query(Payment).filter(Payment.merchant_id == merchant.id).order_by(Payment.created_at.desc()).all()
    return TransactionsResponse(items=payments)
