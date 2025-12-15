from typing import Dict

from services.common.constants import DEFAULT_CARD_TOKEN, DEFAULT_PAYMENT_METHOD


def book_slot_payload(
    training_id: int,
    customer_id: int,
    payment_method: str = DEFAULT_PAYMENT_METHOD,
    card_token: str = DEFAULT_CARD_TOKEN,
) -> Dict:
    """
    Создает payload для записи на слот тренировки
    
    Args:
        training_id: ID тренировки
        customer_id: ID клиента
        payment_method: Способ оплаты (по умолчанию APP_BALANCE)
        card_token: Токен карты для оплаты
    
    Returns:
        Dict с данными для записи на слот
    """
    return {
        "paymentMethod": payment_method,
        "cardToken": card_token,
        "trainingId": training_id,
        "customerId": customer_id,
    }

