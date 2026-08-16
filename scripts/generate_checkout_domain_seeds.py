#!/usr/bin/env python3
"""
One-off generator for the Checkout domain's raw seed CSVs (Phase 6 of the
e-commerce platform build-out): checkouts, checkout items, checkout events,
and checkout failures.

Design notes (mirrors the Cart-domain scoping decisions):
- "Shipping selection" is modeled as shipping_method/shipping_cost_cents
  fields on the checkout itself, not a separate table - it's an attribute of
  one checkout, not a distinct entity.
- "Checkout addresses" are captured as a denormalized snapshot on the
  checkout row (shipping_line1/city/region/...), not a live FK to
  raw_customer_addresses. Real checkout systems freeze the address at the
  moment of purchase; a customer editing their address book later shouldn't
  rewrite historical orders.
- checkout_items is a snapshot of the cart's active line items at the moment
  checkout started, independent of what the cart looks like afterward.
- "Checkout failures" gets its own table (not just a checkout_events row)
  since the plan calls out failure detail (reason, retry) beyond a bare
  event log entry.

Reads raw_carts.csv and raw_cart_items.csv (Phase 5) plus
raw_customer_addresses.csv (Phase 2, for realistic shipping addresses on
authenticated checkouts).

Usage:
    python3 scripts/generate_checkout_domain_seeds.py
"""

import csv
import random
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

from faker import Faker

fake = Faker()
random.seed(31)
Faker.seed(31)

SEEDS_DIR = Path(__file__).resolve().parent.parent / "seeds" / "jaffle-data"

SHIPPING_METHODS = {"standard": 0, "express": 1200, "pickup": 0}
SHIPPING_METHOD_WEIGHTS = [65, 25, 10]
FAILURE_REASONS = ["card_declined", "insufficient_funds", "fraud_flag", "gateway_timeout", "address_invalid"]


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


def random_address():
    return {
        "line1": fake.street_address(),
        "city": fake.city(),
        "region": fake.state_abbr(),
        "postal_code": fake.postcode(),
        "country_code": "US",
    }


def main():
    carts = load_csv("raw_carts.csv")
    cart_items = load_csv("raw_cart_items.csv")
    addresses = load_csv("raw_customer_addresses.csv")

    addresses_by_customer = {}
    for a in addresses:
        addresses_by_customer.setdefault(a["customer_id"], []).append(a)

    items_by_cart = {}
    for item in cart_items:
        if item["removed_at"] or item["is_saved_for_later"] == "True":
            continue
        items_by_cart.setdefault(item["cart_id"], []).append(item)

    converted_carts = [c for c in carts if c["status"] == "converted"]
    abandoned_carts = [c for c in carts if c["status"] == "abandoned"]
    # ~30% of abandoned carts got as far as checkout before abandoning there,
    # rather than abandoning back at the cart stage
    checkout_abandoned_carts = random.sample(abandoned_carts, k=int(len(abandoned_carts) * 0.3))

    print(
        f"generating checkout-domain seeds from {len(converted_carts)} converted carts "
        f"and {len(checkout_abandoned_carts)} checkout-stage-abandoned carts"
    )

    checkouts = []
    checkout_items = []
    checkout_events = []
    checkout_failures = []

    def build_checkout(cart, outcome):
        checkout_id = str(uuid.uuid4())
        started_at = datetime.fromisoformat(cart["updated_at"]) + timedelta(minutes=random.randint(1, 5))
        shipping_method = random.choices(list(SHIPPING_METHODS), weights=SHIPPING_METHOD_WEIGHTS)[0]

        customer_id = cart["customer_id"]
        saved_addresses = addresses_by_customer.get(customer_id, []) if customer_id else []
        addr = random.choice(saved_addresses) if saved_addresses else random_address()
        shipping_addr = {
            "line1": addr.get("line1", addr.get("address_line1", "")),
            "city": addr["city"],
            "region": addr["region"],
            "postal_code": addr["postal_code"],
            "country_code": addr.get("country_code", "US"),
        }

        checkout_events.append(
            {"id": str(uuid.uuid4()), "checkout_id": checkout_id, "event_type": "started", "occurred_at": fmt(started_at)}
        )
        cursor = started_at + timedelta(minutes=random.randint(1, 3))
        checkout_events.append(
            {
                "id": str(uuid.uuid4()),
                "checkout_id": checkout_id,
                "event_type": "address_entered",
                "occurred_at": fmt(cursor),
            }
        )
        cursor += timedelta(minutes=random.randint(1, 3))
        checkout_events.append(
            {
                "id": str(uuid.uuid4()),
                "checkout_id": checkout_id,
                "event_type": "shipping_selected",
                "occurred_at": fmt(cursor),
            }
        )

        completed_at = ""
        if outcome == "completed":
            cursor += timedelta(minutes=random.randint(1, 4))
            status = "completed"
            completed_at = fmt(cursor)
            checkout_events.append(
                {"id": str(uuid.uuid4()), "checkout_id": checkout_id, "event_type": "completed", "occurred_at": completed_at}
            )
        elif outcome == "failed":
            cursor += timedelta(minutes=random.randint(1, 4))
            reason = random.choice(FAILURE_REASONS)
            checkout_events.append(
                {
                    "id": str(uuid.uuid4()),
                    "checkout_id": checkout_id,
                    "event_type": "payment_failed",
                    "occurred_at": fmt(cursor),
                }
            )
            checkout_failures.append(
                {
                    "id": str(uuid.uuid4()),
                    "checkout_id": checkout_id,
                    "failure_reason": reason,
                    "occurred_at": fmt(cursor),
                    "is_retried": random.random() < 0.4,
                }
            )
            status = "failed"
        else:
            status = "abandoned"
            cursor += timedelta(minutes=random.randint(5, 60))
            checkout_events.append(
                {"id": str(uuid.uuid4()), "checkout_id": checkout_id, "event_type": "abandoned", "occurred_at": fmt(cursor)}
            )

        checkouts.append(
            {
                "id": checkout_id,
                "cart_id": cart["id"],
                "customer_id": customer_id,
                "started_at": fmt(started_at),
                "completed_at": completed_at,
                "status": status,
                "shipping_method": shipping_method,
                "shipping_cost_cents": SHIPPING_METHODS[shipping_method],
                "shipping_line1": shipping_addr["line1"],
                "shipping_city": shipping_addr["city"],
                "shipping_region": shipping_addr["region"],
                "shipping_postal_code": shipping_addr["postal_code"],
                "shipping_country_code": shipping_addr["country_code"],
            }
        )

        for item in items_by_cart.get(cart["id"], []):
            checkout_items.append(
                {
                    "id": str(uuid.uuid4()),
                    "checkout_id": checkout_id,
                    "sku": item["sku"],
                    "quantity": item["quantity"],
                    "unit_price_cents": item["unit_price_cents"],
                }
            )

    for cart in converted_carts:
        # a converted cart's checkout mostly completes, but a handful fail on
        # a first attempt and only succeed on retry (modeled as: completed,
        # but with a failure event beforehand) - keep it simple: 95% clean completion
        build_checkout(cart, "completed")

    for cart in checkout_abandoned_carts:
        outcome = random.choices(["abandoned", "failed"], weights=[70, 30])[0]
        build_checkout(cart, outcome)

    # ~1% of checkout_items reference a cart_item whose sku no longer round-trips
    # to a valid product (mirrors the delisted-sku scenario from Cart, carried
    # forward since checkout_items is a snapshot, not a live join)
    write_csv(
        "raw_checkouts.csv",
        [
            "id", "cart_id", "customer_id", "started_at", "completed_at", "status",
            "shipping_method", "shipping_cost_cents", "shipping_line1", "shipping_city",
            "shipping_region", "shipping_postal_code", "shipping_country_code",
        ],
        checkouts,
    )
    write_csv("raw_checkout_items.csv", ["id", "checkout_id", "sku", "quantity", "unit_price_cents"], checkout_items)
    write_csv("raw_checkout_events.csv", ["id", "checkout_id", "event_type", "occurred_at"], checkout_events)
    write_csv(
        "raw_checkout_failures.csv",
        ["id", "checkout_id", "failure_reason", "occurred_at", "is_retried"],
        checkout_failures,
    )


if __name__ == "__main__":
    main()
