#!/usr/bin/env python3
"""
One-off generator for the Web/App Behaviour domain's raw seed CSVs (Phase 4
of the e-commerce platform build-out): sessions and a single unified event
stream.

Design note: the build-out plan lists "page views / product views / searches
/ events / user interactions" as separate bullets, but modeling each as its
own raw table would mean five near-identical tables (session_id, sku,
timestamp...) with no real difference in grain. Real clickstream systems
(Segment, Snowplow, GA4) emit one typed event stream instead, so that's what
this generates: raw_web_events with an event_type discriminator column.

Reads raw_customers.csv and raw_customer_devices.csv for realistic
authenticated-session linkage, and raw_products.csv for product_view/search
targets.

Usage:
    python3 scripts/generate_web_behaviour_seeds.py
"""

import csv
import random
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

from faker import Faker

fake = Faker()
random.seed(11)
Faker.seed(11)

SEEDS_DIR = Path(__file__).resolve().parent.parent / "seeds" / "jaffle-data"

REFERRERS = ["direct", "organic_search", "paid_search", "social", "email", "referral"]
PAGE_TYPES = ["home", "category", "product", "search_results", "cart", "account"]
N_SESSIONS = 3000


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


def rand_dt(days_back_max=180):
    delta = timedelta(days=random.randint(0, days_back_max), seconds=random.randint(0, 86400))
    return datetime.now(timezone.utc).replace(tzinfo=None) - delta


def fmt(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%S")


def gen_sessions(customers, devices_by_customer):
    sessions = []
    for _ in range(N_SESSIONS):
        started_at = rand_dt()
        duration_min = random.choices([1, 3, 8, 20, 45], weights=[20, 30, 25, 15, 10])[0]
        ended_at = started_at + timedelta(minutes=duration_min)

        is_authenticated = random.random() < 0.6
        customer_id = ""
        device_id = ""
        if is_authenticated:
            customer = random.choice(customers)
            customer_id = customer["id"]
            candidate_devices = devices_by_customer.get(customer_id)
            if candidate_devices:
                device_id = random.choice(candidate_devices)

        session = {
            "id": str(uuid.uuid4()),
            "customer_id": customer_id,
            "device_id": device_id,
            "started_at": fmt(started_at),
            "ended_at": fmt(ended_at),
            "landing_page": "/" + random.choice(["", "category/jaffles", "category/beverages", "search"]),
            "referrer_source": random.choice(REFERRERS),
            "is_authenticated": is_authenticated,
        }
        sessions.append(session)

    # ~1% of sessions never closed (dropped connection, app killed mid-browse)
    for s in random.sample(sessions, k=int(N_SESSIONS * 0.01)):
        s["ended_at"] = ""

    # ~0.5% have clock-skew: ended_at logged before started_at
    for s in random.sample(sessions, k=int(N_SESSIONS * 0.005)):
        if s["ended_at"]:
            s["started_at"], s["ended_at"] = s["ended_at"], s["started_at"]

    return sessions


SEARCH_TERMS = ["jaffle", "coffee", "vegetarian", "spicy", "smoothie", "gluten free", "iced coffee", "chai"]


def gen_events(sessions, products):
    events = []
    skus = [p["sku"] for p in products]

    for session in sessions:
        if not session["started_at"]:
            continue
        try:
            session_start = datetime.fromisoformat(session["started_at"])
        except ValueError:
            continue

        n_events = random.choices([1, 2, 4, 7, 12], weights=[15, 25, 30, 20, 10])[0]
        cursor = session_start
        funnel_progressed_to_cart = False

        for i in range(n_events):
            cursor += timedelta(seconds=random.randint(5, 240))

            if i == 0:
                event_type = "page_view"
            elif random.random() < 0.15:
                event_type = "search"
            elif random.random() < 0.5:
                event_type = "product_view"
            elif not funnel_progressed_to_cart and random.random() < 0.2:
                event_type = "add_to_cart"
                funnel_progressed_to_cart = True
            else:
                event_type = "page_view"

            event = {
                "id": str(uuid.uuid4()),
                "session_id": session["id"],
                "event_type": event_type,
                "occurred_at": fmt(cursor),
                "page_url": "",
                "product_sku": "",
                "search_query": "",
            }
            if event_type == "search":
                event["search_query"] = random.choice(SEARCH_TERMS)
                event["page_url"] = "/search"
            elif event_type in ("product_view", "add_to_cart"):
                event["product_sku"] = random.choice(skus)
                event["page_url"] = f"/product/{event['product_sku'].lower()}"
            else:
                event["page_url"] = "/" + random.choice(PAGE_TYPES)

            events.append(event)

    # ~0.3% of events are orphaned: reference a session_id that doesn't exist
    # (a dropped/purged session record, or an event that arrived from a
    # client whose session was never persisted upstream)
    n_orphans = int(len(events) * 0.003)
    for _ in range(n_orphans):
        occurred_at = rand_dt()
        events.append(
            {
                "id": str(uuid.uuid4()),
                "session_id": str(uuid.uuid4()),
                "event_type": "page_view",
                "occurred_at": fmt(occurred_at),
                "page_url": "/" + random.choice(PAGE_TYPES),
                "product_sku": "",
                "search_query": "",
            }
        )

    random.shuffle(events)
    return events


def main():
    customers = load_csv("raw_customers.csv")
    devices = load_csv("raw_customer_devices.csv")
    products = load_csv("raw_products.csv")

    devices_by_customer = {}
    for d in devices:
        devices_by_customer.setdefault(d["customer_id"], []).append(d["id"])

    print(f"generating web-behaviour seeds for {len(customers)} customers, {len(products)} products")

    sessions = gen_sessions(customers, devices_by_customer)
    events = gen_events(sessions, products)

    write_csv(
        "raw_sessions.csv",
        ["id", "customer_id", "device_id", "started_at", "ended_at", "landing_page", "referrer_source", "is_authenticated"],
        sessions,
    )
    write_csv(
        "raw_web_events.csv",
        ["id", "session_id", "event_type", "occurred_at", "page_url", "product_sku", "search_query"],
        events,
    )


if __name__ == "__main__":
    main()
