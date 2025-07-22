from flask import Flask, request, jsonify, render_template,session
from utils.email_otp_sender import send_email_otp, OTP_STORE
from utils.sheet_operations import get_gsheet_client_and_creds, append_to_sheet, archive_and_create_new_sheet, get_current_sheet_name
import razorpay, time
import requests, random
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "9f378e4b3122efb1b5a7862a57a679236ca12cf6d833fef3a35e9482f41cba12"

#razorpay_client = razorpay.Client(auth=(os.getenv("RAZORPAY_KEY_ID"), os.getenv("RAZORPAY_SECRET_KEY")))

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/cash-auth')
def cash_auth():
    return render_template('cash-auth.html')

@app.route('/send-otp', methods=['POST'])
def send_otp():
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({'message': 'Email is required'}), 400

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
        return jsonify({"message": "OTP verified"}), 200
    else:
        return jsonify({"message": "Invalid OTP"}), 400
    
@app.route('/submit-cash', methods=['POST'])
def submit_cash():
    data = request.get_json()
    donor_name = data.get('donorName')
    treasurer_name = data.get('treasurerName')
    amount = data.get('amount')

    email = session.get('email')
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if not (donor_name and amount and email):
        return jsonify({'success': False, 'message': 'Missing data'}), 400

    # Store this in a Google Sheet or Database
    sheet_name = get_current_sheet_name()  
    print(sheet_name)
    append_to_sheet([donor_name, amount, "Cash", timestamp ],sheet_name)

    return jsonify({'success': True})


    
@app.route("/create-order", methods=["POST"])
# def create_order():
#     data = request.get_json()
#     amount = data["amount"]
#     name = data["name"]
    
#     payment_amount = calculate_adjusted_amount(amount)
#     order = razorpay_client.order.create(dict(amount=payment_amount, currency="INR", payment_capture='1'))

#     return jsonify({
#         "order_id": order["id"],
#         "amount": payment_amount,
#         "name": name
#     })

@app.route("/payment-success", methods=["POST"])
def payment_success():
    data = request.get_json()
    name = data["name"]
    amount = data["amount"]
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    append_to_sheet([name, amount / 100, timestamp])  # Store in sheet
    return jsonify({"status": "success"})

@app.route('/treasurer-section')
def treasurer_section():
    return render_template('treasurer-auth.html')

@app.route('/pay-salary', methods=['POST'])
def pay_salary():
    data = request.get_json()
    payer = data.get('payer')
    amount = float(data.get('amount'))
    pay_date = data.get('date')

    sheet_name = get_current_sheet_name()
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
    archive_and_create_new_sheet(sheet_name)
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