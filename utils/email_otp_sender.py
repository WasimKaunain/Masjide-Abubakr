import smtplib
import os
import time
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

OTP_STORE = {}

def generate_otp():
    return str(random.randint(100000, 999999))

def send_email_otp(to_email):
    otp = generate_otp()
    OTP_STORE[to_email] = {
        'otp': otp,
        'expires': time.time() + 300  # 5 minutes
    }

    sender = os.getenv('DEVELOPER_EMAIL')
    password = os.getenv('EMAIL_APP_PASSWORD')

    if not sender or not password:
        print("DEVELOPER_EMAIL or EMAIL_APP_PASSWORD not set!")
        return False

    try:
        message = MIMEMultipart()
        message["From"] = sender
        message["To"] = to_email
        message["Subject"] = "Your OTP Code"

        body = f"Your OTP is {otp}. Valid for 5 minutes."
        message.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender, password)
        server.send_message(message)
        server.quit()

        print("OTP sent to", to_email)
        return True

    except Exception as e:
        print("SMTP Error:", str(e))
        return False