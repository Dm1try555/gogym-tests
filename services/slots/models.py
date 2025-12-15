from pydantic import BaseModel
from typing import Optional, Dict, Any

class Person(BaseModel):
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
    meta: Dict[str, Any]
    timezone: str

class Customer(BaseModel):
    id: int
    createdAt: str
    updatedAt: str
    height: Optional[int] = None
    weight: Optional[int] = None
    step: int
    rating: float
    hiddenFromCustomersAt: Optional[str] = None
    deletedAt: Optional[str] = None
    person: Person

class SlotResponse(BaseModel):
    id: int
    createdAt: str
    updatedAt: str
    paidAt: str
    isNewTimeConfirmed: Optional[bool] = None
    isPackageRelated: bool
    isPaidViaPaymentProvider: bool
    customer: Customer
    ward: Optional[Any] = None
