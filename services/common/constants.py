import os

from dotenv import load_dotenv

load_dotenv()

# Общие константы для платежей, чтобы не дублировать строки по проекту

DEFAULT_PAYMENT_METHOD = os.getenv("DEFAULT_PAYMENT_METHOD", "APP_BALANCE")

DEFAULT_CARD_TOKEN = os.getenv(
    "DEFAULT_CARD_TOKEN",
    "e2522cca-9151-4691-a069-bb2e69bd12d5",
)


