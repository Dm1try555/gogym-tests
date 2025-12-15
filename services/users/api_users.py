import allure
from .endpoints import UsersEndpoints
from .models import LoginSuccessResponse, ErrorResponse, PersonalDataResponse
from .payloads import login_by_email_payload, login_by_phone_payload
from utils.client import APIClient

class UsersAPI:
    def __init__(self, client: APIClient):
        self.client = client
        self.endpoints = UsersEndpoints

    @allure.step("Логин по email")
    def login_by_email(self, email: str, password: str) -> str:
        payload = login_by_email_payload(email, password)
        response = self.client.post(self.endpoints.LOGIN_BY_EMAIL, json=payload)

        if response.status_code == 400:
            try:
                error = ErrorResponse(**response.json())
                if "logged in" in error.message.lower():
                    with allure.step("Обнаружен активный логин → принудительный логаут"):
                        self.client.clear_auth()
                    # Повторный логин
                    response = self.client.post(self.endpoints.LOGIN_BY_EMAIL, json=payload)
            except:
                pass

        response.raise_for_status()
        data = LoginSuccessResponse(**response.json())
        self.client.set_auth_token(data.accessToken)
        return data.accessToken

    @allure.step("Логин по телефону")
    def login_by_phone(self, phone: str, password: str) -> str:
        payload = login_by_phone_payload(phone, password)
        response = self.client.post(self.endpoints.LOGIN_BY_PHONE, json=payload)

        if response.status_code == 400:
            try:
                error = ErrorResponse(**response.json())
                if "logged in" in error.message.lower():
                    with allure.step("Обнаружен активный логин → принудительный логаут"):
                        self.client.clear_auth()
                    response = self.client.post(self.endpoints.LOGIN_BY_PHONE, json=payload)
            except:
                pass

        response.raise_for_status()
        data = LoginSuccessResponse(**response.json())
        self.client.set_auth_token(data.accessToken)
        return data.accessToken
    

    @allure.step("Получить личные данные пользователя (personal-data)")
    def get_personal_data(self) -> PersonalDataResponse:
        response = self.client.get(self.endpoints.PERSONAL_DATA)
        response.raise_for_status()
        data = PersonalDataResponse(**response.json())
        return data