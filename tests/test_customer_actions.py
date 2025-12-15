import pytest
import allure

@allure.feature("Клиент")
@pytest.mark.customer
@pytest.mark.parametrize("logged_in_user", ["customer"], indirect=True)
def test_customer_login_and_check(logged_in_user):
    with allure.step("Проверка, что залогинились под клиентом"):
        personal = logged_in_user.get_personal_data()
        
        print(f"\n=== КЛИЕНТ ===")
        print(f"ID: {personal.user.id}")
        print(f"Role: {personal.user.role} (должен быть 5)")
        print(f"Email: {personal.user.email}")
        print(f"Phone: {personal.user.phone}")
        print(f"Full Name: {personal.fullName}")
        print("================\n")
        
        assert personal.user.role == 5, f"Ожидалась роль клиента (5), получена {personal.user.role}"