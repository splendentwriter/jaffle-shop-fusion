#!/usr/bin/env python3
"""
One-off generator for the Marketing domain's raw seed CSVs (Phase 16 of the
e-commerce platform build-out): campaigns, campaign channels, a unified
marketing event stream, and customer acquisition.

Design notes:
- "Campaign events", "email events", "SMS events", and "push events" from
  the plan are consolidated into one raw_marketing_events table with
  channel + event_type discriminators, not four near-identical tables -
  same reasoning as raw_web_events (Phase 4), the payment ledger (Phase 8),
  and inventory transactions (Phase 10). A campaign can genuinely span more
  than one channel, so campaign_channels stays a real bridge table rather
  than a single field.
- "Attribution" isn't raw data - it's derived. It's built as a core-layer
  model (fct_campaign_attribution) linking marketing events to real
  checkouts, not generated here.

Reads raw_customers.csv and raw_checkouts.csv.

Usage:
    python3 scripts/generate_marketing_domain_seeds.py
"""

import csv
import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path

random.seed(139)

SEEDS_DIR = Path(__file__).resolve().parent.parent / "seeds" / "jaffle-data"

CAMPAIGNS = [
    {"name": "Welcome Series", "type": "lifecycle", "channels": ["email"]},
    {"name": "Summer Sale Blast", "type": "promotional", "channels": ["email", "social"]},
    {"name": "Retargeting Q2", "type": "retargeting", "channels": ["social", "display"]},
    {"name": "New Customer Push", "type": "acquisition", "channels": ["search", "social"]},
    {"name": "Loyalty SMS Alerts", "type": "lifecycle", "channels": ["sms"]},
    {"name": "App Engagement", "type": "engagement", "channels": ["push"]},
    {"name": "BlackFriday Blitz", "type": "promotional", "channels": ["email", "sms", "social"]},
    {"name": "Winback Campaign", "type": "retention", "channels": ["email"]},
]
ACQUISITION_CHANNELS = ["organic", "paid_search", "paid_social", "email", "referral", "direct"]
EMAIL_EVENT_TYPES = ["sent", "delivered", "opened", "clicked", "bounced", "unsubscribed"]
SMS_EVENT_TYPES = ["sent", "delivered", "clicked", "opted_out"]
PUSH_EVENT_TYPES = ["sent", "delivered", "opened"]
SOCIAL_DISPLAY_SEARCH_EVENT_TYPES = ["impression", "click"]


def load_csv(name):
    with open(SEEDS_DIR / name) as f:
        return list(csv.DictReader(f))


def write_csv(name, fieldnames, rows):
    path = SEEDS_DIR / name
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} rows to {path}")


def fmt(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%S")


def event_types_for_channel(channel):
    return {
        "email": EMAIL_EVENT_TYPES,
        "sms": SMS_EVENT_TYPES,
        "push": PUSH_EVENT_TYPES,
    }.get(channel, SOCIAL_DISPLAY_SEARCH_EVENT_TYPES)


def main():
    customers = load_csv("raw_customers.csv")
    print(f"generating marketing-domain seeds for {len(CAMPAIGNS)} campaigns, {len(customers)} customers")

    now = datetime.now()
    campaigns = []
    campaign_channels = []
    campaign_ids_by_channel = {}

    for c in CAMPAIGNS:
        campaign_id = str(uuid.uuid4())
        starts_at = now - timedelta(days=random.randint(20, 300))
        ends_at = starts_at + timedelta(days=random.randint(7, 45))
        campaigns.append(
            {
                "id": campaign_id,
                "name": c["name"],
                "campaign_type": c["type"],
                "starts_at": fmt(starts_at),
                "ends_at": fmt(ends_at),
                "budget_cents": random.randint(50000, 500000),
                "is_active": ends_at > now,
            }
        )
        for channel in c["channels"]:
            campaign_channels.append({"id": str(uuid.uuid4()), "campaign_id": campaign_id, "channel": channel})
            campaign_ids_by_channel.setdefault(channel, []).append((campaign_id, starts_at, ends_at))

    marketing_events = []
    for customer in customers:
        # not every customer is marketed to in this window
        if random.random() < 0.35:
            continue
        n_touches = random.randint(1, 5)
        for _ in range(n_touches):
            channel = random.choice(list(campaign_ids_by_channel))
            campaign_id, starts_at, ends_at = random.choice(campaign_ids_by_channel[channel])
            occurred_at = starts_at + timedelta(seconds=random.randint(0, max(1, int((ends_at - starts_at).total_seconds()))))

            possible_types = event_types_for_channel(channel)
            # funnel-ish: sent/impression always happens; later stages are rarer
            event_type = random.choices(
                possible_types,
                weights=[60] + [max(5, 40 // i) for i in range(1, len(possible_types))],
            )[0]

            marketing_events.append(
                {
                    "id": str(uuid.uuid4()),
                    "campaign_id": campaign_id,
                    "customer_id": customer["id"],
                    "channel": channel,
                    "event_type": event_type,
                    "occurred_at": fmt(occurred_at),
                }
            )

    acquisitions = []
    for customer in customers:
        channel = random.choices(
            ACQUISITION_CHANNELS,
            weights=[30, 20, 15, 15, 10, 10],
        )[0]
        campaign_id = ""
        if channel in ("paid_search", "paid_social", "email"):
            channel_key = {"paid_search": "search", "paid_social": "social", "email": "email"}[channel]
            candidates = campaign_ids_by_channel.get(channel_key)
            if candidates and random.random() < 0.6:
                campaign_id = random.choice(candidates)[0]

        acquisitions.append(
            {
                "customer_id": customer["id"],
                "acquisition_channel": channel,
                "campaign_id": campaign_id,
                "acquired_at": fmt(now - timedelta(days=random.randint(1, 720))),
            }
        )

    write_csv(
        "raw_campaigns.csv",
        ["id", "name", "campaign_type", "starts_at", "ends_at", "budget_cents", "is_active"],
        campaigns,
    )
    write_csv("raw_campaign_channels.csv", ["id", "campaign_id", "channel"], campaign_channels)
    write_csv(
        "raw_marketing_events.csv",
        ["id", "campaign_id", "customer_id", "channel", "event_type", "occurred_at"],
        marketing_events,
    )
    write_csv(
        "raw_customer_acquisition.csv",
        ["customer_id", "acquisition_channel", "campaign_id", "acquired_at"],
        acquisitions,
    )


if __name__ == "__main__":
    main()
