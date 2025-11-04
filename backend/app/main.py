from app.config import settings
from app.database import init_db
from app.routers import auth, payments, transactions
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])  # basic rate limit
app = FastAPI(title="PayQI - Stripe for Crypto")


@app.on_event("startup")
def on_startup() -> None:
    init_db()


app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
def rate_limit_handler(request, exc):  # type: ignore[no-untyped-def]
    return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})


app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.BACKEND_CORS_ORIGINS.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(payments.router, prefix="/api", tags=["payments"])
app.include_router(transactions.router, prefix="/api", tags=["transactions"])


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
