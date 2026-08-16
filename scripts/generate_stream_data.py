#!/usr/bin/env python3
"""
Continuously generates random jaffle-shop activity and streams it into the
`jaffle_shop_raw` BigQuery dataset via `bq insert` (BigQuery's streaming
insert API), simulating a live feed of new customers, stores, products,
supplies, orders, and order items.

Requires the `bq` CLI to already be authenticated (`gcloud auth login`).

Usage:
    python3 scripts/generate_stream_data.py
    python3 scripts/generate_stream_data.py --interval 10 --project my-proj
"""

import argparse
import json
import random
import re
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone

from faker import Faker

fake = Faker()

PROJECT = "jaffle-shop-505616"
DATASET = "jaffle_shop_raw"

PRODUCT_TYPES = {
    "jaffle": {"prefix": "JAF", "price_range": (900, 1500)},
    "beverage": {"prefix": "BEV", "price_range": (400, 800)},
}
SUPPLY_WORDS = [
    "napkin",
    "cutlery - fork",
    "cutlery - knife",
    "cutlery - spoon",
    "to-go box",
    "paper straw",
    "napkin ring",
    "compostable cutlery - fork",
    "compostable cutlery - knife",
    "coffee filter",
    "cup sleeve",
    "wax paper",
]


def bq_query_json(sql):
    result = subprocess.run(
        # bq caps result rows at 100 by default; raise it well above any raw table's row count
        ["bq", "query", "--use_legacy_sql=false", "--format=json", "--max_rows=1000000", sql],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"bq query failed: {result.stderr.strip()}")
    return json.loads(result.stdout or "[]")


def bq_insert(project, dataset, table, rows):
    if not rows:
        return
    payload = "\n".join(json.dumps(row) for row in rows)
    result = subprocess.run(
        ["bq", "insert", "--project_id", project, f"{dataset}.{table}"],
        input=payload,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        print(f"[error] insert into {table} failed: {result.stderr.strip()}", file=sys.stderr)


def next_sequence(existing_ids, prefix):
    """Given ids like 'SUP-014', find the next free number for a prefix."""
    nums = [int(m.group(1)) for i in existing_ids if (m := re.fullmatch(rf"{prefix}-(\d+)", i))]
    return (max(nums) + 1) if nums else 1


def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")


class World:
    def __init__(self, project, dataset):
        print(f"Loading existing reference data from {project}.{dataset} ...")
        self.customers = [{"id": r["id"], "name": r["name"]} for r in bq_query_json(
            f"SELECT id, name FROM `{project}.{dataset}.raw_customers`"
        )]
        self.stores = [
            {"id": r["id"], "name": r["name"], "tax_rate": float(r["tax_rate"])}
            for r in bq_query_json(f"SELECT id, name, tax_rate FROM `{project}.{dataset}.raw_stores`")
        ]
        self.products = [
            {"sku": r["sku"], "name": r["name"], "type": r["type"], "price": int(r["price"])}
            for r in bq_query_json(f"SELECT sku, name, type, price FROM `{project}.{dataset}.raw_products`")
        ]
        supply_ids = [r["id"] for r in bq_query_json(f"SELECT id FROM `{project}.{dataset}.raw_supplies`")]
        self.next_supply_seq = next_sequence(supply_ids, "SUP")
        self.next_product_seq = {
            ptype: next_sequence([p["sku"] for p in self.products], cfg["prefix"])
            for ptype, cfg in PRODUCT_TYPES.items()
        }
        print(
            f"Loaded {len(self.customers)} customers, {len(self.stores)} stores, "
            f"{len(self.products)} products."
        )

    def new_customer(self):
        customer = {"id": str(uuid.uuid4()), "name": fake.name()}
        self.customers.append(customer)
        return customer

    def new_store(self):
        store = {
            "id": str(uuid.uuid4()),
            "name": fake.city(),
            "opened_at": now_iso(),
            "tax_rate": round(random.uniform(0.03, 0.09), 4),
        }
        self.stores.append(store)
        return store

    def new_product(self):
        ptype = random.choice(list(PRODUCT_TYPES))
        cfg = PRODUCT_TYPES[ptype]
        seq = self.next_product_seq[ptype]
        self.next_product_seq[ptype] += 1
        product = {
            "sku": f"{cfg['prefix']}-{seq:03d}",
            "name": fake.catch_phrase().lower(),
            "type": ptype,
            "price": random.randrange(*cfg["price_range"], 50),
            "description": fake.sentence(nb_words=10),
        }
        self.products.append(product)
        return product

    def new_supply(self):
        seq = self.next_supply_seq
        self.next_supply_seq += 1
        product = random.choice(self.products)
        return {
            "id": f"SUP-{seq:03d}",
            "name": random.choice(SUPPLY_WORDS),
            "cost": random.randrange(3, 15),
            "perishable": random.random() < 0.1,
            "sku": product["sku"],
        }

    def new_order_with_items(self):
        customer = random.choice(self.customers)
        store = random.choice(self.stores)
        items = random.choices(self.products, k=random.randint(1, 4))
        subtotal = sum(item["price"] for item in items)
        tax_paid = round(subtotal * store["tax_rate"])
        order = {
            "id": str(uuid.uuid4()),
            "customer": customer["id"],
            "ordered_at": now_iso(),
            "store_id": store["id"],
            "subtotal": subtotal,
            "tax_paid": tax_paid,
            "order_total": subtotal + tax_paid,
        }
        order_items = [
            {"id": str(uuid.uuid4()), "order_id": order["id"], "sku": item["sku"]} for item in items
        ]
        return order, order_items


def run(project, dataset, interval):
    world = World(project, dataset)
    print(f"Streaming random activity into {project}.{dataset} every {interval}s. Ctrl+C to stop.\n")

    try:
        while True:
            batch = {
                "raw_customers": [],
                "raw_stores": [],
                "raw_products": [],
                "raw_supplies": [],
                "raw_orders": [],
                "raw_items": [],
            }

            if random.random() < 0.30:
                batch["raw_customers"].append(world.new_customer())
            if random.random() < 0.03:
                batch["raw_stores"].append(world.new_store())
            if random.random() < 0.08:
                batch["raw_products"].append(world.new_product())
            if random.random() < 0.15:
                batch["raw_supplies"].append(world.new_supply())

            for _ in range(random.randint(1, 3)):
                order, order_items = world.new_order_with_items()
                batch["raw_orders"].append(order)
                batch["raw_items"].extend(order_items)

            for table, rows in batch.items():
                bq_insert(project, dataset, table, rows)

            counts = ", ".join(f"+{len(rows)} {table}" for table, rows in batch.items() if rows)
            print(f"[{now_iso()}] {counts}")

            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nStopped.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", default=PROJECT, help="BigQuery project id")
    parser.add_argument("--dataset", default=DATASET, help="Raw dataset name")
    parser.add_argument("--interval", type=float, default=5, help="Seconds between streamed batches")
    args = parser.parse_args()
    run(args.project, args.dataset, args.interval)


if __name__ == "__main__":
    main()
