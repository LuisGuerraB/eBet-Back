import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'secret-secure-key-default'
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or 'postgresql://username:password@localhost/database-name'
    API_TITLE = "api"
    API_VERSION = "v1"
    UPLOAD_FOLDER = "static"
    OPENAPI_VERSION = "3.0.2"
    OPENAPI_URL_PREFIX = "apidocs"
    OPENAPI_SWAGGER_UI_PATH = "swagger"
    OPENAPI_SWAGGER_UI_VERSION = "3.22.2"
    PERMANENT_SESSION_LIFETIME = 86400  # Expiration 1 day

    # Gmail configuration
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_DEFAULT_SENDER = 'Ebet-prizes@gmail.com'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'correo-electronico'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'contraseña-segura'


