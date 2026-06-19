from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass
class FlightDeal:
    source: str
    title: str
    origin: str
    destination: str
    destination_country: str
    price_cny: int
    currency: str
    trip_type: str
    departure_date: str
    return_date: str
    url: str
    raw_text: str

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "FlightDeal":
        return cls(
            source=str(data.get("source", "")),
            title=str(data.get("title", "")),
            origin=str(data.get("origin", "")),
            destination=str(data.get("destination", "")),
            destination_country=str(data.get("destination_country", "")),
            price_cny=int(data.get("price_cny") or 0),
            currency=str(data.get("currency", "CNY")),
            trip_type=str(data.get("trip_type", "")),
            departure_date=str(data.get("departure_date", "")),
            return_date=str(data.get("return_date", "")),
            url=str(data.get("url", "")),
            raw_text=str(data.get("raw_text", "")),
        )
