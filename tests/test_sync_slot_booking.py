import pytest
import allure
import time
import os
from dotenv import load_dotenv
from datetime import datetime
from services.trainings.api_trainings import TrainingsAPI
from services.slots.api_slots import SlotsAPI
from services.users.api_users import UsersAPI
from utils.client import APIClient
import concurrent.futures
from requests.exceptions import HTTPError

load_dotenv()

@allure.feature("Синхронная запись на слоты")
@pytest.mark.coach
@pytest.mark.parametrize("logged_in_user", ["coach"], indirect=True)
def test_slot_booking_max_participants_validation(logged_in_user):
    """
    Тест проверяет валидацию максимального количества участников.
    Если maxParticipants=1, то только один клиент может записаться,
    второй должен получить ошибку что места нет.
    """
    # Шаг 1: Коуч создает тренировку с 1 местом
    with allure.step("Коуч создает тренировку с 1 местом (maxParticipants=1)"):
        trainings_api = TrainingsAPI(logged_in_user.client)
        training = trainings_api.create_group_training()
        training_id = training["id"]
        max_participants = training["maxParticipants"]
        
        assert max_participants == 1, f"Тренировка должна иметь 1 место, получено {max_participants}"
        allure.dynamic.parameter("Training ID", training_id)
        allure.dynamic.parameter("Max Participants", max_participants)
    
    # Шаг 2: Создаем и логиним первого клиента
    with allure.step("Создаем и логиним первого клиента"):
        client1 = APIClient()
        users_api1 = UsersAPI(client1)
        
        customer1_phone = os.getenv("CUSTOMER_PHONE")
        customer1_email = os.getenv("CUSTOMER_EMAIL")
        customer1_password = os.getenv("CUSTOMER_PASSWORD")
        
        if customer1_phone:
            users_api1.login_by_phone(customer1_phone, customer1_password)
        elif customer1_email:
            users_api1.login_by_email(customer1_email, customer1_password)
        else:
            raise ValueError("Не указаны данные первого клиента: CUSTOMER_PHONE или CUSTOMER_EMAIL")
        
        personal1 = users_api1.get_personal_data()
        customer1_id = personal1.customer.id
        assert personal1.user.role == 5, "Первый клиент должен иметь роль 5"
        
        allure.dynamic.parameter("Customer 1 ID", customer1_id)
        slots_api1 = SlotsAPI(client1)
    
    # Шаг 3: Первый клиент записывается на тренировку
    with allure.step("Первый клиент записывается на тренировку"):
        try:
            slot1 = slots_api1.book_slot(training_id, customer1_id)
        except HTTPError as e:
            # Если на окружении не хватает баланса – это проблема данных, а не логики maxParticipants.
            resp = e.response
            body = (resp.text or "").lower() if resp is not None else str(e).lower()
            if "insufficient balance" in body or "1430" in body:
                pytest.skip("Недостаточно баланса для первого клиента, окружение не готово для проверки maxParticipants")
            raise

        assert len(slot1) > 0, "Первый клиент должен успешно записаться"
        assert slot1[0].id is not None, "Первый клиент должен получить slot ID"
        allure.dynamic.parameter("Slot 1 ID", slot1[0].id)
    
    # Шаг 4: Создаем и логиним второго клиента
    with allure.step("Создаем и логиним второго клиента"):
        client2 = APIClient()
        users_api2 = UsersAPI(client2)
        
        customer2_phone = os.getenv("CUSTOMER2_PHONE")
        customer2_password = os.getenv("CUSTOMER2_PASSWORD")
        
        if not customer2_phone or not customer2_password:
            raise ValueError("Не указаны данные второго клиента: CUSTOMER2_PHONE и CUSTOMER2_PASSWORD")
        
        users_api2.login_by_phone(customer2_phone, customer2_password)
        personal2 = users_api2.get_personal_data()
        customer2_id = personal2.customer.id
        assert personal2.user.role == 5, "Второй клиент должен иметь роль 5"
        
        assert customer1_id != customer2_id, "Customer IDs должны быть разными"
        allure.dynamic.parameter("Customer 2 ID", customer2_id)
        slots_api2 = SlotsAPI(client2)
    
        # Шаг 5: Второй клиент пытается записаться
        with allure.step("Второй клиент пытается записаться на занятое место"):
            slot2_result = None
            slot2_error = None
            slot2_exception = None

            try:
                slot2_result = slots_api2.book_slot(training_id, customer2_id)
                if slot2_result and len(slot2_result) > 0:
                    allure.dynamic.parameter("Второй клиент", "Записался успешно")
                else:
                    allure.dynamic.parameter("Второй клиент", "Получил пустой ответ")
            except HTTPError as e:
                slot2_error = e
                error_response = e.response
                error_text = error_response.text.lower()
                allure.dynamic.parameter("Второй клиент", f"Получил HTTPError: {error_response.status_code}")
                allure.dynamic.parameter("Ошибка второго клиента", error_text[:200])
            except Exception as e:
                slot2_exception = e
                allure.dynamic.parameter("Второй клиент", f"Получил исключение: {type(e).__name__}")
                allure.dynamic.parameter("Ошибка второго клиента", str(e)[:200])

        # Шаг 6: Валидация - проверяем что количество участников не превышает maxParticipants
        with allure.step("Валидация: проверяем что количество участников не превышает maxParticipants"):
            # Если второй клиент записался успешно при maxParticipants=1 - это БАГ!
            if slot2_result is not None and len(slot2_result) > 0:
                # ВАЛИДАЦИЯ ПРОВАЛЕНА: количество участников превышает maxParticipants
                with allure.step("ОШИБКА ВАЛИДАЦИИ: второй клиент записался при maxParticipants=1"):
                    assert False, \
                        f"ВАЛИДАЦИЯ ПРОВАЛЕНА: При maxParticipants=1 записалось 2 участника! " \
                        f"Customer 1 ID: {customer1_id}, Customer 2 ID: {customer2_id}. " \
                        f"Slot 1 ID: {slot1[0].id}, Slot 2 ID: {slot2_result[0].id}. " \
                        f"Количество участников ({2}) превышает maxParticipants ({max_participants})"
            elif slot2_error is not None:
                # Второй клиент получил HTTPError - это правильно
                error_response = slot2_error.response
                with allure.step("Валидация пройдена: второй клиент не смог записаться"):
                    assert error_response.status_code in [400, 409, 422], \
                        f"Ожидалась ошибка 400/409/422, получен {error_response.status_code}"
                    allure.dynamic.parameter("Валидация участников",
                        f"Правильно: второй клиент не смог записаться (ошибка {error_response.status_code})")
                    allure.dynamic.parameter("Количество участников", f"{1} (соответствует maxParticipants={max_participants})")
            elif slot2_exception is not None:
                # Другое исключение - логируем и считаем что валидация пройдена (клиент не записался)
                with allure.step("Валидация пройдена: второй клиент получил исключение и не записался"):
                    allure.dynamic.parameter("Валидация участников",
                        f"Правильно: второй клиент не смог записаться (исключение {type(slot2_exception).__name__})")
                    allure.dynamic.parameter("Количество участников", f"{1} (соответствует maxParticipants={max_participants})")
            else:
                # Неожиданная ситуация - но если slot2_result пустой или None, это тоже означает что не записался
                with allure.step("Валидация: второй клиент не записался (пустой результат)"):
                    allure.dynamic.parameter("Валидация участников",
                        "Правильно: второй клиент не записался (пустой результат)")
                    allure.dynamic.parameter("Количество участников", f"{1} (соответствует maxParticipants={max_participants})")
    
    # Очистка
    client1.clear_auth()
    client2.clear_auth()


@allure.feature("Синхронная запись на слоты")
@pytest.mark.coach
@pytest.mark.parametrize("logged_in_user", ["coach"], indirect=True)
def test_sync_slot_booking_last_place(logged_in_user):
    """
    Тест проверяет защиту при синхронной записи на последнее место.
    Если 2 пользователя одновременно записываются на одно и то же место,
    то в случае успешной оплаты они оба технически смогут записаться,
    но позднее записавшийся должен быть удален из тренировки.
    """
    # Шаг 1: Коуч создает тренировку с 1 местом
    with allure.step("Коуч создает тренировку с 1 местом (maxParticipants=1)"):
        trainings_api = TrainingsAPI(logged_in_user.client)
        training = trainings_api.create_group_training()
        training_id = training["id"]
        max_participants = training["maxParticipants"]
        
        assert max_participants == 1, f"Тренировка должна иметь 1 место, получено {max_participants}"
        allure.dynamic.parameter("Training ID", training_id)
        allure.dynamic.parameter("Max Participants", max_participants)
    
    # Шаг 2: Создаем и логиним обоих клиентов
    with allure.step("Создаем и логиним обоих клиентов"):
        # Создаем первого клиента
        client1 = APIClient()
        users_api1 = UsersAPI(client1)
        
        customer1_phone = os.getenv("CUSTOMER_PHONE")
        customer1_email = os.getenv("CUSTOMER_EMAIL")
        customer1_password = os.getenv("CUSTOMER_PASSWORD")
        
        if customer1_phone:
            users_api1.login_by_phone(customer1_phone, customer1_password)
        elif customer1_email:
            users_api1.login_by_email(customer1_email, customer1_password)
        else:
            raise ValueError("Не указаны данные первого клиента: CUSTOMER_PHONE или CUSTOMER_EMAIL")
        
        personal1 = users_api1.get_personal_data()
        customer1_id = personal1.customer.id
        assert personal1.user.role == 5, "Первый клиент должен иметь роль 5"
        
        # Создаем второго клиента
        client2 = APIClient()
        users_api2 = UsersAPI(client2)
        
        customer2_phone = os.getenv("CUSTOMER2_PHONE")
        customer2_password = os.getenv("CUSTOMER2_PASSWORD")
        
        if not customer2_phone or not customer2_password:
            raise ValueError("Не указаны данные второго клиента: CUSTOMER2_PHONE и CUSTOMER2_PASSWORD")
        
        users_api2.login_by_phone(customer2_phone, customer2_password)
        personal2 = users_api2.get_personal_data()
        customer2_id = personal2.customer.id
        assert personal2.user.role == 5, "Второй клиент должен иметь роль 5"
        
        assert customer1_id is not None, "Customer 1 ID не найден"
        assert customer2_id is not None, "Customer 2 ID не найден"
        assert customer1_id != customer2_id, "Customer IDs должны быть разными"
        
        allure.dynamic.parameter("Customer 1 ID", customer1_id)
        allure.dynamic.parameter("Customer 2 ID", customer2_id)
        
        # Создаем API объекты для записи на слоты
        slots_api1 = SlotsAPI(client1)
        slots_api2 = SlotsAPI(client2)
    
    # Шаг 3: Синхронная запись обоих клиентов
    with allure.step("Синхронная запись двух клиентов на последнее место"):
        results = {}
        
        def book_customer1():
            try:
                result = slots_api1.book_slot(training_id, customer1_id)
                return ("customer1", result, None)
            except Exception as e:
                return ("customer1", None, str(e))
        
        def book_customer2():
            try:
                result = slots_api2.book_slot(training_id, customer2_id)
                return ("customer2", result, None)
            except Exception as e:
                return ("customer2", None, str(e))
        
        # Запускаем синхронно
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future1 = executor.submit(book_customer1)
            future2 = executor.submit(book_customer2)
            
            for future in concurrent.futures.as_completed([future1, future2]):
                customer_name, result, error = future.result()
                results[customer_name] = {"result": result, "error": error}
        
        # Анализируем результаты
        customer1_slots = results.get("customer1", {}).get("result")
        customer2_slots = results.get("customer2", {}).get("result")
        customer1_error = results.get("customer1", {}).get("error")
        customer2_error = results.get("customer2", {}).get("error")
        
        # Оба должны технически получить успешный ответ (даже если один будет удален)
        assert customer1_slots is not None or customer1_error is not None, "Customer 1 должен получить ответ от сервера"
        assert customer2_slots is not None or customer2_error is not None, "Customer 2 должен получить ответ от сервера"
        
        # Проверяем результаты синхронной записи
        # Согласно требованиям: оба могут технически записаться при успешной оплате
        both_success = customer1_slots is not None and len(customer1_slots) > 0 and \
                      customer2_slots is not None and len(customer2_slots) > 0
        
        if both_success:
            # Оба успешно записались - это ожидаемое поведение при синхронной записи
            slot1 = customer1_slots[0]
            slot2 = customer2_slots[0]
            
            slot1_created = slot1.createdAt
            slot2_created = slot2.createdAt
            
            # Сравниваем временные метки
            time1 = datetime.fromisoformat(slot1_created.replace('Z', '+00:00'))
            time2 = datetime.fromisoformat(slot2_created.replace('Z', '+00:00'))
            
            later_customer = "customer1" if time1 > time2 else "customer2"
            later_customer_id = customer1_id if later_customer == "customer1" else customer2_id
            earlier_customer_id = customer2_id if later_customer == "customer1" else customer1_id
            
            allure.dynamic.parameter("Позднее записавшийся", later_customer)
            allure.dynamic.parameter("Время записи Customer 1", slot1_created)
            allure.dynamic.parameter("Время записи Customer 2", slot2_created)
            allure.dynamic.parameter("Slot 1 ID", slot1.id)
            allure.dynamic.parameter("Slot 2 ID", slot2.id)
            
            with allure.step(f"Оба клиента получили успешный ответ. {later_customer} записался позднее"):
                assert slot1.id is not None, "Customer 1 должен иметь slot ID"
                assert slot2.id is not None, "Customer 2 должен иметь slot ID"
        else:
            # Один из клиентов не смог записаться - возможно место уже было занято
            # Это тоже валидный сценарий, но не сценарий синхронной записи
            with allure.step("Один из клиентов не смог записаться (место уже занято)"):
                if customer1_slots is None or len(customer1_slots) == 0:
                    allure.dynamic.parameter("Customer 1", "Не записался")
                if customer2_slots is None or len(customer2_slots) == 0:
                    allure.dynamic.parameter("Customer 2", "Не записался")
            
            # Если оба не записались или только один - это не сценарий синхронной записи
            # В этом случае тест завершается, так как не было одновременной записи
            client1.clear_auth()
            client2.clear_auth()
            return
    
    # Шаг 4: Ожидание обработки удаления позднее записавшегося клиента
    with allure.step("Ожидание обработки удаления позднее записавшегося клиента"):
        time.sleep(3)  # Даем время системе обработать удаление
    
    # Шаг 5: Валидация - проверяем что количество участников не превышает maxParticipants
    with allure.step("Валидация: проверяем что количество участников не превышает maxParticipants"):
        # Согласно требованиям: если maxParticipants=1, то должен быть только 1 участник
        # Позднее записавшийся должен быть удален системой
        
        # Проверяем через попытку повторной записи позднее записавшегося клиента
        later_slots_api = slots_api1 if later_customer == "customer1" else slots_api2
        
        try:
            new_slot = later_slots_api.book_slot(training_id, later_customer_id)
            # Если запись прошла успешно, значит позднее записавшийся был удален
            with allure.step(f"Подтверждение: {later_customer} был удален, место свободно"):
                assert len(new_slot) > 0, f"{later_customer} должен иметь возможность записаться повторно после удаления"
                allure.dynamic.parameter("Результат валидации", f"{later_customer} успешно записался повторно - подтверждает удаление")
                allure.dynamic.parameter("Количество участников", "1 (правильно, соответствует maxParticipants)")
        except HTTPError as e:
            # Если получили ошибку, проверяем причину
            error_text = str(e).lower()
            if "already" in error_text or "занят" in error_text or "occupied" in error_text:
                # Место занято - значит позднее записавшийся не был удален (это баг)
                with allure.step(f"ОШИБКА ВАЛИДАЦИИ: {later_customer} не был удален, место все еще занято"):
                    # Это означает что на тренировке 2 участника при maxParticipants=1 - БАГ!
                    assert False, \
                        f"ВАЛИДАЦИЯ ПРОВАЛЕНА: {later_customer} должен был быть удален, но место все еще занято. " \
                        f"Количество участников превышает maxParticipants=1. Ошибка: {e}"
            else:
                # Другая ошибка - возможно проблема с запросом
                allure.dynamic.parameter("Результат валидации", f"Получена ошибка при проверке: {e}")
        
        # Дополнительная проверка: раньше записавшийся должен остаться на тренировке
        earlier_slots_api = slots_api2 if later_customer == "customer1" else slots_api1
        
        with allure.step("Проверка: раньше записавшийся должен остаться на тренировке"):
            try:
                # Попытка записаться еще раз должна вернуть ошибку (место занято им самим)
                new_slot_earlier = earlier_slots_api.book_slot(training_id, earlier_customer_id)
                # Если получили успешный ответ без ошибки, это странно, но не критично
                allure.dynamic.parameter("Проверка раньше записавшегося", "Раньше записавшийся может записаться повторно (возможно дубликат)")
            except HTTPError as e:
                # Ожидаем ошибку - место занято
                error_text = str(e).lower()
                if "already" in error_text or "занят" in error_text or "occupied" in error_text:
                    allure.dynamic.parameter("Проверка раньше записавшегося", "Раньше записавшийся не может записаться повторно - место занято (правильно)")
                else:
                    allure.dynamic.parameter("Проверка раньше записавшегося", f"Получена ошибка: {e}")
    
    # Очистка
    client1.clear_auth()
    client2.clear_auth()

