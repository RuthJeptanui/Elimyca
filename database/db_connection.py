import mysql.connector
import psycopg2
import logging

logger = logging.getLogger(__name__)

def get_db_connection():
    from config import Config
    try:
        if Config.DB_ENGINE == 'postgresql':
            conn = psycopg2.connect(
                dbengine=Config.DB_ENGINE,
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
                port=Config.DB_PORT  # Explicit port
            )
            if conn.is_connected():
                logger.debug("✅ MySQL database connection successful!")
                return conn
    except Exception as e:
        logger.error(f"❌ Database connection failed ({Config.DB_ENGINE}): {e}")
        return None

def execute_query(query, params=None, fetch=False):
    conn = get_db_connection()
    if not conn:
        return None

    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params or ())

            if fetch and query.strip().upper().startswith('SELECT'):
                columns = [desc[0] for desc in cursor.description] if cursor.description else []
                rows = cursor.fetchall()
                return [dict(zip(columns, row)) for row in rows]

            conn.commit()

            if query.strip().upper().startswith('INSERT'):
                if hasattr(cursor, 'lastrowid') and cursor.lastrowid:
                    return cursor.lastrowid  # MySQL
                elif conn.__class__.__module__.startswith('psycopg2'):
                    cursor.execute("SELECT LASTVAL()")
                    return cursor.fetchone()[0]
            return True

    except Exception as e:
        logger.error(f"❌ Query execution failed: {e}")
        conn.rollback()
        return None
    finally:
        conn.close()
