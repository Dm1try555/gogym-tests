from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
import random
from typing import Dict

load_dotenv()


def create_group_training_payload() -> Dict:
    # Даты
    min_days = int(os.getenv("TRAINING_MIN_OFFSET_DAYS", "90"))
    max_days = int(os.getenv("TRAINING_MAX_OFFSET_DAYS", "120"))
    random_days = random.randint(min_days, max_days)
    future_date = (datetime.now() + timedelta(days=random_days)).strftime("%Y-%m-%d")

    # Рандомное время
    start_hour_min = int(os.getenv("TRAINING_RANDOM_TIME_START_HOUR_MIN", "8"))
    start_hour_max = int(os.getenv("TRAINING_RANDOM_TIME_START_HOUR_MAX", "20"))
    minutes_str = os.getenv("TRAINING_RANDOM_TIME_MINUTES", "0,15,30,45")
    possible_minutes = [int(m.strip()) for m in minutes_str.split(",")]

    start_hour = random.randint(start_hour_min, start_hour_max)
    start_minute = random.choice(possible_minutes)
    time_from = f"{start_hour:02d}:{start_minute:02d}:00"

    # Длительность
    TRAINING_DURATION_MINUTES = int(os.getenv("TRAINING_DURATION_MINUTES", "20"))
    end_datetime = datetime.strptime(time_from, "%H:%M:%S") + timedelta(minutes=TRAINING_DURATION_MINUTES)
    time_to = end_datetime.strftime("%H:%M:00")

    return {
        "name": os.getenv("TRAINING_NAME", "test training fitness"),
        "format": int(os.getenv("TRAINING_FORMAT", "2")),
        "isOnline": os.getenv("TRAINING_IS_ONLINE", "true").lower() == "true",
        "description": os.getenv("TRAINING_DESCRIPTION", "You will sweat, bleed and suffer"),
        "link": os.getenv("TRAINING_LINK", "somelink.com"),
        "gender": int(os.getenv("TRAINING_GENDER", "2")),
        "countryCode": os.getenv("TRAINING_COUNTRY_CODE", "EE"),
        "townId": os.getenv("TRAINING_TOWN_ID", "1526273"),
        "toponymName": os.getenv("TRAINING_TOPONYM_NAME", "Astana"),
        "street": os.getenv("TRAINING_STREET", "Sytova"),
        "block": os.getenv("TRAINING_BLOCK", "3"),
        "venue": os.getenv("TRAINING_VENUE", "Overcompensation Hall"),
        "longitude": float(os.getenv("TRAINING_LONGITUDE", "35.22223536")),
        "latitude": float(os.getenv("TRAINING_LATITUDE", "47.78690321")),
        "repeatStartDate": future_date,
        "repeatEndDate": future_date,
        "trainingSingleDate": {
            "dateFrom": future_date,
            "dateTo": future_date,
            "timeFrom": time_from,
            "timeTo": time_to
        },
        "minAge": int(os.getenv("TRAINING_MIN_AGE", "10")),
        "maxAge": int(os.getenv("TRAINING_MAX_AGE", "90")),
        "maxParticipants": int(os.getenv("TRAINING_MAX_PARTICIPANTS", "1")),
        "price": int(os.getenv("TRAINING_PRICE", "500")),
        "paymentType": os.getenv("TRAINING_PAYMENT_TYPE", "ONLINE")
    }