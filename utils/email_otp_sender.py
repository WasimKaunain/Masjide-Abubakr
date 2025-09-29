import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random, time, os

OTP_STORE = {}  # Store OTP temporarily (email → otp + expiry)

def generate_otp():
    return str(random.randint(100000, 999999))

def send_email_otp(to_email):
    otp = generate_otp()
    OTP_STORE[to_email] = {'otp': otp, 'expires': time.time() + 300}

    sender_email = os.getenv("DEVELOPER_EMAIL")
    smtp_user = os.getenv("SES_SMTP_USERNAME")
    smtp_pass = os.getenv("SES_SMTP_PASSWORD")

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = "Your OTP Code"
    msg.attach(MIMEText(f"Your OTP is: {otp}. It is valid for 5 minutes.", 'plain'))
    print("Mail is ready to be sent...")

    try:
        print("Connecting to SMTP...")
        server = smtplib.SMTP('email-smtp.ap-south-1.amazonaws.com', 587)
        print("connected to server..")
        server.starttls()
        print("starting TLS...")
        server.login(smtp_user, smtp_pass)
        print("Sending email...")
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()
        print("OTP sent to", to_email)
        return True
    except Exception as e:
        print("Error sending OTP:", e)
        return False
