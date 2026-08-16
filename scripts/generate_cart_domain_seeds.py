#!/usr/bin/env python3
"""
One-off generator for the Cart domain's raw seed CSVs (Phase 5 of the
e-commerce platform build-out): carts, cart items, and cart events.

"Saved items" from the plan is modeled as a state on cart_items
(is_saved_for_later) rather than a separate raw table, and "abandoned carts"
as a cart.status value rather than a derived table — both are properties of
a cart/item, not distinct entities with their own grain.

Reads raw_sessions.csv (Phase 4) and raw_products.csv for realistic linkage.

Usage:
    python3 scripts/generate_cart_domain_seeds.py
"""

import csv
import random
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

random.seed(23)

SEEDS_DIR = Path(__file__).resolve().parent.parent / "seeds" / "jaffle-data"

N_CARTS = 1200
CART_STATUSES = ["active", "abandoned", "converted", "merged"]
CART_STATUS_WEIGHTS = [15, 45, 35, 5]


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
    sessions = load_csv("raw_sessions.csv")
    products = load_csv("raw_products.csv")
    skus = [p["sku"] for p in products]
    prices = {p["sku"]: int(p["price"]) for p in products}

    print(f"generating cart-domain seeds against {len(sessions)} sessions, {len(skus)} products")

    carts = []
    cart_items = []
    cart_events = []

    # a random sample of sessions get a cart; skip sessions with no start time
    candidate_sessions = [s for s in sessions if s["started_at"]]
    cart_sessions = random.sample(candidate_sessions, k=min(N_CARTS, len(candidate_sessions)))

    for session in cart_sessions:
        cart_id = str(uuid.uuid4())
        created_at = datetime.fromisoformat(session["started_at"]) + timedelta(minutes=random.randint(1, 15))
        status = random.choices(CART_STATUSES, weights=CART_STATUS_WEIGHTS)[0]
        updated_at = created_at + timedelta(minutes=random.randint(2, 240))

        carts.append(
            {
                "id": cart_id,
                "customer_id": session["customer_id"],
                "session_id": session["id"],
                "created_at": fmt(created_at),
                "updated_at": fmt(updated_at),
                "status": status,
            }
        )

        cart_events.append(
            {"id": str(uuid.uuid4()), "cart_id": cart_id, "event_type": "created", "occurred_at": fmt(created_at)}
        )

        # ~4% of carts are created but never get an item added (bounced immediately)
        if random.random() < 0.04:
            continue

        n_items = random.choices([1, 2, 3, 4], weights=[40, 30, 20, 10])[0]
        cursor = created_at
        for _ in range(n_items):
            cursor += timedelta(minutes=random.randint(1, 20))
            sku = random.choice(skus)
            quantity = random.choices([1, 2, 3], weights=[70, 22, 8])[0]

            # ~1.5% of line items have a data-entry bug: non-positive quantity
            if random.random() < 0.015:
                quantity = random.choice([0, -1])

            removed_at = ""
            is_saved_for_later = False
            if status in ("abandoned", "active") and random.random() < 0.15:
                if random.random() < 0.3:
                    is_saved_for_later = True
                else:
                    removed_at_dt = cursor + timedelta(minutes=random.randint(1, 30))
                    removed_at = fmt(removed_at_dt)
                    cart_events.append(
                        {
                            "id": str(uuid.uuid4()),
                            "cart_id": cart_id,
                            "event_type": "item_removed",
                            "occurred_at": removed_at,
                        }
                    )

            cart_items.append(
                {
                    "id": str(uuid.uuid4()),
                    "cart_id": cart_id,
                    "sku": sku,
                    "quantity": quantity,
                    "unit_price_cents": prices[sku],
                    "added_at": fmt(cursor),
                    "removed_at": removed_at,
                    "is_saved_for_later": is_saved_for_later,
                }
            )
            cart_events.append(
                {"id": str(uuid.uuid4()), "cart_id": cart_id, "event_type": "item_added", "occurred_at": fmt(cursor)}
            )

        if status == "abandoned":
            cart_events.append(
                {"id": str(uuid.uuid4()), "cart_id": cart_id, "event_type": "abandoned", "occurred_at": fmt(updated_at)}
            )
        elif status == "converted":
            cart_events.append(
                {"id": str(uuid.uuid4()), "cart_id": cart_id, "event_type": "converted", "occurred_at": fmt(updated_at)}
            )

    # ~1% of cart_items reference a sku that's since been delisted (not in
    # the current product catalogue) - a common stale-cart-data scenario
    for item in random.sample(cart_items, k=max(1, int(len(cart_items) * 0.01))):
        item["sku"] = "JAF-999-DELISTED"

    write_csv(
        "raw_carts.csv",
        ["id", "customer_id", "session_id", "created_at", "updated_at", "status"],
        carts,
    )
    write_csv(
        "raw_cart_items.csv",
        ["id", "cart_id", "sku", "quantity", "unit_price_cents", "added_at", "removed_at", "is_saved_for_later"],
        cart_items,
    )
    write_csv("raw_cart_events.csv", ["id", "cart_id", "event_type", "occurred_at"], cart_events)


if __name__ == "__main__":
    main()
