import pytest
import allure

@allure.feature("Клиенты")
@pytest.mark.customer
def test_two_customers_login_success(customer1, customer2):
    with allure.step("Проверка первого клиента"):
        personal1 = customer1.get_personal_data()
        print(f"\n=== КЛИЕНТ 1 ===")
        print(f"ID: {personal1.user.id}")
        print(f"Phone: {personal1.user.phone}")
        print(f"Full Name: {personal1.fullName}")

    with allure.step("Проверка второго клиента"):
        personal2 = customer2.get_personal_data()
        print(f"\n=== КЛИЕНТ 2 ===")
        print(f"ID: {personal2.user.id}")
        print(f"Phone: {personal2.user.phone}")
        print(f"Full Name: {personal2.fullName}")

    with allure.step("Проверка, что это разные пользователи"):
        assert personal1.user.id != personal2.user.id
        assert personal1.user.phone != personal2.user.phone

    allure.dynamic.title("Два разных клиента успешно залогинены")