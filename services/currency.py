from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP


class CurrencyConverter:
    """Fixed-rate currency converter with a small surface for future live rates."""

    DEFAULT_RATES_TO_CNY = {
        "CNY": Decimal("1"),
        "RMB": Decimal("1"),
        "EUR": Decimal("7.80"),
        "USD": Decimal("7.20"),
        "HKD": Decimal("0.92"),
        "GBP": Decimal("9.10"),
        "JPY": Decimal("0.05"),
        "SGD": Decimal("5.35"),
    }

    def __init__(self, rates_to_cny: dict[str, Decimal] | None = None) -> None:
        self.rates_to_cny = rates_to_cny or self.DEFAULT_RATES_TO_CNY

    def to_cny(self, amount: float | int | Decimal, currency: str) -> int:
        normalized = self.normalize_currency(currency)
        rate = self.rates_to_cny.get(normalized)
        if rate is None:
            raise ValueError(f"Unsupported currency: {currency}")
        value = Decimal(str(amount)) * rate
        return int(value.quantize(Decimal("1"), rounding=ROUND_HALF_UP))

    @staticmethod
    def normalize_currency(currency: str) -> str:
        value = currency.strip().upper()
        if value in {"¥", "￥", "RMB", "CNY", "CN¥"}:
            return "CNY"
        if value in {"€", "EUR"}:
            return "EUR"
        if value in {"$", "US$", "USD"}:
            return "USD"
        if value in {"HK$", "HKD"}:
            return "HKD"
        if value in {"£", "GBP"}:
            return "GBP"
        if value in {"JPY", "JP¥"}:
            return "JPY"
        if value in {"SGD", "S$"}:
            return "SGD"
        return value
