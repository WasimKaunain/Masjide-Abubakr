from flask import Flask, request, jsonify, render_template,session,url_for,redirect
from utils.email_otp_sender import send_email_otp, OTP_STORE
from utils.sheet_operations import get_gsheet_client_and_creds, append_to_sheet, archive_and_create_new_sheet, get_current_sheet_name,get_month_year
import razorpay, time
import requests, random, os
from datetime import datetime
from dotenv import load_dotenv


app = Flask(__name__)
app.secret_key = "9f378e4b3122efb1b5a7862a57a679236ca12cf6d833fef3a35e9482f41cba12"

razorpay_client = razorpay.Client(auth=(os.getenv("RAZORPAY_KEY_ID"), os.getenv("RAZORPAY_SECRET_KEY")))

@app.route("/")
def index():
    rzp_ki = os.getenv('RAZORPAY_KEY_ID')
    return render_template("index.html", rzp_ki=rzp_ki)

@app.route('/send-otp', methods=['POST'])
def send_otp():
    data = request.get_json()
    email = data.get('email')
    treasurer_email = os.getenv('TREASURER_EMAIL')

    if not email:
        return jsonify({'message': 'Email is required'}), 400
    
    if email != treasurer_email:
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
    donor_name = data.get('donor_name')
    amount = data.get('amount')


    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if not (donor_name and amount ):
        return jsonify({'success': False, 'message': 'Missing data'}), 400

    # Store this in a Google Sheet or Database
    sheet_name = get_current_sheet_name()  
    append_to_sheet([donor_name, amount, "Cash", timestamp ],sheet_name)

    return jsonify({'success': True})


@app.route("/verify_payment", methods=["POST"])
def verify_payment():
    try:
        data = request.get_json()
        razorpay_payment_id = data.get('razorpay_payment_id')
        razorpay_order_id = data.get('razorpay_order_id')
        razorpay_signature = data.get('razorpay_signature')

        # Verify signature
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }

        result = razorpay_client.utility.verify_payment_signature(params_dict)

        # If signature is valid
        return jsonify({"status": "success", "message": "Payment verified successfully."}), 200

    except razorpay.errors.SignatureVerificationError:
        return jsonify({"status": "failure", "message": "Payment verification failed."}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/create_order', methods=['POST'])
def create_order():
    try:
        data = request.get_json()
        amount = data.get("amount")
        if not amount:
            return jsonify({"status": "failure", "message": "Amount is required"}), 400

        # Amount in paise
        order = razorpay_client.order.create({
            "amount": int(amount) * 100,
            "currency": "INR",
            "payment_capture": "1"  # Auto capture
        })

        return jsonify({
            "status": "success",
            "order_id": order["id"],
            "amount": order["amount"],
            "currency": order["currency"],
            "key": os.getenv("RAZORPAY_KEY_ID")
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/payment-success", methods=["POST"])
def payment_success():
    data = request.get_json()
    name = data["name"]
    amount = data["amount"]
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    sheet_name = get_current_sheet_name() 
    append_to_sheet([name, amount / 100, "Online", timestamp],sheet_name)  # Store in sheet
    return jsonify({"status": "success"})

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
    data = request.get_json()
    payer = data.get('payerName')
    amount = float(data.get('amount'))
    pay_date = data.get('date')

    sheet_name = get_current_sheet_name()

    common_year,common_month = get_month_year(sheet_name)
    # Step 3: Rename the sheet
    new_title = f"Donation {common_year} {common_month}"

    append_to_sheet([payer, amount, 'Salary Paid', pay_date], sheet_name)

    # Calculate totals
    gc, creds = get_gsheet_client_and_creds()
    sheet = gc.open(sheet_name).sheet1
    records = sheet.get_all_values()
    total_donations = sum(float(row[1]) for row in records[1:] if row[2] in ['Cash', 'Online'])
    total_salary_paid = sum(float(row[1]) for row in records[1:] if row[2] == 'Salary Paid')
    remaining = total_donations - total_salary_paid

    # Append remaining
    sheet.append_row(['Remaining for this month = ₹' + str(remaining)])

    # Archive and create new sheet
    archive_and_create_new_sheet(sheet_name,new_title)
    return jsonify({'success': True})

@app.route('/get-transactions')
def get_transactions():
    sheet_name = get_current_sheet_name()
    gc,creds = get_gsheet_client_and_creds()
    sheet = gc.open(sheet_name).sheet1
    rows = sheet.get_all_records()
    return jsonify(rows)


def calculate_adjusted_amount(settlement_amount):
    # Fees = 1.99% + 18% GST on fees = approx 2.35%
    fees_percent = 0.0235
    return int((settlement_amount * 100) / (1 - fees_percent))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=10000)