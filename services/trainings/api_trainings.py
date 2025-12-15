import allure
import os
from dotenv import load_dotenv
from .endpoints import TrainingsEndpoints
from .models import TrainingResponse
from .payloads import create_group_training_payload
from utils.client import APIClient

load_dotenv()

class TrainingsAPI:
    def __init__(self, client: APIClient):
        self.client = client
        self.endpoints = TrainingsEndpoints

    @allure.step("Коуч создаёт групповую тренировку по спорту {sport}")
    def create_group_training(self, sport: str = None) -> dict:
        sport = sport or os.getenv("TRAINING_SPORT", "fitness")
        url = self.endpoints.CREATE_GROUP.format(sport=sport)
        payload = create_group_training_payload()

        response = self.client.post(url, json=payload)
        response.raise_for_status()

        training_data = TrainingResponse(**response.json()[0])

        with allure.step(f"Тренировка создана: ID={training_data.id}"):
            pass

        return training_data.__dict__

    @allure.step("Коуч пытается создать тренировку на занятое время")
    def create_overlapping_training(self, date: str, time_from: str, time_to: str, sport: str = "fitness"):
        payload = create_group_training_payload()
        payload.update({
            "repeatStartDate": date,
            "repeatEndDate": date,
            "trainingSingleDate": {
                "dateFrom": date,
                "dateTo": date,
                "timeFrom": time_from,
                "timeTo": time_to
            },
            "name": payload["name"] + " (overlapping)"
        })

        url = self.endpoints.CREATE_GROUP.format(sport=sport)
        response = self.client.post(url, json=payload)
        response.raise_for_status()  
        return response.json()