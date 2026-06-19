from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage

from models.flight import FlightDeal


SUBJECT = "发现符合条件的欧洲特价机票"
DEFAULT_EMAIL_TO = "orchidzhang@outlook.com"

TRIP_TYPE_LABELS = {
    "round_trip": "往返",
    "open_jaw": "开口",
    "one_way": "单程",
}

ORIGIN_LABELS = {
    "HKG": "香港 HKG",
    "SZX": "深圳 SZX",
    "CAN": "广州 CAN",
    "TOS": "特罗姆瑟 TOS",
    "PAR": "巴黎 PAR",
}


def build_email_body(deals: list[FlightDeal]) -> str:
    parts = [f"发现 {len(deals)} 条符合条件的机票", ""]

    for deal in deals:
        parts.extend(
            [
                "--------------------------------",
                "",
                "来源：",
                deal.source,
                "",
                "行程类型：",
                TRIP_TYPE_LABELS.get(deal.trip_type, deal.trip_type),
                "",
                "出发地：",
                ORIGIN_LABELS.get(deal.origin, deal.origin),
                "",
                "目的地：",
                f"{deal.destination} ({deal.destination_country})".strip(),
                "",
                "价格：",
                f"{deal.price_cny} RMB",
                "",
                "去程：",
                deal.departure_date,
                "",
                "返程：",
                deal.return_date or "未识别",
                "",
                "链接：",
                deal.url,
                "",
            ]
        )

    parts.append("--------------------------------")
    return "\n".join(parts)


class EmailNotifier:
    def __init__(self) -> None:
        self.smtp_host = os.getenv("SMTP_HOST", "").strip()
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "").strip()
        self.smtp_password = os.getenv("SMTP_PASSWORD", "").strip()
        self.email_to = os.getenv("EMAIL_TO", DEFAULT_EMAIL_TO).strip() or DEFAULT_EMAIL_TO

    def is_configured(self) -> bool:
        return bool(self.smtp_host and self.smtp_user and self.smtp_password and self.email_to)

    def send(self, deals: list[FlightDeal]) -> bool:
        if not deals:
            return True

        if not self.is_configured():
            print("SMTP is not configured. Matched deals were not marked as notified.")
            print(build_email_body(deals))
            return False

        message = EmailMessage()
        message["Subject"] = SUBJECT
        message["From"] = self.smtp_user
        message["To"] = self.email_to
        message.set_content(build_email_body(deals))

        with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=30) as smtp:
            smtp.starttls()
            smtp.login(self.smtp_user, self.smtp_password)
            smtp.send_message(message)

        return True
