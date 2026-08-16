#!/usr/bin/env python3
"""
One-off generator for the Fulfillment domain's raw seed CSVs (Phase 12 of
the e-commerce platform build-out): fulfillment orders, fulfillment items,
and fulfillment events.

Design note: "picking" and "packing" from the plan are event_type values on
one raw_fulfillment_events log, not separate tables - they're stages a
fulfillment order passes through, same reasoning as every other
event/state consolidation in this build (cart_events, checkout_events,
inventory_transactions).

Reads raw_checkouts.csv (only completed ones - a checkout without a
captured payment has nothing to fulfill), raw_checkout_items.csv, and
raw_warehouses.csv.

Usage:
    python3 scripts/generate_fulfillment_domain_seeds.py
"""

import csv
import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path

random.seed(97)

SEEDS_DIR = Path(__file__).resolve().parent.parent / "seeds" / "jaffle-data"


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
    checkouts = load_csv("raw_checkouts.csv")
    warehouses = load_csv("raw_warehouses.csv")
    warehouse_ids = [w["id"] for w in warehouses]
    completed = [c for c in checkouts if c["status"] == "completed"]

    checkout_items_by_checkout = {}
    for item in load_csv("raw_checkout_items.csv"):
        checkout_items_by_checkout.setdefault(item["checkout_id"], []).append(item)

    print(f"generating fulfillment-domain seeds for {len(completed)} completed checkouts")

    fulfillment_orders = []
    fulfillment_items = []
    fulfillment_events = []

    for checkout in completed:
        items = checkout_items_by_checkout.get(checkout["id"], [])
        if not items:
            continue

        fo_id = str(uuid.uuid4())
        completed_at = datetime.fromisoformat(checkout["completed_at"])
        cursor = completed_at + timedelta(minutes=random.randint(5, 60))

        fulfillment_events.append(
            {"id": str(uuid.uuid4()), "fulfillment_order_id": fo_id, "event_type": "created", "occurred_at": fmt(cursor)}
        )

        # progression: most orders go all the way to shipped; some are still
        # mid-flight (recent orders), a few get cancelled before shipping
        outcome = random.choices(["shipped", "in_progress", "cancelled"], weights=[75, 15, 10])[0]
        stages = ["picking_started", "picking_completed", "packing_started", "packing_completed", "shipped"]

        if outcome == "cancelled":
            n_stages = random.randint(0, 2)
        elif outcome == "in_progress":
            n_stages = random.randint(1, 4)
        else:
            n_stages = len(stages)

        for stage in stages[:n_stages]:
            cursor += timedelta(hours=random.uniform(0.5, 12))
            fulfillment_events.append(
                {"id": str(uuid.uuid4()), "fulfillment_order_id": fo_id, "event_type": stage, "occurred_at": fmt(cursor)}
            )

        if outcome == "cancelled":
            cursor += timedelta(hours=random.uniform(0.5, 6))
            fulfillment_events.append(
                {"id": str(uuid.uuid4()), "fulfillment_order_id": fo_id, "event_type": "cancelled", "occurred_at": fmt(cursor)}
            )
            status = "cancelled"
            completed_ts = ""
        elif outcome == "shipped":
            status = "shipped"
            completed_ts = fmt(cursor)
        else:
            status = {0: "pending", 1: "picking", 2: "picking", 3: "packed", 4: "packed"}[n_stages]
            completed_ts = ""

        fulfillment_orders.append(
            {
                "id": fo_id,
                "checkout_id": checkout["id"],
                "warehouse_id": random.choice(warehouse_ids),
                "status": status,
                "created_at": fmt(completed_at + timedelta(minutes=random.randint(5, 60))),
                "completed_at": completed_ts,
            }
        )

        for item in items:
            fulfillment_items.append(
                {
                    "id": str(uuid.uuid4()),
                    "fulfillment_order_id": fo_id,
                    "sku": item["sku"],
                    "quantity": item["quantity"],
                }
            )

    write_csv(
        "raw_fulfillment_orders.csv",
        ["id", "checkout_id", "warehouse_id", "status", "created_at", "completed_at"],
        fulfillment_orders,
    )
    write_csv("raw_fulfillment_items.csv", ["id", "fulfillment_order_id", "sku", "quantity"], fulfillment_items)
    write_csv(
        "raw_fulfillment_events.csv",
        ["id", "fulfillment_order_id", "event_type", "occurred_at"],
        fulfillment_events,
    )


if __name__ == "__main__":
    main()
