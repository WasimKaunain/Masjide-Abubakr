import os
import time
import random
import requests
import logging
import sys
import traceback
from dotenv import load_dotenv

load_dotenv()

# Configure logger (Render-friendly)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stdout,
)

logger = logging.getLogger(__name__)

OTP_STORE = {}

def generate_otp():
    return str(random.randint(100000, 999999))

def send_email_otp(to_email):
    logger.info("========== MAILGUN DEBUG START ==========")
    logger.info(f"Sending OTP to: {to_email}")

    try:
        otp = generate_otp()

        OTP_STORE[to_email] = {
            "otp": otp,
            "expires": time.time() + 300
        }

        domain = os.getenv("MAILGUN_DOMAIN")
        api_key = os.getenv("MAILGUN_API_KEY")
        sender = os.getenv("MAIL_FROM")

        logger.info(f"DOMAIN: {repr(domain)}")
        logger.info(f"API KEY exists: {bool(api_key)}")
        logger.info(f"SENDER: {repr(sender)}")

        if not domain or not api_key or not sender:
            logger.error("❌ Missing environment variables")
            return False

        url = f"https://api.mailgun.net/v3/{domain}/messages"
        logger.info(f"Mailgun URL: {url}")

        response = requests.post(
            url,
            auth=("api", api_key.strip()),
            data={
                "from": sender.strip(),
                "to": to_email,
                "subject": "Your OTP Code",
                "text": f"Your OTP is {otp}. Valid for 5 minutes."
            },
            timeout=15
        )

        logger.info(f"HTTP STATUS: {response.status_code}")
        logger.info(f"RESPONSE BODY: {response.text}")

        if response.status_code == 200:
            logger.info("✅ OTP sent successfully")
            logger.info("========== MAILGUN DEBUG END ==========")
            return True
        else:
            logger.error("❌ Mailgun returned non-200 status")
            logger.info("========== MAILGUN DEBUG END ==========")
            return False

    except Exception as e:
        logger.error("❌ Exception while sending Mailgun")
        logger.error(str(e))
        traceback.print_exc()
        logger.info("========== MAILGUN DEBUG END ==========")
        return False