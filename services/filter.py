from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from models.flight import FlightDeal


ALLOWED_ORIGINS = {"HKG", "SZX", "CAN"}
MAX_PRICE_CNY = 4000
DEPARTURE_BEFORE = date.fromisoformat("2026-10-05")
ALLOWED_TRIP_TYPES = {"round_trip", "open_jaw"}


@dataclass(frozen=True)
class RouteAlert:
    name: str
    origin: str
    destinations: set[str]
    start_date: date
    end_date: date
    max_price_cny: int
    trip_types: set[str]


ROUTE_ALERTS = [
    RouteAlert(
        name="TOS to Tallinn or Helsinki, February 2027",
        origin="TOS",
        destinations={"TLL", "HEL"},
        start_date=date.fromisoformat("2027-02-01"),
        end_date=date.fromisoformat("2027-03-01"),
        max_price_cny=500,
        trip_types={"one_way"},
    ),
    RouteAlert(
        name="Paris to Hamburg, late January 2027",
        origin="PAR",
        destinations={"HAM"},
        start_date=date.fromisoformat("2027-01-20"),
        end_date=date.fromisoformat("2027-02-01"),
        max_price_cny=300,
        trip_types={"one_way"},
    ),
    RouteAlert(
        name="Copenhagen to Evenes, February 1-5 2027",
        origin="CPH",
        destinations={"EVE"},
        start_date=date.fromisoformat("2027-02-01"),
        end_date=date.fromisoformat("2027-02-06"),
        max_price_cny=600,
        trip_types={"one_way"},
    ),
]

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
    if matches_route_alert(deal):
        return True

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


def matches_route_alert(deal: FlightDeal) -> bool:
    try:
        departure = date.fromisoformat(deal.departure_date)
    except ValueError:
        return False

    for alert in ROUTE_ALERTS:
        if deal.origin != alert.origin:
            continue
        if not _destination_matches(deal.destination, alert.destinations):
            continue
        if not alert.start_date <= departure < alert.end_date:
            continue
        if deal.price_cny <= 0 or deal.price_cny > alert.max_price_cny:
            continue
        if deal.trip_type not in alert.trip_types:
            continue
        return True

    return False


def _destination_matches(destination: str, allowed_codes: set[str]) -> bool:
    value = destination.upper()
    return any(code in value.split() or value == code for code in allowed_codes)


def filter_deals(deals: list[FlightDeal]) -> list[FlightDeal]:
    return [deal for deal in deals if is_valid_deal(deal)]
