from pydantic import BaseModel, field_validator
from typing import Dict, Any

class TrainingLocation(BaseModel):
    id: int
    countryCode: str
    townId: Any
    toponymName: str
    address: Dict[str, str]
    longitude: float
    latitude: float

    @field_validator('address', mode='before')
    def parse_address(cls, v):
        if isinstance(v, str):
            import json
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                raise ValueError(f"Invalid JSON in address: {v}")
        return v

class Coach(BaseModel):
    id: int

class TrainingResponse(BaseModel):
    id: int
    name: str
    format: int
    isOnline: bool
    gender: int
    maxParticipants: int
    price: int
    paymentType: str
    dateFrom: str
    timeFrom: str
    timeTo: str
    sportName: str
    groupId: str
    coach: Coach
    trainingLocation: TrainingLocation