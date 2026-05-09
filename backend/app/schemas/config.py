from pydantic import BaseModel


class KioskConfigOut(BaseModel):
    weather_city: str
    quote_text: str | None
    quote_author: str | None
    quote_work: str | None

    model_config = {"from_attributes": True}


class WeatherCityUpdate(BaseModel):
    weather_city: str


class QuoteUpdate(BaseModel):
    quote_text: str | None = None
    quote_author: str | None = None
    quote_work: str | None = None
