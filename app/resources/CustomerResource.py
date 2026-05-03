from __future__ import annotations

import os

from pydantic import BaseModel, Field

from .AbstractBaseResource import AbstractBaseResource
from ..services.MySQLDataService import MySQLDataService


class Customer(BaseModel):
    customerNumber: int | None = None
    customerName: str = ""
    contactLastName: str = ""
    contactFirstName: str = ""
    phone: str = ""
    addressLine1: str = ""
    addressLine2: str | None = None
    city: str = ""
    state: str | None = None
    postalCode: str | None = None
    country: str = ""
    salesRepEmployeeNumber: int | None = None
    creditLimit: float | None = None


class CustomerCollection(BaseModel):
    items: list[Customer] = Field(default_factory=list)


def _make_service_config(cfg: dict) -> dict:
    return {
        "host": cfg.get("host", os.getenv("MYSQL_HOST", "localhost")),
        "port": int(cfg.get("port", os.getenv("MYSQL_PORT", 3306))),
        "user": cfg.get("user", os.getenv("MYSQL_USER", "")),
        "password": cfg.get("password", os.getenv("MYSQL_PASSWORD", "")),
        "database": cfg.get("database", os.getenv("MYSQL_DATABASE", "classicmodels")),
        "table": "customers",
        "primary_key_fields": ["customerNumber"],
    }


class CustomerResource(AbstractBaseResource):
    def __init__(self, config: dict | None = None) -> None:
        cfg = dict(config or {})
        super().__init__(cfg)
        self._service = MySQLDataService(_make_service_config(cfg))

    def get(self, template: dict) -> CustomerCollection:
        rows = self._service.retrieveByTemplate(template)
        return CustomerCollection(items=[Customer.model_validate(r) for r in rows])

    def get_by_id(self, id: str) -> Customer:  # noqa: A002
        row = self._service.retrieveByPrimaryKey(str(id))
        if not row:
            raise ValueError(f"No customer with customerNumber {id!r}")
        return Customer.model_validate(row)

    def post(self, new_data: Customer) -> str:
        data = {k: v for k, v in new_data.model_dump().items() if v is not None}
        return self._service.create(data)

    def put(self, customer_id: str, new_data: Customer) -> int:
        data = {k: v for k, v in new_data.model_dump().items() if v is not None}
        result = self._service.updateByPrimaryKey(customer_id, data)
        if result == 0:
            raise ValueError(f"No customer with customerNumber {customer_id!r}")
        return result

    def delete(self, id: str) -> int:  # noqa: A002
        return self._service.deleteByPrimaryKey(str(id))
