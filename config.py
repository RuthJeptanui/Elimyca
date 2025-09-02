import os
import secrets
from dotenv import load_dotenv

# Load base .env first
load_dotenv()

# Environment selector: "production" (PostgreSQL) or "local" (MySQL)
ENVIRONMENT = os.getenv("ENVIRONMENT", "local").lower()

# Load environment-specific overrides
if ENVIRONMENT == "production":
    load_dotenv(".env.production", override=True)
else:
    load_dotenv(".env.local", override=True)

# -------------------------
# Helper functions
# -------------------------
def safe_float(value, default):
    try:
        return float(value)
    except (ValueError, TypeError):
        return float(default)

def safe_int(value, default):
    try:
        return int(value)
    except (ValueError, TypeError):
        return int(default)

def safe_bool(value, default=False):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in ("true", "1", "yes", "y")
    return bool(default)

# -------------------------
# Database Configuration
# -------------------------
DB_ENGINE = os.getenv('DB_ENGINE', 'mysql').lower()
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')

# Set default ports if not provided
DB_PORT = safe_int(DB_PORT, 3306 if DB_ENGINE == 'mysql' else 5432)

# Connection dictionaries for direct use in get_db_connection()
PROD_DB = {
    "dbengine": DB_ENGINE,
    "port": DB_PORT,
    "host": DB_HOST,
    "user": DB_USER,
    "password": DB_PASSWORD,
    "dbname": DB_NAME,
  
}

LOCAL_DB = {
    "host": DB_HOST,
    "user": DB_USER,
    "password": DB_PASSWORD,
    "database": DB_NAME,
    "port": DB_PORT
}



# -------------------------
# Hugging Face API
# -------------------------
HF_API_URL = "https://api-inference.huggingface.co/models/distilbert/distilbert-base-uncased-finetuned-sst-2-english"
HF_API_TOKEN = os.getenv('H_F', '')

# -------------------------
# App Defaults
# -------------------------
DEFAULT_SESSION_PRICE = safe_float(os.getenv('DEFAULT_SESSION_PRICE', '10.00'), 10.00)
DEFAULT_CURRENCY = os.getenv('DEFAULT_CURRENCY', 'KES')
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_hex(32))

# -------------------------
# IntaSend configuration
# -------------------------
INTASEND_PUBLIC_KEY = os.getenv('INTASEND_PUBLIC_KEY')
INTASEND_SECRET_KEY = os.getenv('INTASEND_SECRET_KEY')
INTASEND_TEST_MODE = safe_bool(os.getenv("INTASEND_TEST_MODE", "True"), True)
INTASEND_PRODUCTION_MODE = safe_bool(os.getenv("INTASEND_PRODUCTION_MODE", "False"), False)

# -------------------------
# Email configuration
# -------------------------
MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
MAIL_PORT = safe_int(os.getenv('MAIL_PORT', '587'), 587)
MAIL_USE_TLS = safe_bool(os.getenv('MAIL_USE_TLS', 'True'), True)
MAIL_USERNAME = os.getenv('MAIL_USERNAME', '')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '')
MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', '')

# -------------------------
# Connection string helper
# -------------------------
def get_db_uri():
    """Return database URI for SQLAlchemy or direct connections."""
    if DB_ENGINE == 'mysql':
        return f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    elif DB_ENGINE == 'postgresql':
        return f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    else:
        raise ValueError("Unsupported DB_ENGINE. Use 'mysql' or 'postgresql'.")
