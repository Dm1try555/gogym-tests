from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
import random
from typing import Dict

load_dotenv()

def create_training_package_payload() -> Dict:
    """
    Payload для создания пакета тренировок.
    Все переменные в .env — редактируй их сам.
    """
    sessions_count = int(os.getenv("TRAINING_PACKAGE_SESSIONS_COUNT", "5"))

    min_days = int(os.getenv("TRAINING_PACKAGE_MIN_DAYS", "180"))
    max_days = int(os.getenv("TRAINING_PACKAGE_MAX_DAYS", "365"))
    random_days = random.randint(min_days, max_days)
    start_date = (datetime.now() + timedelta(days=random_days)).strftime("%Y-%m-%d")
    end_date = (datetime.now() + timedelta(days=random_days + sessions_count - 1)).strftime("%Y-%m-%d")

    time_from = os.getenv("TRAINING_PACKAGE_TIME_FROM", "10:00:00")
    time_to = os.getenv("TRAINING_PACKAGE_TIME_TO", "10:01:00")  # 1 минута

    return {
        "name": os.getenv("TRAINING_PACKAGE_NAME", "Test Package Training"),
        "format": int(os.getenv("TRAINING_PACKAGE_FORMAT", "2")),
        "isOnline": os.getenv("TRAINING_PACKAGE_IS_ONLINE", "true").lower() == "true",
        "description": os.getenv("TRAINING_PACKAGE_DESCRIPTION", "Package of trainings"),
        "link": os.getenv("TRAINING_PACKAGE_LINK", "somelink.com"),
        "gender": int(os.getenv("TRAINING_PACKAGE_GENDER", "2")),
        "countryCode": os.getenv("TRAINING_PACKAGE_COUNTRY_CODE", "EE"),
        "townId": os.getenv("TRAINING_PACKAGE_TOWN_ID", "1526273"),
        "toponymName": os.getenv("TRAINING_PACKAGE_TOPONYM_NAME", "Astana"),
        "street": os.getenv("TRAINING_PACKAGE_STREET", "Sytova"),
        "block": os.getenv("TRAINING_PACKAGE_BLOCK", "3"),
        "venue": os.getenv("TRAINING_PACKAGE_VENUE", "Test Hall"),
        "longitude": float(os.getenv("TRAINING_PACKAGE_LONGITUDE", "35.2222")),
        "latitude": float(os.getenv("TRAINING_PACKAGE_LATITUDE", "47.7869")),
        "repeatStartDate": start_date,
        "repeatEndDate": end_date,
        "repeatInterval": 1,
        "trainingSingleDate": {
            "dateFrom": start_date,
            "dateTo": start_date,
            "timeFrom": time_from,
            "timeTo": time_to
        },
        "minAge": int(os.getenv("TRAINING_PACKAGE_MIN_AGE", "10")),
        "maxAge": int(os.getenv("TRAINING_PACKAGE_MAX_AGE", "90")),
        "maxParticipants": int(os.getenv("TRAINING_PACKAGE_MAX_PARTICIPANTS", "1")),
        "price": int(os.getenv("TRAINING_PACKAGE_PRICE", "500")),
        "paymentType": os.getenv("TRAINING_PACKAGE_PAYMENT_TYPE", "ONLINE"),
        "trainingPackages": [
            {
                "name": os.getenv("TRAINING_PACKAGE_PACKAGE_NAME", "Super Package"),
                "sessionsCount": sessions_count,
                "discountPercent": int(os.getenv("TRAINING_PACKAGE_DISCOUNT_PERCENT", "20"))
            }
        ]
    }

def buy_package_payload(
    training_package_id: int,
    payment_method: str = "APP_BALANCE",
    card_token: str = "e2522cca-9151-4691-a069-bb2e69bd12d5",
    include_self: bool = True,
) -> Dict:
    return {
        "paymentMethod": payment_method,
        "cardToken": card_token,
        "trainingPackageId": training_package_id,
        "includeSelf": include_self,
    }

def refund_package_payload(
    training_package_id: int,
    include_self: bool = True,
) -> Dict:
    return {
        "trainingPackageId": training_package_id,
        "includeSelf": include_self,
    }