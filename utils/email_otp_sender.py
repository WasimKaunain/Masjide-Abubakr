import os
import time
import random
import requests
import traceback
from dotenv import load_dotenv
load_dotenv()

import requests
import os
import time
import random

OTP_STORE = {}

def generate_otp():
    return str(random.randint(100000, 999999))

def send_email_otp(to_email):
    print("=== MAILGUN OTP DEBUG START ===")

    otp = generate_otp()

    OTP_STORE[to_email] = {
        "otp": otp,
        "expires": time.time() + 300
    }

    domain = os.getenv("MAILGUN_DOMAIN")
    api_key = os.getenv("MAILGUN_API_KEY")
    sender = os.getenv("MAIL_FROM")

    print("DOMAIN:", repr(domain))
    print("API KEY:", repr(api_key))
    print("SENDER:", repr(sender))

    if not domain or not api_key or not sender:
        print("❌ Missing env variables")
        return False

    try:
        response = requests.post(
            f"https://api.mailgun.net/v3/{domain}/messages",
            auth=("api", api_key.strip()),
            data={
                "from": sender.strip(),
                "to": to_email,
                "subject": "Your OTP Code",
                "text": f"Your OTP is {otp}. Valid for 5 minutes."
            }
        )

        print("STATUS:", response.status_code)
        print("BODY:", response.text)
        print("=== MAILGUN OTP DEBUG END ===")

        return response.status_code == 200

    except Exception as e:
        print("❌ Exception:", str(e))
        return False