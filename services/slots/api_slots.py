import allure
from .endpoints import SlotsEndpoints
from .models import SlotResponse
from .payloads import book_slot_payload
from utils.client import APIClient

class SlotsAPI:
    def __init__(self, client: APIClient):
        self.client = client
        self.endpoints = SlotsEndpoints

    @allure.step("Клиент записывается на тренировку {training_id}")
    def book_slot(
        self,
        training_id: int,
        customer_id: int,
        payment_method: str = "APP_BALANCE",
        card_token: str = "e2522cca-9151-4691-a069-bb2e69bd12d5"
    ) -> list[SlotResponse]:
        """
        Записывает клиента на слот тренировки
        
        Args:
            training_id: ID тренировки
            customer_id: ID клиента
            payment_method: Способ оплаты
            card_token: Токен карты
        
        Returns:
            Список SlotResponse объектов
        """
        url = self.endpoints.BOOK_SLOT
        payload = book_slot_payload(training_id, customer_id, payment_method, card_token)

        response = self.client.post(url, json=payload)
        response.raise_for_status()

        # Ответ приходит как массив
        slots_data = response.json()
        slots = [SlotResponse(**slot) for slot in slots_data]

        with allure.step(f"Клиент {customer_id} записан на тренировку {training_id}, slot ID={slots[0].id if slots else 'N/A'}"):
            pass

        return slots
