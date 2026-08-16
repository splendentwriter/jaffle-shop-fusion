#!/usr/bin/env python3
"""
One-off generator for the Product Catalogue domain's raw seed CSVs (Phase 3
of the e-commerce platform build-out): brands, categories (hierarchical),
product-category mapping, attributes (EAV), images, and tags.

Reads seeds/jaffle-data/raw_products.csv for the product sku population.
Only covers the 10 products present in that seed file at generation time —
products added later by the live streaming generator won't have catalogue
detail rows yet, which is itself a realistic "incomplete dimension" scenario
rather than a bug to hide.

Usage:
    python3 scripts/generate_product_domain_seeds.py
"""

import csv
import random
import uuid
from pathlib import Path

random.seed(7)

SEEDS_DIR = Path(__file__).resolve().parent.parent / "seeds" / "jaffle-data"


def load_products():
    with open(SEEDS_DIR / "raw_products.csv") as f:
        return list(csv.DictReader(f))


def write_csv(name, fieldnames, rows):
    path = SEEDS_DIR / name
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} rows to {path}")


def gen_brands():
    return [
        {"id": "BRD-001", "brand_name": "Jaffle Shop House", "brand_description": "In-house jaffle recipes"},
        {"id": "BRD-002", "brand_name": "Roast & Co", "brand_description": "Third-party coffee and tea roaster"},
        {"id": "BRD-003", "brand_name": "Fresh Press", "brand_description": "Cold-pressed juice and smoothie supplier"},
    ]


def gen_categories():
    # top-level categories have no parent; sub-categories reference a parent.
    # CAT-902's parent_category_id is intentionally wrong (dangling FK) to
    # simulate a since-deleted category left behind by an upstream cleanup.
    return [
        {"id": "CAT-100", "category_name": "Jaffles", "parent_category_id": ""},
        {"id": "CAT-200", "category_name": "Beverages", "parent_category_id": ""},
        {"id": "CAT-110", "category_name": "Savory Jaffles", "parent_category_id": "CAT-100"},
        {"id": "CAT-120", "category_name": "Sweet Jaffles", "parent_category_id": "CAT-100"},
        {"id": "CAT-210", "category_name": "Hot Beverages", "parent_category_id": "CAT-200"},
        {"id": "CAT-220", "category_name": "Cold Beverages", "parent_category_id": "CAT-200"},
        {"id": "CAT-902", "category_name": "Seasonal (retired)", "parent_category_id": "CAT-999"},
    ]


SAVORY_JAFFLES = {"JAF-001", "JAF-002", "JAF-003", "JAF-004"}
HOT_BEVERAGES = {"BEV-002", "BEV-004"}


def gen_category_map(products):
    rows = []
    for p in products:
        sku = p["sku"]
        if p["type"] == "jaffle":
            category_id = "CAT-110" if sku in SAVORY_JAFFLES else "CAT-120"
        else:
            category_id = "CAT-210" if sku in HOT_BEVERAGES else "CAT-220"
        rows.append({"sku": sku, "category_id": category_id})
    # one product also gets tagged as seasonal (multi-category membership)
    rows.append({"sku": products[0]["sku"], "category_id": "CAT-902"})
    return rows


def gen_product_brands(products):
    rows = []
    for p in products:
        if p["type"] == "jaffle":
            brand_id = "BRD-001"
        else:
            brand_id = random.choice(["BRD-002", "BRD-003"])
        rows.append({"sku": p["sku"], "brand_id": brand_id})
    # last product deliberately has no brand assigned yet (new SKU, catalogue
    # data entry hasn't caught up)
    rows[-1]["brand_id"] = ""
    return rows


def gen_attributes(products):
    rows = []
    for p in products:
        sku = p["sku"]
        is_jaffle = p["type"] == "jaffle"
        attrs = {
            "is_vegetarian": "true" if sku in {"JAF-005"} else "false",
            "spice_level": random.choice(["mild", "medium", "hot"]) if is_jaffle else "none",
            "calories": str(random.randint(350, 650) if is_jaffle else random.randint(120, 320)),
            "allergens": random.choice(["gluten,dairy", "gluten", "dairy", "none"]),
        }
        for name, value in attrs.items():
            rows.append({"id": str(uuid.uuid4()), "sku": sku, "attribute_name": name, "attribute_value": value})
    # duplicate attribute key for one sku with a conflicting value (common
    # upstream re-entry issue the pivot layer has to resolve deterministically)
    rows.append(
        {"id": str(uuid.uuid4()), "sku": products[0]["sku"], "attribute_name": "spice_level", "attribute_value": "extra hot"}
    )
    return rows


def gen_images(products):
    rows = []
    for p in products:
        sku = p["sku"]
        n_images = random.choice([1, 1, 2])
        for i in range(n_images):
            rows.append(
                {
                    "id": str(uuid.uuid4()),
                    "sku": sku,
                    "image_url": f"https://cdn.jaffleshop.example/products/{sku.lower()}/{i}.jpg",
                    "is_primary": i == 0,
                    "sort_order": i,
                }
            )
    return rows


TAG_POOL = ["bestseller", "new", "vegetarian", "spicy", "seasonal", "staff-pick", "gluten-free"]


def gen_tags(products):
    rows = []
    for p in products:
        for tag in random.sample(TAG_POOL, k=random.randint(0, 3)):
            rows.append({"sku": p["sku"], "tag": tag})
    return rows


def main():
    products = load_products()
    print(f"generating product-domain seeds for {len(products)} products")

    write_csv("raw_brands.csv", ["id", "brand_name", "brand_description"], gen_brands())
    write_csv("raw_product_categories.csv", ["id", "category_name", "parent_category_id"], gen_categories())
    write_csv("raw_product_category_map.csv", ["sku", "category_id"], gen_category_map(products))
    write_csv("raw_product_brands.csv", ["sku", "brand_id"], gen_product_brands(products))
    write_csv("raw_product_attributes.csv", ["id", "sku", "attribute_name", "attribute_value"], gen_attributes(products))
    write_csv("raw_product_images.csv", ["id", "sku", "image_url", "is_primary", "sort_order"], gen_images(products))
    write_csv("raw_product_tags.csv", ["sku", "tag"], gen_tags(products))


if __name__ == "__main__":
    main()
