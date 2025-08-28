from flask import Flask, request, jsonify, render_template,session,url_for,redirect
from utils.email_otp_sender import send_email_otp, OTP_STORE
from utils.sheet_operations import*
import time, mysql.connector
import os, datetime
from dotenv import load_dotenv
from mysql.connector import pooling


app = Flask(__name__)
app.secret_key = "9f378e4b3122efb1b5a7862a57a679236ca12cf6d833fef3a35e9482f41cba12"
load_dotenv()

# Database configuration
db_config = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DATABASE_NAME'),
    'port': os.getenv('DB_PORT')  
}

connection_pool = pooling.MySQLConnectionPool(pool_name="mypool", pool_size=10,pool_reset_session=True, **db_config)

# Test connection
def get_db_connection():
    return connection_pool.get_connection()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/config")
def get_config():
    return jsonify({
        "upiId": os.getenv("UPI_ID")
    })

@app.route('/send-otp', methods=['POST'])
def send_otp():
    data = request.get_json()
    email = data.get('email').lower()
    treasurer_email = os.getenv('TREASURER_EMAIL')
    tester_email = os.getenv('TESTER_EMAIL')

    if not email:
        return jsonify({'message': 'Email is required'}), 400
    
    if email != treasurer_email or email != tester_email:
        return jsonify({'message': 'Unauthorized email'}), 403

    try:
        send_email_otp(email)
        session['email'] = email  # ✅ STORE EMAIL IN SESSION
        return jsonify({'message': 'OTP sent successfully'}), 200
    except Exception as e:
        print(f"Error sending OTP: {e}")
        return jsonify({'message': 'Failed to send OTP'}), 500

@app.route('/cash-form')
def cash_form():
    return render_template('cash-form.html')

@app.route('/treasurer-form')
def treasurer_form():
    return render_template('treasurer-form.html')

@app.route('/logout', methods=['POST'])
def logout():
    # Clear the treasurer's session
    session.pop('treasurer_name', None)
    
    # Optionally, clear all session data
    session.clear()
    # Redirect to the login or treasurer section page
    return redirect(url_for('index'))

@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    entered_otp = data.get('otp')
    email = session.get('email')

    if not email or email not in OTP_STORE:
        return jsonify({"message": "Session expired or email not found"}), 400

    stored_data = OTP_STORE[email]
    if time.time() > stored_data['expires']:
        return jsonify({"message": "OTP expired"}), 400

    if entered_otp == stored_data['otp']:
        session['treasurer_name'] = os.getenv('TREASURER_NAME')
        return jsonify({"message": "OTP verified"}), 200
    else:
        return jsonify({"message": "Invalid OTP"}), 400
    
@app.route('/submit-cash', methods=['POST'])
def submit_cash():
    data = request.get_json()
    txn_type = data.get('type')  # "Credit" or "Debit"
    amount = data.get('amount')
    timestamp = datetime.datetime.now()

    # Validate common fields
    if not (txn_type and amount):
        return jsonify({'success': False, 'message': 'Missing transaction type or amount'}), 400

    # Prepare data based on transaction type
    if txn_type == "Credit":
        donor_name = data.get('donor_name')
        if not donor_name:
            return jsonify({'success': False, 'message': 'Missing donor name'}), 400
        description = "Donation"
        # row = [donor_name, amount, "Credit", "Donation", timestamp]

    elif txn_type == "Debit":
        description = data.get('description')
        if not description:
            return jsonify({'success': False, 'message': 'Missing description'}), 400

    else:
        return jsonify({'success': False, 'message': 'Invalid transaction type'}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()  

        query = """
            INSERT INTO transactions (Name, Amount, Type, Description, Timestamp)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (donor_name, amount, txn_type, description, timestamp))
        if conn:
            conn.commit()

        cursor.close()
        conn.close()

        return jsonify({'success': True})

    except mysql.connector.Error as err:
        return jsonify({'success': False, 'message': str(err)}), 500


@app.route('/treasurer-section')
def treasurer_section():
    return render_template('treasurer-auth.html')

@app.route('/treasurer-dashboard')
def treasurer_dashboard():
    if 'treasurer_name' not in session:
        return redirect(url_for('treasurer_section'))  # or OTP page again
    return render_template('treasurer-dashboard.html', treasurer_name=session['treasurer_name'])

@app.route('/salary-form')
def salary_form():
    if 'treasurer_name' not in session:
        return redirect(url_for('treasurer_section'))  # or OTP page again
    return render_template('salary-form.html')


@app.route('/pay-salary', methods=['POST'])
def pay_salary():
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        data = request.get_json()
        payer = data.get('payerName')
        amount = float(data.get('amount'))
        pay_date_str = data.get('date')
        
        # Step 1: Get the common month and year to archive against.
        common_year, common_month = get_common_month_year(conn)
        print(f"Most common month/year in transactions: {common_month}/{common_year}")

        new_title = f"transactions_{common_year}_{common_month:02d}"
        
        # Step 2: Insert the new salary payment into the transactions table
        print("Inserting new salary payment...")
        cursor.execute(
            """INSERT INTO transactions (Name, Amount, Type, Description) 
            VALUES (%s, %s, %s, %s)""",
            (payer, amount, 'Debit', 'Imam Sahab ka Wazeefa'))
        if conn:
            conn.commit()
        print("Salary payment inserted successfully.")
        
        # Step 3: Calculate totals and remaining amount for the common month and year.
        print("Calculating totals for the common month...")
        
        # Calculate total donations for the common month
        cursor.execute("SELECT SUM(Amount) FROM transactions WHERE Type = 'Credit'")
        total_donations = cursor.fetchone()[0] or 0.0
        total_donations = float(total_donations)

        # aininCalculate total debit transactions for the common month
        cursor.execute("SELECT SUM(Amount) FROM transactions WHERE Type = 'Debit'")
        total_debit = cursor.fetchone()[0] or 0.0
        total_debit = float(total_debit)
        
        remaining = total_donations - total_debit

        # Step 4: Get last row from monthly_report to calculate prev_amount and total_remaining_amount
        cursor.execute("SELECT total_remaining_amount FROM monthly_report ORDER BY month_name DESC LIMIT 1")
        last_row = cursor.fetchone()
        
        prev_amount = float(last_row[0]) if last_row else 0.0
        total_rem_amount = prev_amount + remaining
        cursor.execute(""" INSERT INTO monthly_report (month_name,total_credit,total_debit,remaining_amount,previous_amount,total_remaining_amount) VALUES (%s,%s,%s,%s,%s,%s)""", (new_title,total_donations,total_debit,remaining,prev_amount,total_rem_amount))
        conn.commit()

        print("Monthly report updated successfully.")
        print(f"Monthly donations: ₹{total_donations}")
        print(f"Monthly debits: ₹{total_debit}")
        print(f"Remaining balance: ₹{remaining}")
        
        # Step 4: Archive the table and create a new one.
        archive_and_create_new_table(new_title,conn)
        
        return jsonify({
            'success': True,
            'message': 'Salary paid successfully.',
            'remaining_balance': remaining
        })

    except Exception as e:
        conn.rollback() # Rollback the transaction on error
        print(f"❌ A critical error occurred: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    
    finally:
        cursor.close()
        conn.close()

@app.route('/get-transactions')
def get_transactions():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)  # Return rows as dictionaries

        cursor.execute("SELECT Name, Amount, Type, Description FROM transactions ORDER BY Timestamp DESC")
        rows = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify(rows)

    except Exception as e:
        print(f"Error fetching transactions: {e}")
        return jsonify({'error': 'Failed to fetch transactions'}), 500

@app.route('/get-previous-balance')
def get_previous_balance():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT total_remaining_amount FROM monthly_report ORDER BY month_name DESC LIMIT 1")
        row = cursor.fetchone()

        cursor.close()
        conn.close()

        if row:
            return jsonify({'previous_balance': float(row['total_remaining_amount'])})
        else:
            return jsonify({'previous_balance': 0.0})
    except Exception as e:
        print(f"Error fetching previous balance: {e}")
        return jsonify({'error': 'Failed to fetch balance'}), 500
    
@app.route('/get_tables')
def get_tables():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()   # from your connection pool
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES LIKE 'transactions%'")
        tables = [row[0] for row in cursor.fetchall()]
        return jsonify(tables)

    except Exception as e:
        print("Error in /get_tables:", e)
        return jsonify({"error": "Failed to fetch tables"}), 500

    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()  # returns it to the pool


@app.route('/get_table_data/<table>')
def get_table_data(table):
    conn = None
    cursor = None
    try:
        # ✅ re-check table is valid
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES LIKE 'transactions%'")
        valid_tables = [row[0] for row in cursor.fetchall()]

        if table not in valid_tables:
            return jsonify({"error": "Invalid table name"}), 400

        cursor.close()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(f"SELECT Name,Amount,Type,Description FROM `{table}`")
        rows = cursor.fetchall()

        cursor.execute(f"SELECT SUM(Amount) as total FROM `{table}` WHERE Type='Credit'")
        total_credit = float(cursor.fetchone()["total"] or 0.0)

        cursor.execute(f"SELECT SUM(Amount) as total FROM `{table}` WHERE Type='Debit'")
        total_debit = float(cursor.fetchone()["total"] or 0.0)

        cursor.execute("SELECT total_remaining_amount FROM monthly_report WHERE month_name = %s", (table,))
        last_row = cursor.fetchone()
        prev_balance = float(last_row["total_remaining_amount"]) if last_row else 0.0

        remaining = total_credit - total_debit

        return jsonify({
            "rows": rows,
            "total_credit": total_credit,
            "total_debit": total_debit,
            "remaining": remaining,
            "prev_balance" : prev_balance
        })

    except Exception as e:
        print("Error in /get_table_data:", e)
        return jsonify({"error": "Failed to fetch table data"}), 500

    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=10000)