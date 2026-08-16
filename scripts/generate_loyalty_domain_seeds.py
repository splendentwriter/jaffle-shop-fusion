#!/usr/bin/env python3
"""
One-off generator for the Loyalty domain's raw seed CSVs (Phase 18 of the
e-commerce platform build-out): loyalty tiers, accounts, a unified points
ledger, and rewards.

Design note: "reward redemptions" is a transaction_type='redeem' row (with
reward_id set) on one unified raw_loyalty_transactions ledger, not a
separate table - same unified-ledger pattern as payments (Phase 8) and
inventory transactions (Phase 10): earn, redeem, expire, and adjustment are
all just points moving, differing only in type.

Reads raw_customers.csv and raw_checkouts.csv (completed ones earn points).

Usage:
    python3 scripts/generate_loyalty_domain_seeds.py
"""

import csv
import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path

random.seed(163)

SEEDS_DIR = Path(__file__).resolve().parent.parent / "seeds" / "jaffle-data"

TIERS = [
    {"id": "TIER-BRONZE", "name": "bronze", "min_points_threshold": 0, "perk_description": "Standard earning rate"},
    {"id": "TIER-SILVER", "name": "silver", "min_points_threshold": 500, "perk_description": "1.25x points earning"},
    {"id": "TIER-GOLD", "name": "gold", "min_points_threshold": 2000, "perk_description": "1.5x points earning, free shipping"},
    {"id": "TIER-PLATINUM", "name": "platinum", "min_points_threshold": 5000, "perk_description": "2x points earning, priority support"},
]
REWARDS = [
    {"id": "RWD-001", "name": "$5 off coupon", "points_cost": 500, "reward_type": "discount_coupon"},
    {"id": "RWD-002", "name": "$10 off coupon", "points_cost": 900, "reward_type": "discount_coupon"},
    {"id": "RWD-003", "name": "Free shipping", "points_cost": 300, "reward_type": "free_shipping"},
    {"id": "RWD-004", "name": "Free beverage", "points_cost": 400, "reward_type": "free_item"},
]


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


def tier_for_points(points):
    tier = TIERS[0]
    for t in TIERS:
        if points >= t["min_points_threshold"]:
            tier = t
    return tier


def main():
    customers = load_csv("raw_customers.csv")
    checkouts = load_csv("raw_checkouts.csv")
    checkout_items_by_checkout = {}
    for item in load_csv("raw_checkout_items.csv"):
        checkout_items_by_checkout.setdefault(item["checkout_id"], []).append(item)

    checkouts_by_customer = {}
    for c in checkouts:
        if c["status"] == "completed" and c["customer_id"]:
            checkouts_by_customer.setdefault(c["customer_id"], []).append(c)

    # ~40% of customers are enrolled in the loyalty program
    enrolled_customers = random.sample(customers, k=int(len(customers) * 0.4))
    print(f"generating loyalty-domain seeds for {len(enrolled_customers)} enrolled customers")

    now = datetime.now()
    accounts = []
    transactions = []

    for customer in enrolled_customers:
        account_id = str(uuid.uuid4())
        enrolled_at = now - timedelta(days=random.randint(30, 720))
        points_balance = 0
        cursor = enrolled_at

        transactions.append(
            {
                "id": str(uuid.uuid4()),
                "loyalty_account_id": account_id,
                "transaction_type": "earn",
                "points": 100,
                "reward_id": "",
                "related_checkout_id": "",
                "occurred_at": fmt(enrolled_at),
            }
        )
        points_balance += 100

        for checkout in checkouts_by_customer.get(customer["id"], []):
            items = checkout_items_by_checkout.get(checkout["id"], [])
            spend_cents = sum(int(i["quantity"]) * int(i["unit_price_cents"]) for i in items)
            earned = max(1, spend_cents // 100)
            earned_at = datetime.fromisoformat(checkout["started_at"])
            transactions.append(
                {
                    "id": str(uuid.uuid4()),
                    "loyalty_account_id": account_id,
                    "transaction_type": "earn",
                    "points": earned,
                    "reward_id": "",
                    "related_checkout_id": checkout["id"],
                    "occurred_at": fmt(earned_at),
                }
            )
            points_balance += earned
            cursor = max(cursor, earned_at)

        # occasional redemption once enough points have accrued
        if points_balance >= 300 and random.random() < 0.5:
            reward = random.choice([r for r in REWARDS if r["points_cost"] <= points_balance])
            redeemed_at = cursor + timedelta(days=random.randint(1, 30))
            transactions.append(
                {
                    "id": str(uuid.uuid4()),
                    "loyalty_account_id": account_id,
                    "transaction_type": "redeem",
                    "points": -reward["points_cost"],
                    "reward_id": reward["id"],
                    "related_checkout_id": "",
                    "occurred_at": fmt(redeemed_at),
                }
            )
            points_balance -= reward["points_cost"]

        # a small number of accounts have unused points expire after a year
        # of inactivity
        if random.random() < 0.05 and points_balance > 0:
            expired_points = min(points_balance, random.randint(50, 200))
            transactions.append(
                {
                    "id": str(uuid.uuid4()),
                    "loyalty_account_id": account_id,
                    "transaction_type": "expire",
                    "points": -expired_points,
                    "reward_id": "",
                    "related_checkout_id": "",
                    "occurred_at": fmt(now - timedelta(days=random.randint(1, 30))),
                }
            )
            points_balance -= expired_points

        tier = tier_for_points(points_balance)
        accounts.append(
            {
                "id": account_id,
                "customer_id": customer["id"],
                "tier_id": tier["id"],
                "points_balance": points_balance,
                "enrolled_at": fmt(enrolled_at),
                "status": random.choices(["active", "inactive", "suspended"], weights=[90, 8, 2])[0],
            }
        )

    write_csv("raw_loyalty_tiers.csv", ["id", "name", "min_points_threshold", "perk_description"], TIERS)
    write_csv("raw_rewards.csv", ["id", "name", "points_cost", "reward_type"], REWARDS)
    write_csv(
        "raw_loyalty_accounts.csv",
        ["id", "customer_id", "tier_id", "points_balance", "enrolled_at", "status"],
        accounts,
    )
    write_csv(
        "raw_loyalty_transactions.csv",
        ["id", "loyalty_account_id", "transaction_type", "points", "reward_id", "related_checkout_id", "occurred_at"],
        transactions,
    )


if __name__ == "__main__":
    main()
