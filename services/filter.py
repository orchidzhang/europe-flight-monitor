from __future__ import annotations

from datetime import date

from models.flight import FlightDeal


ALLOWED_ORIGINS = {"HKG", "SZX", "CAN"}
MAX_PRICE_CNY = 4000
DEPARTURE_BEFORE = date.fromisoformat("2026-10-05")
ALLOWED_TRIP_TYPES = {"round_trip", "open_jaw"}

EXCLUDED_COUNTRIES = {
    "United Kingdom",
    "England",
    "Scotland",
    "Wales",
    "Northern Ireland",
    "Britain",
    "Ireland",
}

EUROPE_COUNTRIES = {
    "Albania",
    "Andorra",
    "Austria",
    "Belarus",
    "Belgium",
    "Bosnia and Herzegovina",
    "Bulgaria",
    "Croatia",
    "Cyprus",
    "Czech Republic",
    "Denmark",
    "Estonia",
    "Finland",
    "France",
    "Germany",
    "Greece",
    "Hungary",
    "Iceland",
    "Italy",
    "Kosovo",
    "Latvia",
    "Liechtenstein",
    "Lithuania",
    "Luxembourg",
    "Malta",
    "Moldova",
    "Monaco",
    "Montenegro",
    "Netherlands",
    "North Macedonia",
    "Norway",
    "Poland",
    "Portugal",
    "Romania",
    "San Marino",
    "Serbia",
    "Slovakia",
    "Slovenia",
    "Spain",
    "Sweden",
    "Switzerland",
    "Turkey",
    "Ukraine",
    "Vatican City",
}


def is_valid_deal(deal: FlightDeal) -> bool:
    if deal.origin not in ALLOWED_ORIGINS:
        return False

    if deal.destination_country not in EUROPE_COUNTRIES:
        return False

    if deal.destination_country in EXCLUDED_COUNTRIES:
        return False

    if deal.price_cny <= 0 or deal.price_cny > MAX_PRICE_CNY:
        return False

    if deal.trip_type not in ALLOWED_TRIP_TYPES:
        return False

    try:
        departure = date.fromisoformat(deal.departure_date)
    except ValueError:
        return False

    return departure < DEPARTURE_BEFORE


def filter_deals(deals: list[FlightDeal]) -> list[FlightDeal]:
    return [deal for deal in deals if is_valid_deal(deal)]
