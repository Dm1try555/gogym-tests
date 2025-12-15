# from __future__ import annotations

# from typing import Any, Dict, List, Optional

# from pydantic import BaseModel, field_validator


# class TrainingLocation(BaseModel):
#     id: int
#     countryCode: str
#     townId: Any
#     toponymName: Optional[str] = None
#     address: Dict[str, Any]
#     longitude: float
#     latitude: float

#     @field_validator("address", mode="before")
#     def parse_address(cls, v: Any) -> Dict[str, Any]:
#         """
#         В ответе address может приходить как JSON-строка, поэтому парсим как в trainings.models.
#         """
#         if isinstance(v, str):
#             import json

#             return json.loads(v)
#         return v


# class Coach(BaseModel):
#     id: int


# class TrainingPackageTrainingItem(BaseModel):
#     """
#     Описание одной тренировки, входящей в пакет (по образцу из таски).
#     """

#     id: int
#     name: str
#     gender: int
#     format: int
#     dateRangeStart: str
#     dateRangeEnd: str
#     minAge: int
#     maxAge: int
#     maxParticipants: int
#     price: int
#     paymentType: str
#     currency: str
#     dateFrom: str
#     dateTo: str
#     timeFrom: str
#     timeTo: str
#     weekDayFrom: str
#     weekDayTo: str
#     sportName: str
#     sportCategory: Optional[str] = None
#     sportSeason: Optional[str] = None
#     groupId: str
#     coach: Coach
#     trainingLocation: TrainingLocation
#     # служебные флаги оплаты/отмены и т.п.
#     isPaidToCoach: bool
#     isPaidToCoachFromTrainingPackage: bool
#     meta: Optional[str] = None


# class CreateTrainingPackageResponse(BaseModel):
#     """
#     Вспомогательная модель: просто оборачивает список тренировок пакета.
#     """

#     items: List[TrainingPackageTrainingItem]


