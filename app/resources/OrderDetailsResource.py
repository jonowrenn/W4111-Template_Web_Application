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


class OrderDetailWithProduct(BaseModel):
    orderNumber: int
    productCode: str
    productName: str
    productLine: str
    quantityOrdered: int
    priceEach: float
    orderLineNumber: int
    lineTotal: float


class OrderDetailCollection(BaseModel):
    items: list[OrderDetail] = Field(default_factory=list)


class OrderDetailWithProductCollection(BaseModel):
    items: list[OrderDetailWithProduct] = Field(default_factory=list)
    orderTotal: float = 0.0


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
    return json.dumps({"orderNumber": order_number, "productCode": product_code})


class OrderDetailsResource(AbstractBaseResource):
    def __init__(self, config: dict | None = None) -> None:
        cfg = dict(config or {})
        super().__init__(cfg)
        self._service = MySQLDataService(_make_service_config(cfg))

    def get(self, template: dict, limit: int | None = None, offset: int | None = None) -> OrderDetailCollection:
        rows = self._service.retrieveByTemplate(template, limit=limit, offset=offset)
        return OrderDetailCollection(items=[OrderDetail.model_validate(r) for r in rows])

    def get_by_id(self, id: str) -> OrderDetail:  # noqa: A002
        row = self._service.retrieveByPrimaryKey(id)
        if not row:
            raise ValueError(f"No order detail with key {id!r}")
        return OrderDetail.model_validate(row)

    def get_by_order_and_product(self, order_number: str | int, product_code: str) -> OrderDetail:
        return self.get_by_id(_composite_key(order_number, product_code))

    def get_by_order_with_products(self, order_number: int) -> OrderDetailWithProductCollection:
        """Return all details for an order, joined with product info and line totals."""
        sql = """
            SELECT
                od.orderNumber,
                od.productCode,
                p.productName,
                p.productLine,
                od.quantityOrdered,
                od.priceEach,
                od.orderLineNumber,
                ROUND(od.quantityOrdered * od.priceEach, 2) AS lineTotal
            FROM orderdetails od
            JOIN products p ON od.productCode = p.productCode
            WHERE od.orderNumber = %s
            ORDER BY od.orderLineNumber
        """
        rows = self._service.execute_query(sql, [order_number])
        items = [OrderDetailWithProduct.model_validate(r) for r in rows]
        order_total = round(sum(i.lineTotal for i in items), 2)
        return OrderDetailWithProductCollection(items=items, orderTotal=order_total)

    def post(self, new_data: OrderDetail) -> str:
        data = {k: v for k, v in new_data.model_dump().items() if v is not None}
        return self._service.create(data)

    def put(self, order_id: str, new_data: OrderDetail) -> int:
        data = {k: v for k, v in new_data.model_dump().items() if v is not None}
        result = self._service.updateByPrimaryKey(order_id, data)
        if result == 0:
            raise ValueError(f"No order detail with key {order_id!r}")
        return result

    def put_by_order_and_product(self, order_number: str | int, product_code: str, new_data: OrderDetail) -> int:
        return self.put(_composite_key(order_number, product_code), new_data)

    def delete(self, id: str) -> int:  # noqa: A002
        return self._service.deleteByPrimaryKey(id)

    def delete_by_order_and_product(self, order_number: str | int, product_code: str) -> int:
        return self.delete(_composite_key(order_number, product_code))
