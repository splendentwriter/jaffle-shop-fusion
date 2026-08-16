#!/usr/bin/env python3
"""
One-off generator for the Customer domain's raw seed CSVs (Phase 2 of the
e-commerce platform build-out): accounts, addresses, preferences, consent,
and devices. Reads seeds/jaffle-data/raw_customers.csv for the customer_id
population and writes sibling CSVs into the same directory.

Deliberately introduces the messy-real-world scenarios called for in the
build-out plan: orphan/duplicate accounts, customers with zero addresses,
duplicate address rows, missing preferences, null postal codes.

Usage:
    python3 scripts/generate_customer_domain_seeds.py
"""

import csv
import random
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

from faker import Faker

fake = Faker()
random.seed(42)
Faker.seed(42)

SEEDS_DIR = Path(__file__).resolve().parent.parent / "seeds" / "jaffle-data"

ACCOUNT_STATUSES = ["active", "active", "active", "active", "inactive", "suspended", "closed"]
DEVICE_TYPES = ["ios", "android", "web"]
CONSENT_TYPES = ["marketing_email", "data_processing", "sms", "analytics_cookies"]
CHANNELS = ["email", "sms", "push", "none"]
LANGUAGES = ["en", "en", "en", "es", "fr", "de"]


def load_customer_ids():
    with open(SEEDS_DIR / "raw_customers.csv") as f:
        return [row["id"] for row in csv.DictReader(f)]


def rand_timestamp(days_back_max=900):
    delta = timedelta(days=random.randint(0, days_back_max), seconds=random.randint(0, 86400))
    return (datetime.now(timezone.utc) - delta).strftime("%Y-%m-%dT%H:%M:%S")


def write_csv(name, fieldnames, rows):
    path = SEEDS_DIR / name
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} rows to {path}")


def gen_accounts(customer_ids):
    rows = []
    for cid in customer_ids:
        created_at = rand_timestamp()
        rows.append(
            {
                "id": str(uuid.uuid4()),
                "customer_id": cid,
                "email": fake.email(),
                "account_status": random.choice(ACCOUNT_STATUSES),
                "account_type": "vip" if random.random() < 0.08 else "standard",
                "created_at": created_at,
                "updated_at": created_at,
            }
        )
        # ~1.5% of customers accidentally get a second account (dup signup)
        if random.random() < 0.015:
            dup_created_at = rand_timestamp()
            rows.append(
                {
                    "id": str(uuid.uuid4()),
                    "customer_id": cid,
                    "email": fake.email(),
                    "account_status": random.choice(ACCOUNT_STATUSES),
                    "account_type": "standard",
                    "created_at": dup_created_at,
                    "updated_at": dup_created_at,
                }
            )
    # ~1% orphan accounts: signup flow created an account row before the
    # customer record existed (or the customer was later purged)
    for _ in range(int(len(customer_ids) * 0.01)):
        created_at = rand_timestamp()
        rows.append(
            {
                "id": str(uuid.uuid4()),
                "customer_id": "",
                "email": fake.email(),
                "account_status": "active",
                "account_type": "standard",
                "created_at": created_at,
                "updated_at": created_at,
            }
        )
    random.shuffle(rows)
    return rows


def gen_addresses(customer_ids):
    rows = []
    for cid in customer_ids:
        # ~6% of customers never added an address
        if random.random() < 0.06:
            continue
        n_addresses = random.choices([1, 2, 3], weights=[70, 22, 8])[0]
        for i in range(n_addresses):
            row = {
                "id": str(uuid.uuid4()),
                "customer_id": cid,
                "address_type": "shipping" if i == 0 else random.choice(["shipping", "billing"]),
                "line1": fake.street_address(),
                "city": fake.city(),
                "region": fake.state_abbr(),
                # ~3% missing postal code (common ingestion gap)
                "postal_code": "" if random.random() < 0.03 else fake.postcode(),
                "country_code": "US",
                "is_default": i == 0,
            }
            rows.append(row)
            # ~2% of address rows get accidentally double-inserted (exact dup)
            if random.random() < 0.02:
                rows.append(dict(row, id=str(uuid.uuid4())))
    random.shuffle(rows)
    return rows


def gen_preferences(customer_ids):
    rows = []
    for cid in customer_ids:
        # ~15% of customers never filled out preferences
        if random.random() < 0.15:
            continue
        rows.append(
            {
                "customer_id": cid,
                "marketing_opt_in": random.random() < 0.55,
                "preferred_channel": random.choice(CHANNELS),
                "preferred_language": random.choice(LANGUAGES),
            }
        )
    random.shuffle(rows)
    return rows


def gen_consent(customer_ids):
    rows = []
    for cid in customer_ids:
        if random.random() < 0.1:
            continue
        for consent_type in random.sample(CONSENT_TYPES, k=random.randint(1, 3)):
            granted_at = rand_timestamp()
            revoked_at = ""
            # ~10% of grants are later revoked
            if random.random() < 0.10:
                revoked_dt = datetime.fromisoformat(granted_at) + timedelta(days=random.randint(1, 200))
                if revoked_dt < datetime.now(timezone.utc).replace(tzinfo=None):
                    revoked_at = revoked_dt.strftime("%Y-%m-%dT%H:%M:%S")
            rows.append(
                {
                    "id": str(uuid.uuid4()),
                    "customer_id": cid,
                    "consent_type": consent_type,
                    "granted_at": granted_at,
                    "revoked_at": revoked_at,
                    "consent_version": random.choice(["v1", "v2", "v3"]),
                }
            )
    random.shuffle(rows)
    return rows


def gen_devices(customer_ids):
    rows = []
    for cid in customer_ids:
        if random.random() < 0.2:
            continue
        for _ in range(random.choices([1, 2, 3], weights=[60, 30, 10])[0]):
            first_seen = rand_timestamp()
            last_seen_dt = datetime.fromisoformat(first_seen) + timedelta(days=random.randint(0, 300))
            now_naive = datetime.now(timezone.utc).replace(tzinfo=None)
            last_seen_dt = min(last_seen_dt, now_naive)
            rows.append(
                {
                    "id": str(uuid.uuid4()),
                    "customer_id": cid,
                    "device_type": random.choice(DEVICE_TYPES),
                    "first_seen_at": first_seen,
                    "last_seen_at": last_seen_dt.strftime("%Y-%m-%dT%H:%M:%S"),
                    "is_active": random.random() < 0.7,
                }
            )
    random.shuffle(rows)
    return rows


def main():
    customer_ids = load_customer_ids()
    print(f"generating customer-domain seeds for {len(customer_ids)} customers")

    write_csv(
        "raw_customer_accounts.csv",
        ["id", "customer_id", "email", "account_status", "account_type", "created_at", "updated_at"],
        gen_accounts(customer_ids),
    )
    write_csv(
        "raw_customer_addresses.csv",
        ["id", "customer_id", "address_type", "line1", "city", "region", "postal_code", "country_code", "is_default"],
        gen_addresses(customer_ids),
    )
    write_csv(
        "raw_customer_preferences.csv",
        ["customer_id", "marketing_opt_in", "preferred_channel", "preferred_language"],
        gen_preferences(customer_ids),
    )
    write_csv(
        "raw_customer_consent.csv",
        ["id", "customer_id", "consent_type", "granted_at", "revoked_at", "consent_version"],
        gen_consent(customer_ids),
    )
    write_csv(
        "raw_customer_devices.csv",
        ["id", "customer_id", "device_type", "first_seen_at", "last_seen_at", "is_active"],
        gen_devices(customer_ids),
    )


if __name__ == "__main__":
    main()
