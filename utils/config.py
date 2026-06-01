import os


class Config:
    """Configuracion centralizada mediante variables de entorno."""

    SECRET_KEY = os.getenv("SECRET_KEY", "fama-dev-secret")
    FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
    FLASK_PORT = int(os.getenv("FLASK_PORT", "5000"))
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", "0") == "1"

    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "fama_db")

    # Resend - servicio de envio de emails transaccionales
    RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
    # Remitente de los emails (debe ser un dominio verificado en Resend o el dominio de prueba)
    MAIL_FROM = os.getenv("MAIL_FROM", "FAMA <onboarding@resend.dev>")
    # URL base de la app para generar enlaces absolutos en los emails
    APP_URL = os.getenv("APP_URL", "http://localhost:5000")

    # Tamano maximo de archivo subido: 5 MB (Flask rechaza automaticamente lo que supere este limite)
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024
