import concurrent.futures
import os
import time
from typing import Dict

import allure
import pytest
from requests import HTTPError

from services.package.api_packages import TrainingPackagesAPI
from services.slots.api_slots import SlotsAPI
from services.users.api_users import UsersAPI
from utils.client import APIClient


def _login_customer_from_env(phone_env: str, password_env: str, label: str):
    phone = os.getenv(phone_env)
    password = os.getenv(password_env)
    if not phone or not password:
        raise ValueError(f"Не заданы {phone_env}/{password_env}")

    client = APIClient()
    api = UsersAPI(client)
    with allure.step(f"Логин {label}"):
        api.login_by_phone(phone, password)

    personal = api.get_personal_data()
    assert personal.user.role == 5
    return api, personal.customer.id


@allure.feature("Пакеты тренировок - синхронная покупка")
@pytest.mark.coach
@pytest.mark.parametrize("logged_in_user", ["coach"], indirect=True)
def test_sync_package_buy_two_customers_last_place(logged_in_user):
    coach_api = TrainingPackagesAPI(logged_in_user.client)

    # Создание пакета
    with allure.step("Коуч создаёт пакет"):
        package_info = coach_api.create_training_package()
        training_package_id = package_info["training_package_id"]
        allure.dynamic.parameter("Package ID", training_package_id)

    # Клиенты
    with allure.step("Логиним клиентов"):
        c1_api, c1_id = _login_customer_from_env("CUSTOMER_PHONE", "CUSTOMER_PASSWORD", "Клиент 1")
        c2_api, c2_id = _login_customer_from_env("CUSTOMER2_PHONE", "CUSTOMER2_PASSWORD", "Клиент 2")

        api_c1 = TrainingPackagesAPI(c1_api.client)
        api_c2 = TrainingPackagesAPI(c2_api.client)

    # Покупка
    with allure.step("Синхронная покупка пакета"):
        def buy(api):
            try:
                success, resp = api.buy_package(training_package_id)
                return success
            except HTTPError:
                return False

        with concurrent.futures.ThreadPoolExecutor() as exec:
            f1 = exec.submit(buy, api_c1)
            f2 = exec.submit(buy, api_c2)
            concurrent.futures.wait([f1, f2])

    time.sleep(3)

    # Refund — только один должен остаться
    with allure.step("Проверка: только один может вернуть пакет"):
        successes = 0
        for api in [api_c1, api_c2]:
            try:
                success, resp = api.refund_package(training_package_id)
                if success and resp.status_code in (200, 201):
                    successes += 1
            except HTTPError:
                pass
        assert successes == 1

    # Удаление
    coach_api.delete_package(training_package_id)

    c1_api.client.clear_auth()
    c2_api.client.clear_auth()


@allure.feature("Пакеты тренировок - пакет vs поштучная")
@pytest.mark.coach
@pytest.mark.parametrize("logged_in_user", ["coach"], indirect=True)
def test_sync_package_vs_single_booking_last_place(logged_in_user):
    coach_api = TrainingPackagesAPI(logged_in_user.client)

    with allure.step("Создание пакета"):
        package_info = coach_api.create_training_package()
        package_id = package_info["training_package_id"]
        target_training_id = package_info["training_ids"][0]

    with allure.step("Логиним клиентов"):
        c1_api, c1_id = _login_customer_from_env("CUSTOMER_PHONE", "CUSTOMER_PASSWORD", "Поштучный")
        c2_api, c2_id = _login_customer_from_env("CUSTOMER2_PHONE", "CUSTOMER2_PASSWORD", "Пакет")

        slots_api = SlotsAPI(c1_api.client)
        packages_api = TrainingPackagesAPI(c2_api.client)

    with allure.step("Синхронная покупка"):
        def single():
            try:
                return bool(slots_api.book_slot(target_training_id, c1_id))
            except HTTPError:
                return False

        def package():
            try:
                success, _ = packages_api.buy_package(package_id)
                return success
            except HTTPError:
                return False

        with concurrent.futures.ThreadPoolExecutor() as exec:
            f1 = exec.submit(single)
            f2 = exec.submit(package)
            concurrent.futures.wait([f1, f2])

    time.sleep(3)

    with allure.step("Проверка авто-отписки"):
        try:
            success, _ = packages_api.refund_package(package_id)
            package_remains = success
        except HTTPError:
            package_remains = False

        try:
            slots_api.book_slot(target_training_id, c1_id)
            single_can_book_again = True
        except HTTPError:
            single_can_book_again = False

        if package_remains:
            assert single_can_book_again
        else:
            assert not single_can_book_again

    c1_api.client.clear_auth()
    c2_api.client.clear_auth()