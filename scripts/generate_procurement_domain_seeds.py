#!/usr/bin/env python3
"""
One-off generator for the Procurement domain's raw seed CSVs (Phase 11 of
the e-commerce platform build-out): suppliers, supplier products, purchase
orders, purchase order items, and goods receipts.

Ties into Phase 10's warehouses (purchase orders replenish a specific
warehouse) and Phase 3's products (supplier_products references real skus).
Scoped to finished-goods procurement only ("supplier products" in the plan)
- the existing raw_supplies (napkins, cutlery) already has its own cost
field and isn't re-modeled as a second procurement stream here.

Reads raw_products.csv and raw_warehouses.csv.

Usage:
    python3 scripts/generate_procurement_domain_seeds.py
"""

import csv
import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path

from faker import Faker

fake = Faker()
random.seed(83)
Faker.seed(83)

SEEDS_DIR = Path(__file__).resolve().parent.parent / "seeds" / "jaffle-data"

N_SUPPLIERS = 5
N_PURCHASE_ORDERS = 40
PO_STATUSES = ["received", "received", "received", "partially_received", "confirmed", "cancelled"]
RECEIPT_CONDITIONS = ["good", "good", "good", "good", "damaged", "short_shipped"]


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
    warehouses = load_csv("raw_warehouses.csv")
    skus = [p["sku"] for p in products]
    warehouse_ids = [w["id"] for w in warehouses]
    print(f"generating procurement-domain seeds for {N_SUPPLIERS} suppliers, {len(skus)} products")

    suppliers = []
    for _ in range(N_SUPPLIERS):
        suppliers.append(
            {
                "id": str(uuid.uuid4()),
                "name": fake.company(),
                "contact_email": fake.company_email(),
                "is_active": random.random() < 0.9,
            }
        )

    supplier_products = []
    for sku in skus:
        product_price = int(next(p["price"] for p in products if p["sku"] == sku))
        n_suppliers_for_sku = random.choices([1, 2], weights=[75, 25])[0]
        for supplier in random.sample(suppliers, k=n_suppliers_for_sku):
            supplier_products.append(
                {
                    "id": str(uuid.uuid4()),
                    "supplier_id": supplier["id"],
                    "sku": sku,
                    "supplier_sku": fake.bothify(text="??-####").upper(),
                    "unit_cost_cents": int(product_price * random.uniform(0.3, 0.55)),
                    "lead_time_days": random.randint(2, 21),
                }
            )

    purchase_orders = []
    purchase_order_items = []
    goods_receipts = []
    now = datetime.now()

    for _ in range(N_PURCHASE_ORDERS):
        supplier = random.choice(suppliers)
        supplier_skus = [sp for sp in supplier_products if sp["supplier_id"] == supplier["id"]]
        if not supplier_skus:
            continue

        po_id = str(uuid.uuid4())
        ordered_at = now - timedelta(days=random.randint(5, 180))
        lead_time = max(sp["lead_time_days"] for sp in supplier_skus)
        expected_at = ordered_at + timedelta(days=lead_time)
        status = random.choice(PO_STATUSES)
        warehouse_id = random.choice(warehouse_ids)

        purchase_orders.append(
            {
                "id": po_id,
                "supplier_id": supplier["id"],
                "warehouse_id": warehouse_id,
                "status": status,
                "ordered_at": fmt(ordered_at),
                "expected_at": fmt(expected_at),
            }
        )

        n_items = random.randint(1, min(4, len(supplier_skus)))
        for sp in random.sample(supplier_skus, k=n_items):
            quantity_ordered = random.randint(20, 150)
            item_id = str(uuid.uuid4())
            purchase_order_items.append(
                {
                    "id": item_id,
                    "purchase_order_id": po_id,
                    "sku": sp["sku"],
                    "quantity_ordered": quantity_ordered,
                    "unit_cost_cents": sp["unit_cost_cents"],
                }
            )

            if status in ("received", "partially_received"):
                received_at = expected_at + timedelta(days=random.randint(-1, 4))
                condition = random.choice(RECEIPT_CONDITIONS)
                if status == "partially_received" or condition == "short_shipped":
                    quantity_received = int(quantity_ordered * random.uniform(0.4, 0.9))
                else:
                    quantity_received = quantity_ordered

                goods_receipts.append(
                    {
                        "id": str(uuid.uuid4()),
                        "purchase_order_id": po_id,
                        "sku": sp["sku"],
                        "quantity_received": quantity_received,
                        "received_at": fmt(received_at),
                        "condition": condition,
                    }
                )

    write_csv("raw_suppliers.csv", ["id", "name", "contact_email", "is_active"], suppliers)
    write_csv(
        "raw_supplier_products.csv",
        ["id", "supplier_id", "sku", "supplier_sku", "unit_cost_cents", "lead_time_days"],
        supplier_products,
    )
    write_csv(
        "raw_purchase_orders.csv",
        ["id", "supplier_id", "warehouse_id", "status", "ordered_at", "expected_at"],
        purchase_orders,
    )
    write_csv(
        "raw_purchase_order_items.csv",
        ["id", "purchase_order_id", "sku", "quantity_ordered", "unit_cost_cents"],
        purchase_order_items,
    )
    write_csv(
        "raw_goods_receipts.csv",
        ["id", "purchase_order_id", "sku", "quantity_received", "received_at", "condition"],
        goods_receipts,
    )


if __name__ == "__main__":
    main()
