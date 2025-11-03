from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MerchantOut(BaseModel):
    id: int
    email: EmailStr
    kyc_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


class CreatePaymentRequest(BaseModel):
    amount: float
    currency: str


class CreatePaymentResponse(BaseModel):
    payment_id: int
    status: str
    provider_invoice_id: Optional[str]
    pay_address: Optional[str]
    checkout_url: Optional[str]


class PaymentOut(BaseModel):
    id: int
    merchant_id: int
    amount: float
    currency: str
    status: str
    provider: str
    provider_invoice_id: Optional[str]
    pay_address: Optional[str]
    checkout_url: Optional[str]
    tx_hash: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class TransactionsResponse(BaseModel):
    items: List[PaymentOut]


