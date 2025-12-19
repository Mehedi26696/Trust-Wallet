"""
Configuration settings for the TrustWallet backend application.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""
    
    # Database - Supabase Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    SUPABASE_URL: Optional[str] = os.getenv("SUPABASE_URL")
    SUPABASE_ANON_KEY: Optional[str] = os.getenv("SUPABASE_ANON_KEY")
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    # JWT Authentication
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))


    # GROQ
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    
    # Gemini (for chatbot)
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")

    
    # Application
    APP_NAME: str = "TrustWallet MVP Backend"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # CORS
    ALLOWED_ORIGINS: list[str] = os.getenv("ALLOWED_ORIGINS", "*").split(",")
    
    # Fraud Detection
    MAX_TRANSACTION_AMOUNT: float = float(os.getenv("MAX_TRANSACTION_AMOUNT", "100000"))
    HIGH_VALUE_THRESHOLD: float = float(os.getenv("HIGH_VALUE_THRESHOLD", "50000"))
    HIGH_VALUE_TIME_WINDOW_MINUTES: int = int(os.getenv("HIGH_VALUE_TIME_WINDOW_MINUTES", "5"))
    MAX_HIGH_VALUE_TRANSACTIONS: int = int(os.getenv("MAX_HIGH_VALUE_TRANSACTIONS", "3"))
    # ML anomaly handling: when true, block anomalous sends; when false, return warning JSON and proceed
    BLOCK_ML_ANOMALY: bool = os.getenv("BLOCK_ML_ANOMALY", "False").lower() == "true"
    
    # NID Validation
    ENABLE_NID_API_VALIDATION: bool = os.getenv("ENABLE_NID_API_VALIDATION", "False").lower() == "true"
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Email (for future notifications)
    SMTP_SERVER: Optional[str] = os.getenv("SMTP_SERVER")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: Optional[str] = os.getenv("SMTP_USERNAME")
    SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD")
    
    # ML Autoencoder (raw) settings
    AUTOENCODER_THRESHOLD: float = float(os.getenv("AUTOENCODER_THRESHOLD", "1.96"))
    MODEL_DIR: Optional[str] = os.getenv("MODEL_DIR")
    
    @property
    def is_supabase_configured(self) -> bool:
        """Check if Supabase is properly configured."""
        return bool(self.SUPABASE_URL and self.SUPABASE_ANON_KEY)
    
    @property
    def supabase_database_url(self) -> str:
        """Generate Supabase database URL from environment variables."""
        if not self.is_supabase_configured:
            return self.DATABASE_URL
        
        # Extract database details from Supabase URL
        # Supabase URL format: https://your-project-ref.supabase.co
        if self.SUPABASE_URL:
            project_ref = self.SUPABASE_URL.replace("https://", "").replace(".supabase.co", "")
            # Supabase PostgreSQL connection format
            return f"postgresql://postgres:{os.getenv('SUPABASE_DB_PASSWORD', '')}@db.{project_ref}.supabase.co:5432/postgres"
        
        return self.DATABASE_URL


# Global settings instance
settings = Settings()