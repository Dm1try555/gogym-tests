from dotenv import load_dotenv
import os

load_dotenv()

def login_by_email_payload(email: str, password: str) -> dict:
    return {
        "fcmToken": os.getenv("FCM_TOKEN"),
        "email": email,
        "password": password,
        "deviceId": os.getenv("DEVICE_ID")
    }

def login_by_phone_payload(phone: str, password: str) -> dict:
    return {
        "fcmToken": os.getenv("FCM_TOKEN"),
        "phone": phone,
        "password": password,
        "deviceId": os.getenv("DEVICE_ID")
    }