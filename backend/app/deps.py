from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Merchant
from app.security import decode_token


bearer_scheme = HTTPBearer(auto_error=False)


def get_current_merchant(
    creds: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):  # type: ignore[no-untyped-def]
    if not creds:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload = decode_token(creds.credentials)
        email = payload.get("sub")
        if not email:
            raise ValueError("missing sub")
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    merchant = db.query(Merchant).filter(Merchant.email == email).first()
    if not merchant:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return merchant


