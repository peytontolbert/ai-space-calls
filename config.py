import os
class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'my_secret_key')  # For session management, etc.
    DEBUG = os.getenv('DEBUG', 'True')  # Set to False in production

class DevelopmentConfig(Config):
    ENV = 'development'
    DEBUG = True

class ProductionConfig(Config):
    ENV = 'production'
    DEBUG = False
