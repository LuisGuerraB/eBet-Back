import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'secret-secure-key-default'
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or 'postgresql://username:password@localhost/database-name'
