from __future__ import annotations

import json
import os

import pymysql
import pymysql.cursors

from .AbstractBaseDataService import AbstractBaseDataService


class MySQLDataService(AbstractBaseDataService):
    """Persists records in a MySQL table.

    Required config keys: ``table``, ``primary_key_fields`` (list of column names).
    Connection settings default to environment variables: MYSQL_HOST, MYSQL_PORT,
    MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE.
    """

    def __init__(self, config: dict) -> None:
        super().__init__(config)
        self._table = config["table"]
        pk = config.get("primary_key_fields", ["id"])
        self._primary_key_fields: list[str] = pk if isinstance(pk, list) else [pk]

    def _get_connection(self) -> pymysql.connections.Connection:
        return pymysql.connect(
            host=str(self.config.get("host", os.getenv("MYSQL_HOST", "localhost"))),
            port=int(self.config.get("port", os.getenv("MYSQL_PORT", 3306))),
            user=str(self.config.get("user", os.getenv("MYSQL_USER", ""))),
            password=str(self.config.get("password", os.getenv("MYSQL_PASSWORD", ""))),
            database=str(self.config.get("database", os.getenv("MYSQL_DATABASE", "classicmodels"))),
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False,
        )

    def _parse_primary_key(self, primary_key: str) -> dict:
        if len(self._primary_key_fields) == 1:
            return {self._primary_key_fields[0]: primary_key}
        parsed = json.loads(primary_key)
        return {f: parsed[f] for f in self._primary_key_fields}

    def retrieveByPrimaryKey(self, primary_key: str) -> dict:
        pk_dict = self._parse_primary_key(primary_key)
        where = " AND ".join(f"`{k}` = %s" for k in pk_dict)
        sql = f"SELECT * FROM `{self._table}` WHERE {where}"
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql, list(pk_dict.values()))
                row = cursor.fetchone()
        finally:
            conn.close()
        return dict(row) if row else {}

    def retrieveByTemplate(
        self,
        template: dict,
        limit: int | None = None,
        offset: int | None = None,
        order_by: str | None = None,
    ) -> list[dict]:
        params: list = []
        if template:
            where = " AND ".join(f"`{k}` = %s" for k in template)
            sql = f"SELECT * FROM `{self._table}` WHERE {where}"
            params = list(template.values())
        else:
            sql = f"SELECT * FROM `{self._table}`"

        if order_by:
            sql += f" ORDER BY `{order_by}`"
        if limit is not None:
            sql += " LIMIT %s"
            params.append(limit)
        if offset is not None:
            sql += " OFFSET %s"
            params.append(offset)

        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                rows = cursor.fetchall()
        finally:
            conn.close()
        return [dict(r) for r in rows]

    def count(self, template: dict) -> int:
        """Return total row count matching template (for pagination metadata)."""
        if template:
            where = " AND ".join(f"`{k}` = %s" for k in template)
            sql = f"SELECT COUNT(*) as n FROM `{self._table}` WHERE {where}"
            params: list = list(template.values())
        else:
            sql = f"SELECT COUNT(*) as n FROM `{self._table}`"
            params = []
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                row = cursor.fetchone()
        finally:
            conn.close()
        return int(row["n"]) if row else 0

    def execute_query(self, sql: str, params: list | None = None) -> list[dict]:
        """Run arbitrary read-only SQL and return rows as dicts."""
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql, params or [])
                rows = cursor.fetchall()
        finally:
            conn.close()
        return [dict(r) for r in rows]

    def create(self, payload: dict) -> str:
        cols = list(payload.keys())
        col_names = ", ".join(f"`{c}`" for c in cols)
        placeholders = ", ".join(["%s"] * len(cols))
        sql = f"INSERT INTO `{self._table}` ({col_names}) VALUES ({placeholders})"
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql, list(payload.values()))
                last_id = cursor.lastrowid
            conn.commit()
        finally:
            conn.close()
        if len(self._primary_key_fields) == 1:
            pk_val = payload.get(self._primary_key_fields[0], last_id)
            return str(pk_val)
        return json.dumps({f: payload[f] for f in self._primary_key_fields})

    def updateByPrimaryKey(self, primary_key: str, payload: dict) -> int:
        pk_dict = self._parse_primary_key(primary_key)
        update_data = {k: v for k, v in payload.items() if k not in pk_dict}
        if not update_data:
            return 0
        set_clause = ", ".join(f"`{k}` = %s" for k in update_data)
        where = " AND ".join(f"`{k}` = %s" for k in pk_dict)
        sql = f"UPDATE `{self._table}` SET {set_clause} WHERE {where}"
        params = list(update_data.values()) + list(pk_dict.values())
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                affected = cursor.rowcount
            conn.commit()
        finally:
            conn.close()
        return affected

    def deleteByPrimaryKey(self, primary_key: str) -> int:
        pk_dict = self._parse_primary_key(primary_key)
        where = " AND ".join(f"`{k}` = %s" for k in pk_dict)
        sql = f"DELETE FROM `{self._table}` WHERE {where}"
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql, list(pk_dict.values()))
                affected = cursor.rowcount
            conn.commit()
        finally:
            conn.close()
        return affected
