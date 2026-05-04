"""
Load the ClassicModels sample database into MySQL.

Downloads the SQL dump from mysqltutorial.org, extracts it, and
executes it against the database configured via environment variables
(or a local .env file).

Usage:
    python scripts/load_classicmodels.py

Requires: pymysql, python-dotenv, requests
"""
from __future__ import annotations

import io
import os
import re
import zipfile

import pymysql
import requests
from dotenv import load_dotenv

load_dotenv()

SQL_URL = "https://www.mysqltutorial.org/wp-content/uploads/2023/10/mysqlsampledatabase.zip"
SQL_FILENAME = "mysqlsampledatabase.sql"


def get_connection() -> pymysql.connections.Connection:
    return pymysql.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        port=int(os.getenv("MYSQL_PORT", 3306)),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        database=os.getenv("MYSQL_DATABASE", "classicmodels"),
        charset="utf8mb4",
        autocommit=True,
    )


def download_sql() -> str:
    print(f"Downloading ClassicModels SQL from {SQL_URL} ...")
    resp = requests.get(SQL_URL, timeout=30)
    resp.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
        name = next(n for n in zf.namelist() if n.endswith(".sql"))
        sql = zf.read(name).decode("utf-8", errors="replace")
    print(f"  Downloaded and extracted '{name}' ({len(sql):,} chars)")
    return sql


def split_statements(sql: str) -> list[str]:
    """Split SQL into individual statements, skipping USE / CREATE DATABASE lines."""
    statements = []
    buf: list[str] = []
    for line in sql.splitlines():
        stripped = line.strip()
        # Skip database-switching statements so we stay in the Railway DB
        if re.match(r"^\s*(USE|CREATE\s+DATABASE|DROP\s+DATABASE)\b", stripped, re.IGNORECASE):
            continue
        buf.append(line)
        if stripped.endswith(";"):
            stmt = "\n".join(buf).strip()
            if stmt:
                statements.append(stmt)
            buf = []
    return statements


def load(sql: str) -> None:
    conn = get_connection()
    statements = split_statements(sql)
    print(f"Executing {len(statements)} statements ...")
    errors = 0
    with conn.cursor() as cursor:
        for i, stmt in enumerate(statements, 1):
            try:
                cursor.execute(stmt)
            except Exception as exc:
                errors += 1
                if errors <= 5:
                    print(f"  [stmt {i}] WARNING: {exc}")
    conn.close()
    print(f"Done. {len(statements) - errors} succeeded, {errors} skipped/warned.")


if __name__ == "__main__":
    sql = download_sql()
    load(sql)
    print("\nClassicModels data loaded successfully.")
