#!/usr/bin/env python3
"""
One-off generator for the Reviews domain's raw seed CSVs (Phase 15 of the
e-commerce platform build-out): reviews, review votes, moderation actions,
and merchant responses.

Design note: "review moderation" gets its own table (not just a status
field) since it carries a moderator's decision + reason, the same level of
detail already given to checkout_failures and return_inspections elsewhere
in this build.

Reads raw_customers.csv and raw_products.csv.

Usage:
    python3 scripts/generate_review_domain_seeds.py
"""

import csv
import random
import uuid
from datetime import datetime, timedelta

from faker import Faker
from pathlib import Path

fake = Faker()
random.seed(127)
Faker.seed(127)

SEEDS_DIR = Path(__file__).resolve().parent.parent / "seeds" / "jaffle-data"

N_REVIEWS = 180
MODERATION_REASONS = ["spam", "offensive_language", "off_topic", "fake_review"]
POSITIVE_TITLES = ["Loved it!", "Great choice", "Will buy again", "Exactly what I wanted", "Highly recommend"]
NEGATIVE_TITLES = ["Not what I expected", "Disappointed", "Could be better", "Wouldn't order again"]


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
    customers = load_csv("raw_customers.csv")
    products = load_csv("raw_products.csv")
    print(f"generating review-domain seeds: {N_REVIEWS} reviews across {len(products)} products")

    reviews = []
    moderation_actions = []
    responses = []

    now = datetime.now()

    for _ in range(N_REVIEWS):
        review_id = str(uuid.uuid4())
        customer = random.choice(customers)
        product = random.choice(products)
        rating = random.choices([1, 2, 3, 4, 5], weights=[5, 5, 10, 30, 50])[0]
        created_at = now - timedelta(days=random.randint(1, 400))

        title = random.choice(POSITIVE_TITLES if rating >= 4 else NEGATIVE_TITLES)
        moderation_outcome = random.choices(["approved", "rejected", "pending"], weights=[85, 8, 7])[0]
        status = {"approved": "published", "rejected": "rejected", "pending": "pending"}[moderation_outcome]

        reviews.append(
            {
                "id": review_id,
                "product_id": product["sku"],
                "customer_id": customer["id"],
                "rating": rating,
                "title": title,
                "body": fake.paragraph(nb_sentences=3),
                "status": status,
                "created_at": fmt(created_at),
            }
        )

        if moderation_outcome != "pending":
            moderated_at = created_at + timedelta(hours=random.uniform(1, 48))
            reason = "" if moderation_outcome == "approved" else random.choice(MODERATION_REASONS)
            moderation_actions.append(
                {
                    "id": str(uuid.uuid4()),
                    "review_id": review_id,
                    "action": moderation_outcome,
                    "reason": reason,
                    "moderated_at": fmt(moderated_at),
                }
            )

        # merchant responses skew toward low ratings and published reviews
        if status == "published" and (rating <= 2 and random.random() < 0.5 or random.random() < 0.08):
            responded_at = created_at + timedelta(days=random.randint(1, 10))
            responses.append(
                {
                    "id": str(uuid.uuid4()),
                    "review_id": review_id,
                    "response_body": fake.sentence(nb_words=15),
                    "responder_role": random.choice(["merchant", "support"]),
                    "responded_at": fmt(responded_at),
                }
            )

    published_review_ids = [r["id"] for r in reviews if r["status"] == "published"]
    review_votes = []
    for review_id in published_review_ids:
        n_votes = random.choices([0, 1, 2, 5, 10], weights=[30, 25, 20, 15, 10])[0]
        voters = random.sample(customers, k=min(n_votes, len(customers)))
        for voter in voters:
            review_votes.append(
                {
                    "id": str(uuid.uuid4()),
                    "review_id": review_id,
                    "customer_id": voter["id"],
                    "vote_type": random.choices(["helpful", "not_helpful"], weights=[80, 20])[0],
                }
            )

    # ~1.5% of votes are a duplicate customer voting twice on the same
    # review (a known client-side double-submit bug)
    for _ in range(max(1, int(len(review_votes) * 0.015))):
        original = random.choice(review_votes)
        review_votes.append(dict(original, id=str(uuid.uuid4())))

    write_csv(
        "raw_reviews.csv",
        ["id", "product_id", "customer_id", "rating", "title", "body", "status", "created_at"],
        reviews,
    )
    write_csv("raw_review_votes.csv", ["id", "review_id", "customer_id", "vote_type"], review_votes)
    write_csv(
        "raw_review_moderation_actions.csv",
        ["id", "review_id", "action", "reason", "moderated_at"],
        moderation_actions,
    )
    write_csv(
        "raw_review_responses.csv",
        ["id", "review_id", "response_body", "responder_role", "responded_at"],
        responses,
    )


if __name__ == "__main__":
    main()
