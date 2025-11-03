from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Merchant
from app.schemas import RegisterRequest, LoginRequest, TokenResponse, MerchantOut
from app.security import hash_password, verify_password, create_access_token
from app.deps import get_current_merchant

router = APIRouter()


@router.post("/register", response_model=MerchantOut)
def register(request: RegisterRequest, db: Session = Depends(get_db)):  # type: ignore[no-untyped-def]
    existing = db.query(Merchant).filter(Merchant.email == request.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    merchant = Merchant(
        email=request.email,
        password_hash=hash_password(request.password),
        kyc_verified=False,
    )
    db.add(merchant)
    db.commit()
    db.refresh(merchant)
    return merchant


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):  # type: ignore[no-untyped-def]
    merchant = db.query(Merchant).filter(Merchant.email == request.email).first()
    if not merchant or not verify_password(request.password, merchant.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    token = create_access_token(merchant.email)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=MerchantOut)
def get_me(merchant: Merchant = Depends(get_current_merchant)):  # type: ignore[no-untyped-def]
    return merchant
