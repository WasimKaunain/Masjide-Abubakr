import boto3
import os
import time
import random
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

OTP_STORE = {}

# Get AWS region from environment
AWS_REGION = os.getenv("AWS_DEFAULT_REGION")  # fallback if not set

# Create SES client
ses = boto3.client(
    "ses",
    region_name=AWS_REGION
    # No need to pass aws_access_key_id / aws_secret_access_key if env vars are set
)

def generate_otp():
    return str(random.randint(100000, 999999))

def send_email_otp(to_email):
    otp = generate_otp()
    OTP_STORE[to_email] = {'otp': otp, 'expires': time.time() + 300}
    sender = os.getenv('DEVELOPER_EMAIL')

    if not sender:
        print("DEVELOPER_EMAIL not set in environment!")
        return False

    try:
        ses.send_email(
            Source=sender,
            Destination={"ToAddresses": [to_email]},
            Message={
                "Subject": {"Data": "Your OTP Code"},
                "Body": {"Text": {"Data": f"Your OTP is {otp}. Valid for 5 minutes."}}
            }
        )
        print("OTP sent to", to_email)
        return True
    except ClientError as e:
        print("SES Error:", e.response["Error"]["Message"])
        return False

# # Debug: print environment variables
# print("AWS_ACCESS_KEY_ID:", os.getenv("AWS_ACCESS_KEY_ID"))
# print("AWS_SECRET_ACCESS_KEY:", os.getenv("AWS_SECRET_ACCESS_KEY"))
# print("AWS_DEFAULT_REGION:", os.getenv("AWS_DEFAULT_REGION"))
# print("DEVELOPER_EMAIL:", os.getenv("DEVELOPER_EMAIL"))
