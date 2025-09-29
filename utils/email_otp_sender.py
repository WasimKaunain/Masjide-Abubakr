import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random, time, os

OTP_STORE = {}  # Store OTP temporarily (email → otp + expiry)

def generate_otp():
    return str(random.randint(100000, 999999))

def send_email_otp(to_email):
    otp = generate_otp()
    OTP_STORE[to_email] = {
        'otp': otp,
        'expires': time.time() + 300  # valid for 5 minutes
    }

    sender_email = os.getenv("DEVELOPER_EMAIL")
    app_password = os.getenv("EMAIL_APP_PASSWORD")

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = "Your OTP Code"

    body = f"Your OTP is: {otp}. It is valid for 5 minutes."
    msg.attach(MIMEText(body, 'plain'))

    try:
        print("Connecting to SMTP...")
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        print("Logging in...")
        server.login(sender_email, app_password)
        print("Sending email...")
        server.sendmail(sender_email, to_email, msg.as_string())
        print("Email sent, quitting server...")
        server.quit()

        print("OTP sent to", to_email)
        return True
    except Exception as e:
        print("Error sending OTP:", e)
        return False
