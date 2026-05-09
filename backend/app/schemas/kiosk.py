from datetime import date

from pydantic import BaseModel


class KioskInfoOut(BaseModel):
    date: date
    saint: str | None
    weather: str | None
    quote_text: str | None
    quote_author: str | None
    quote_work: str | None
