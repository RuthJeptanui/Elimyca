import mysql.connector
from mysql.connector import Error
import psycopg2
import logging

logger = logging.getLogger(__name__)

def get_db_connection():
    from config import Config
    
    try:
        if Config.DB_ENGINE == 'postgresql':
            # PostgreSQL connection
            conn = psycopg2.connect(
                host=Config.DB_HOST,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                database=Config.DB_NAME,
                port=Config.DB_PORT
            )
            logger.debug("✅ PostgreSQL database connection successful!")
            return conn
        else:
            # MySQL connection
            conn = mysql.connector.connect(
                host=Config.DB_HOST,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                database=Config.DB_NAME
            )
            if conn.is_connected():
                logger.debug("✅ MySQL database connection successful!")
                return conn
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return None

def execute_query(query, params=None, fetch=False):
    """
    Universal query execution function that works with both MySQL and PostgreSQL
    """
    conn = get_db_connection()
    if not conn:
        return None
        
    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
            
        if fetch:
            if query.strip().upper().startswith('SELECT'):
                result = cursor.fetchall()
                
                # Get column names for both databases
                if hasattr(cursor, 'description') and cursor.description:
                    columns = [desc[0] for desc in cursor.description]
                    # Convert to list of dictionaries for consistency
                    result = [dict(zip(columns, row)) for row in result]
                return result
            return None
        else:
            conn.commit()
            if query.strip().upper().startswith('INSERT'):
                # Handle lastrowid for both databases
                if hasattr(cursor, 'lastrowid'):
                    return cursor.lastrowid  # MySQL
                else:
                    # For PostgreSQL, we need to return the last inserted ID differently
                    cursor.execute("SELECT LASTVAL()")
                    return cursor.fetchone()[0]
            return True
            
    except Exception as e:
        logger.error(f"❌ Query execution failed: {e}")
        conn.rollback()
        return None
    finally:
        cursor.close()
        conn.close()