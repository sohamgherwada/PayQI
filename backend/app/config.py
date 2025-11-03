from pydantic_settings import BaseSettings
from pydantic import Field, field_validator


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+psycopg2://payqi:payqi@db:5432/payqi"
    JWT_SECRET: str = "change_me"
    JWT_EXPIRES_MINUTES: int = 60
    NOWPAYMENTS_API_KEY: str = ""
    NOWPAYMENTS_IPN_SECRET: str = ""
    XRP_WALLET_ADDRESS: str = ""
    BACKEND_CORS_ORIGINS: str = "http://localhost:5173"
    
    # Security settings
    MAX_REQUEST_SIZE: int = Field(default=1048576, description="Max request size in bytes (1MB)")
    MAX_PAYMENT_AMOUNT: float = Field(default=1000000.0, description="Maximum payment amount in USD")
    MIN_PAYMENT_AMOUNT: float = Field(default=0.01, description="Minimum payment amount in USD")
    RATE_LIMIT_PER_MINUTE: int = Field(default=100, description="Rate limit per minute per IP")
    RATE_LIMIT_AUTH_PER_MINUTE: int = Field(default=5, description="Rate limit for auth endpoints per minute")
    
    # Performance settings
    DB_POOL_SIZE: int = Field(default=20, description="Database connection pool size")
    DB_MAX_OVERFLOW: int = Field(default=10, description="Database max overflow connections")
    DB_POOL_TIMEOUT: int = Field(default=30, description="Database pool timeout in seconds")
    HTTP_TIMEOUT: int = Field(default=30, description="HTTP request timeout in seconds")
    EXCHANGE_RATE_CACHE_TTL: int = Field(default=60, description="Exchange rate cache TTL in seconds")
    
    # Redis (optional, for advanced caching)
    REDIS_URL: str = Field(default="", description="Redis URL for caching (optional)")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    
    @field_validator("JWT_SECRET", mode="before")
    @classmethod
    def validate_jwt_secret(cls, v: str) -> str:
        # Allow short secrets for testing
        import os
        if os.getenv("TESTING") == "true":
            return v if v else "test_secret_key_for_testing_only_change_in_production"
        if v == "change_me" or (len(v) < 32 if v else False):
            raise ValueError("JWT_SECRET must be at least 32 characters and not the default value")
        return v

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()  # type: ignore[call-arg]


