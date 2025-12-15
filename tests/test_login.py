# import allure
# import os
# from dotenv import load_dotenv

# load_dotenv()

# @allure.feature("Авторизация")
# @allure.story("Успешный логин разных пользователей через personal-data")
# def test_two_different_users_can_login(client1_logged_in, client2_logged_in):
#     with allure.step("Получение данных пользователя 1 (попытка логина по email)"):
#         personal1 = client1_logged_in.get_personal_data()
#         assert personal1.user.id > 0
#         print(f"User 1 (email login): ID={personal1.user.id}, Role={personal1.user.role}, Email={personal1.user.email}, Phone={personal1.user.phone}")

#     with allure.step("Получение данных пользователя 2 (логин по телефону)"):
#         personal2 = client2_logged_in.get_personal_data()
#         assert personal2.user.id > 0
#         print(f"User 2 (phone login): ID={personal2.user.id}, Role={personal2.user.role}, Email={personal2.user.email}, Phone={personal2.user.phone}")

#     with allure.step("Проверка, что это два разных пользователя"):
#         assert personal1.user.id != personal2.user.id, f"Оба логина привели к одному и тому же пользователю ID={personal1.user.id}"

#     with allure.step("Проверка соответствия способу логина"):
#         # Для логина по телефону — должен быть phone
#         expected_phone = os.getenv("CLIENT2_PHONE").lstrip('+')
#         assert str(personal2.user.phone) == expected_phone, \
#             f"Ожидался phone {expected_phone}, получен {personal2.user.phone}"

#         # Для логина по email — хотя бы проверяем, что логин прошёл (даже если роль не та)
#         assert personal1.user.id > 0

#     allure.dynamic.parameter("User 1 (email) ID", personal1.user.id)
#     allure.dynamic.parameter("User 1 Role", personal1.user.role)
#     allure.dynamic.parameter("User 2 (phone) ID", personal2.user.id)
#     allure.dynamic.parameter("User 2 Role", personal2.user.role)