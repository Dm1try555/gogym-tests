import os
from typing import Any, Dict, Optional, Tuple

import allure
from requests import Response

from .endpoints import TrainingPackagesEndpoints
from .payloads import (
    buy_package_payload,
    create_training_package_payload,
    refund_package_payload,
)
from utils.client import APIClient


class TrainingPackagesAPI:
    """
    Высокоуровневый API для работы с пакетами тренировок.
    """

    def __init__(self, client: APIClient):
        self.client = client
        self.endpoints = TrainingPackagesEndpoints

    @allure.step("Коуч создаёт пакет тренировок по спорту {sport}")
    def create_training_package(self, sport: Optional[str] = None) -> Dict[str, Any]:
        sport = sport or os.getenv("TRAINING_PACKAGE_SPORT", "fitness")
        url = self.endpoints.CREATE_TRAINING_PACKAGE.format(sport=sport)
        payload = create_training_package_payload()

        response = self.client.post(url, json=payload)
        response.raise_for_status()

        raw_data = response.json()
        if not isinstance(raw_data, list) or not raw_data:
            raise AssertionError("Неожиданный формат ответа")

        training_ids = [item["id"] for item in raw_data]

        # Получаем список пакетов коуча — последний созданный — наш
        packages_response = self.client.get("/training-packages/coach")
        packages_response.raise_for_status()
        packages = packages_response.json()

        if not packages:
            raise AssertionError("Пакет не появился в списке после создания")

        # Берём последний (самый новый) пакет
        latest_package = packages[0]  # список отсортирован по createdAt desc
        training_package_id = latest_package["id"]

        return {
            "raw": raw_data,
            "training_package_id": training_package_id,
            "training_ids": training_ids,
        }

    @staticmethod
    def _assert_success_boolean(response: Response) -> bool:
        """
        Вспомогательный метод: ожидаем bool в body и статус 2xx.
        """
        response.raise_for_status()
        body = response.json()
        if isinstance(body, bool):
            return body
        return bool(body)

    @allure.step("Клиент покупает пакет тренировок {training_package_id}")
    def buy_package(
        self,
        training_package_id: int,
        payment_method: str = "APP_BALANCE",
        card_token: str = "e2522cca-9151-4691-a069-bb2e69bd12d5",
        include_self: bool = True,
        raise_for_status: bool = True,
    ) -> Tuple[bool, Response]:
        """
        Покупка пакета тренировок.

        Возвращает (успех_по_body, raw_response).
        """
        url = self.endpoints.BUY_PACKAGE
        payload = buy_package_payload(
            training_package_id=training_package_id,
            payment_method=payment_method,
            card_token=card_token,
            include_self=include_self,
        )

        response = self.client.post(url, json=payload)
        if raise_for_status:
            response.raise_for_status()

        success = False
        try:
            success = self._assert_success_boolean(response)
        except Exception:
            pass

        return success, response

    @allure.step("Клиент отказывается от пакета тренировок {training_package_id}")
    def refund_package(
        self,
        training_package_id: int,
        include_self: bool = True,
        raise_for_status: bool = False,
    ) -> Tuple[bool, Response]:
        """
        Отказ клиента от пакета тренировок.

        Возвращает (success_bool, raw_response).
        """
        url = self.endpoints.REFUND_PACKAGE
        payload = refund_package_payload(
            training_package_id=training_package_id,
            include_self=include_self,
        )

        response = self.client.post(url, json=payload)
        if raise_for_status:
            response.raise_for_status()

        success = False
        try:
            success = self._assert_success_boolean(response)
        except Exception:
            pass

        return success, response

    @allure.step("Коуч удаляет пакет тренировок {training_package_id}")
    def delete_package(self, training_package_id: int) -> Response:
        """
        Удаление пакета тренировок коучем.
        Ожидаемый статус-код: 204 No Content.
        """
        url = self.endpoints.delete_package(training_package_id)
        response = self.client.delete(url)
        response.raise_for_status()
        return response

    @allure.step(
        "Проверка доступности пакета тренировок {training_package_id} для покупки (coachId={coach_id})"
    )
    def is_available_to_buy(
        self,
        coach_id: int,
        training_package_id: int,
    ) -> Tuple[bool, Response]:
        """
        Обёртка над /training-packages/customer/available-to-buy.
        Ожидаем boolean в теле.
        """
        params = {"coachId": coach_id, "trainingPackageId": training_package_id}
        response = self.client.get(self.endpoints.AVAILABLE_TO_BUY, params=params)
        response.raise_for_status()
        body = response.json()
        return bool(body), response

    @allure.step("Коуч удаляет все свои пакеты тренировок")
    def delete_all_packages(self):
        """Удаляет все пакеты, которые можно удалить (canRemovePackage=true)"""
        try:
            response = self.client.get("/training-packages/coach")
            response.raise_for_status()
            packages = response.json()

            if not packages:
                with allure.step("Нет пакетов для удаления"):
                    return

            for package in packages:
                package_id = package["id"]
                if package.get("canRemovePackage", False):
                    with allure.step(f"Удаляем пакет ID {package_id}"):
                        try:
                            self.delete_package(package_id)
                        except Exception as e:
                            with allure.step(f"Не удалось удалить пакет {package_id}: {str(e)}"):
                                pass
                else:
                    with allure.step(f"Пропускаем пакет ID {package_id} (нельзя удалить — canRemovePackage=false)"):
                        pass
        except Exception as e:
            with allure.step(f"Ошибка при получении списка пакетов: {str(e)}"):
                pass



