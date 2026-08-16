#!/usr/bin/env python3
"""
One-off generator for the Finance domain's raw seed CSVs (Phase 20, the
last domain phase, of the e-commerce platform build-out): tax rates,
processing fee config, and payouts.

Design notes - this phase deliberately does NOT duplicate work already done
elsewhere:
- "Chargebacks" already exists (Phase 8's stg_disputes, status='chargeback')
  - not re-modeled here.
- "Financial transactions" already exists as fct_payment_transaction
  (Phase 8) and the gift card / loyalty ledgers (Phases 18-19).
- "Revenue", "taxes", "fees", and "reconciliation" are computed, not raw
  data, so only their *inputs* are seeded here (tax rates, a fee schedule,
  payout batches); the actual revenue/tax/fee/reconciliation logic is built
  as core models that pull together Checkout (6), Payments (8), and
  Promotions (9) - this is the capstone tying six phases together.

Reads raw_checkouts.csv for the shipping_region population (so tax rates
cover every region actually used) and raw_captures.csv for payout batching.

Usage:
    python3 scripts/generate_finance_domain_seeds.py
"""

import csv
import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path

random.seed(191)

SEEDS_DIR = Path(__file__).resolve().parent.parent / "seeds" / "jaffle-data"


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
    regions = sorted({c["shipping_region"] for c in checkouts if c["shipping_region"]})
    print(f"generating finance-domain seeds for {len(regions)} shipping regions")

    tax_rates = []
    for region in regions:
        tax_rates.append(
            {
                "id": str(uuid.uuid4()),
                "region": region,
                "tax_rate": round(random.uniform(0.0, 0.095), 4),
                "effective_from": "2020-01-01T00:00:00",
            }
        )

    fee_config = [
        {
            "id": str(uuid.uuid4()),
            "provider": "platform",
            "percentage_fee": 0.029,
            "fixed_fee_cents": 30,
            "effective_from": "2020-01-01T00:00:00",
        }
    ]

    captures = load_csv("raw_captures.csv")
    dated_captures = [(c, datetime.fromisoformat(c["captured_at"])) for c in captures]
    if dated_captures:
        earliest = min(dt for _, dt in dated_captures)
        latest = max(dt for _, dt in dated_captures)
    else:
        earliest = latest = datetime.now()

    payouts = []
    period_start = earliest - timedelta(days=earliest.weekday())
    while period_start <= latest:
        period_end = period_start + timedelta(days=7)
        period_captures = [c for c, dt in dated_captures if period_start <= dt < period_end]
        gross_cents = sum(int(c["amount_cents"]) for c in period_captures)
        fee_cents = sum(round(int(c["amount_cents"]) * 0.029) + 30 for c in period_captures)
        net_cents = gross_cents - fee_cents

        payout_date = period_end + timedelta(days=2)
        status = "paid" if payout_date < datetime.now() else "pending"
        payouts.append(
            {
                "id": str(uuid.uuid4()),
                "period_start": fmt(period_start),
                "period_end": fmt(period_end),
                "payout_date": fmt(payout_date),
                "amount_cents": net_cents,
                "status": status if net_cents > 0 else "no_payout_due",
                "bank_reference": f"PO-{uuid.uuid4().hex[:10].upper()}",
            }
        )
        period_start = period_end

    write_csv("raw_tax_rates.csv", ["id", "region", "tax_rate", "effective_from"], tax_rates)
    write_csv(
        "raw_processing_fee_config.csv",
        ["id", "provider", "percentage_fee", "fixed_fee_cents", "effective_from"],
        fee_config,
    )
    write_csv(
        "raw_payouts.csv",
        ["id", "period_start", "period_end", "payout_date", "amount_cents", "status", "bank_reference"],
        [p for p in payouts if p["status"] != "no_payout_due"],
    )


if __name__ == "__main__":
    main()
