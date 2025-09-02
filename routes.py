from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from flask_mail import Mail, Message
import mysql.connector
import requests
import config
from intasend import APIService
import logging
from mysql.connector import Error
import json
import re
from difflib import SequenceMatcher

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create blueprint
main_bp = Blueprint('main', __name__)

# Initialize Flask-Mail
mail = Mail()

# Hugging Face API Configuration
HF_API_URL = "https://api-inference.huggingface.co/models/distilbert/distilbert-base-uncased-finetuned-sst-2-english"
HF_KEYPHRASE_URL = "https://api-inference.huggingface.co/models/ml6team/keyphrase-extraction-kbir-inspec"

# IntaSend service
intasend = APIService(
    token=config.INTASEND_SECRET_KEY, 
    publishable_key=config.INTASEND_PUBLIC_KEY, 
    test=config.INTASEND_TEST_MODE
)

# Subject keywords for matching and suggestions
SUBJECT_KEYWORDS = {
    'mathematics': ['math', 'mathematics', 'algebra', 'geometry', 'calculus', 'statistics', 'trigonometry', 'arithmetic'],
    'science': ['science', 'physics', 'chemistry', 'biology', 'astronomy', 'geology', 'environmental'],
    'english': ['english', 'literature', 'writing', 'grammar', 'reading', 'composition', 'essay'],
    'programming': ['programming', 'coding', 'python', 'javascript', 'java', 'html', 'css', 'web development'],
    'history': ['history', 'social studies', 'geography', 'civics', 'government', 'politics'],
    'languages': ['kiswahili', 'spanish', 'french', 'german', 'chinese', 'japanese', 'italian', 'portuguese'],
    'arts': ['art', 'music', 'drawing', 'painting', 'design', 'photography', 'theater']
}

# Database connection
import config
import psycopg2
import mysql.connector
from mysql.connector import Error as MySQLError
from psycopg2 import OperationalError as PGError
from psycopg2.extras import RealDictCursor

def get_db_connection():
    try:
        if config.ENVIRONMENT == "production":  # PostgreSQL
            conn = psycopg2.connect(
                host=config.PROD_DB["host"],
                user=config.PROD_DB["user"],
                password=config.PROD_DB["password"],
                dbname=config.PROD_DB["dbname"]
            )
        else:  # MySQL
            conn = mysql.connector.connect(
                host=config.LOCAL_DB["host"],
                user=config.LOCAL_DB["user"],
                password=config.LOCAL_DB["password"],
                database=config.LOCAL_DB["database"]
            )
        return conn
    except (MySQLError, PGError) as e:
        logger.error(f"❌ Database connection failed: {e}")
        return None

def get_cursor(conn, dict_mode=False):
    if config.ENVIRONMENT == "production":
        return conn.cursor(cursor_factory=RealDictCursor) if dict_mode else conn.cursor()
    else:
        return conn.cursor(dictionary=dict_mode)
    

#helper functions for inserting students and updating payment statuses so we don’t repeat DB‑specific quirks:
def insert_student(conn, name, needs_description, sentiment_score, tutor_id, email, phone_number, subject_tags):
    cur = get_cursor(conn)
    if config.ENVIRONMENT == "production":
        cur.execute("""
            INSERT INTO students (name, needs_description, sentiment, matched_tutor_id, payment_status, email, phone_number, subject_tags)
            VALUES (%s, %s, %s, %s, 'PENDING', %s, %s, %s)
            RETURNING id;
        """, (name, needs_description, str(sentiment_score), tutor_id, email, phone_number, subject_tags))
        student_id = cur.fetchone()['id']
    else:
        cur.execute("""
            INSERT INTO students (name, needs_description, sentiment, matched_tutor_id, payment_status, email, phone_number, subject_tags)
            VALUES (%s, %s, %s, %s, 'PENDING', %s, %s, %s)
        """, (name, needs_description, str(sentiment_score), tutor_id, email, phone_number, subject_tags))
        student_id = cur.lastrowid
    conn.commit()
    cur.close()
    return student_id

def update_payment_status(conn, table, entity_id, status):
    cur = get_cursor(conn)
    cur.execute(f"UPDATE {table} SET payment_status = %s WHERE id = %s", (status, entity_id))
    conn.commit()
    cur.close()




# Enhanced sentiment analysis with Hugging Face
def get_sentiment(text):
    headers = {"Authorization": f"Bearer {config.HF_API_TOKEN}"} if hasattr(config, 'HF_API_TOKEN') and config.HF_API_TOKEN else {}
    payload = {"inputs": text}
    try:
        response = requests.post(HF_API_URL, headers=headers, json=payload)
        if response.status_code == 200:
            result = response.json()[0]
            # Return sentiment score (higher = more negative/urgent)
            return result['score'] if result['label'] == 'NEGATIVE' else 0.0
        else:
            logger.warning(f"HF API returned status {response.status_code}: {response.text}")
    except Exception as e:
        logger.error(f"Sentiment analysis error: {e}")
    return 0.0  # Default neutral sentiment

# AI-powered subject detection and keyword extraction
def extract_subjects_and_keywords(text):
    text_lower = text.lower()
    detected_subjects = []
    keywords = []
    
    for subject, subject_keywords in SUBJECT_KEYWORDS.items():
        for keyword in subject_keywords:
            if keyword in text_lower:
                if subject not in detected_subjects:
                    detected_subjects.append(subject)
                keywords.append(keyword)
    
    return detected_subjects, keywords

# Smart subject suggestions API endpoint
@main_bp.route('/api/suggest_subjects', methods=['POST'])
def suggest_subjects():
    data = request.get_json()
    text = data.get('text', '').lower()
    
    suggestions = []
    for subject, keywords in SUBJECT_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text and subject not in suggestions:
                suggestions.append(subject.title())
                break
    
    # Add partial matches
    for subject, keywords in SUBJECT_KEYWORDS.items():
        if subject.title() not in suggestions:
            for keyword in keywords:
                if any(word in keyword for word in text.split()) or any(word in text for word in keyword.split()):
                    suggestions.append(subject.title())
                    break
    
    return jsonify({'suggestions': suggestions[:5]})  # Return top 5 suggestions

# Routes
@main_bp.route('/')
def index():
    return render_template('index.html')


@main_bp.route('/tutor_register', methods=['GET', 'POST'])
def tutor_register():
    if request.method == 'POST':
        name = request.form['name']
        expertise = request.form['expertise']
        availability = request.form['availability']  # keep as string to match schema
        email = request.form['email']
        phone_number = request.form['phone_number']

        # Extract and store subject tags for better matching
        subjects, _ = extract_subjects_and_keywords(expertise)
        subject_tags = ','.join(subjects)

        conn = get_db_connection()
        if not conn:
            flash("Database connection failed", "error")
            return render_template('tutor_register.html')

        try:
            cursor = get_cursor(conn)

            if config.ENVIRONMENT == "production":  # PostgreSQL
                cursor.execute("""
                    INSERT INTO tutors (name, expertise, availability, payment_status, email, phone_number, subject_tags)
                    VALUES (%s, %s, %s, 'PENDING', %s, %s, %s)
                    RETURNING id;
                """, (name, expertise, availability, email, phone_number, subject_tags))
                tutor_id = cursor.fetchone()[0]
            else:  # MySQL
                cursor.execute("""
                    INSERT INTO tutors (name, expertise, availability, payment_status, email, phone_number, subject_tags)
                    VALUES (%s, %s, %s, 'PENDING', %s, %s, %s)
                """, (name, expertise, availability, email, phone_number, subject_tags))
                tutor_id = cursor.lastrowid

            conn.commit()

            # IntaSend checkout for tutor monthly payment
            try:
                response = intasend.collect.checkout(
                    phone_number=phone_number,
                    email=email,
                    amount=10.00,
                    currency='KES',
                    comment=f"Tutor Monthly Payment for ID {tutor_id}"
                )

                logger.debug(f"IntaSend tutor response: {response}")

                # Extract invoice_id and redirect_url
                if 'invoice' in response:
                    invoice = response['invoice']
                    invoice_id = invoice.get('invoice_id') or invoice.get('id')
                    redirect_url = invoice.get('url')
                else:
                    invoice_id = response.get('invoice_id') or response.get('id')
                    redirect_url = response.get('url') or response.get('redirect_url')

                if not invoice_id or not redirect_url:
                    logger.error(f"Missing invoice_id or URL in IntaSend response: {response}")
                    flash("Payment service error: Could not process payment", "error")
                    return render_template('tutor_register.html')

                # Store payment session data
                session.update({
                    'payment_type': 'tutor',
                    'entity_id': tutor_id,
                    'invoice_id': invoice_id
                })

                logger.debug(f"Redirecting tutor to IntaSend URL: {redirect_url}")
                return redirect(redirect_url)

            except Exception as e:
                logger.error(f"Tutor Payment Error: {str(e)}")
                flash(f"Payment Error: {str(e)}", "error")
                return render_template('tutor_register.html')

        except Exception as e:
            logger.error(f"Database Error in tutor registration: {str(e)}")
            flash(f"Database Error: {str(e)}", "error")
            return render_template('tutor_register.html')

        finally:
            cursor.close()
            conn.close()

    return render_template('tutor_register.html')

@main_bp.route('/student_form', methods=['GET', 'POST'])
def student_form():
    if request.method == 'POST':
        name = request.form.get('name')
        needs_description = request.form.get('needs_description')
        email = request.form.get('email')
        phone_number = request.form.get('phone_number')

        # AI analysis
        sentiment_score = get_sentiment(needs_description)
        subjects, keywords = extract_subjects_and_keywords(needs_description)
        subject_tags = ','.join(subjects)

        # Fallback keyword extraction
        fallback_keywords = [
            word.lower() for word in needs_description.split()
            if word.lower() in ['math', 'science', 'english', 'programming', 'history', 'physics', 'chemistry', 'biology']
        ]
        if not keywords:
            keywords = fallback_keywords

        conn = get_db_connection()
        if not conn:
            flash("Database connection failed", "error")
            return render_template('student_form.html')

        try:
            cursor = get_cursor(conn, dict_mode=True)

            # Decide ordering based on sentiment
            order_by = "ORDER BY current_load ASC" if sentiment_score > 0.5 else "ORDER BY current_load DESC"

            # Base query — use string match for payment_status
            query = "SELECT * FROM tutors WHERE current_load < availability AND payment_status = 'PAID'"

            # Add keyword filtering if present
            if keywords:
                like_op = "ILIKE" if config.ENVIRONMENT == "production" else "LIKE"
                like_conditions = " OR ".join([f"expertise {like_op} %s" for _ in keywords])
                query += f" AND ({like_conditions})"
                search_params = [f"%{kw}%" for kw in keywords]
                cursor.execute(query + f" {order_by} LIMIT 1", search_params)
            else:
                cursor.execute(query + f" {order_by} LIMIT 1")

            tutor = cursor.fetchone()

            if tutor:
                # Insert student in a DB‑agnostic way
                if config.ENVIRONMENT == "production":
                    cursor.execute("""
                        INSERT INTO students (name, needs_description, sentiment, matched_tutor_id, payment_status, email, phone_number, subject_tags)
                        VALUES (%s, %s, %s, %s, 'PENDING', %s, %s, %s)
                        RETURNING id;
                    """, (name, needs_description, str(sentiment_score), tutor['id'], email, phone_number, subject_tags))
                    student_id = cursor.fetchone()['id']
                else:
                    cursor.execute("""
                        INSERT INTO students (name, needs_description, sentiment, matched_tutor_id, payment_status, email, phone_number, subject_tags)
                        VALUES (%s, %s, %s, %s, 'PENDING', %s, %s, %s)
                    """, (name, needs_description, str(sentiment_score), tutor['id'], email, phone_number, subject_tags))
                    student_id = cursor.lastrowid

                conn.commit()

                # Store in session for payment callback
                session.update({
                    'student_id': student_id,
                    'tutor_id': tutor['id'],
                    'student_email': email,
                    'student_phone': phone_number
                })

                return redirect(url_for('main.payment', student_id=student_id, tutor_id=tutor['id']))
            else:
                flash("No available tutors found. Please try again later.", "error")

        except Exception as e:
            logger.error(f"Database Error in student_form: {e}")
            flash(f"Database Error: {str(e)}", "error")
        finally:
            cursor.close()
            conn.close()

    return render_template('student_form.html')


@main_bp.route('/payment/<int:student_id>/<int:tutor_id>')
def payment(student_id, tutor_id):
    conn = get_db_connection()
    if not conn:
        flash("Database connection failed", "error")
        return redirect(url_for('main.index'))

    try:
        cursor = get_cursor(conn, dict_mode=True)

        # Get student details
        cursor.execute("SELECT * FROM students WHERE id = %s", (student_id,))
        student = cursor.fetchone()

        # Get tutor details
        cursor.execute("SELECT * FROM tutors WHERE id = %s", (tutor_id,))
        tutor = cursor.fetchone()

        if not student or not tutor:
            flash("Invalid student or tutor ID", "error")
            return redirect(url_for('main.index'))

        return render_template('payment.html', student=student, tutor=tutor)

    except Exception as e:
        logger.error(f"Database Error in payment(): {e}")
        flash(f"Database Error: {str(e)}", "error")
        return redirect(url_for('main.index'))
    finally:
        cursor.close()
        conn.close()


@main_bp.route('/process_payment', methods=['POST'])
def process_payment():
    student_id = request.form['student_id']
    tutor_id = request.form['tutor_id']
    phone_number = request.form['phone_number']
    email = request.form['email']

    conn = get_db_connection()
    if not conn:
        flash("Database connection failed", "error")
        return redirect(url_for('main.payment', student_id=student_id, tutor_id=tutor_id))

    try:
        cursor = get_cursor(conn, dict_mode=True)

        # Validate student and tutor exist
        cursor.execute("SELECT * FROM students WHERE id = %s", (student_id,))
        student = cursor.fetchone()
        cursor.execute("SELECT * FROM tutors WHERE id = %s", (tutor_id,))
        tutor = cursor.fetchone()

        if not student or not tutor:
            flash("Invalid student or tutor ID", "error")
            return redirect(url_for('main.index'))

        # IntaSend checkout
        try:
            logger.debug(f"Creating IntaSend checkout for student {student_id}, tutor {tutor_id}")
            response = intasend.collect.checkout(
                phone_number=phone_number,
                email=email,
                amount=config.DEFAULT_SESSION_PRICE,
                currency=config.DEFAULT_CURRENCY,
                comment=f"Student Session Payment for Tutor {tutor_id}"
            )
            logger.debug(f"IntaSend response: {response}")

            # Extract invoice_id
            invoice_id = None
            if 'invoice' in response and isinstance(response['invoice'], dict):
                invoice_id = response['invoice'].get('invoice_id') or response['invoice'].get('id')
                redirect_url = response['invoice'].get('url')
            else:
                invoice_id = response.get('invoice_id') or response.get('id')
                redirect_url = (
                    response.get('url') or
                    response.get('redirect_url') or
                    response.get('checkout_url') or
                    response.get('invoice_url')
                )

            if invoice_id and redirect_url:
                session.update({
                    'payment_type': 'student',
                    'entity_id': student_id,
                    'tutor_id': tutor_id,
                    'invoice_id': invoice_id
                })
                logger.debug(f"Redirecting to IntaSend URL: {redirect_url}")
                return redirect(redirect_url)
            else:
                logger.error(f"Missing invoice_id or redirect_url in IntaSend response: {response}")
                flash("Payment service error: Invalid response from payment provider", "error")
                return redirect(url_for('main.payment', student_id=student_id, tutor_id=tutor_id))

        except Exception as e:
            logger.error(f"IntaSend Error: {str(e)}")
            flash(f"Payment Error: {str(e)}", "error")
            return redirect(url_for('main.payment', student_id=student_id, tutor_id=tutor_id))

    except Exception as e:
        logger.error(f"Database Error in process_payment(): {e}")
        flash(f"Database Error: {str(e)}", "error")
        return redirect(url_for('main.payment', student_id=student_id, tutor_id=tutor_id))
    finally:
        cursor.close()
        conn.close()


@main_bp.route('/payment_callback')
def payment_callback():
    invoice_id = session.get('invoice_id')
    if not invoice_id:
        flash("Invalid payment callback", "error")
        return redirect(url_for('main.index'))

    try:
        status_response = intasend.collect.status(invoice_id)
        payment_successful = (
            status_response.get('state') == 'COMPLETE'
            or status_response.get('code') == 'TS100'
        )

        payment_type = session.get('payment_type')
        entity_id = session.get('entity_id')

        conn = get_db_connection()
        if not conn:
            flash("Database connection failed", "error")
            return redirect(url_for('main.index'))

        try:
            cursor = get_cursor(conn, dict_mode=True)

            if payment_successful:
                if payment_type == 'tutor':
                    cursor.execute(
                        "UPDATE tutors SET payment_status = 'PAID' WHERE id = %s",
                        (entity_id,)
                    )
                    conn.commit()
                    flash("Tutor registration payment successful!", "success")
                    return redirect(url_for('main.index'))

                elif payment_type == 'student':
                    tutor_id = session.get('tutor_id')

                    # Update student payment status
                    cursor.execute(
                        "UPDATE students SET payment_status = 'PAID' WHERE id = %s",
                        (entity_id,)
                    )

                    # Increment tutor load
                    cursor.execute(
                        "UPDATE tutors SET current_load = current_load + 1 WHERE id = %s",
                        (tutor_id,)
                    )

                    # Insert payment record
                    amount = status_response.get('amount', config.DEFAULT_SESSION_PRICE)
                    currency = status_response.get('currency', config.DEFAULT_CURRENCY)
                    phone_number = session.get('student_phone')
                    email = session.get('student_email')
                    status_db = 'COMPLETED'
                    api_ref = status_response.get('api_ref', f"student_{entity_id}")

                    cursor.execute("""
                        INSERT INTO payments (
                            student_id, tutor_id, amount, currency, phone_number, email,
                            intasend_invoice_id, status, api_ref
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        entity_id, tutor_id, amount, currency, phone_number, email,
                        invoice_id, status_db, api_ref
                    ))
                    conn.commit()

                    # Fetch tutor info for results page
                    cursor.execute("SELECT * FROM tutors WHERE id = %s", (tutor_id,))
                    tutor = cursor.fetchone()

                    # Fetch all tutors for stats
                    cursor.execute("SELECT name, current_load, availability FROM tutors")
                    all_tutors = cursor.fetchall()

                    # Clear session
                    for key in [
                        'payment_type', 'entity_id', 'tutor_id', 'invoice_id',
                        'student_phone', 'student_email'
                    ]:
                        session.pop(key, None)

                    return render_template(
                        'match_results.html',
                        tutor=tutor,
                        student_id=entity_id,
                        tutors_data=all_tutors
                    )

            else:
                # Payment failed
                if payment_type == 'student':
                    cursor.execute(
                        "UPDATE students SET payment_status = 'FAILED' WHERE id = %s",
                        (entity_id,)
                    )
                    conn.commit()

                # Clear session
                for key in [
                    'payment_type', 'entity_id', 'tutor_id', 'invoice_id',
                    'student_phone', 'student_email'
                ]:
                    session.pop(key, None)

                return render_template(
                    'payment_failed.html',
                    reason=status_response.get('failed_reason', 'Unknown error')
                )

        except Exception as e:
            logger.error(f"Database Error in payment_callback: {e}")
            flash(f"Database Error: {str(e)}", "error")
            return redirect(url_for('main.index'))
        finally:
            cursor.close()
            conn.close()

    except Exception as e:
        logger.error(f"Payment callback error: {e}")
        flash(f"Payment callback error: {str(e)}", "error")
        return redirect(url_for('main.index'))


@main_bp.route('/payment_success')
def payment_success():
    return render_template('payment_success.html')

