from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from decimal import Decimal
import httpx
from app.database import get_db
from app.models import Payment, Merchant
from app.schemas import CreatePaymentRequest, CreatePaymentResponse, PaymentOut
from app.deps import get_current_merchant
from app.config import settings

router = APIRouter()


async def create_nowpayments_invoice(amount: float, currency: str) -> dict:  # type: ignore[no-untyped-def]
    """Create an invoice using NOWPayments API"""
    url = "https://api.nowpayments.io/v1/payment"
    headers = {
        "x-api-key": settings.NOWPAYMENTS_API_KEY,
        "Content-Type": "application/json",
    }
    data = {
        "price_amount": amount,
        "price_currency": currency.lower(),
        "pay_currency": currency.lower(),
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=data, headers=headers, timeout=30.0)
        response.raise_for_status()
        return response.json()


@router.post("/payments", response_model=CreatePaymentResponse)
async def create_payment(
    request: CreatePaymentRequest,
    merchant: Merchant = Depends(get_current_merchant),
    db: Session = Depends(get_db),
):  # type: ignore[no-untyped-def]
    # Validate currency - support XRP (XRP Ledger) and other cryptocurrencies for daily products and services
    supported_currencies = ["xrp", "btc", "eth", "ltc", "bch", "usdt", "usdc", "usd", "eur"]
    currency_lower = request.currency.lower()
    
    # Ensure XRP is prominently supported for daily payments
    if currency_lower not in supported_currencies:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Currency {request.currency} not supported. Supported cryptocurrencies include XRP, BTC, ETH, and others: {', '.join(supported_currencies)}"
        )
    
    # Create payment record
    payment = Payment(
        merchant_id=merchant.id,
        amount=Decimal(str(request.amount)),
        currency=currency_lower,
        status="pending",
        provider="nowpayments",
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    
    try:
        # Create invoice with NOWPayments
        invoice = await create_nowpayments_invoice(request.amount, currency_lower)
        
        # Update payment with invoice details
        payment.provider_invoice_id = invoice.get("payment_id")
        payment.pay_address = invoice.get("pay_address")
        payment.raw_payload = str(invoice)
        db.commit()
        db.refresh(payment)
        
        return CreatePaymentResponse(
            payment_id=payment.id,
            status=payment.status,
            provider_invoice_id=payment.provider_invoice_id,
            pay_address=payment.pay_address,
            checkout_url=invoice.get("invoice_url"),
        )
    except httpx.HTTPStatusError as e:
        payment.status = "failed"
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Payment provider error: {e.response.text if hasattr(e, 'response') else str(e)}"
        )
    except Exception as e:
        payment.status = "failed"
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create payment: {str(e)}"
        )


@router.get("/payments/{payment_id}", response_model=PaymentOut)
def get_payment(
    payment_id: int,
    merchant: Merchant = Depends(get_current_merchant),
    db: Session = Depends(get_db),
):  # type: ignore[no-untyped-def]
    payment = db.query(Payment).filter(
        Payment.id == payment_id,
        Payment.merchant_id == merchant.id
    ).first()
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    return payment
