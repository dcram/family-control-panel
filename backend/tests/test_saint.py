from datetime import date

from app.services.saint import get_saint_of_day


def test_known_saints() -> None:
    assert get_saint_of_day(d=date(2026, 1, 1)) == "Marie"
    assert get_saint_of_day(d=date(2026, 6, 24)) == "Jean-Baptiste"
    assert get_saint_of_day(d=date(2026, 12, 25)) == "Noël"
    assert get_saint_of_day(d=date(2026, 11, 1)) == "Toussaint"
    assert get_saint_of_day(d=date(2026, 12, 31)) == "Sylvestre"


def test_leap_day() -> None:
    assert get_saint_of_day(d=date(2028, 2, 29)) == "Auguste"
