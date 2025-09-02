# config.py
import os
import secrets
from dotenv import load_dotenv

# Load .env file
load_dotenv()


# Database configuration (update with your MySQL details)
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME') 



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
 

# Hugging Face API (for sentiment analysis)
HF_API_URL="https://api-inference.huggingface.co/models/distilbert/distilbert-base-uncased-finetuned-sst-2-english"  
HF_API_TOKEN=os.getenv('HF_API_TOKEN', '')  


#Tip: Don't commit passwords to git! Use environment variables for real projects. For now, hardcode if testing locally.

DEFAULT_SESSION_PRICE = safe_float(os.getenv('DEFAULT_SESSION_PRICE', '10.00'), '10.00') 
DEFAULT_CURRENCY=os.getenv('DEFAULT_CURRENCY', 'KES')

SECRET_KEY=os.getenv("SECRET_KEY", secrets.token_hex(32))  

INTASEND_PUBLIC_KEY=os.getenv('INTASEND_PUBLIC_KEY')  
INTASEND_SECRET_KEY=os.getenv('INTASEND_SECRET_KEY')
INTASEND_TEST_MODE=os.getenv("INTASEND_TEST_MODE", "True").lower() == "true"
INTASEND_PRODUCTION_MODE=os.getenv("INTASEND_PRODUCTION_MODE", "False").lower() == "true"

# Email configuration
MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
MAIL_PORT = safe_int(os.getenv('MAIL_PORT', '587'), '587')
MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True') == 'True'
MAIL_USERNAME = os.getenv('MAIL_USERNAME', '')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '')
MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', '')
