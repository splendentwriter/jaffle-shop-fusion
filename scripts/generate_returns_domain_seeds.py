#!/usr/bin/env python3
"""
One-off generator for the Returns domain's raw seed CSVs (Phase 14 of the
e-commerce platform build-out): returns, return items, return events, and
return inspections.

Design notes:
- "Return reasons" is a reason field on raw_returns, not a separate lookup
  table - same treatment as every other reason/type field in this build
  (dispute reason, refund reason, adjustment reason).
- "Refunds" from the plan is NOT linked to Phase 8's raw_refunds table.
  Phase 8's refunds are tied to a specific payment capture from the
  original completed-checkout flow; forcing a new return to reference one
  of those old rows would be the same kind of fake join already avoided in
  Phase 7 (checkout vs. the pre-existing bulk orders) and Phase 9 (coupon
  redemptions attaching to checkouts, not bulk orders). Instead, the refund
  outcome (refund_status, refund_amount_cents, refunded_at) lives directly
  on the return record as its terminal state.

Reads raw_shipments.csv (Phase 13, only delivered ones) and
raw_shipment_items.csv.

Usage:
    python3 scripts/generate_returns_domain_seeds.py
"""

import csv
import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path

from faker import Faker

fake = Faker()
random.seed(113)
Faker.seed(113)

SEEDS_DIR = Path(__file__).resolve().parent.parent / "seeds" / "jaffle-data"

RETURN_REASONS = ["defective", "wrong_item", "no_longer_needed", "damaged_in_transit", "not_as_described"]
INSPECTION_RESULTS = ["resellable", "resellable", "damaged", "missing_parts", "not_as_described"]


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
    shipments = load_csv("raw_shipments.csv")
    checkouts_by_id = {c["id"]: c for c in load_csv("raw_checkouts.csv")}
    fulfillment_orders_by_id = {fo["id"]: fo for fo in load_csv("raw_fulfillment_orders.csv")}
    shipment_items_by_shipment = {}
    for item in load_csv("raw_shipment_items.csv"):
        shipment_items_by_shipment.setdefault(item["shipment_id"], []).append(item)

    delivered = [s for s in shipments if s["status"] == "delivered"]
    # ~9% of delivered shipments get a return request
    returning_shipments = random.sample(delivered, k=max(1, int(len(delivered) * 0.09)))
    print(f"generating returns-domain seeds for {len(returning_shipments)} of {len(delivered)} delivered shipments")

    returns = []
    return_items = []
    return_events = []
    return_inspections = []

    for shipment in returning_shipments:
        fo = fulfillment_orders_by_id.get(shipment["fulfillment_order_id"], {})
        checkout = checkouts_by_id.get(fo.get("checkout_id"), {})
        items = shipment_items_by_shipment.get(shipment["id"], [])
        if not items or not checkout.get("customer_id"):
            continue

        return_id = str(uuid.uuid4())
        requested_at = datetime.fromisoformat(shipment["estimated_delivery_at"]) + timedelta(days=random.randint(1, 21))
        reason = random.choice(RETURN_REASONS)
        outcome = random.choices(["refunded", "rejected", "in_progress"], weights=[70, 10, 20])[0]

        cursor = requested_at
        return_events.append(
            {"id": str(uuid.uuid4()), "return_id": return_id, "event_type": "requested", "occurred_at": fmt(cursor)}
        )

        approved = outcome != "rejected" or random.random() < 0.3
        if approved:
            cursor += timedelta(hours=random.uniform(2, 24))
            return_events.append(
                {"id": str(uuid.uuid4()), "return_id": return_id, "event_type": "approved", "occurred_at": fmt(cursor)}
            )
        else:
            cursor += timedelta(hours=random.uniform(2, 24))
            return_events.append(
                {"id": str(uuid.uuid4()), "return_id": return_id, "event_type": "rejected", "occurred_at": fmt(cursor)}
            )

        n_return_items = random.randint(1, len(items))
        chosen_items = random.sample(items, k=n_return_items)
        return_item_ids = []
        for item in chosen_items:
            ri_id = str(uuid.uuid4())
            return_item_ids.append(ri_id)
            return_items.append(
                {
                    "id": ri_id,
                    "return_id": return_id,
                    "sku": item["sku"],
                    "quantity": item["quantity"],
                    "condition_reported": random.choice(["opened", "unopened", "damaged"]),
                }
            )

        status = "rejected"
        refund_status = "rejected"
        refund_amount_cents = 0
        refunded_at = ""

        if approved:
            cursor += timedelta(days=random.randint(2, 7))
            return_events.append(
                {"id": str(uuid.uuid4()), "return_id": return_id, "event_type": "item_received", "occurred_at": fmt(cursor)}
            )

            for ri_id in return_item_ids:
                inspected_at = cursor + timedelta(hours=random.uniform(1, 48))
                return_inspections.append(
                    {
                        "id": str(uuid.uuid4()),
                        "return_item_id": ri_id,
                        "inspected_at": fmt(inspected_at),
                        "inspection_result": random.choice(INSPECTION_RESULTS),
                        "inspector_notes": fake.sentence(nb_words=8),
                    }
                )
            cursor += timedelta(hours=random.uniform(1, 48))
            return_events.append(
                {
                    "id": str(uuid.uuid4()),
                    "return_id": return_id,
                    "event_type": "inspection_completed",
                    "occurred_at": fmt(cursor),
                }
            )

            if outcome == "refunded":
                cursor += timedelta(hours=random.uniform(2, 24))
                return_events.append(
                    {"id": str(uuid.uuid4()), "return_id": return_id, "event_type": "refund_issued", "occurred_at": fmt(cursor)}
                )
                status = "closed"
                refund_status = "completed"
                # shipment_items doesn't carry unit price, so this scales
                # returned quantity by a plausible per-unit price rather
                # than an exact recompute back to the original order total
                refund_amount_cents = sum(int(i["quantity"]) for i in chosen_items) * random.randint(400, 1400)
                refunded_at = fmt(cursor)
            else:
                status = "inspected"
        else:
            status = "rejected"

        returns.append(
            {
                "id": return_id,
                "shipment_id": shipment["id"],
                "customer_id": checkout["customer_id"],
                "reason": reason,
                "status": status,
                "requested_at": fmt(requested_at),
                "refund_status": refund_status,
                "refund_amount_cents": refund_amount_cents,
                "refunded_at": refunded_at,
            }
        )

    write_csv(
        "raw_returns.csv",
        ["id", "shipment_id", "customer_id", "reason", "status", "requested_at", "refund_status", "refund_amount_cents", "refunded_at"],
        returns,
    )
    write_csv(
        "raw_return_items.csv",
        ["id", "return_id", "sku", "quantity", "condition_reported"],
        return_items,
    )
    write_csv("raw_return_events.csv", ["id", "return_id", "event_type", "occurred_at"], return_events)
    write_csv(
        "raw_return_inspections.csv",
        ["id", "return_item_id", "inspected_at", "inspection_result", "inspector_notes"],
        return_inspections,
    )


if __name__ == "__main__":
    main()
