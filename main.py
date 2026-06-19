from __future__ import annotations

from sources import SecretFlyingSource
from services.dedupe import NotifiedStore
from services.filter import filter_deals
from services.notifier_email import EmailNotifier


def run() -> int:
    sources = [
        SecretFlyingSource(),
    ]

    all_deals = []
    for source in sources:
        print(f"Fetching deals from {source.name}...")
        try:
            all_deals.extend(source.fetch())
        except Exception as exc:
            print(f"Source failed: {source.name}: {exc}")

    print(f"Fetched {len(all_deals)} normalized deals.")

    matched = filter_deals(all_deals)
    print(f"Matched {len(matched)} deals after filtering.")

    store = NotifiedStore("data/notified.json")
    new_deals = store.filter_new(matched)
    print(f"Found {len(new_deals)} new deals after dedupe.")

    if not new_deals:
        return 0

    notifier = EmailNotifier()
    if notifier.send(new_deals):
        store.mark_notified(new_deals)
        print(f"Sent email and marked {len(new_deals)} deals as notified.")
    else:
        print("Email was not sent. Deals remain unmarked for a future retry.")

    return 0


if __name__ == "__main__":
    raise SystemExit(run())
