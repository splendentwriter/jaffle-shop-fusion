#!/usr/bin/env python3
"""
Generates one batch of new operations activity across the purchase funnel
built out in Phases 4-13 (sessions -> carts -> checkouts -> payments ->
fulfillment -> shipments) and streams it into BigQuery.

Designed to run once per invocation (Cloud Run Job semantics) on a
recurring Cloud Scheduler trigger, mirroring the existing dbt-daily-run /
dbt-daily-run-trigger pattern in this project — not an always-on service
like scripts/generate_stream_data.py, which only touches the original 6
reference tables (customers/orders/items/products/stores/supplies).

Scope, deliberately: each run is self-contained — a cart created this run
either converts or abandons within the same run, rather than being left
"open" for a future run to resolve. Payments only cover the
attempt->authorization->capture happy path (no disputes/refunds, which are
longer-tail events already covered by the one-time Phase 8 seed).
Fulfillment/shipment only apply to non-pickup completed checkouts.

Auth: Application Default Credentials, same as scripts/generate_stream_data.py.

Usage:
    python3 scripts/generate_operations_data.py
    python3 scripts/generate_operations_data.py --sessions 200
"""

import argparse
import json
import os
import random
import urllib.request
import uuid
from datetime import datetime, timedelta, timezone

from faker import Faker
from google.cloud import bigquery

fake = Faker()

PROJECT = os.environ.get("PROJECT", "jaffle-shop-505616")
DATASET = os.environ.get("DATASET", "jaffle_shop_raw")

REFERRERS = ["direct", "organic_search", "paid_search", "social", "email", "referral"]
PAGE_TYPES = ["home", "category", "product", "search_results", "cart", "account"]
SHIPPING_METHODS = {"standard": 0, "express": 1200, "pickup": 0}
SHIPPING_METHOD_WEIGHTS = [60, 25, 15]
DECLINE_REASONS = ["card_declined", "insufficient_funds", "fraud_flag", "gateway_timeout"]


def now_iso(dt=None):
    return (dt or datetime.now(timezone.utc)).strftime("%Y-%m-%dT%H:%M:%S")


def fetch_pool(client, sql, limit=300):
    return [dict(row) for row in client.query(f"{sql} LIMIT {limit}").result()]


def insert(client, table, rows):
    if not rows:
        return
    errors = client.insert_rows_json(f"{PROJECT}.{DATASET}.{table}", rows)
    if errors:
        print(f"[error] insert into {table} failed: {errors}")


def notify_slack(text, blocks=None):
    webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
    if not webhook_url:
        print("SLACK_WEBHOOK_URL not set, skipping Slack notification")
        return
    body = {"text": text}
    if blocks:
        body["blocks"] = blocks
    payload = json.dumps(body).encode("utf-8")
    request = urllib.request.Request(
        webhook_url, data=payload, headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            if response.status != 200:
                print(f"[error] Slack notification returned status {response.status}")
    except Exception as e:
        print(f"[error] failed to send Slack notification: {e}")


# (table name, display label) in funnel order, not alphabetical, so the
# Slack summary reads top-to-bottom the same way the funnel runs
TABLE_DISPLAY_ORDER = [
    ("raw_sessions", "Sessions"),
    ("raw_web_events", "Web events"),
    ("raw_carts", "Carts"),
    ("raw_cart_items", "Cart items"),
    ("raw_cart_events", "Cart events"),
    ("raw_checkouts", "Checkouts"),
    ("raw_checkout_items", "Checkout items"),
    ("raw_checkout_events", "Checkout events"),
    ("raw_payment_attempts", "Payment attempts"),
    ("raw_authorizations", "Authorizations"),
    ("raw_captures", "Captures"),
    ("raw_fulfillment_orders", "Fulfillment orders"),
    ("raw_fulfillment_items", "Fulfillment items"),
    ("raw_fulfillment_events", "Fulfillment events"),
    ("raw_shipments", "Shipments"),
    ("raw_shipment_items", "Shipment items"),
    ("raw_tracking_events", "Tracking events"),
]


def build_success_blocks(n_sessions, n_carts, n_converted, n_completed_checkouts, table_counts):
    conversion_line = ""
    if n_converted:
        rate = 100 * n_completed_checkouts / n_converted
        conversion_line = (
            f"*Result:* {n_completed_checkouts} successful payments generated from {n_converted} "
            f"checkouts (*{rate:.1f}%* checkout-to-payment conversion)."
        )
    else:
        conversion_line = "*Result:* no checkouts were generated this run."

    raw_data_lines = "\n".join(
        f"• {label}: *{table_counts[table]}*" for table, label in TABLE_DISPLAY_ORDER if table_counts.get(table)
    )

    return [
        {"type": "header", "text": {"type": "plain_text", "text": "Jaffle Shop — Operations Data Generated"}},
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    "*E-commerce flow*\n"
                    f":globe_with_meridians: *{n_sessions}* sessions\n"
                    f":shopping_trolley: *{n_carts}* carts\n"
                    f":credit_card: *{n_converted}* checkouts\n"
                    f":white_check_mark: *{n_completed_checkouts}* paid orders"
                ),
            },
        },
        {"type": "section", "text": {"type": "mrkdwn", "text": f"*Raw data generated*\n{raw_data_lines}"}},
        {"type": "section", "text": {"type": "mrkdwn", "text": conversion_line}},
    ]


class Batch:
    """Accumulates rows per table for one run, inserted all at once at the end."""

    def __init__(self):
        self.tables = {}

    def add(self, table, row):
        self.tables.setdefault(table, []).append(row)

    def flush(self, client):
        for table, rows in self.tables.items():
            insert(client, table, rows)
            print(f"  +{len(rows)} {table}")

    def counts(self):
        return {table: len(rows) for table, rows in self.tables.items()}


def generate_session(batch, customers, devices_by_customer):
    started_at = datetime.now(timezone.utc) - timedelta(minutes=random.randint(0, 55))
    duration_min = random.choices([1, 3, 8, 20, 45], weights=[20, 30, 25, 15, 10])[0]
    ended_at = started_at + timedelta(minutes=duration_min)

    is_authenticated = random.random() < 0.6
    customer_id = ""
    device_id = ""
    customer = None
    if is_authenticated and customers:
        customer = random.choice(customers)
        customer_id = customer["id"]
        candidate_devices = devices_by_customer.get(customer_id)
        if candidate_devices:
            device_id = random.choice(candidate_devices)

    session_id = str(uuid.uuid4())
    batch.add(
        "raw_sessions",
        {
            "id": session_id,
            "customer_id": customer_id,
            "device_id": device_id,
            "started_at": now_iso(started_at),
            "ended_at": now_iso(ended_at),
            "landing_page": "/" + random.choice(["", "category/jaffles", "category/beverages", "search"]),
            "referrer_source": random.choice(REFERRERS),
            "is_authenticated": is_authenticated,
        },
    )
    return session_id, customer, started_at, ended_at


def generate_web_events(batch, session_id, products, started_at):
    cursor = started_at
    n_events = random.choices([1, 2, 4, 7], weights=[25, 30, 30, 15])[0]
    for i in range(n_events):
        cursor += timedelta(seconds=random.randint(5, 180))
        if i == 0:
            event_type = "page_view"
        elif random.random() < 0.15:
            event_type = "search"
        else:
            event_type = random.choice(["page_view", "product_view"])

        row = {
            "id": str(uuid.uuid4()),
            "session_id": session_id,
            "event_type": event_type,
            "occurred_at": now_iso(cursor),
            "page_url": "",
            "product_sku": "",
            "search_query": "",
        }
        if event_type == "search":
            row["search_query"] = random.choice(["jaffle", "coffee", "vegetarian", "iced coffee"])
            row["page_url"] = "/search"
        elif event_type == "product_view" and products:
            product = random.choice(products)
            row["product_sku"] = product["sku"]
            row["page_url"] = f"/product/{product['sku'].lower()}"
        else:
            row["page_url"] = "/" + random.choice(PAGE_TYPES)
        batch.add("raw_web_events", row)


def generate_cart(batch, session_id, customer_id, started_at, products):
    cart_id = str(uuid.uuid4())
    created_at = started_at + timedelta(minutes=random.randint(1, 10))
    status = random.choices(["converted", "abandoned"], weights=[40, 60])[0]
    updated_at = created_at + timedelta(minutes=random.randint(2, 60))

    batch.add(
        "raw_carts",
        {
            "id": cart_id,
            "customer_id": customer_id,
            "session_id": session_id,
            "created_at": now_iso(created_at),
            "updated_at": now_iso(updated_at),
            "status": status,
        },
    )
    batch.add(
        "raw_cart_events",
        {"id": str(uuid.uuid4()), "cart_id": cart_id, "event_type": "created", "occurred_at": now_iso(created_at)},
    )

    items = []
    if products:
        n_items = random.choices([1, 2, 3], weights=[50, 30, 20])[0]
        cursor = created_at
        for _ in range(n_items):
            cursor += timedelta(minutes=random.randint(1, 15))
            product = random.choice(products)
            quantity = random.choices([1, 2], weights=[80, 20])[0]
            items.append({"sku": product["sku"], "quantity": quantity, "unit_price_cents": int(product["price"])})
            batch.add(
                "raw_cart_items",
                {
                    "id": str(uuid.uuid4()),
                    "cart_id": cart_id,
                    "sku": product["sku"],
                    "quantity": quantity,
                    "unit_price_cents": int(product["price"]),
                    "added_at": now_iso(cursor),
                    "removed_at": None,
                    "is_saved_for_later": False,
                },
            )
            batch.add(
                "raw_cart_events",
                {"id": str(uuid.uuid4()), "cart_id": cart_id, "event_type": "item_added", "occurred_at": now_iso(cursor)},
            )

    batch.add(
        "raw_cart_events",
        {
            "id": str(uuid.uuid4()),
            "cart_id": cart_id,
            "event_type": "converted" if status == "converted" else "abandoned",
            "occurred_at": now_iso(updated_at),
        },
    )
    return cart_id, status, updated_at, items


def generate_checkout(batch, cart_id, customer, items, updated_at):
    checkout_id = str(uuid.uuid4())
    started_at = updated_at + timedelta(minutes=random.randint(1, 5))
    shipping_method = random.choices(list(SHIPPING_METHODS), weights=SHIPPING_METHOD_WEIGHTS)[0]

    addr = {
        "line1": fake.street_address(),
        "city": fake.city(),
        "region": fake.state_abbr(),
        "postal_code": fake.postcode(),
        "country_code": "US",
    }

    cursor = started_at
    for event_type in ("started", "address_entered", "shipping_selected"):
        cursor += timedelta(minutes=random.randint(1, 3))
        batch.add(
            "raw_checkout_events",
            {"id": str(uuid.uuid4()), "checkout_id": checkout_id, "event_type": event_type, "occurred_at": now_iso(cursor)},
        )

    outcome = random.choices(["completed", "failed"], weights=[90, 10])[0]
    completed_at = None
    if outcome == "completed":
        cursor += timedelta(minutes=random.randint(1, 4))
        completed_at = now_iso(cursor)
        batch.add(
            "raw_checkout_events",
            {"id": str(uuid.uuid4()), "checkout_id": checkout_id, "event_type": "completed", "occurred_at": completed_at},
        )
    else:
        cursor += timedelta(minutes=random.randint(1, 4))
        batch.add(
            "raw_checkout_events",
            {"id": str(uuid.uuid4()), "checkout_id": checkout_id, "event_type": "payment_failed", "occurred_at": now_iso(cursor)},
        )

    batch.add(
        "raw_checkouts",
        {
            "id": checkout_id,
            "cart_id": cart_id,
            "customer_id": customer["id"] if customer else "",
            "started_at": now_iso(started_at),
            "completed_at": completed_at,
            "status": outcome,
            "shipping_method": shipping_method,
            "shipping_cost_cents": SHIPPING_METHODS[shipping_method],
            "shipping_line1": addr["line1"],
            "shipping_city": addr["city"],
            "shipping_region": addr["region"],
            "shipping_postal_code": addr["postal_code"],
            "shipping_country_code": addr["country_code"],
        },
    )
    for item in items:
        batch.add(
            "raw_checkout_items",
            {
                "id": str(uuid.uuid4()),
                "checkout_id": checkout_id,
                "sku": item["sku"],
                "quantity": item["quantity"],
                "unit_price_cents": item["unit_price_cents"],
            },
        )

    return checkout_id, outcome, shipping_method, cursor, items


def generate_payment(batch, checkout_id, outcome, items, occurred_at):
    amount_cents = sum(i["quantity"] * i["unit_price_cents"] for i in items)
    attempt_id = str(uuid.uuid4())
    attempt_time = occurred_at + timedelta(seconds=random.randint(5, 60))

    if outcome == "completed":
        batch.add(
            "raw_payment_attempts",
            {
                "id": attempt_id,
                "checkout_id": checkout_id,
                "payment_method_id": "",
                "attempted_at": now_iso(attempt_time),
                "status": "captured",
                "amount_cents": amount_cents,
                "decline_reason": "",
            },
        )
        auth_id = str(uuid.uuid4())
        auth_time = attempt_time + timedelta(seconds=random.randint(1, 20))
        batch.add(
            "raw_authorizations",
            {
                "id": auth_id,
                "payment_attempt_id": attempt_id,
                "authorized_at": now_iso(auth_time),
                "amount_cents": amount_cents,
                "status": "approved",
            },
        )
        capture_time = auth_time + timedelta(seconds=random.randint(1, 30))
        batch.add(
            "raw_captures",
            {
                "id": str(uuid.uuid4()),
                "authorization_id": auth_id,
                "captured_at": now_iso(capture_time),
                "amount_cents": amount_cents,
            },
        )
        return True
    else:
        batch.add(
            "raw_payment_attempts",
            {
                "id": attempt_id,
                "checkout_id": checkout_id,
                "payment_method_id": "",
                "attempted_at": now_iso(attempt_time),
                "status": random.choice(["declined", "error"]),
                "amount_cents": amount_cents,
                "decline_reason": random.choice(DECLINE_REASONS),
            },
        )
        return False


def generate_fulfillment(batch, checkout_id, items, warehouse_ids, shipping_method, occurred_at, carrier_ids):
    if shipping_method == "pickup" or not warehouse_ids:
        return

    fo_id = str(uuid.uuid4())
    cursor = occurred_at + timedelta(minutes=random.randint(5, 30))
    events = [("created", cursor)]

    # most orders generated this run haven't had time to ship yet; a
    # minority (older within the batch window) make it all the way through
    ships = random.random() < 0.2 and bool(carrier_ids)
    if ships:
        for stage in ("picking_started", "picking_completed", "packing_started", "packing_completed", "shipped"):
            cursor += timedelta(minutes=random.randint(5, 45))
            events.append((stage, cursor))

    batch.add(
        "raw_fulfillment_orders",
        {
            "id": fo_id,
            "checkout_id": checkout_id,
            "warehouse_id": random.choice(warehouse_ids),
            "status": "shipped" if ships else "pending",
            "created_at": now_iso(events[0][1]),
            "completed_at": now_iso(cursor) if ships else None,
        },
    )
    for event_type, occurred in events:
        batch.add(
            "raw_fulfillment_events",
            {"id": str(uuid.uuid4()), "fulfillment_order_id": fo_id, "event_type": event_type, "occurred_at": now_iso(occurred)},
        )
    for item in items:
        batch.add(
            "raw_fulfillment_items",
            {"id": str(uuid.uuid4()), "fulfillment_order_id": fo_id, "sku": item["sku"], "quantity": item["quantity"]},
        )

    if ships:
        shipment_id = str(uuid.uuid4())
        batch.add(
            "raw_shipments",
            {
                "id": shipment_id,
                "fulfillment_order_id": fo_id,
                "carrier_id": random.choice(carrier_ids),
                "tracking_number": str(random.randint(10**11, 10**12 - 1)),
                "shipped_at": now_iso(cursor),
                "estimated_delivery_at": now_iso(cursor + timedelta(days=random.randint(2, 5))),
                "status": "in_transit",
            },
        )
        for item in items:
            batch.add(
                "raw_shipment_items",
                {"id": str(uuid.uuid4()), "shipment_id": shipment_id, "sku": item["sku"], "quantity": item["quantity"]},
            )
        batch.add(
            "raw_tracking_events",
            {
                "id": str(uuid.uuid4()),
                "shipment_id": shipment_id,
                "event_type": "label_created",
                "location": "Origin Facility",
                "occurred_at": now_iso(cursor),
            },
        )


def run(n_sessions):
    client = bigquery.Client(project=PROJECT)
    print(f"Loading reference pools from {PROJECT}.{DATASET} ...")
    customers = fetch_pool(client, f"SELECT id FROM `{PROJECT}.{DATASET}.raw_customers`", limit=500)
    products = fetch_pool(client, f"SELECT sku, price FROM `{PROJECT}.{DATASET}.raw_products`", limit=100)
    warehouses = fetch_pool(client, f"SELECT id FROM `{PROJECT}.{DATASET}.raw_warehouses`", limit=20)
    carriers = fetch_pool(client, f"SELECT id FROM `{PROJECT}.{DATASET}.raw_carriers`", limit=20)
    devices = fetch_pool(client, f"SELECT id, customer_id FROM `{PROJECT}.{DATASET}.raw_customer_devices`", limit=1000)

    devices_by_customer = {}
    for d in devices:
        devices_by_customer.setdefault(d["customer_id"], []).append(d["id"])
    warehouse_ids = [w["id"] for w in warehouses]
    carrier_ids = [c["id"] for c in carriers]

    print(
        f"Pools: {len(customers)} customers, {len(products)} products, "
        f"{len(warehouse_ids)} warehouses, {len(carrier_ids)} carriers"
    )
    print(f"Generating {n_sessions} sessions worth of operations activity...")

    batch = Batch()
    n_carts = n_converted = n_completed_checkouts = 0

    for _ in range(n_sessions):
        session_id, customer, started_at, ended_at = generate_session(batch, customers, devices_by_customer)
        generate_web_events(batch, session_id, products, started_at)

        if random.random() < 0.35:
            cart_id, cart_status, updated_at, items = generate_cart(batch, session_id, customer["id"] if customer else "", started_at, products)
            n_carts += 1

            if cart_status == "converted" and items:
                n_converted += 1
                checkout_id, outcome, shipping_method, occurred_at, items = generate_checkout(
                    batch, cart_id, customer, items, updated_at
                )
                captured = generate_payment(batch, checkout_id, outcome, items, occurred_at)
                if captured:
                    n_completed_checkouts += 1
                    generate_fulfillment(batch, checkout_id, items, warehouse_ids, shipping_method, occurred_at, carrier_ids)

    print(f"Generated {n_carts} carts, {n_converted} converted -> checkout, {n_completed_checkouts} paid")
    print("Inserting...")
    batch.flush(client)
    print("Done.")

    fallback_text = (
        f"Jaffle Shop operations data generated: {n_sessions} sessions, {n_carts} carts, "
        f"{n_converted} checkouts, {n_completed_checkouts} paid orders."
    )
    blocks = build_success_blocks(n_sessions, n_carts, n_converted, n_completed_checkouts, batch.counts())
    return fallback_text, blocks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sessions", type=int, default=int(os.environ.get("SESSIONS_PER_RUN", 120)))
    args = parser.parse_args()
    try:
        fallback_text, blocks = run(args.sessions)
        notify_slack(fallback_text, blocks=blocks)
    except Exception as e:
        notify_slack(f":x: jaffle-shop-fusion operations-data-generator failed: {e}")
        raise


if __name__ == "__main__":
    main()
