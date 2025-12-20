"""
Configuration management for EarlyCare Gateway.
Loads configuration from environment variables and .env file.
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load .env file from project root
project_root = Path(__file__).parent.parent
env_path = project_root / '.env'
load_dotenv(dotenv_path=env_path)


class Config:
    """Application configuration."""
    
    # ============================================
    # MongoDB Configuration
    # ============================================
    MONGODB_CONNECTION_STRING: str = os.getenv(
        'MONGODB_CONNECTION_STRING',
        'mongodb+srv://angelospeed2003:kjhwoP4rXR3UsnaV@mav.0zz64yh.mongodb.net/'
    )
    MONGODB_DATABASE_NAME: str = os.getenv('MONGODB_DATABASE_NAME', 'earlycare')
    MONGODB_USERNAME: Optional[str] = os.getenv('MONGODB_USERNAME')
    MONGODB_PASSWORD: Optional[str] = os.getenv('MONGODB_PASSWORD')
    
    # SSL/TLS Settings
    MONGODB_USE_SSL: bool = os.getenv('MONGODB_USE_SSL', 'true').lower() == 'true'
    MONGODB_SSL_ALLOW_INVALID_CERTIFICATES: bool = os.getenv(
        'MONGODB_SSL_ALLOW_INVALID_CERTIFICATES', 
        'true'
    ).lower() == 'true'
    
    # Connection Timeouts (milliseconds)
    MONGODB_SERVER_SELECTION_TIMEOUT: int = int(os.getenv('MONGODB_SERVER_SELECTION_TIMEOUT', '10000'))
    MONGODB_CONNECT_TIMEOUT: int = int(os.getenv('MONGODB_CONNECT_TIMEOUT', '20000'))
    MONGODB_SOCKET_TIMEOUT: int = int(os.getenv('MONGODB_SOCKET_TIMEOUT', '20000'))
    
    # ============================================
    # Flask Configuration
    # ============================================
    FLASK_SECRET_KEY: str = os.getenv('FLASK_SECRET_KEY', 'earlycare-secret-key-change-in-production')
    FLASK_ENV: str = os.getenv('FLASK_ENV', 'development')
    FLASK_DEBUG: bool = os.getenv('FLASK_DEBUG', 'true').lower() == 'true'
    
    # Upload Settings
    MAX_UPLOAD_SIZE_MB: int = int(os.getenv('MAX_UPLOAD_SIZE_MB', '100'))
    
    # ============================================
    # Gateway Configuration
    # ============================================
    GATEWAY_NAME: str = os.getenv('GATEWAY_NAME', 'EarlyCare Gateway')
    GATEWAY_VERSION: str = os.getenv('GATEWAY_VERSION', '1.0.0')
    
    # Logging
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT: str = os.getenv('LOG_FORMAT', 'json')
    
    # ============================================
    # Optional: Advanced Settings
    # ============================================
    ENABLE_CACHING: bool = os.getenv('ENABLE_CACHING', 'true').lower() == 'true'
    CACHE_TTL_SECONDS: int = int(os.getenv('CACHE_TTL_SECONDS', '300'))
    MAX_PROCESSING_TIME_MS: int = int(os.getenv('MAX_PROCESSING_TIME_MS', '30000'))
    
    # ============================================
    # AI Configuration
    # ============================================
    GEMINI_API_KEY: Optional[str] = os.getenv('GEMINI_API_KEY')
    OPENAI_API_KEY: Optional[str] = os.getenv('OPENAI_API_KEY')
    
    # Chatbot AI Configuration (usa una chiave separata)
    CHATBOT_GEMINI_API_KEY: Optional[str] = os.getenv('CHATBOT_GEMINI_API_KEY')
    
    @classmethod
    def get_mongodb_connection_params(cls) -> dict:
        """
        Get MongoDB connection parameters as a dictionary.
        
        Returns:
            dict: Connection parameters for MongoClient
        """
        params = {
            'serverSelectionTimeoutMS': cls.MONGODB_SERVER_SELECTION_TIMEOUT,
            'connectTimeoutMS': cls.MONGODB_CONNECT_TIMEOUT,
            'socketTimeoutMS': cls.MONGODB_SOCKET_TIMEOUT,
        }
        
        if cls.MONGODB_USE_SSL:
            params.update({
                'tls': True,
                'tlsAllowInvalidCertificates': cls.MONGODB_SSL_ALLOW_INVALID_CERTIFICATES,
                'tlsAllowInvalidHostnames': cls.MONGODB_SSL_ALLOW_INVALID_CERTIFICATES,
            })
        
        return params
    
    @classmethod
    def validate(cls) -> bool:
        """
        Validate that all required configuration is present.
        
        Returns:
            bool: True if configuration is valid
        """
        if not cls.MONGODB_CONNECTION_STRING:
            raise ValueError("MONGODB_CONNECTION_STRING is required")
        
        if not cls.MONGODB_DATABASE_NAME:
            raise ValueError("MONGODB_DATABASE_NAME is required")
        
        return True
    
    @classmethod
    def print_config(cls, hide_secrets: bool = True):
        """
        Print current configuration (for debugging).
        
        Args:
            hide_secrets: If True, hide sensitive information
        """
        print("=" * 50)
        print("EarlyCare Gateway Configuration")
        print("=" * 50)
        
        if hide_secrets:
            conn_str = cls.MONGODB_CONNECTION_STRING
            if '@' in conn_str:
                # Hide password in connection string
                parts = conn_str.split('@')
                if '://' in parts[0]:
                    protocol, creds = parts[0].split('://')
                    if ':' in creds:
                        username = creds.split(':')[0]
                        conn_str = f"{protocol}://{username}:****@{parts[1]}"
            print(f"MongoDB Connection: {conn_str}")
        else:
            print(f"MongoDB Connection: {cls.MONGODB_CONNECTION_STRING}")
        
        print(f"Database Name: {cls.MONGODB_DATABASE_NAME}")
        print(f"Use SSL: {cls.MONGODB_USE_SSL}")
        print(f"Flask Environment: {cls.FLASK_ENV}")
        print(f"Debug Mode: {cls.FLASK_DEBUG}")
        print(f"Log Level: {cls.LOG_LEVEL}")
        print("=" * 50)


# Validate configuration on import
try:
    Config.validate()
except ValueError as e:
    print(f"⚠️  Configuration error: {e}")
    print("⚠️  Please create a .env file with the required settings")
    print(f"⚠️  See {project_root / '.env.example'} for a template")
