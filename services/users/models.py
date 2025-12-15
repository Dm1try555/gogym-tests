from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class Person(BaseModel):
    id: int

class UserInfo(BaseModel):
    id: int
    isActive: bool
    role: int
    person: Person

class LoginSuccessResponse(BaseModel):
    user: UserInfo
    accessToken: str

class ErrorResponse(BaseModel):
    statusCode: int
    exceptionType: str = Field(default="HttpException")
    message: str
    errorParams: dict = Field(default_factory=dict)
    errorParamsArray: list = Field(default_factory=list)
    timestamp: Optional[str] = None
    endpoint: Optional[str] = None
    method: Optional[str] = None


class Avatar(BaseModel):
    id: int
    createdAt: str
    updatedAt: str
    url: str
    key: str
    type: str
    name: str

class UserInPersonal(BaseModel):
    id: int
    createdAt: str
    updatedAt: str
    email: Optional[str] = None
    phone: Optional[str] = None
    role: int  # 4 = coach, 5 = customer (client)
    isActive: bool
    lastActivity: str
    lastSeenAt: str
    permissions: Optional[Any] = None
    language: str
    firebaseSignInProvider: Optional[Any] = None
    company: Optional[Any] = None

class CustomerInfo(BaseModel):
    id: int
    createdAt: str
    updatedAt: str
    height: Optional[int] = None
    weight: Optional[int] = None
    step: int
    rating: int
    reviewsCount: Optional[int] = None
    completedTrainingCount: int
    # другие поля по необходимости

class CoachLevel(BaseModel):
    id: int
    createdAt: str
    updatedAt: str
    level: str
    sportName: str
    sportCategory: str
    sportSeason: Optional[str] = None

class CoachInfo(BaseModel):
    id: int
    createdAt: str
    updatedAt: str
    rating: int
    step: int
    isVerified: bool
    # ... другие поля, если нужно
    completedTrainingCount: Optional[int] = None
    coachLevels: Optional[List[CoachLevel]] = None

class MetaInfo(BaseModel):
    isWelcomeToApp: bool
    isProfileCompleted: bool
    isPreReleaseSignUp: bool
    isFirstProTariff: bool
    isFirstPremiumTariff: bool
    isWelcomeGuidePassed: bool
    completedTrainingsCount: int
    completedUniqueSportTrainingsCount: int

class PersonalDataResponse(BaseModel):
    id: int
    createdAt: str
    updatedAt: str
    firstName: str
    lastName: str
    fullName: str
    gender: int
    birthDate: str
    geonameId: int
    toponymName: str
    countryCode: str
    selfDescription: Optional[str] = None
    step: int
    deletedAt: Optional[str] = None
    meta: MetaInfo
    timezone: str
    user: UserInPersonal
    avatar: Avatar
    coach: Optional[CoachInfo] = None
    customer: Optional[CustomerInfo] = None