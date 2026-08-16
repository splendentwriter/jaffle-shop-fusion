#!/usr/bin/env python3
"""
One-off generator for the Promotions domain's raw seed CSVs (Phase 9 of the
e-commerce platform build-out): promotions, coupons, and coupon redemptions.

Design notes:
- "Discount rules" are fields on the promotion itself (discount_value,
  min_order_value_cents, max_discount_cents), not a separate table - a rule
  is the promotion's configuration, not a distinct entity.
- "Order discounts" ties to Phase 6's checkout funnel (redemptions reference
  checkout_id), not the pre-existing bulk orders table - same boundary
  reasoning documented in Phase 7: the two order-ish datasets don't share
  real row-level identity, so redemptions attach to the funnel that
  actually has a live cart/checkout/payment trail behind it.

Reads raw_checkouts.csv (Phase 6) for which checkouts redeemed a coupon.

Usage:
    python3 scripts/generate_promotion_domain_seeds.py
"""

import csv
import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path

random.seed(61)

SEEDS_DIR = Path(__file__).resolve().parent.parent / "seeds" / "jaffle-data"

PROMOTIONS = [
    {"name": "Welcome10", "type": "percentage_off", "value": 10, "min_order_cents": 0, "max_discount_cents": 500},
    {"name": "Summer20", "type": "percentage_off", "value": 20, "min_order_cents": 1500, "max_discount_cents": 1000},
    {"name": "FreeShipWeekend", "type": "free_shipping", "value": 0, "min_order_cents": 2000, "max_discount_cents": 1200},
    {"name": "Flat5Off", "type": "fixed_amount_off", "value": 500, "min_order_cents": 1000, "max_discount_cents": 500},
    {"name": "BOGOJaffle", "type": "bogo", "value": 100, "min_order_cents": 0, "max_discount_cents": 1500},
    {"name": "LoyaltyThanks", "type": "fixed_amount_off", "value": 300, "min_order_cents": 500, "max_discount_cents": 300},
    {"name": "BlackFriday", "type": "percentage_off", "value": 30, "min_order_cents": 2000, "max_discount_cents": 2000},
    {"name": "NewYear15", "type": "percentage_off", "value": 15, "min_order_cents": 1000, "max_discount_cents": 800},
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


def fake_suffix():
    return str(random.randint(2, 9))


def main():
    checkouts = load_csv("raw_checkouts.csv")
    checkout_items_by_checkout = {}
    for item in load_csv("raw_checkout_items.csv"):
        checkout_items_by_checkout.setdefault(item["checkout_id"], []).append(item)

    completed = [c for c in checkouts if c["status"] == "completed"]
    print(f"generating promotion-domain seeds against {len(completed)} completed checkouts")

    promotions = []
    coupons = []
    now = datetime.now()

    for promo in PROMOTIONS:
        promo_id = str(uuid.uuid4())
        starts_at = now - timedelta(days=random.randint(30, 300))
        # most promotions have already ended; a couple are still active
        is_active = random.random() < 0.25
        ends_at = "" if is_active else fmt(starts_at + timedelta(days=random.randint(14, 60)))

        promotions.append(
            {
                "id": promo_id,
                "name": promo["name"],
                "description": f"{promo['name']} promotional offer",
                "promotion_type": promo["type"],
                "discount_value": promo["value"],
                "min_order_value_cents": promo["min_order_cents"],
                "max_discount_cents": promo["max_discount_cents"],
                "starts_at": fmt(starts_at),
                "ends_at": ends_at,
                "is_active": is_active,
            }
        )

        n_codes = random.choices([1, 2], weights=[70, 30])[0]
        for i in range(n_codes):
            suffix = "" if i == 0 else f"-{fake_suffix()}"
            coupons.append(
                {
                    "id": str(uuid.uuid4()),
                    "promotion_id": promo_id,
                    "code": promo["name"].upper() + suffix,
                    "max_redemptions": random.choice(["", "500", "1000"]),
                    "max_redemptions_per_customer": 1,
                    "is_active": is_active,
                }
            )

    def order_total_cents(checkout):
        items = checkout_items_by_checkout.get(checkout["id"], [])
        subtotal = sum(int(i["quantity"]) * int(i["unit_price_cents"]) for i in items)
        return subtotal + int(checkout["shipping_cost_cents"])

    redemptions = []
    # ~15% of completed checkouts redeemed a coupon
    redeeming_checkouts = random.sample(completed, k=int(len(completed) * 0.15))
    for checkout in redeeming_checkouts:
        eligible_coupons = [c for c in coupons if c["is_active"] in (True, "True")]
        if not eligible_coupons:
            eligible_coupons = coupons
        coupon = random.choice(eligible_coupons)
        promo = next(p for p in promotions if p["id"] == coupon["promotion_id"])
        total = order_total_cents(checkout)

        if promo["promotion_type"] == "percentage_off":
            discount = min(int(total * promo["discount_value"] / 100), promo["max_discount_cents"])
        elif promo["promotion_type"] == "fixed_amount_off":
            discount = min(promo["discount_value"], promo["max_discount_cents"])
        else:
            discount = min(int(checkout["shipping_cost_cents"]), promo["max_discount_cents"]) or 300

        redeemed_at = datetime.fromisoformat(checkout["started_at"]) + timedelta(minutes=random.randint(1, 3))
        redemptions.append(
            {
                "id": str(uuid.uuid4()),
                "coupon_id": coupon["id"],
                "customer_id": checkout["customer_id"],
                "checkout_id": checkout["id"],
                "redeemed_at": fmt(redeemed_at),
                "discount_amount_cents": discount,
            }
        )

    # ~2% of redemptions double-redeem the same coupon on the same checkout
    # (a known upstream retry-button bug that doesn't dedupe client-side)
    for _ in range(max(1, int(len(redemptions) * 0.02))):
        original = random.choice(redemptions)
        redemptions.append(dict(original, id=str(uuid.uuid4())))

    write_csv(
        "raw_promotions.csv",
        [
            "id", "name", "description", "promotion_type", "discount_value",
            "min_order_value_cents", "max_discount_cents", "starts_at", "ends_at", "is_active",
        ],
        promotions,
    )
    write_csv(
        "raw_coupons.csv",
        ["id", "promotion_id", "code", "max_redemptions", "max_redemptions_per_customer", "is_active"],
        coupons,
    )
    write_csv(
        "raw_coupon_redemptions.csv",
        ["id", "coupon_id", "customer_id", "checkout_id", "redeemed_at", "discount_amount_cents"],
        redemptions,
    )


if __name__ == "__main__":
    main()
