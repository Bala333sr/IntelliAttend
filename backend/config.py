import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'dev-jwt-secret-key'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    CORS_ORIGINS = ['http://localhost:5002', 'http://127.0.0.1:5002']
    
    # Use SQLite for development
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///intelliattend.db'

class DevelopmentConfig(Config):
    DEBUG = True
    # Use SQLite for development
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'sqlite:///intelliattend_dev.db'

class TestingConfig(Config):
    TESTING = True
    # Use SQLite for testing
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or 'sqlite:///intelliattend_test.db'

class ProductionConfig(Config):
    # Use MySQL for production
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f"mysql+pymysql://{os.environ.get('MYSQL_USER', 'root')}:{os.environ.get('MYSQL_PASSWORD', '')}@{os.environ.get('MYSQL_HOST', 'localhost')}:{os.environ.get('MYSQL_PORT', 3306)}/{os.environ.get('MYSQL_DB', 'intelliattend_db')}"

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}