from __future__ import annotations

from abc import ABC, abstractmethod

from models.flight import FlightDeal


class FlightSource(ABC):
    name: str

    @abstractmethod
    def fetch(self) -> list[FlightDeal]:
        """Fetch and normalize flight deals from this source."""
