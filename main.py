from __future__ import annotations

from sources import SecretFlyingSource
from services.dedupe import NotifiedStore
from services.filter import filter_deals
from services.notifier_email import EmailNotifier
from services.report import write_run_report


def run() -> int:
    sources = [
        SecretFlyingSource(),
    ]

    all_deals = []
    failed_sources = 0
    failed_source_names = []
    source_counts = {}
    for source in sources:
        print(f"Fetching deals from {source.name}...")
        try:
            source_deals = source.fetch()
            all_deals.extend(source_deals)
            source_counts[source.name] = len(source_deals)
            print(f"{source.name} returned {len(source_deals)} normalized deals.")
        except Exception as exc:
            failed_sources += 1
            failed_source_names.append(source.name)
            print(f"Source failed: {source.name}: {exc}")

    if failed_sources == len(sources):
        print("All sources failed. Marking this run as failed.")
        write_run_report(
            source_counts=source_counts,
            fetched_count=len(all_deals),
            matched_deals=[],
            new_deals=[],
            email_sent=False,
            failed_sources=failed_source_names,
        )
        return 1

    print(f"Fetched {len(all_deals)} normalized deals.")

    matched = filter_deals(all_deals)
    print(f"Matched {len(matched)} deals after filtering.")

    store = NotifiedStore("data/notified.json")
    new_deals = store.filter_new(matched)
    print(f"Found {len(new_deals)} new deals after dedupe.")

    email_sent = False
    if not new_deals:
        write_run_report(
            source_counts=source_counts,
            fetched_count=len(all_deals),
            matched_deals=matched,
            new_deals=new_deals,
            email_sent=email_sent,
            failed_sources=failed_source_names,
        )
        return 0

    notifier = EmailNotifier()
    if notifier.send(new_deals):
        email_sent = True
        store.mark_notified(new_deals)
        print(f"Sent email and marked {len(new_deals)} deals as notified.")
    else:
        print("Email was not sent. Deals remain unmarked for a future retry.")

    write_run_report(
        source_counts=source_counts,
        fetched_count=len(all_deals),
        matched_deals=matched,
        new_deals=new_deals,
        email_sent=email_sent,
        failed_sources=failed_source_names,
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(run())
