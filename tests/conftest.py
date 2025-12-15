import pytest
import os
from dotenv import load_dotenv
from utils.client import APIClient
from services.users.api_users import UsersAPI
import allure
from services.package.api_packages import TrainingPackagesAPI

load_dotenv()

# === Регистрация кастомного аргумента ===
def pytest_addoption(parser):
    parser.addoption(
        "--role",
        action="store",
        default="customer",
        choices=["coach", "customer"],
        help="Роль для логина: coach или customer"
    )

def pytest_configure(config):
    os.environ["TEST_ROLE"] = config.getoption("--role")

# =========================================

def _create_logged_in_user(login_type: str) -> UsersAPI:
    """Создаёт и логинит пользователя по типу роли"""
    client = APIClient()
    api = UsersAPI(client)

    if login_type == "coach":
        email = os.getenv("COACH_EMAIL")
        phone = os.getenv("COACH_PHONE")
        password = os.getenv("COACH_PASSWORD")

        if email:
            with allure.step("Логин коуча по email"):
                api.login_by_email(email, password)
        elif phone:
            with allure.step("Логин коуча по телефону"):
                api.login_by_phone(phone, password)
        else:
            raise ValueError("Не указаны данные коуча в .env (COACH_EMAIL или COACH_PHONE)")

    elif login_type == "customer":
        phone = os.getenv("CUSTOMER_PHONE")
        email = os.getenv("CUSTOMER_EMAIL")
        password = os.getenv("CUSTOMER_PASSWORD")

        if phone:
            with allure.step("Логин первого клиента по телефону"):
                api.login_by_phone(phone, password)
        elif email:
            with allure.step("Логин первого клиента по email"):
                api.login_by_email(email, password)
        else:
            raise ValueError("Не указаны данные первого клиента в .env (CUSTOMER_PHONE или CUSTOMER_EMAIL)")

    else:
        raise ValueError("Неподдерживаемая роль")

    return api

@pytest.fixture(scope="function")
def logged_in_user():
    """
    Основная фикстура для тестов под одной ролью.
    Используется в обычных тестах (создание тренировки, поиск и т.д.)
    Роль берётся из --role
    """
    role = os.getenv("TEST_ROLE", "customer")
    user_api = _create_logged_in_user(role)

    # Проверка правильности роли
    personal = user_api.get_personal_data()
    expected_role = 4 if role == "coach" else 5
    assert personal.user.role == expected_role, f"Ожидалась роль {expected_role}, получена {personal.user.role}"

    with allure.step(f"Успешный логин под ролью {role} (ID: {personal.user.id})"):
        pass

    yield user_api
    user_api.client.clear_auth()

# ===================== НОВЫЕ ФИКСТУРЫ ДЛЯ ДВУХ КЛИЕНТОВ =====================

@pytest.fixture(scope="function")
def customer1(logged_in_user):
    """
    Первый клиент — использует основную роль customer из --role customer
    """
    personal = logged_in_user.get_personal_data()
    assert personal.user.role == 5
    assert str(personal.user.phone or personal.user.email)  # хотя бы один способ логина

    with allure.step(f"Клиент 1 готов (ID: {personal.user.id}, Phone: {personal.user.phone})"):
        pass

    yield logged_in_user

@pytest.fixture(scope="function")
def customer2():
    """
    Второй клиент — полностью независимая сессия
    Логинится по фиксированным данным CUSTOMER2_*
    """
    client = APIClient()
    api = UsersAPI(client)

    phone = os.getenv("CUSTOMER2_PHONE")
    password = os.getenv("CUSTOMER2_PASSWORD")

    if not phone or not password:
        raise ValueError("Не указаны данные второго клиента: CUSTOMER2_PHONE и CUSTOMER2_PASSWORD в .env")

    with allure.step("Логин второго клиента"):
        api.login_by_phone(phone, password)

    personal = api.get_personal_data()
    assert personal.user.role == 5, f"Второй клиент должен иметь role=5, получен {personal.user.role}"

    with allure.step(f"Клиент 2 готов (ID: {personal.user.id}, Phone: {personal.user.phone})"):
        pass

    yield api
    client.clear_auth()

@pytest.fixture(autouse=True, scope="function")
def clean_packages_before_test(logged_in_user):
    """
    Автоматическая очистка всех удаляемых пакетов коуча перед каждым тестом.
    Запускается только для тестов с ролью coach.
    """
    personal = logged_in_user.get_personal_data()
    if personal.user.role == 4:  # role 4 = coach
        coach_api = TrainingPackagesAPI(logged_in_user.client)
        with allure.step("Автоочистка: удаляем все возможные пакеты коуча перед тестом"):
            coach_api.delete_all_packages()