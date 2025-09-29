import boto3, os, time, random
from botocore.exceptions import ClientError

OTP_STORE = {}

ses = boto3.client(
    "ses",
    region_name="ap-south-1",
    aws_access_key_id=os.getenv("ACCESS_KEY"),
    aws_secret_access_key=os.getenv("SECRET_ACCESS_KEY")
)

def generate_otp():
    return str(random.randint(100000, 999999))

def send_email_otp(to_email):
    otp = generate_otp()
    OTP_STORE[to_email] = {'otp': otp, 'expires': time.time() + 300}
    sender = os.getenv("DEVELOPER_EMAIL")

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
