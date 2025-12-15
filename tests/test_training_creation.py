from services.trainings.api_trainings import TrainingsAPI
import pytest
import allure
from requests.exceptions import HTTPError

@allure.feature("Тренировки")
@pytest.mark.coach
@pytest.mark.parametrize("logged_in_user", ["coach"], indirect=True)
def test_coach_can_create_training(logged_in_user):
    trainings_api = TrainingsAPI(logged_in_user.client)
    
    with allure.step("Коуч создаёт тренировку с 1 местом"):
        training = trainings_api.create_group_training()
        training_id = training["id"]
    
    assert training_id > 0
    allure.dynamic.parameter("Созданная тренировка ID", training_id)

@allure.feature("Тренировки")
@pytest.mark.coach
@pytest.mark.parametrize("logged_in_user", ["coach"], indirect=True)
def test_coach_cannot_create_overlapping_training(logged_in_user):
    trainings_api = TrainingsAPI(logged_in_user.client)
    
    with allure.step("Создаём первую тренировку"):
        training1 = trainings_api.create_group_training()
        date = training1["dateFrom"]
        time_from = training1["timeFrom"]
        time_to = training1["timeTo"]

    with allure.step(f"Пытаемся создать вторую на то же время — ожидаем 400 overlapping"):
        with pytest.raises(HTTPError) as exc_info:
            trainings_api.create_overlapping_training(date, time_from, time_to)

        assert exc_info.value.response.status_code == 400
        assert "overlapping" in exc_info.value.response.text.lower()