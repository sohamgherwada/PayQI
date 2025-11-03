from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from decimal import Decimal
from app.database import get_db
from app.models import Payment, Merchant
from app.schemas import CreatePaymentRequest, CreatePaymentResponse, PaymentOut
from app.deps import get_current_merchant
from app.config import settings
import httpx
import json

router = APIRouter()

# Supported currencies
SUPPORTED_CRYPTOS = ["BTC", "ETH", "USDT", "USDC", "XRP", "LTC", "DOGE"]
XRP_DROPS_PER_XRP = Decimal("1000000")  # XRP uses drops (6 decimal places)


def create_nowpayments_invoice(amount: float, currency: str, merchant_id: int):  # type: ignore[no-untyped-def]
    """Create invoice via NOWPayments API"""
    if not settings.NOWPAYMENTS_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="NOWPayments API key not configured"
        )
    
    url = "https://api.nowpayments.io/v1/payment"
    headers = {
        "x-api-key": settings.NOWPAYMENTS_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "price_amount": amount,
        "price_currency": "usd",
        "pay_currency": currency.lower(),
        "order_id": f"merchant_{merchant_id}_payment",
        "order_description": f"Payment for merchant {merchant_id}",
        "ipn_callback_url": f"{settings.BACKEND_CORS_ORIGINS}/api/payments/webhook"
    }
    
    try:
        with httpx.Client() as client:
            response = client.post(url, headers=headers, json=payload, timeout=30.0)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to create NOWPayments invoice: {str(e)}"
        )


def generate_xrp_payment_address(merchant_id: int, payment_id: int):  # type: ignore[no-untyped-def]
    """
    Generate XRP payment address and destination tag.
    For production, you should use your own XRP wallet address.
    Here we generate a destination tag based on merchant and payment IDs.
    """
    # In production, ensure XRP_WALLET_ADDRESS is set in environment variables
    xrp_wallet_address = settings.XRP_WALLET_ADDRESS if hasattr(settings, 'XRP_WALLET_ADDRESS') else ""
    
    if not xrp_wallet_address:
        # For demo purposes, we'll use a placeholder
        # In production, you MUST configure a real XRP wallet address
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="XRP wallet address not configured. Please set XRP_WALLET_ADDRESS in environment."
        )
    
    # Generate a unique destination tag (max 32 bits, so max value is 4294967295)
    # Using merchant_id and payment_id to create a unique tag
    destination_tag = (merchant_id * 1000000 + payment_id) % 4294967295
    
    return {
        "address": xrp_wallet_address,
        "destination_tag": destination_tag,
        "amount_xrp": None,  # Will be calculated based on USD amount
    }


def convert_usd_to_xrp(usd_amount: float):  # type: ignore[no-untyped-def]
    """
    Convert USD amount to XRP.
    In production, you should fetch live rates from an exchange API.
    For now, we'll use a placeholder rate.
    """
    # Note: For production, implement real-time rate fetching from CoinGecko, Binance, or XRP Ledger
    # For now, using a default rate (update with real API)
    try:
        # Try to fetch from CoinGecko API
        url = "https://api.coingecko.com/api/v3/simple/price?ids=ripple&vs_currencies=usd"
        with httpx.Client() as client:
            response = client.get(url, timeout=10.0)
            if response.status_code == 200:
                data = response.json()
                xrp_rate = data.get("ripple", {}).get("usd", 0.5)
            else:
                xrp_rate = 0.5  # Fallback rate
    except Exception:
        xrp_rate = 0.5  # Fallback rate
    
    return Decimal(str(usd_amount)) / Decimal(str(xrp_rate))


@router.post("/payments", response_model=CreatePaymentResponse, status_code=status.HTTP_201_CREATED)
def create_payment(
    request: CreatePaymentRequest,
    merchant: Merchant = Depends(get_current_merchant),
    db: Session = Depends(get_db)
):  # type: ignore[no-untyped-def]
    """Create a payment request. Supports NOWPayments and direct XRP payments."""
    
    # Validate currency
    currency_upper = request.currency.upper()
    if currency_upper not in SUPPORTED_CRYPTOS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported currency. Supported: {', '.join(SUPPORTED_CRYPTOS)}"
        )
    
    # Create payment record
    payment = Payment(
        merchant_id=merchant.id,
        amount=Decimal(str(request.amount)),
        currency=currency_upper,
        status="pending",
        provider="xrp" if currency_upper == "XRP" else "nowpayments"
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    
    # Handle XRP payments directly
    if currency_upper == "XRP":
        try:
            xrp_info = generate_xrp_payment_address(merchant.id, payment.id)
            xrp_amount = convert_usd_to_xrp(request.amount)
            
            payment.pay_address = xrp_info["address"]
            payment.provider_invoice_id = f"xrp_{payment.id}_{xrp_info['destination_tag']}"
            payment.raw_payload = json.dumps({
                "destination_tag": xrp_info["destination_tag"],
                "amount_xrp": str(xrp_amount),
                "amount_usd": request.amount
            })
            db.commit()
            
            return CreatePaymentResponse(
                payment_id=payment.id,
                status=payment.status,
                provider_invoice_id=payment.provider_invoice_id,
                pay_address=payment.pay_address,
                checkout_url=None
            )
        except HTTPException:
            raise
        except Exception as e:
            payment.status = "failed"
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create XRP payment: {str(e)}"
            )
    
    # Handle other currencies via NOWPayments
    try:
        invoice_data = create_nowpayments_invoice(request.amount, currency_upper, merchant.id)
        
        payment.provider_invoice_id = invoice_data.get("payment_id")
        payment.pay_address = invoice_data.get("pay_address")
        payment.checkout_url = invoice_data.get("invoice_url") or invoice_data.get("pay_url")
        payment.raw_payload = json.dumps(invoice_data)
        db.commit()
        
        return CreatePaymentResponse(
            payment_id=payment.id,
            status=payment.status,
            provider_invoice_id=payment.provider_invoice_id,
            pay_address=payment.pay_address,
            checkout_url=payment.checkout_url
        )
    except HTTPException:
        raise
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
    db: Session = Depends(get_db)
):  # type: ignore[no-untyped-def]
    """Get payment details"""
    payment = db.query(Payment).filter(
        Payment.id == payment_id,
        Payment.merchant_id == merchant.id
    ).first()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    return payment


@router.post("/payments/webhook")
def payment_webhook(request_data: dict, db: Session = Depends(get_db)):  # type: ignore[no-untyped-def]
    """Handle payment webhooks from NOWPayments"""
    # Note: Implement webhook signature verification and payment status updates
    # For NOWPayments, verify IPN signature
    # For XRP, this would be called by your XRP monitoring service
    pass
