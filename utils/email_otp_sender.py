import smtplib
import os
import time
import random
import traceback
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

OTP_STORE = {}

def generate_otp():
    return str(random.randint(100000, 999999))

def send_email_otp(to_email):
    print("🔹 send_email_otp called for:", to_email)

    otp = generate_otp()
    OTP_STORE[to_email] = {
        'otp': otp,
        'expires': time.time() + 300
    }

    sender = os.getenv('DEVELOPER_EMAIL')
    password = os.getenv('EMAIL_APP_PASSWORD')

    print("🔹 DEVELOPER_EMAIL exists:", bool(sender), sender)
    print("🔹 EMAIL_APP_PASSWORD exists:", bool(password), password)

    if not sender or not password:
        print("❌ Missing EMAIL credentials in environment")
        return False

    try:
        print("🔹 Creating message object")
        message = MIMEMultipart()
        message["From"] = sender
        message["To"] = to_email
        message["Subject"] = "Your OTP Code"

        body = f"Your OTP is {otp}. Valid for 5 minutes."
        message.attach(MIMEText(body, "plain"))

        print("🔹 Connecting to smtp.gmail.com:587")
        server = smtplib.SMTP("smtp.gmail.com", 587, timeout=10)

        print("🔹 Starting TLS")
        server.starttls()

        print("🔹 Logging in to Gmail")
        server.login(sender, password)

        print("🔹 Sending email")
        server.send_message(message)

        print("🔹 Quitting SMTP server")
        server.quit()

        print("✅ OTP sent successfully to", to_email)
        return True

    except Exception as e:
        print("❌ SMTP Exception occurred:")
        print("Error type:", type(e).__name__)
        print("Error message:", str(e))
        traceback.print_exc()
        return False