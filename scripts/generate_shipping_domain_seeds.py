#!/usr/bin/env python3
"""
One-off generator for the Shipping domain's raw seed CSVs (Phase 13 of the
e-commerce platform build-out): carriers, shipments, shipment items,
tracking events, and delivery attempts.

Design note: "shipping methods" from the plan already exists as a field on
raw_checkouts (Phase 6: standard/express/pickup) - not re-modeled here.
Shipments are only created for shipped fulfillment orders whose checkout
picked an actual shipping method; pickup orders never get a shipment,
which is a real consistency check tying back to Phase 6, not an omission.

Reads raw_fulfillment_orders.csv (Phase 12, only status='shipped' rows),
raw_fulfillment_items.csv, and raw_checkouts.csv (to exclude pickup orders).

Usage:
    python3 scripts/generate_shipping_domain_seeds.py
"""

import csv
import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path

random.seed(101)

SEEDS_DIR = Path(__file__).resolve().parent.parent / "seeds" / "jaffle-data"

CARRIERS = [
    {"id": "CAR-UPS", "name": "UPS", "tracking_url_template": "https://ups.example/track/{tracking_number}"},
    {"id": "CAR-FEDEX", "name": "FedEx", "tracking_url_template": "https://fedex.example/track/{tracking_number}"},
    {"id": "CAR-USPS", "name": "USPS", "tracking_url_template": "https://usps.example/track/{tracking_number}"},
]
TRACKING_STAGES = ["label_created", "picked_up", "in_transit", "out_for_delivery", "delivered"]


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
    fulfillment_orders = load_csv("raw_fulfillment_orders.csv")
    checkouts_by_id = {c["id"]: c for c in load_csv("raw_checkouts.csv")}
    fulfillment_items_by_order = {}
    for item in load_csv("raw_fulfillment_items.csv"):
        fulfillment_items_by_order.setdefault(item["fulfillment_order_id"], []).append(item)

    shippable_orders = [
        fo
        for fo in fulfillment_orders
        if fo["status"] == "shipped" and checkouts_by_id.get(fo["checkout_id"], {}).get("shipping_method") != "pickup"
    ]
    print(f"generating shipping-domain seeds for {len(shippable_orders)} shippable fulfillment orders")

    shipments = []
    shipment_items = []
    tracking_events = []
    delivery_attempts = []

    for fo in shippable_orders:
        shipment_id = str(uuid.uuid4())
        carrier = random.choice(CARRIERS)
        shipped_at = datetime.fromisoformat(fo["completed_at"])
        checkout = checkouts_by_id[fo["checkout_id"]]
        transit_days = {"express": 2, "standard": 5}.get(checkout["shipping_method"], 5)
        estimated_delivery_at = shipped_at + timedelta(days=transit_days)

        outcome = random.choices(["delivered", "delayed", "lost", "in_transit"], weights=[80, 10, 3, 7])[0]
        status = "delivered" if outcome == "delivered" else outcome

        shipments.append(
            {
                "id": shipment_id,
                "fulfillment_order_id": fo["id"],
                "carrier_id": carrier["id"],
                "tracking_number": str(random.randint(10**11, 10**12 - 1)),
                "shipped_at": fmt(shipped_at),
                "estimated_delivery_at": fmt(estimated_delivery_at),
                "status": status,
            }
        )

        for item in fulfillment_items_by_order.get(fo["id"], []):
            shipment_items.append(
                {
                    "id": str(uuid.uuid4()),
                    "shipment_id": shipment_id,
                    "sku": item["sku"],
                    "quantity": item["quantity"],
                }
            )

        cursor = shipped_at
        stages = TRACKING_STAGES if outcome in ("delivered", "delayed") else TRACKING_STAGES[: random.randint(2, 4)]
        actual_delivery_at = None
        for stage in stages:
            cursor += timedelta(hours=random.uniform(2, 30))
            if outcome == "delayed" and stage == "delivered":
                cursor += timedelta(days=random.randint(1, 4))
            if stage == "delivered":
                actual_delivery_at = cursor
            tracking_events.append(
                {
                    "id": str(uuid.uuid4()),
                    "shipment_id": shipment_id,
                    "event_type": stage,
                    "location": random.choice(["Origin Facility", "Regional Hub", "Local Facility", "Destination"]),
                    "occurred_at": fmt(cursor),
                }
            )
        if outcome == "lost":
            tracking_events.append(
                {
                    "id": str(uuid.uuid4()),
                    "shipment_id": shipment_id,
                    "event_type": "exception",
                    "location": "Regional Hub",
                    "occurred_at": fmt(cursor + timedelta(hours=random.randint(1, 12))),
                }
            )

        if actual_delivery_at:
            n_attempts = random.choices([1, 2], weights=[85, 15])[0]
            for attempt_number in range(1, n_attempts + 1):
                attempt_time = actual_delivery_at - timedelta(days=(n_attempts - attempt_number))
                outcome_choice = "delivered" if attempt_number == n_attempts else random.choice(["no_access", "refused"])
                delivery_attempts.append(
                    {
                        "id": str(uuid.uuid4()),
                        "shipment_id": shipment_id,
                        "attempted_at": fmt(attempt_time),
                        "outcome": outcome_choice,
                        "attempt_number": attempt_number,
                    }
                )

    write_csv("raw_carriers.csv", ["id", "name", "tracking_url_template"], CARRIERS)
    write_csv(
        "raw_shipments.csv",
        ["id", "fulfillment_order_id", "carrier_id", "tracking_number", "shipped_at", "estimated_delivery_at", "status"],
        shipments,
    )
    write_csv("raw_shipment_items.csv", ["id", "shipment_id", "sku", "quantity"], shipment_items)
    write_csv(
        "raw_tracking_events.csv",
        ["id", "shipment_id", "event_type", "location", "occurred_at"],
        tracking_events,
    )
    write_csv(
        "raw_delivery_attempts.csv",
        ["id", "shipment_id", "attempted_at", "outcome", "attempt_number"],
        delivery_attempts,
    )


if __name__ == "__main__":
    main()
