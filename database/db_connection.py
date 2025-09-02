import mysql.connector
import psycopg2
import logging
import os

logger = logging.getLogger(__name__)

def get_db_connection():
    from config import Config
    try:
        if Config.DB_ENGINE == 'postgresql':
            if Config.DATABASE_URL:
                # Use DATABASE_URL directly (recommended on Render)
                conn = psycopg2.connect(Config.DATABASE_URL)
            else:
                conn = psycopg2.connect(
                    host=Config.DB_HOST,
                    user=Config.DB_USER,
                    password=Config.DB_PASSWORD,
                    dbname=Config.DB_NAME,
                    port=Config.DB_PORT
                )
            logger.debug("✅ PostgreSQL database connection successful!")
            return conn
        else:
            conn = mysql.connector.connect(
                host=Config.DB_HOST,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                database=Config.DB_NAME,
                port=Config.DB_PORT
            )
            if conn.is_connected():
                logger.debug("✅ MySQL database connection successful!")
                return conn
    except Exception as e:
        logger.error(f"❌ Database connection failed ({Config.DB_ENGINE}): {e}")
        return None
