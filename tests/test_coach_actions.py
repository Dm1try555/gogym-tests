import pytest
import allure

@allure.feature("Коуч")
@pytest.mark.coach
@pytest.mark.parametrize("logged_in_user", ["coach"], indirect=True)
def test_coach_login_and_check(logged_in_user):
    with allure.step("Проверка, что залогинились под коучем"):
        personal = logged_in_user.get_personal_data()
        
        print(f"\n=== КОУЧ ===")
        print(f"ID: {personal.user.id}")
        print(f"Role: {personal.user.role} (должен быть 4)")
        print(f"Email: {personal.user.email}")
        print(f"Phone: {personal.user.phone}")
        print(f"Full Name: {personal.fullName}")
        print("=============\n")
        
        assert personal.user.role == 4, f"Ожидалась роль коуча (4), получена {personal.user.role}"