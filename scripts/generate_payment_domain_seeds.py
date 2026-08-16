#!/usr/bin/env python3
"""
One-off generator for the Payments domain's raw seed CSVs (Phase 8 of the
e-commerce platform build-out): payment methods, payment attempts,
authorizations, captures, refunds, and disputes.

Design notes:
- "Payment transactions" from the plan isn't a new raw table here - it's
  modeled as a core-layer fact (fct_payment_transaction) that unions
  authorizations/captures/refunds into one ledger view. Making it a raw
  table would just duplicate rows already captured at their source stage.
- "Disputes" and "chargebacks" are merged into one raw_disputes table with
  a status value for each outcome (open / resolved_merchant_favor /
  resolved_customer_favor / chargeback) - a chargeback is a dispute outcome,
  not a separate entity with its own grain, same reasoning as Cart's
  saved-items/abandoned-carts states.
- Payment failures reuse raw_checkouts' existing status='failed' population
  rather than re-deriving which checkouts failed.

Reads raw_checkouts.csv (Phase 6) for which checkouts to attach payment
attempts to.

Usage:
    python3 scripts/generate_payment_domain_seeds.py
"""

import csv
import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path

random.seed(53)

SEEDS_DIR = Path(__file__).resolve().parent.parent / "seeds" / "jaffle-data"

METHOD_TYPES = ["credit_card", "debit_card", "paypal", "apple_pay", "gift_card"]
CARD_BRANDS = ["visa", "mastercard", "amex", "discover"]
DECLINE_REASONS = ["card_declined", "insufficient_funds", "fraud_flag", "gateway_timeout"]
DISPUTE_REASONS = ["fraudulent", "product_not_received", "product_unacceptable", "duplicate"]
REFUND_REASONS = ["customer_request", "defective_item", "order_cancelled", "duplicate_charge"]


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
    completed = [c for c in checkouts if c["status"] == "completed"]
    failed = [c for c in checkouts if c["status"] == "failed"]
    print(f"generating payment-domain seeds from {len(completed)} completed and {len(failed)} failed checkouts")

    customer_ids = sorted({c["customer_id"] for c in checkouts if c["customer_id"]})

    payment_methods = []
    method_by_customer = {}
    for cid in customer_ids:
        n_methods = random.choices([1, 2], weights=[80, 20])[0]
        methods = []
        for i in range(n_methods):
            method_type = random.choice(METHOD_TYPES)
            pm = {
                "id": str(uuid.uuid4()),
                "customer_id": cid,
                "method_type": method_type,
                "card_brand": random.choice(CARD_BRANDS) if method_type in ("credit_card", "debit_card") else "",
                "last4": f"{random.randint(0, 9999):04d}",
                "expiry_month": str(random.randint(1, 12)),
                "expiry_year": str(random.randint(2026, 2031)),
                "is_default": i == 0,
                "created_at": fmt(datetime.now() - timedelta(days=random.randint(30, 700))),
            }
            payment_methods.append(pm)
            methods.append(pm)
        method_by_customer[cid] = methods

    payment_attempts = []
    authorizations = []
    captures = []
    refunds = []
    disputes = []

    checkout_items_by_checkout = {}
    for item in load_csv("raw_checkout_items.csv"):
        checkout_items_by_checkout.setdefault(item["checkout_id"], []).append(item)

    def compute_total(checkout):
        items = checkout_items_by_checkout.get(checkout["id"], [])
        subtotal = sum(int(i["quantity"]) * int(i["unit_price_cents"]) for i in items)
        return subtotal + int(checkout["shipping_cost_cents"])

    for checkout in completed:
        started = datetime.fromisoformat(checkout["started_at"])
        amount = compute_total(checkout)
        customer_methods = method_by_customer.get(checkout["customer_id"], [])
        payment_method_id = random.choice(customer_methods)["id"] if customer_methods else ""

        attempt_id = str(uuid.uuid4())
        attempt_time = started + timedelta(minutes=random.randint(1, 5))
        payment_attempts.append(
            {
                "id": attempt_id,
                "checkout_id": checkout["id"],
                "payment_method_id": payment_method_id,
                "attempted_at": fmt(attempt_time),
                "status": "captured",
                "amount_cents": amount,
                "decline_reason": "",
            }
        )

        auth_id = str(uuid.uuid4())
        auth_time = attempt_time + timedelta(seconds=random.randint(1, 30))
        authorizations.append(
            {
                "id": auth_id,
                "payment_attempt_id": attempt_id,
                "authorized_at": fmt(auth_time),
                "amount_cents": amount,
                "status": "approved",
            }
        )

        capture_time = auth_time + timedelta(seconds=random.randint(1, 60))
        # ~3% of captures are partial (item shipped short, captured less than authorized)
        capture_amount = amount
        if random.random() < 0.03:
            capture_amount = int(amount * random.uniform(0.5, 0.95))
        captures.append(
            {
                "id": str(uuid.uuid4()),
                "authorization_id": auth_id,
                "captured_at": fmt(capture_time),
                "amount_cents": capture_amount,
            }
        )

        # ~5% of completed orders later get a refund
        if random.random() < 0.05:
            requested_at = capture_time + timedelta(days=random.randint(1, 20))
            is_partial = random.random() < 0.4
            refund_amount = int(capture_amount * random.uniform(0.2, 0.6)) if is_partial else capture_amount
            refund_status = random.choices(["completed", "pending", "rejected"], weights=[80, 10, 10])[0]
            refunds.append(
                {
                    "id": str(uuid.uuid4()),
                    "capture_id": captures[-1]["id"],
                    "requested_at": fmt(requested_at),
                    "refunded_at": fmt(requested_at + timedelta(days=random.randint(0, 3))) if refund_status == "completed" else "",
                    "amount_cents": refund_amount,
                    "reason": random.choice(REFUND_REASONS),
                    "status": refund_status,
                }
            )

        # ~1.5% of completed orders get disputed
        if random.random() < 0.015:
            opened_at = capture_time + timedelta(days=random.randint(3, 60))
            outcome = random.choices(
                ["open", "resolved_merchant_favor", "resolved_customer_favor", "chargeback"],
                weights=[15, 40, 25, 20],
            )[0]
            disputes.append(
                {
                    "id": str(uuid.uuid4()),
                    "payment_attempt_id": attempt_id,
                    "opened_at": fmt(opened_at),
                    "reason": random.choice(DISPUTE_REASONS),
                    "amount_cents": amount,
                    "status": outcome,
                }
            )

    for checkout in failed:
        started = datetime.fromisoformat(checkout["started_at"])
        amount = compute_total(checkout)
        customer_methods = method_by_customer.get(checkout["customer_id"], [])
        payment_method_id = random.choice(customer_methods)["id"] if customer_methods else ""
        attempt_time = started + timedelta(minutes=random.randint(1, 5))
        payment_attempts.append(
            {
                "id": str(uuid.uuid4()),
                "checkout_id": checkout["id"],
                "payment_method_id": payment_method_id,
                "attempted_at": fmt(attempt_time),
                "status": random.choice(["declined", "error"]),
                "amount_cents": amount,
                "decline_reason": random.choice(DECLINE_REASONS),
            }
        )

    # ~1% of payment_attempts reference a payment_method_id that's since
    # been removed from the customer's wallet (common if a card expires and
    # gets deleted between purchase and a later data pull)
    for attempt in random.sample(payment_attempts, k=max(1, int(len(payment_attempts) * 0.01))):
        if attempt["payment_method_id"]:
            attempt["payment_method_id"] = str(uuid.uuid4())

    write_csv(
        "raw_payment_methods.csv",
        ["id", "customer_id", "method_type", "card_brand", "last4", "expiry_month", "expiry_year", "is_default", "created_at"],
        payment_methods,
    )
    write_csv(
        "raw_payment_attempts.csv",
        ["id", "checkout_id", "payment_method_id", "attempted_at", "status", "amount_cents", "decline_reason"],
        payment_attempts,
    )
    write_csv(
        "raw_authorizations.csv",
        ["id", "payment_attempt_id", "authorized_at", "amount_cents", "status"],
        authorizations,
    )
    write_csv("raw_captures.csv", ["id", "authorization_id", "captured_at", "amount_cents"], captures)
    write_csv(
        "raw_refunds.csv",
        ["id", "capture_id", "requested_at", "refunded_at", "amount_cents", "reason", "status"],
        refunds,
    )
    write_csv(
        "raw_disputes.csv",
        ["id", "payment_attempt_id", "opened_at", "reason", "amount_cents", "status"],
        disputes,
    )


if __name__ == "__main__":
    main()
