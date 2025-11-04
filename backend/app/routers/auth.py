from app.database import get_db
from app.deps import get_current_merchant
from app.models import Merchant
from app.schemas import LoginRequest, MerchantOut, RegisterRequest, TokenResponse
from app.security import create_access_token, hash_password, verify_password
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

router = APIRouter()


@router.post("/register", response_model=MerchantOut, status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest, db: Session = Depends(get_db)):  # type: ignore[no-untyped-def]
    # Check if merchant already exists
    existing = db.query(Merchant).filter(Merchant.email == request.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    # Create new merchant
    merchant = Merchant(email=request.email, password_hash=hash_password(request.password), kyc_verified=False)
    db.add(merchant)
    db.commit()
    db.refresh(merchant)

    return merchant


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):  # type: ignore[no-untyped-def]
    merchant = db.query(Merchant).filter(Merchant.email == request.email).first()
    if not merchant or not verify_password(request.password, merchant.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    token = create_access_token(subject=merchant.email)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=MerchantOut)
def get_me(merchant: Merchant = Depends(get_current_merchant)):  # type: ignore[no-untyped-def]
    return merchant
