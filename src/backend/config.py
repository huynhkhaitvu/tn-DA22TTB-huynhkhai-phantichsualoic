"""
Flask Configuration
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration"""
    DEBUG = False
    TESTING = False
    JSON_SORT_KEYS = False
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max
    
    # Session configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    SESSION_COOKIE_SECURE = False  # Set True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours
    
    # API Keys
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY', '')
    GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
    # Note: OpenRouter support removed
    
    # CORS
    CORS_ORIGINS = ["http://localhost:5000", "http://127.0.0.1:5000", 
                    "file://"]
    


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False
    ENV = 'development'


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    ENV = 'production'


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True


# Get configuration based on FLASK_ENV
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Get current configuration"""
    env = os.getenv('FLASK_ENV', 'development')
    return config.get(env, config['default'])
