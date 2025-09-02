# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
import requests
import config
from intasend import APIService
import logging
from mysql.connector import Error

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

# IntaSend service
intasend = APIService(
    token=config.INTASEND_SECRET_KEY, 
    publishable_key=config.INTASEND_PUBLIC_KEY, 
    test=config.INTASEND_TEST_MODE
)

# Database connection
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=config.DB_HOST,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            database=config.DB_NAME
        )
        if conn.is_connected():
            logger.debug("✅ Database connection successful!")
            return conn
    except Error as e:
        logger.error(f"❌ Database connection failed: {e}")
        return None

# Sentiment analysis
def get_sentiment(text):
    headers = {"Authorization": f"Bearer {config.HF_API_TOKEN}"} if config.HF_API_TOKEN else {}
    payload = {"inputs": text}
    try:
        response = requests.post(config.HF_API_URL, headers=headers, json=payload)
        if response.status_code == 200:
            result = response.json()[0]
            return result['score'] if result['label'] == 'NEGATIVE' else 0.0
    except Exception as e:
        logger.error(f"Sentiment analysis error: {e}")
    return 0.0

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/student_dashboard')
def dashboard():
    return render_template('dashboard.html')



@app.route('/tutor_register', methods=['GET', 'POST'])
def tutor_register():
    if request.method == 'POST':
        name = request.form['name']
        expertise = request.form['expertise']
        availability = int(request.form['availability'])
        email = request.form['email']
        phone_number = request.form['phone_number']
        
        conn = get_db_connection()
        if not conn:
            flash("Database connection failed", "error")
            return render_template('tutor_register.html')
            
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO tutors (name, expertise, availability, payment_status, email, phone_number) VALUES (%s, %s, %s, %s, %s, %s)",
                (name, expertise, availability, False, email, phone_number)
            )
            tutor_id = cursor.lastrowid
            conn.commit()
            
            # IntaSend checkout for tutor monthly payment
            try:
                response = intasend.collect.checkout(
                    phone_number=phone_number,
                    email=email,
                    amount=1000.00,
                    currency='KES',
                    comment=f"Tutor Monthly Payment for ID {tutor_id}"
                )
                
                # DEBUG: Log the IntaSend response
                logger.debug(f"IntaSend tutor response: {response}")
                
                # Extract invoice_id from different possible response structures
                invoice_id = None
                if 'invoice_id' in response:
                    invoice_id = response['invoice_id']
                elif 'id' in response:
                    invoice_id = response['id']
                elif 'invoice' in response and 'invoice_id' in response['invoice']:
                    invoice_id = response['invoice']['invoice_id']
                
                if not invoice_id:
                    logger.error(f"No invoice_id found in IntaSend response: {response}")
                    flash("Payment service error: Could not process payment", "error")
                    return render_template('tutor_register.html')
                
                session['payment_type'] = 'tutor'
                session['entity_id'] = tutor_id
                session['invoice_id'] = invoice_id
                
                # Extract redirect URL
                redirect_url = None
                if 'url' in response:
                    redirect_url = response['url']
                elif 'redirect_url' in response:
                    redirect_url = response['redirect_url']
                elif 'invoice' in response and 'url' in response['invoice']:
                    redirect_url = response['invoice']['url']
                
                if redirect_url:
                    logger.debug(f"Redirecting tutor to IntaSend URL: {redirect_url}")
                    return redirect(redirect_url)
                else:
                    logger.error(f"No redirect URL found in IntaSend response: {response}")
                    flash("Payment service error: Could not redirect to payment", "error")
                    return render_template('tutor_register.html')
                    
            except Exception as e:
                logger.error(f"Tutor Payment Error: {str(e)}")
                flash(f"Payment Error: {str(e)}", "error")
                return render_template('tutor_register.html')
                
        except Error as e:
            logger.error(f"Database Error in tutor registration: {str(e)}")
            flash(f"Database Error: {str(e)}", "error")
            return render_template('tutor_register.html')
        finally:
            cursor.close()
            conn.close()
    
    return render_template('tutor_register.html')
    if request.method == 'POST':
        name = request.form['name']
        expertise = request.form['expertise']
        availability = int(request.form['availability'])
        email = request.form['email']
        phone_number = request.form['phone_number']
        
        conn = get_db_connection()
        if not conn:
            flash("Database connection failed", "error")
            return render_template('tutor_register.html')
            
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO tutors (name, expertise, availability, payment_status, email, phone_number) VALUES (%s, %s, %s, %s, %s, %s)",
                (name, expertise, availability, False, email, phone_number)
            )
            tutor_id = cursor.lastrowid
            conn.commit()
            
            # IntaSend checkout for tutor monthly payment
            try:
                response = intasend.collect.checkout(
                    phone_number=phone_number,
                    email=email,
                    amount=1000.00,
                    currency='KES',
                    comment=f"Tutor Monthly Payment for ID {tutor_id}"
                )
                session['payment_type'] = 'tutor'
                session['entity_id'] = tutor_id
                session['invoice_id'] = response['invoice_id']
                return redirect(response['url'])
            except Exception as e:
                flash(f"Payment Error: {str(e)}", "error")
                return render_template('tutor_register.html')
                
        except Error as e:
            flash(f"Database Error: {str(e)}", "error")
            return render_template('tutor_register.html')
        finally:
            cursor.close()
            conn.close()
    
    return render_template('tutor_register.html')

@app.route('/student_form', methods=['GET', 'POST'])
def student_form():
    if request.method == 'POST':
        name = request.form.get('name')
        needs_description = request.form.get('needs_description')
        email = request.form.get('email')
        phone_number = request.form.get('phone_number')
        
        sentiment_score = get_sentiment(needs_description)
        keywords = [word.lower() for word in needs_description.split() 
                   if word.lower() in ['math', 'science', 'english', 'programming', 'history', 'physics', 'chemistry', 'biology']]
        
        conn = get_db_connection()
        if not conn:
            flash("Database connection failed", "error")
            return render_template('student_form.html')
            
        try:
            cursor = conn.cursor(dictionary=True)
            
            query = "SELECT * FROM tutors WHERE current_load < availability AND payment_status = 1"
            if keywords:
                like_clauses = " OR ".join([f"expertise LIKE '%{kw}%'" for kw in keywords])
                query += f" AND ({like_clauses})"
            
            order_by = "ORDER BY current_load ASC" if sentiment_score > 0.5 else "ORDER BY current_load DESC"
            cursor.execute(query + " " + order_by + " LIMIT 1")
            tutor = cursor.fetchone()
            
            if tutor:
                # Insert student with PENDING status
                cursor.execute(
                    "INSERT INTO students (name, needs_description, sentiment_score, matched_tutor_id, payment_status, email, phone_number) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (name, needs_description, sentiment_score, tutor['id'], 'PENDING', email, phone_number)
                )
                student_id = cursor.lastrowid
                conn.commit()
                
                # Store in session for payment callback
                session['student_id'] = student_id
                session['tutor_id'] = tutor['id']
                session['student_email'] = email
                session['student_phone'] = phone_number
                
                # Redirect to payment page instead of directly to IntaSend
                return redirect(url_for('payment', student_id=student_id, tutor_id=tutor['id']))
            else:
                flash("No available tutors found. Please try again later.", "error")
                return render_template('student_form.html')
                
        except Error as e:
            flash(f"Database Error: {str(e)}", "error")
            return render_template('student_form.html')
        finally:
            cursor.close()
            conn.close()
    
    return render_template('student_form.html')

@app.route('/payment/<int:student_id>/<int:tutor_id>')
def payment(student_id, tutor_id):
    conn = get_db_connection()
    if not conn:
        flash("Database connection failed", "error")
        return redirect(url_for('index'))
        
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Get student details
        cursor.execute("SELECT * FROM students WHERE id = %s", (student_id,))
        student = cursor.fetchone()
        
        # Get tutor details
        cursor.execute("SELECT * FROM tutors WHERE id = %s", (tutor_id,))
        tutor = cursor.fetchone()
        
        if not student or not tutor:
            flash("Invalid student or tutor ID", "error")
            return redirect(url_for('index'))
            
        return render_template('payment.html', student=student, tutor=tutor)
        
    except Error as e:
        flash(f"Database Error: {str(e)}", "error")
        return redirect(url_for('index'))
    finally:
        cursor.close()
        conn.close()

@app.route('/process_payment', methods=['POST'])
def process_payment():
    student_id = request.form['student_id']
    tutor_id = request.form['tutor_id']
    phone_number = request.form['phone_number']
    email = request.form['email']
    
    # Get student and tutor info from DB
    conn = get_db_connection()
    if not conn:
        flash("Database connection failed", "error")
        return redirect(url_for('payment', student_id=student_id, tutor_id=tutor_id))
        
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM students WHERE id = %s", (student_id,))
        student = cursor.fetchone()
        
        cursor.execute("SELECT * FROM tutors WHERE id = %s", (tutor_id,))
        tutor = cursor.fetchone()
        
        if not student or not tutor:
            flash("Invalid student or tutor ID", "error")
            return redirect(url_for('index'))
            
        # IntaSend checkout for student session
        try:
            logger.debug(f"Creating IntaSend checkout for student {student_id}, tutor {tutor_id}")
            response = intasend.collect.checkout(
                phone_number=phone_number,
                email=email,
                amount=config.DEFAULT_SESSION_PRICE,
                currency=config.DEFAULT_CURRENCY,
                comment=f"Student Session Payment for Tutor {tutor_id}"
            )
            
            # DEBUG: Log the entire response
            logger.debug(f"IntaSend response type: {type(response)}")
            logger.debug(f"IntaSend response content: {response}")
            
            # Check if response is a dictionary and has the expected keys
            if isinstance(response, dict):
                logger.debug(f"Response keys: {list(response.keys())}")
            
            # Try different possible keys for invoice_id and URL
            invoice_id_keys = ['invoice_id', 'id', 'invoice', 'reference']
            url_keys = ['url', 'redirect_url', 'checkout_url', 'invoice_url']
            
            invoice_id = None
            redirect_url = None
            
            # Find invoice_id
            for key in invoice_id_keys:
                if key in response:
                    invoice_id = response[key]
                    logger.debug(f"Found invoice_id with key '{key}': {invoice_id}")
                    break
            
            # Find redirect URL
            for key in url_keys:
                if key in response:
                    redirect_url = response[key]
                    logger.debug(f"Found redirect URL with key '{key}': {redirect_url}")
                    break
            
            if redirect_url and invoice_id:
                session['payment_type'] = 'student'
                session['entity_id'] = student_id
                session['tutor_id'] = tutor_id
                session['invoice_id'] = invoice_id
                
                logger.debug(f"Redirecting to IntaSend URL: {redirect_url}")
                return redirect(redirect_url)
            else:
                logger.error(f"Missing required fields in IntaSend response. Invoice ID: {invoice_id}, URL: {redirect_url}")
                logger.error(f"Full response: {response}")
                flash("Payment service error: Invalid response from payment provider", "error")
                return redirect(url_for('payment', student_id=student_id, tutor_id=tutor_id))
                
        except Exception as e:
            logger.error(f"IntaSend Error: {str(e)}")
            flash(f"Payment Error: {str(e)}", "error")
            return redirect(url_for('payment', student_id=student_id, tutor_id=tutor_id))
            
    except Error as e:
        logger.error(f"Database Error: {str(e)}")
        flash(f"Database Error: {str(e)}", "error")
        return redirect(url_for('payment', student_id=student_id, tutor_id=tutor_id))
    finally:
        cursor.close()
        conn.close()

    student_id = request.form['student_id']
    tutor_id = request.form['tutor_id']
    phone_number = request.form['phone_number']
    email = request.form['email']
    
    # Get student and tutor info from DB
    conn = get_db_connection()
    if not conn:
        flash("Database connection failed", "error")
        return redirect(url_for('payment', student_id=student_id, tutor_id=tutor_id))
        
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM students WHERE id = %s", (student_id,))
        student = cursor.fetchone()
        
        cursor.execute("SELECT * FROM tutors WHERE id = %s", (tutor_id,))
        tutor = cursor.fetchone()
        
        if not student or not tutor:
            flash("Invalid student or tutor ID", "error")
            return redirect(url_for('index'))
            
        # IntaSend checkout for student session
        try:
            response = intasend.collect.checkout(
                phone_number=phone_number,
                email=email,
                amount=config.DEFAULT_SESSION_PRICE,
                currency=config.DEFAULT_CURRENCY,
                comment=f"Student Session Payment for Tutor {tutor_id}"
            )
            session['payment_type'] = 'student'
            session['entity_id'] = student_id
            session['tutor_id'] = tutor_id
            session['invoice_id'] = response['invoice_id']
            
            return redirect(response['url'])
        except Exception as e:
            flash(f"Payment Error: {str(e)}", "error")
            return redirect(url_for('payment', student_id=student_id, tutor_id=tutor_id))
            
    except Error as e:
        flash(f"Database Error: {str(e)}", "error")
        return redirect(url_for('payment', student_id=student_id, tutor_id=tutor_id))
    finally:
        cursor.close()
        conn.close()

@app.route('/payment_callback')
def payment_callback():
    invoice_id = session.get('invoice_id')
    if not invoice_id:
        flash("Invalid payment callback", "error")
        return redirect(url_for('index'))
    
    try:
        status_response = intasend.collect.status(invoice_id)
        if status_response.get('state') == 'COMPLETE' or status_response.get('code') == 'TS100':
            payment_type = session.get('payment_type')
            entity_id = session.get('entity_id')
            
            conn = get_db_connection()
            if not conn:
                flash("Database connection failed", "error")
                return redirect(url_for('index'))
                
            try:
                cursor = conn.cursor(dictionary=True)
                
                if payment_type == 'tutor':
                    cursor.execute("UPDATE tutors SET payment_status = TRUE WHERE id = %s", (entity_id,))
                    conn.commit()
                    flash("Tutor registration payment successful!", "success")
                    return redirect(url_for('index'))
                
                elif payment_type == 'student':
                    tutor_id = session.get('tutor_id')
                    cursor.execute("UPDATE students SET payment_status = 'PAID' WHERE id = %s", (entity_id,))
                    
                    # Update tutor load
                    cursor.execute("UPDATE tutors SET current_load = current_load + 1 WHERE id = %s", (tutor_id,))
                    
                    # Insert payment record
                    amount = status_response.get('amount', config.DEFAULT_SESSION_PRICE)
                    currency = status_response.get('currency', config.DEFAULT_CURRENCY)
                    phone_number = session.get('student_phone')
                    email = session.get('student_email')
                    intasend_invoice_id = invoice_id
                    status_db = 'COMPLETED'
                    api_ref = status_response.get('api_ref', f"student_{entity_id}")
                    
                    cursor.execute(
                        "INSERT INTO payments (student_id, tutor_id, amount, currency, phone_number, email, intasend_invoice_id, status, api_ref) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                        (entity_id, tutor_id, amount, currency, phone_number, email, intasend_invoice_id, status_db, api_ref)
                    )
                    conn.commit()
                    
                    # Get tutor info for results page
                    cursor.execute("SELECT * FROM tutors WHERE id = %s", (tutor_id,))
                    tutor = cursor.fetchone()
                    
                    # Get all tutors for stats
                    cursor.execute("SELECT name, current_load, availability FROM tutors")
                    all_tutors = cursor.fetchall()
                    
                    # Clear session data
                    session.pop('payment_type', None)
                    session.pop('entity_id', None)
                    session.pop('tutor_id', None)
                    session.pop('invoice_id', None)
                    session.pop('student_phone', None)
                    session.pop('student_email', None)
                    
                    return render_template('match_results.html', tutor=tutor, student_id=entity_id, tutors_data=all_tutors)
                    
            except Error as e:
                flash(f"Database Error: {str(e)}", "error")
                return redirect(url_for('index'))
            finally:
                cursor.close()
                conn.close()
        else:
            # Payment failed
            payment_type = session.get('payment_type')
            entity_id = session.get('entity_id')
            
            conn = get_db_connection()
            if conn:
                try:
                    cursor = conn.cursor()
                    if payment_type == 'student':
                        cursor.execute("UPDATE students SET payment_status = 'FAILED' WHERE id = %s", (entity_id,))
                    conn.commit()
                except Error as e:
                    logger.error(f"Failed to update payment status: {e}")
                finally:
                    cursor.close()
                    conn.close()
            
            # Clear session
            session.pop('payment_type', None)
            session.pop('entity_id', None)
            session.pop('tutor_id', None)
            session.pop('invoice_id', None)
            session.pop('student_phone', None)
            session.pop('student_email', None)
            
            return render_template('payment_failed.html', reason=status_response.get('failed_reason', 'Unknown error'))
            
    except Exception as e:
        flash(f"Payment callback error: {str(e)}", "error")
        return redirect(url_for('index'))

@app.route('/payment_success')
def payment_success():
    return render_template('payment_success.html')

if __name__ == '__main__':
    app.run(debug=True)