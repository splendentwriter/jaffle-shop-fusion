#!/usr/bin/env python3
"""
One-off generator for the Inventory domain's raw seed CSVs (Phase 10 of the
e-commerce platform build-out): warehouses, inventory levels, inventory
transactions, and stock reservations.

Design notes:
- Warehouses are modeled as distinct distribution centers, separate from
  the 6 retail stores - the retail stores serve walk-in/pickup, warehouses
  fulfill the shippable checkout flow built in Phase 6.
- "Stock movements" (transfers) and "inventory adjustments" are both
  transaction_type values on one raw_inventory_transactions ledger rather
  than separate tables, same reasoning as Payments' unified transaction
  ledger in Phase 8: a movement or an adjustment IS a transaction, not a
  different kind of thing.
- raw_inventory_levels is a current-state snapshot (one row per
  warehouse+sku); it gets an SCD2 dbt snapshot in the core layer
  (inventory_levels_snapshot -> dim_inventory_level), matching the plan's
  explicit "dim_inventory_location" SCD2 candidate.

Reads raw_products.csv for the sku population and raw_checkouts.csv for
which checkouts to attach a stock reservation to.

Usage:
    python3 scripts/generate_inventory_domain_seeds.py
"""

import csv
import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path

random.seed(71)

SEEDS_DIR = Path(__file__).resolve().parent.parent / "seeds" / "jaffle-data"

WAREHOUSES = [
    {"id": "WH-EAST", "name": "East Coast Distribution Center", "region": "US-EAST"},
    {"id": "WH-WEST", "name": "West Coast Distribution Center", "region": "US-WEST"},
]
ADJUSTMENT_REASONS = ["cycle_count_correction", "damaged_goods", "expired_stock", "theft_shrinkage"]


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
    products = load_csv("raw_products.csv")
    checkouts = load_csv("raw_checkouts.csv")
    skus = [p["sku"] for p in products]
    print(f"generating inventory-domain seeds for {len(WAREHOUSES)} warehouses x {len(skus)} products")

    warehouses = [{"id": w["id"], "name": w["name"], "region": w["region"], "is_active": True} for w in WAREHOUSES]

    transactions = []
    levels = []
    now = datetime.now()

    for warehouse in WAREHOUSES:
        for sku in skus:
            cursor = now - timedelta(days=120)
            quantity = 0
            n_events = random.randint(15, 30)
            for _ in range(n_events):
                cursor += timedelta(days=random.uniform(1, 6))
                if cursor > now:
                    break
                roll = random.random()
                if roll < 0.35:
                    tx_type, delta = "receipt", random.randint(20, 100)
                elif roll < 0.85:
                    tx_type, delta = "sale", -random.randint(1, 15)
                elif roll < 0.93:
                    direction = random.choice(["transfer_in", "transfer_out"])
                    tx_type, delta = direction, (random.randint(5, 20) if direction == "transfer_in" else -random.randint(5, 20))
                else:
                    tx_type = "adjustment"
                    delta = random.choice([-1, 1]) * random.randint(1, 10)

                # don't let a sale/transfer_out/adjustment push stock negative
                # in the ledger itself; a real system would reject the tx
                if quantity + delta < 0:
                    delta = -quantity if quantity > 0 else 0
                    if delta == 0:
                        continue

                quantity += delta
                transactions.append(
                    {
                        "id": str(uuid.uuid4()),
                        "warehouse_id": warehouse["id"],
                        "sku": sku,
                        "transaction_type": tx_type,
                        "quantity_delta": delta,
                        "adjustment_reason": random.choice(ADJUSTMENT_REASONS) if tx_type == "adjustment" else "",
                        "occurred_at": fmt(cursor),
                    }
                )

            levels.append(
                {
                    "id": str(uuid.uuid4()),
                    "warehouse_id": warehouse["id"],
                    "sku": sku,
                    "quantity_on_hand": quantity,
                    "reorder_point": random.randint(10, 30),
                    "updated_at": fmt(now),
                }
            )

    # ~2% of transactions reference a sku that's since been delisted (mirrors
    # the same scenario introduced in Cart/Checkout for consistency)
    for tx in random.sample(transactions, k=max(1, int(len(transactions) * 0.02))):
        tx["sku"] = "JAF-999-DELISTED"

    reservations = []
    reservable_checkouts = [c for c in checkouts if c["status"] in ("completed", "failed", "abandoned")]
    sampled_checkouts = random.sample(reservable_checkouts, k=int(len(reservable_checkouts) * 0.6))
    checkout_items_by_checkout = {}
    for item in load_csv("raw_checkout_items.csv"):
        checkout_items_by_checkout.setdefault(item["checkout_id"], []).append(item)

    for checkout in sampled_checkouts:
        items = checkout_items_by_checkout.get(checkout["id"], [])
        if not items:
            continue
        warehouse = random.choice(WAREHOUSES)
        reserved_at = datetime.fromisoformat(checkout["started_at"])
        for item in items:
            if checkout["status"] == "completed":
                status = "committed"
                released_at = ""
            elif checkout["status"] == "failed":
                status = "released"
                released_at = fmt(reserved_at + timedelta(minutes=random.randint(2, 10)))
            else:
                status = random.choice(["released", "expired"])
                released_at = fmt(reserved_at + timedelta(minutes=random.randint(10, 60)))

            reservations.append(
                {
                    "id": str(uuid.uuid4()),
                    "warehouse_id": warehouse["id"],
                    "sku": item["sku"],
                    "checkout_id": checkout["id"],
                    "quantity": item["quantity"],
                    "reserved_at": fmt(reserved_at),
                    "released_at": released_at,
                    "status": status,
                }
            )

    write_csv("raw_warehouses.csv", ["id", "name", "region", "is_active"], warehouses)
    write_csv(
        "raw_inventory_levels.csv",
        ["id", "warehouse_id", "sku", "quantity_on_hand", "reorder_point", "updated_at"],
        levels,
    )
    write_csv(
        "raw_inventory_transactions.csv",
        ["id", "warehouse_id", "sku", "transaction_type", "quantity_delta", "adjustment_reason", "occurred_at"],
        transactions,
    )
    write_csv(
        "raw_stock_reservations.csv",
        ["id", "warehouse_id", "sku", "checkout_id", "quantity", "reserved_at", "released_at", "status"],
        reservations,
    )


if __name__ == "__main__":
    main()
