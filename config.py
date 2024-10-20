import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'my_secret_key')  # For session management, etc.
    DEBUG = os.getenv('DEBUG', 'True')  # Set to False in production
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

class DevelopmentConfig(Config):
    ENV = 'development'
    DEBUG = True

class ProductionConfig(Config):
    ENV = 'production'
    DEBUG = False
