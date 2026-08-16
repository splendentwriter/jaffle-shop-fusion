#!/usr/bin/env python3
"""
One-off generator for the Customer Support domain's raw seed CSVs (Phase 17
of the e-commerce platform build-out): support agents, tickets, messages,
and ticket events.

Design note: "support categories" is a category field on the ticket, not a
separate lookup table - same treatment as every other reason/type field in
this build. A subset of return_refund tickets link to a real Phase 14
return (return_refund category tickets reference return_id), giving support
a genuine cross-domain connection rather than a free-floating category.

Reads raw_customers.csv and raw_returns.csv.

Usage:
    python3 scripts/generate_support_domain_seeds.py
"""

import csv
import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path

from faker import Faker

fake = Faker()
random.seed(151)
Faker.seed(151)

SEEDS_DIR = Path(__file__).resolve().parent.parent / "seeds" / "jaffle-data"

N_AGENTS = 8
N_TICKETS = 250
TEAMS = ["billing", "shipping", "product", "general"]
CATEGORIES = ["billing", "shipping", "product_question", "return_refund", "technical", "other"]
PRIORITIES = ["low", "medium", "high", "urgent"]
STATUSES = ["open", "in_progress", "waiting_on_customer", "resolved", "closed"]


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
    returns = load_csv("raw_returns.csv")
    print(f"generating support-domain seeds: {N_AGENTS} agents, {N_TICKETS} tickets")

    agents = []
    for _ in range(N_AGENTS):
        agents.append(
            {
                "id": str(uuid.uuid4()),
                "name": fake.name(),
                "email": fake.company_email(),
                "team": random.choice(TEAMS),
                "is_active": random.random() < 0.9,
            }
        )

    now = datetime.now()
    tickets = []
    messages = []
    ticket_events = []

    return_ids = [r["id"] for r in returns]

    for _ in range(N_TICKETS):
        ticket_id = str(uuid.uuid4())
        customer = random.choice(customers)
        category = random.choices(CATEGORIES, weights=[15, 20, 20, 15, 20, 10])[0]
        related_return_id = ""
        if category == "return_refund" and return_ids and random.random() < 0.5:
            related_return_id = random.choice(return_ids)

        created_at = now - timedelta(days=random.randint(1, 300))
        priority = random.choices(PRIORITIES, weights=[35, 40, 20, 5])[0]
        status = random.choices(STATUSES, weights=[10, 15, 10, 25, 40])[0]
        agent = random.choice(agents) if status != "open" or random.random() < 0.6 else None

        cursor = created_at
        ticket_events.append(
            {"id": str(uuid.uuid4()), "ticket_id": ticket_id, "event_type": "created", "occurred_at": fmt(cursor), "detail": ""}
        )
        if agent:
            cursor += timedelta(hours=random.uniform(0.5, 12))
            ticket_events.append(
                {
                    "id": str(uuid.uuid4()),
                    "ticket_id": ticket_id,
                    "event_type": "assigned",
                    "occurred_at": fmt(cursor),
                    "detail": agent["id"],
                }
            )

        n_messages = random.randint(1, 6)
        for i in range(n_messages):
            cursor += timedelta(hours=random.uniform(0.5, 24))
            sender_type = "customer" if i % 2 == 0 else "agent"
            messages.append(
                {
                    "id": str(uuid.uuid4()),
                    "ticket_id": ticket_id,
                    "sender_type": sender_type,
                    "body": fake.paragraph(nb_sentences=2),
                    "sent_at": fmt(cursor),
                }
            )

        resolved_at = ""
        if status in ("resolved", "closed"):
            cursor += timedelta(hours=random.uniform(1, 12))
            ticket_events.append(
                {
                    "id": str(uuid.uuid4()),
                    "ticket_id": ticket_id,
                    "event_type": "resolved",
                    "occurred_at": fmt(cursor),
                    "detail": "",
                }
            )
            resolved_at = fmt(cursor)
            # ~5% of resolved tickets get reopened
            if random.random() < 0.05:
                cursor += timedelta(days=random.randint(1, 5))
                ticket_events.append(
                    {
                        "id": str(uuid.uuid4()),
                        "ticket_id": ticket_id,
                        "event_type": "reopened",
                        "occurred_at": fmt(cursor),
                        "detail": "",
                    }
                )
                status = "in_progress"
                resolved_at = ""

        tickets.append(
            {
                "id": ticket_id,
                "customer_id": customer["id"],
                "agent_id": agent["id"] if agent else "",
                "category": category,
                "related_return_id": related_return_id,
                "subject": fake.sentence(nb_words=6),
                "status": status,
                "priority": priority,
                "created_at": fmt(created_at),
                "resolved_at": resolved_at,
            }
        )

    write_csv("raw_support_agents.csv", ["id", "name", "email", "team", "is_active"], agents)
    write_csv(
        "raw_support_tickets.csv",
        ["id", "customer_id", "agent_id", "category", "related_return_id", "subject", "status", "priority", "created_at", "resolved_at"],
        tickets,
    )
    write_csv("raw_support_messages.csv", ["id", "ticket_id", "sender_type", "body", "sent_at"], messages)
    write_csv("raw_ticket_events.csv", ["id", "ticket_id", "event_type", "occurred_at", "detail"], ticket_events)


if __name__ == "__main__":
    main()
