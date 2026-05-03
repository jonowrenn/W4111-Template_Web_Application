from __future__ import annotations

import os
from datetime import date

from pydantic import BaseModel, Field

from .AbstractBaseResource import AbstractBaseResource
from ..services.MySQLDataService import MySQLDataService


class Order(BaseModel):
    orderNumber: int | None = None
    orderDate: date | None = None
    requiredDate: date | None = None
    shippedDate: date | None = None
    status: str = ""
    comments: str | None = None
    customerNumber: int | None = None


class OrderCollection(BaseModel):
    items: list[Order] = Field(default_factory=list)


def _make_service_config(cfg: dict) -> dict:
    return {
        "host": cfg.get("host", os.getenv("MYSQL_HOST", "localhost")),
        "port": int(cfg.get("port", os.getenv("MYSQL_PORT", 3306))),
        "user": cfg.get("user", os.getenv("MYSQL_USER", "")),
        "password": cfg.get("password", os.getenv("MYSQL_PASSWORD", "")),
        "database": cfg.get("database", os.getenv("MYSQL_DATABASE", "classicmodels")),
        "table": "orders",
        "primary_key_fields": ["orderNumber"],
    }


class OrderResource(AbstractBaseResource):
    def __init__(self, config: dict | None = None) -> None:
        cfg = dict(config or {})
        super().__init__(cfg)
        self._service = MySQLDataService(_make_service_config(cfg))

    def get(self, template: dict) -> OrderCollection:
        rows = self._service.retrieveByTemplate(template)
        return OrderCollection(items=[Order.model_validate(r) for r in rows])

    def get_by_id(self, id: str) -> Order:  # noqa: A002
        row = self._service.retrieveByPrimaryKey(str(id))
        if not row:
            raise ValueError(f"No order with orderNumber {id!r}")
        return Order.model_validate(row)

    def post(self, new_data: Order) -> str:
        data = {k: v for k, v in new_data.model_dump().items() if v is not None}
        # Convert date objects to ISO strings for MySQL
        for field in ("orderDate", "requiredDate", "shippedDate"):
            if field in data and isinstance(data[field], date):
                data[field] = data[field].isoformat()
        return self._service.create(data)

    def put(self, order_id: str, new_data: Order) -> int:
        data = {k: v for k, v in new_data.model_dump().items() if v is not None}
        for field in ("orderDate", "requiredDate", "shippedDate"):
            if field in data and isinstance(data[field], date):
                data[field] = data[field].isoformat()
        result = self._service.updateByPrimaryKey(order_id, data)
        if result == 0:
            raise ValueError(f"No order with orderNumber {order_id!r}")
        return result

    def delete(self, id: str) -> int:  # noqa: A002
        return self._service.deleteByPrimaryKey(str(id))
