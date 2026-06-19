from __future__ import annotations

import json
from pathlib import Path

from models.flight import FlightDeal


class NotifiedStore:
    def __init__(self, path: str | Path = "data/notified.json") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._keys = self._load()

    def _load(self) -> set[str]:
        if not self.path.exists():
            self.path.write_text("[]\n", encoding="utf-8")
            return set()

        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return set()

        if not isinstance(data, list):
            return set()

        return {str(item) for item in data}

    def save(self) -> None:
        ordered = sorted(self._keys)
        self.path.write_text(
            json.dumps(ordered, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def key_for(self, deal: FlightDeal) -> str:
        return "|".join(
            [
                deal.origin,
                deal.destination,
                deal.departure_date,
                deal.return_date,
                str(deal.price_cny),
            ]
        )

    def filter_new(self, deals: list[FlightDeal]) -> list[FlightDeal]:
        return [deal for deal in deals if self.key_for(deal) not in self._keys]

    def mark_notified(self, deals: list[FlightDeal]) -> None:
        for deal in deals:
            self._keys.add(self.key_for(deal))
        self.save()
