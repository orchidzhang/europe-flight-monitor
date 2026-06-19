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
    failed_sources = 0
    for source in sources:
        print(f"Fetching deals from {source.name}...")
        try:
            source_deals = source.fetch()
            all_deals.extend(source_deals)
            print(f"{source.name} returned {len(source_deals)} normalized deals.")
        except Exception as exc:
            failed_sources += 1
            print(f"Source failed: {source.name}: {exc}")

    if failed_sources == len(sources):
        print("All sources failed. Marking this run as failed.")
        return 1

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
