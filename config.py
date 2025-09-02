# config.py
import os
import secrets
from dotenv import load_dotenv

# Load .env file
load_dotenv()


# Database configuration (update with your MySQL details)
DB_HOST='localhost'
DB_USER='jeptanui@gmail.com'  
DB_PASSWORD='Tech@1234!'  
DB_NAME='elimyca_db'  
 

# Hugging Face API (for sentiment analysis)
HF_API_URL="https://api-inference.huggingface.co/models/distilbert/distilbert-base-uncased-finetuned-sst-2-english"  # Free sentiment model
HF_API_TOKEN=os.getenv('HF_API_TOKEN', '')  


#Tip: Don't commit passwords to git! Use environment variables for real projects. For now, hardcode if testing locally.

DEFAULT_SESSION_PRICE=float(os.getenv('DEFAULT_SESSION_PRICE'))  
DEFAULT_CURRENCY=os.getenv('DEFAULT_CURRENCY', 'KES')

SECRET_KEY=os.getenv("SECRET_KEY", secrets.token_hex(32))  # For session management

INTASEND_PUBLIC_KEY=os.getenv('INTASEND_PUBLIC_KEY')  
INTASEND_SECRET_KEY=os.getenv('INTASEND_SECRET_KEY')
# INTASEND_TEST_MODE = True  # Sandbox for testing
INTASEND_TEST_MODE=os.getenv("INTASEND_TEST_MODE", "True").lower() == "true"

# Email configuration
MAIL_SERVER=os.getenv("MAIL_SERVER")
MAIL_PORT=int(os.getenv("MAIL_PORT", 587))
MAIL_USE_TLS=os.getenv("MAIL_USE_TLS", "True").lower() == "true"
MAIL_USERNAME=os.getenv("MAIL_USERNAME")
MAIL_PASSWORD=os.getenv("MAIL_PASSWORD")

