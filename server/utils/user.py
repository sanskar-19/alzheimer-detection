import uuid
import smtplib
import random

from ..schema import user as user_schema
from datetime import datetime, timedelta
from passlib.context import CryptContext
from ..models import user
from email.mime.text import MIMEText
from config import setting

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Create new user for the db
def create_new_user(
    first_name: str,
    last_name: str,
    email: str,
    password: str,
    otp: str,
    otp_expiry_at: datetime,
    role: str | None = "admin",
):
    # Generate new uuid here
    uid = uuid.uuid4()

    # Create new user object for the db
    new_user = user_schema.NewUserInDb(
        uid=str(uid),
        first_name=first_name,
        last_name=last_name,
        email=email,
        hashed_password=generate_hash(password),
        role=role,
        created_at=datetime.now(),
        otp=otp,
        otp_expiry_at=otp_expiry_at,
    )

    return user.UserModel(**new_user.dict())


# Verify password
def verify_password(password: str, hashed_password: str):
    return pwd_context.verify(password, hashed_password)


# Generate has password for storing in db
def generate_hash(password: str):
    return pwd_context.hash(password)


# Send email function
def send_email(email: str):
    msg = MIMEText("Hello World")
    msg["Subject"] = "Test Mail"
    msg["From"] = "Your Auth Module"
    msg["To"] = email
    smtp_email_server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    smtp_email_server.login(
        user=setting.EMAIL_SERVICE_SENDER_EMAIL,
        password=setting.EMAIL_SERVICE_SENDER_PASS,
    )
    smtp_email_server.sendmail(
        from_addr=setting.EMAIL_SERVICE_SENDER_EMAIL,
        to_addrs=email,
        msg=msg.as_string(),
    )
    smtp_email_server.quit()


# Generate otp
def generate_otp():
    start = 10**5 + 1
    end = 10**6 - 1
    otp = random.randrange(start, end)
    return otp, datetime.now() + timedelta(minutes=5)
