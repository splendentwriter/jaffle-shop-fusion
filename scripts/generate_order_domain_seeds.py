#!/usr/bin/env python3
"""
One-off generator for the Order domain's raw seed CSVs (Phase 7 of the
e-commerce platform build-out): order addresses, order status history, and
order adjustments.

Scoping decision, flagged explicitly rather than silently decided: this
project already has a fully-built, actively-streamed orders system (the
original Jaffle Shop tutorial's raw_orders/raw_items, fed continuously by
scripts/generate_stream_data.py) with ~62k orders. Phases 5-6 (Cart,
Checkout) built a *separate*, much smaller funnel (1,200 carts / 579
checkouts) grounded in this session's own web-behaviour data. The two don't
share row-level identity - the checkout funnel's timestamps and volumes are
independent of the pre-existing bulk order history, so fabricating a 1:1
checkout->order link would be a fake join dressed up as data. Rather than
force that, Phase 7 extends the *existing* orders (order_addresses,
order_status_history, order_adjustments are new capabilities the original
orders mart never had) and leaves checkout-to-order attribution as an
explicit gap rather than a fabricated one.

Given raw_orders.csv has ~62k rows and keeps growing via the live streaming
service, generating full coverage for every order isn't attempted (or even
meaningful for a synthetic test dataset) - a proportionate sample is used
instead, same "incomplete dimension" realism as Phase 3's product catalogue.

Usage:
    python3 scripts/generate_order_domain_seeds.py
"""

import csv
import random
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

from faker import Faker

fake = Faker()
random.seed(41)
Faker.seed(41)

SEEDS_DIR = Path(__file__).resolve().parent.parent / "seeds" / "jaffle-data"

N_ORDERS_WITH_ADDRESSES = 5000
N_ORDERS_WITH_ADJUSTMENTS = 600
STATUS_SEQUENCE = ["placed", "processing", "fulfilled", "delivered"]
ADJUSTMENT_TYPES = ["discount", "goodwill_credit", "price_correction", "tax_correction"]


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


def main():
    orders = load_csv("raw_orders.csv")
    print(f"generating order-domain seeds against {len(orders)} existing orders")

    address_orders = random.sample(orders, k=min(N_ORDERS_WITH_ADDRESSES, len(orders)))
    adjustment_orders = random.sample(orders, k=min(N_ORDERS_WITH_ADJUSTMENTS, len(orders)))

    order_addresses = []
    for order in address_orders:
        ordered_at = datetime.fromisoformat(order["ordered_at"])
        line1 = fake.street_address()
        city = fake.city()
        region = fake.state_abbr()
        postal_code = fake.postcode()
        order_addresses.append(
            {
                "id": str(uuid.uuid4()),
                "order_id": order["id"],
                "address_type": "shipping",
                "line1": line1,
                "city": city,
                "region": region,
                "postal_code": postal_code,
                "country_code": "US",
            }
        )
        # ~20% of orders also captured a distinct billing address
        if random.random() < 0.2:
            order_addresses.append(
                {
                    "id": str(uuid.uuid4()),
                    "order_id": order["id"],
                    "address_type": "billing",
                    "line1": fake.street_address(),
                    "city": fake.city(),
                    "region": fake.state_abbr(),
                    "postal_code": fake.postcode(),
                    "country_code": "US",
                }
            )

    order_status_history = []
    for order in address_orders:
        ordered_at = datetime.fromisoformat(order["ordered_at"])
        cursor = ordered_at
        is_cancelled = random.random() < 0.06
        sequence = STATUS_SEQUENCE[: random.randint(1, 4)] if is_cancelled else STATUS_SEQUENCE

        for i, status in enumerate(sequence):
            if i > 0:
                cursor += timedelta(hours=random.randint(1, 48))
            order_status_history.append(
                {"id": str(uuid.uuid4()), "order_id": order["id"], "status": status, "occurred_at": fmt(cursor)}
            )
            if is_cancelled and i == len(sequence) - 1:
                cursor += timedelta(hours=random.randint(1, 12))
                order_status_history.append(
                    {"id": str(uuid.uuid4()), "order_id": order["id"], "status": "cancelled", "occurred_at": fmt(cursor)}
                )

    order_adjustments = []
    for order in adjustment_orders:
        ordered_at = datetime.fromisoformat(order["ordered_at"])
        applied_at = ordered_at + timedelta(hours=random.randint(1, 96))
        adjustment_type = random.choice(ADJUSTMENT_TYPES)
        order_total = int(order["order_total"])
        if adjustment_type in ("discount", "goodwill_credit"):
            amount_cents = -random.randint(50, max(51, order_total // 3))
        else:
            amount_cents = random.choice([-1, 1]) * random.randint(10, 200)

        order_adjustments.append(
            {
                "id": str(uuid.uuid4()),
                "order_id": order["id"],
                "adjustment_type": adjustment_type,
                "amount_cents": amount_cents,
                "reason": fake.sentence(nb_words=6),
                "applied_at": fmt(applied_at),
            }
        )

    # ~0.5% of status history rows reference an order_id that's since been
    # purged from the source system (a known upstream retention-policy gap)
    n_orphans = max(1, int(len(order_status_history) * 0.005))
    for _ in range(n_orphans):
        order_status_history.append(
            {
                "id": str(uuid.uuid4()),
                "order_id": str(uuid.uuid4()),
                "status": "placed",
                "occurred_at": fmt(datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=random.randint(1, 300))),
            }
        )

    write_csv(
        "raw_order_addresses.csv",
        ["id", "order_id", "address_type", "line1", "city", "region", "postal_code", "country_code"],
        order_addresses,
    )
    write_csv("raw_order_status_history.csv", ["id", "order_id", "status", "occurred_at"], order_status_history)
    write_csv(
        "raw_order_adjustments.csv",
        ["id", "order_id", "adjustment_type", "amount_cents", "reason", "applied_at"],
        order_adjustments,
    )


if __name__ == "__main__":
    main()
