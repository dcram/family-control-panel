from pydantic import BaseModel, field_validator


class PinSet(BaseModel):
    pin: str

    @field_validator("pin")
    @classmethod
    def validate_format(cls, v: str) -> str:
        if not v.isdigit() or len(v) != 4:
            raise ValueError("Le PIN doit être composé de 4 chiffres")
        return v


class PinOut(BaseModel):
    pin: str | None = None
