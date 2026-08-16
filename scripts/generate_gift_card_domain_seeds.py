#!/usr/bin/env python3
"""
One-off generator for the Gift Cards domain's raw seed CSVs (Phase 19 of
the e-commerce platform build-out): gift cards and a unified gift card
transaction ledger.

Design note: "gift card transactions" and "gift card redemptions" are one
unified raw_gift_card_transactions ledger (transaction_type=issue/redeem/
refund_credit/expire), not two tables - same pattern as payments, inventory,
and loyalty points elsewhere in this build.

Reads raw_customers.csv and raw_checkouts.csv.

Usage:
    python3 scripts/generate_gift_card_domain_seeds.py
"""

import csv
import random
import string
import uuid
from datetime import datetime, timedelta
from pathlib import Path

random.seed(179)

SEEDS_DIR = Path(__file__).resolve().parent.parent / "seeds" / "jaffle-data"

N_GIFT_CARDS = 150
DENOMINATIONS_CENTS = [1000, 2500, 5000, 10000]


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


def gen_code():
    return "GC-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=10))


def main():
    customers = load_csv("raw_customers.csv")
    checkouts = [c for c in load_csv("raw_checkouts.csv") if c["status"] == "completed"]
    print(f"generating gift-card-domain seeds: {N_GIFT_CARDS} cards")

    now = datetime.now()
    gift_cards = []
    transactions = []

    redeeming_checkouts = random.sample(checkouts, k=min(30, len(checkouts)))
    redeeming_checkout_ids = {c["id"] for c in redeeming_checkouts}
    checkout_by_id = {c["id"]: c for c in redeeming_checkouts}

    for i in range(N_GIFT_CARDS):
        card_id = str(uuid.uuid4())
        initial_balance = random.choice(DENOMINATIONS_CENTS)
        purchased_by = random.choice(customers)["id"] if random.random() < 0.7 else ""
        issued_at = now - timedelta(days=random.randint(1, 500))
        expires_at = issued_at + timedelta(days=365 * 2)

        transactions.append(
            {
                "id": str(uuid.uuid4()),
                "gift_card_id": card_id,
                "transaction_type": "issue",
                "amount_cents": initial_balance,
                "related_checkout_id": "",
                "occurred_at": fmt(issued_at),
            }
        )
        balance = initial_balance

        # a subset of cards get redeemed against one of the sampled completed checkouts
        if i < len(redeeming_checkouts) and balance > 0:
            checkout = redeeming_checkouts[i]
            redeemed_at = datetime.fromisoformat(checkout["started_at"])
            redeem_amount = min(balance, random.randint(300, balance))
            transactions.append(
                {
                    "id": str(uuid.uuid4()),
                    "gift_card_id": card_id,
                    "transaction_type": "redeem",
                    "amount_cents": -redeem_amount,
                    "related_checkout_id": checkout["id"],
                    "occurred_at": fmt(redeemed_at),
                }
            )
            balance -= redeem_amount

        # a small number of cards later get a refund credited back (e.g. a
        # return where the original tender was store credit)
        if balance < initial_balance and random.random() < 0.1:
            credit_at = issued_at + timedelta(days=random.randint(60, 300))
            credit_amount = random.randint(100, 500)
            transactions.append(
                {
                    "id": str(uuid.uuid4()),
                    "gift_card_id": card_id,
                    "transaction_type": "refund_credit",
                    "amount_cents": credit_amount,
                    "related_checkout_id": "",
                    "occurred_at": fmt(credit_at),
                }
            )
            balance += credit_amount

        is_expired = expires_at < now
        if is_expired and balance > 0:
            transactions.append(
                {
                    "id": str(uuid.uuid4()),
                    "gift_card_id": card_id,
                    "transaction_type": "expire",
                    "amount_cents": -balance,
                    "related_checkout_id": "",
                    "occurred_at": fmt(expires_at),
                }
            )
            status = "expired"
            balance = 0
        elif balance == 0:
            status = "redeemed"
        else:
            status = "active"

        gift_cards.append(
            {
                "id": card_id,
                "code": gen_code(),
                "initial_balance_cents": initial_balance,
                "current_balance_cents": balance,
                "purchased_by_customer_id": purchased_by,
                "issued_at": fmt(issued_at),
                "expires_at": fmt(expires_at),
                "status": status,
            }
        )

    write_csv(
        "raw_gift_cards.csv",
        ["id", "code", "initial_balance_cents", "current_balance_cents", "purchased_by_customer_id", "issued_at", "expires_at", "status"],
        gift_cards,
    )
    write_csv(
        "raw_gift_card_transactions.csv",
        ["id", "gift_card_id", "transaction_type", "amount_cents", "related_checkout_id", "occurred_at"],
        transactions,
    )


if __name__ == "__main__":
    main()
