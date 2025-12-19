"""
TrustWallet-style MVP Backend
A secure FastAPI backend for a digital wallet application with NID verification and fraud detection.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime, timezone
from contextlib import asynccontextmanager
import uvicorn

from .users.user_routes import router as user_router
from .users.face_routes import router as face_router
from .transactions.transaction_routes import router as transaction_router
from .admin.admin_routes import router as admin_router
from .chatbot.chat_routes import router as chat_router
from .utils.database import test_database_connection
from .config import settings


version = "1.0.0"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.
    Handles startup and shutdown events.
    """
    # Startup code
    print("🚀 Starting TrustWallet Backend...")
    
    # Test database connection
    if not test_database_connection():
        print("❌ Database connection failed!")
        # In development mode, continue with warning instead of crashing
        if settings.DEBUG:
            print("⚠️ Continuing in development mode despite database connection issues...")
            print("⚠️ Some features may not work properly until database is accessible.")
        else:
            raise Exception("Database connection failed")
    
    # Database schema is managed by Alembic migrations
    print("✅ Database tables managed by Alembic migrations")
    print("💡 Use 'alembic upgrade head' to apply any pending migrations")
    
    # Preload XGBoost fraud detection model
    try:
        from .utils.xgboost_fraud_detector import load_xgboost_model
        load_xgboost_model()
        print("✅ XGBoost fraud detection model loaded successfully")
    except FileNotFoundError as e:
        print(f"⚠️ XGBoost model not found: {e}")
        print("⚠️ Fraud detection will not work until model is available")
    except Exception as e:
        print(f"⚠️ Failed to load XGBoost model: {e}")
    
    print("✅ TrustWallet Backend startup completed successfully!")
    
    yield  # <-- App runs while suspended here
    
    # Shutdown code
    print("🛑 Shutting down TrustWallet Backend...")
    print("💾 Cleanup completed")


# Create FastAPI app with lifespan
app = FastAPI(
    lifespan=lifespan,
    title="TrustWallet MVP Backend",
    description="""
    A secure digital wallet backend with NID verification and fraud detection.
    
    ## Features
    
    * **User Management**: Secure registration and authentication with Bangladesh NID validation
    * **Wallet Operations**: Balance management and money transfers
    * **Transaction System**: Complete transaction history and status tracking
    * **Fraud Detection**: Real-time fraud monitoring and prevention
    * **JWT Authentication**: Secure API access with token-based authentication
    
    ## Security
    
    * Password hashing with bcrypt
    * JWT token authentication
    * NID format validation for Bangladesh
    * Real-time fraud detection and blocking
    * Input validation and sanitization
    """,
    version=version,
    contact={
        "name": "TrustWallet Support",
        "email": "support@trustwallet.example.com",
    },
    license_info={
        "name": "MIT",
    },
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual frontend URLs
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Include routers
app.include_router(user_router , prefix="/api/v1", tags=["users"]) 
app.include_router(face_router , prefix="/api/v1", tags=["face"]) 
app.include_router(transaction_router, prefix="/api/v1", tags=["transactions"])
app.include_router(admin_router , prefix="/api/v1/admin", tags=["admin"])
app.include_router(chat_router, prefix="/api/v1", tags=["chat"])


@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "TrustWallet MVP Backend API",
        "version": version,
        "status": "operational",
        "documentation": "/docs",
        "health_check": "/health"
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "trustwallet-backend",
        "version": version
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler to prevent stack traces in production.
    Returns clean JSON error responses.
    """
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.detail}
        )
    
    # Log the actual error for debugging (in production, use proper logging)
    print(f"Unexpected error: {exc}")
    
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )

