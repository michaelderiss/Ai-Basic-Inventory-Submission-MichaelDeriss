from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
PRODUCTS_FILE = DATA_DIR / "products.csv"


def ensure_storage() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if PRODUCTS_FILE.exists():
        return

    with PRODUCTS_FILE.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=["id", "name", "quantity", "price", "location"],
        )
        writer.writeheader()
        writer.writerow({"id": "prod-1001", "name": "Milk", "quantity": 25, "price": 3.5, "location": "North"})
        writer.writerow({"id": "prod-1002", "name": "Bread", "quantity": 15, "price": 2.75, "location": "North"})
        writer.writerow({"id": "prod-1003", "name": "Eggs", "quantity": 40, "price": 4.25, "location": "South"})


app = FastAPI(title="Inventory API", version="1.0.0")


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, description="Product name")
    quantity: int = Field(..., ge=0, description="Initial stock count")
    price: float = Field(..., gt=0, description="Unit price")
    location: str = Field(..., min_length=1, description="Store location")


class InventoryUpdate(BaseModel):
    delta: int = Field(..., description="Positive values add stock; negative values reduce it.")
    reason: str = Field(default="manual update", description="Reason for the stock change")
    price: float | None = Field(default=None, gt=0, description="Optional updated unit price")


def read_products() -> list[dict[str, Any]]:
    ensure_storage()
    with PRODUCTS_FILE.open("r", newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        products: list[dict[str, Any]] = []
        for row in reader:
            products.append(
                {
                    "id": row.get("id", ""),
                    "name": row.get("name", ""),
                    "quantity": int(row.get("quantity", 0) or 0),
                    "price": float(row.get("price", 0) or 0),
                    "location": row.get("location", "Unknown"),
                }
            )
    return products


def write_products(products: list[dict[str, Any]]) -> None:
    ensure_storage()
    with PRODUCTS_FILE.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=["id", "name", "quantity", "price", "location"])
        writer.writeheader()
        for product in products:
            writer.writerow(
                {
                    "id": product["id"],
                    "name": product["name"],
                    "quantity": int(product["quantity"]),
                    "price": float(product["price"]),
                    "location": product["location"],
                }
            )


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Inventory API is running. Use /api/products and /api/inventory/alerts."}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/products")
def list_products() -> list[dict[str, Any]]:
    return read_products()


@app.post("/api/products")
def create_product(product: ProductCreate) -> dict[str, Any]:
    products = read_products()
    new_id = f"prod-{len(products) + 1001:04d}"
    new_product = {
        "id": new_id,
        "name": product.name,
        "quantity": product.quantity,
        "price": product.price,
        "location": product.location,
    }
    products.append(new_product)
    write_products(products)
    return new_product


@app.patch("/api/inventory/{product_id}")
def update_inventory(product_id: str, update: InventoryUpdate) -> dict[str, Any]:
    products = read_products()
    product = next((item for item in products if item["id"] == product_id), None)
    if product is None:
        raise HTTPException(status_code=404, detail=f"Product '{product_id}' not found.")

    product["quantity"] = max(0, int(product["quantity"]) + int(update.delta))
    if update.price is not None:
        product["price"] = float(update.price)

    write_products(products)
    return {
        "id": product["id"],
        "name": product["name"],
        "quantity": product["quantity"],
        "price": product["price"],
        "location": product["location"],
        "delta": update.delta,
        "reason": update.reason,
    }


@app.get("/api/inventory/alerts")
def inventory_alerts(threshold: int = Query(default=10, ge=0)) -> list[dict[str, Any]]:
    products = read_products()
    alerts = [
        product
        for product in products
        if int(product["quantity"]) <= threshold
    ]
    return alerts
