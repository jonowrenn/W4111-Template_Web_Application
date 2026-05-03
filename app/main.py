from __future__ import annotations

import os
import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parents[1]))
    from app.resources.HarryPotterResource import (
        HarryPotterCharacter,
        HarryPotterCollection,
        HarryPotterResource,
    )
    from app.resources.CustomerResource import Customer, CustomerCollection, CustomerResource
    from app.resources.OrderResource import Order, OrderCollection, OrderResource
    from app.resources.OrderDetailsResource import (
        OrderDetail,
        OrderDetailCollection,
        OrderDetailsResource,
    )
else:
    from .resources.HarryPotterResource import (
        HarryPotterCharacter,
        HarryPotterCollection,
        HarryPotterResource,
    )
    from .resources.CustomerResource import Customer, CustomerCollection, CustomerResource
    from .resources.OrderResource import Order, OrderCollection, OrderResource
    from .resources.OrderDetailsResource import (
        OrderDetail,
        OrderDetailCollection,
        OrderDetailsResource,
    )


def _get_app_name() -> str:
    return os.getenv("APP_NAME", "W4111 ClassicModels API")


app = FastAPI(title=_get_app_name(), version="0.1.0")

harry_potter_resource = HarryPotterResource()
customer_resource = CustomerResource()
order_resource = OrderResource()
order_details_resource = OrderDetailsResource()


class EchoRequest(BaseModel):
    message: str


# ---------------------------------------------------------------------------
# Built-in routes
# ---------------------------------------------------------------------------

@app.get("/", tags=["root"])
def read_root() -> dict[str, str]:
    return {"message": "Hello from FastAPI"}


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/echo", tags=["echo"])
def echo(payload: EchoRequest) -> EchoRequest:
    return payload


# ---------------------------------------------------------------------------
# Harry Potter (example — provided by template)
# ---------------------------------------------------------------------------

@app.get("/harry-potter", tags=["harry-potter"])
def get_harry_potter_characters(
    first_name: str | None = None,
    last_name: str | None = None,
    house_name: str | None = None,
) -> HarryPotterCollection:
    template: dict = {}
    if first_name is not None:
        template["first_name"] = first_name
    if last_name is not None:
        template["last_name"] = last_name
    if house_name is not None:
        template["house_name"] = house_name
    return harry_potter_resource.get(template)


@app.get("/harry-potter/{character_id}", tags=["harry-potter"])
def get_harry_potter_character_by_id(character_id: str) -> HarryPotterCharacter:
    try:
        return harry_potter_resource.get_by_id(character_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/harry-potter", tags=["harry-potter"])
def create_harry_potter_character(new_data: HarryPotterCharacter) -> str:
    return str(harry_potter_resource.post(new_data))


@app.put("/harry-potter/{character_id}", tags=["harry-potter"])
def update_harry_potter_character(
    character_id: str, new_data: HarryPotterCharacter
) -> dict[str, int]:
    try:
        updated = harry_potter_resource.put(character_id, new_data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"updated": updated}


@app.delete("/harry-potter/{character_id}", tags=["harry-potter"])
def delete_harry_potter_character(character_id: str) -> dict[str, int]:
    return {"deleted": harry_potter_resource.delete(character_id)}


# ---------------------------------------------------------------------------
# Customers
# ---------------------------------------------------------------------------

@app.get("/customers", tags=["customers"])
def get_customers(
    customerName: str | None = None,
    city: str | None = None,
    country: str | None = None,
    state: str | None = None,
) -> CustomerCollection:
    template: dict = {}
    if customerName is not None:
        template["customerName"] = customerName
    if city is not None:
        template["city"] = city
    if country is not None:
        template["country"] = country
    if state is not None:
        template["state"] = state
    return customer_resource.get(template)


@app.post("/customers", tags=["customers"])
def create_customer(new_data: Customer) -> dict[str, str]:
    new_id = customer_resource.post(new_data)
    return {"customerNumber": str(new_id)}


@app.get("/customers/{customerNumber}", tags=["customers"])
def get_customer(customerNumber: int) -> Customer:
    try:
        return customer_resource.get_by_id(str(customerNumber))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.put("/customers/{customerNumber}", tags=["customers"])
def update_customer(customerNumber: int, new_data: Customer) -> dict[str, int]:
    try:
        updated = customer_resource.put(str(customerNumber), new_data)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"updated": updated}


@app.delete("/customers/{customerNumber}", tags=["customers"])
def delete_customer(customerNumber: int) -> dict[str, int]:
    deleted = customer_resource.delete(str(customerNumber))
    return {"deleted": deleted}


# ---------------------------------------------------------------------------
# Orders
# ---------------------------------------------------------------------------

@app.get("/orders", tags=["orders"])
def get_orders(
    customerNumber: int | None = None,
    status: str | None = None,
) -> OrderCollection:
    template: dict = {}
    if customerNumber is not None:
        template["customerNumber"] = customerNumber
    if status is not None:
        template["status"] = status
    return order_resource.get(template)


@app.post("/orders", tags=["orders"])
def create_order(new_data: Order) -> dict[str, str]:
    new_id = order_resource.post(new_data)
    return {"orderNumber": str(new_id)}


@app.get("/orders/{orderNumber}", tags=["orders"])
def get_order(orderNumber: int) -> Order:
    try:
        return order_resource.get_by_id(str(orderNumber))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.put("/orders/{orderNumber}", tags=["orders"])
def update_order(orderNumber: int, new_data: Order) -> dict[str, int]:
    try:
        updated = order_resource.put(str(orderNumber), new_data)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"updated": updated}


@app.delete("/orders/{orderNumber}", tags=["orders"])
def delete_order(orderNumber: int) -> dict[str, int]:
    deleted = order_resource.delete(str(orderNumber))
    return {"deleted": deleted}


# ---------------------------------------------------------------------------
# Order Details
# ---------------------------------------------------------------------------

@app.get("/orderdetails", tags=["orderdetails"])
def get_order_details(
    orderNumber: int | None = None,
    productCode: str | None = None,
) -> OrderDetailCollection:
    template: dict = {}
    if orderNumber is not None:
        template["orderNumber"] = orderNumber
    if productCode is not None:
        template["productCode"] = productCode
    return order_details_resource.get(template)


@app.post("/orderdetails", tags=["orderdetails"])
def create_order_detail(new_data: OrderDetail) -> dict[str, str]:
    new_key = order_details_resource.post(new_data)
    return {"key": new_key}


@app.get("/orders/{orderNumber}/orderdetails", tags=["orderdetails"])
def get_order_details_by_order(orderNumber: int) -> OrderDetailCollection:
    return order_details_resource.get({"orderNumber": orderNumber})


@app.get("/orders/{orderNumber}/orderdetails/{productCode}", tags=["orderdetails"])
def get_order_detail(orderNumber: int, productCode: str) -> OrderDetail:
    try:
        return order_details_resource.get_by_order_and_product(orderNumber, productCode)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.put("/orders/{orderNumber}/orderdetails/{productCode}", tags=["orderdetails"])
def update_order_detail(
    orderNumber: int, productCode: str, new_data: OrderDetail
) -> dict[str, int]:
    try:
        updated = order_details_resource.put_by_order_and_product(orderNumber, productCode, new_data)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"updated": updated}


@app.delete("/orders/{orderNumber}/orderdetails/{productCode}", tags=["orderdetails"])
def delete_order_detail(orderNumber: int, productCode: str) -> dict[str, int]:
    deleted = order_details_resource.delete_by_order_and_product(orderNumber, productCode)
    return {"deleted": deleted}


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host=host, port=port)
