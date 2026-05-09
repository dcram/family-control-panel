import httpx


def get_current_weather(city: str, api_key: str) -> str | None:
    if not api_key:
        return None
    try:
        with httpx.Client(timeout=5.0) as client:
            r = client.get(
                url="https://api.openweathermap.org/data/2.5/weather",
                params={"q": city, "appid": api_key, "units": "metric", "lang": "fr"},
            )
            r.raise_for_status()
            data = r.json()
            temp = round(data["main"]["temp"])
            desc: str = data["weather"][0]["description"]
            return f"{temp}°C, {desc}"
    except Exception:
        return None
