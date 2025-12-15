import requests
import allure
import json
import os
from typing import Optional, Dict, Any

class APIClient:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = os.getenv("BASE_URL")

    def _log_response(self, response: requests.Response, step_name: str = "Ответ сервера"):
        with allure.step(f"{step_name}: {response.status_code}"):
            try:
                response_json = response.json()
                pretty_text = json.dumps(response_json, indent=2, ensure_ascii=False)
            except:
                pretty_text = response.text

            allure.attach(pretty_text, name="Response", attachment_type=allure.attachment_type.JSON)

            print(f"\n=== {step_name.upper()} ({response.status_code}) ===")
            print(pretty_text)
            print("=" * 50 + "\n")

    @allure.step("POST запрос к {endpoint}")
    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None, **kwargs):
        url = self.base_url + endpoint
        with allure.step(f"POST {url}"):
            payload = data or kwargs.get('json')
            if payload is not None:
                allure.attach(json.dumps(payload, indent=2, ensure_ascii=False),
                            name="Request Payload", attachment_type=allure.attachment_type.JSON)

            kwargs.pop('json', None)  # убираем дубликат

            response = self.session.post(url, json=payload, **kwargs)
            self._log_response(response, "Ответ POST запроса")
        return response

    @allure.step("GET запрос к {endpoint}")
    def get(self, endpoint: str, **kwargs):
        url = self.base_url + endpoint
        response = self.session.get(url, **kwargs)
        self._log_response(response, "Ответ GET запроса")
        return response

    @allure.step("DELETE запрос к {endpoint}")
    def delete(self, endpoint: str, **kwargs):
        url = self.base_url + endpoint
        response = self.session.delete(url, **kwargs)
        self._log_response(response, "Ответ DELETE запроса")
        return response

    def set_auth_token(self, token: str):
        self.session.headers.update({"Authorization": f"Bearer {token}"})

    def clear_auth(self):
        self.session.headers.pop("Authorization", None)
        self.session.cookies.clear()