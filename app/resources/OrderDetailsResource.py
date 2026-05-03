from __future__ import annotations

import json
import os

from pydantic import BaseModel, Field

from .AbstractBaseResource import AbstractBaseResource
from ..services.MySQLDataService import MySQLDataService


class OrderDetail(BaseModel):
    orderNumber: int | None = None
    productCode: str = ""
    quantityOrdered: int | None = None
    priceEach: float | None = None
    orderLineNumber: int | None = None


class OrderDetailCollection(BaseModel):
    items: list[OrderDetail] = Field(default_factory=list)


def _make_service_config(cfg: dict) -> dict:
    return {
        "host": cfg.get("host", os.getenv("MYSQL_HOST", "localhost")),
        "port": int(cfg.get("port", os.getenv("MYSQL_PORT", 3306))),
        "user": cfg.get("user", os.getenv("MYSQL_USER", "")),
        "password": cfg.get("password", os.getenv("MYSQL_PASSWORD", "")),
        "database": cfg.get("database", os.getenv("MYSQL_DATABASE", "classicmodels")),
        "table": "orderdetails",
        "primary_key_fields": ["orderNumber", "productCode"],
    }


def _composite_key(order_number: str | int, product_code: str) -> str:
    """Encode the composite PK as a JSON string for MySQLDataService."""
    return json.dumps({"orderNumber": order_number, "productCode": product_code})


class OrderDetailsResource(AbstractBaseResource):
    def __init__(self, config: dict | None = None) -> None:
        cfg = dict(config or {})
        super().__init__(cfg)
        self._service = MySQLDataService(_make_service_config(cfg))

    def get(self, template: dict) -> OrderDetailCollection:
        rows = self._service.retrieveByTemplate(template)
        return OrderDetailCollection(items=[OrderDetail.model_validate(r) for r in rows])

    def get_by_id(self, id: str) -> OrderDetail:  # noqa: A002
        """id should be a JSON-encoded composite key, e.g. {"orderNumber": 10100, "productCode": "S18_1749"}"""
        row = self._service.retrieveByPrimaryKey(id)
        if not row:
            raise ValueError(f"No order detail with key {id!r}")
        return OrderDetail.model_validate(row)

    def get_by_order_and_product(self, order_number: str | int, product_code: str) -> OrderDetail:
        key = _composite_key(order_number, product_code)
        return self.get_by_id(key)

    def post(self, new_data: OrderDetail) -> str:
        data = {k: v for k, v in new_data.model_dump().items() if v is not None}
        return self._service.create(data)

    def put(self, order_id: str, new_data: OrderDetail) -> int:
        """order_id must be a JSON-encoded composite key."""
        data = {k: v for k, v in new_data.model_dump().items() if v is not None}
        result = self._service.updateByPrimaryKey(order_id, data)
        if result == 0:
            raise ValueError(f"No order detail with key {order_id!r}")
        return result

    def put_by_order_and_product(
        self, order_number: str | int, product_code: str, new_data: OrderDetail
    ) -> int:
        key = _composite_key(order_number, product_code)
        return self.put(key, new_data)

    def delete(self, id: str) -> int:  # noqa: A002
        """id must be a JSON-encoded composite key."""
        return self._service.deleteByPrimaryKey(id)

    def delete_by_order_and_product(self, order_number: str | int, product_code: str) -> int:
        key = _composite_key(order_number, product_code)
        return self.delete(key)
