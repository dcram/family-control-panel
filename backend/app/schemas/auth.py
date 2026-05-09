import uuid

from pydantic import BaseModel


class LoginRequest(BaseModel):
    login: str
    password: str


class ParentOut(BaseModel):
    id: uuid.UUID
    login: str

    model_config = {"from_attributes": True}


class VerifyPinRequest(BaseModel):
    pin: str


class VerifyPinOut(BaseModel):
    holder_type: str
    holder_id: uuid.UUID
