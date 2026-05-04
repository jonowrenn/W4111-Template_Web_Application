# ClassicModels REST API

A production-style REST API built with **FastAPI** and **MySQL**, exposing the [ClassicModels](https://www.mysqltutorial.org/mysql-sample-database/) sample database as a clean, fully-documented HTTP service.

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.114+-009688?logo=fastapi&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-8.0+-4479A1?logo=mysql&logoColor=white)
![Deployed on Vercel](https://img.shields.io/badge/Deployed%20on-Vercel-000000?logo=vercel&logoColor=white)

**Live API & Interactive Docs:** https://template-mauve-eight.vercel.app/docs

---

## Features

- **Full CRUD** for Customers, Orders, and Order Details via a clean layered architecture
- **Pagination** (`limit` / `offset`) on every list endpoint with total count in response
- **Relationship traversal** — `GET /customers/{id}/orders` to navigate the data model
- **Enriched order details** — `GET /orders/{id}/orderdetails` joins product names, product lines, and computes per-line totals
- **Analytics endpoint** — `GET /stats` returns revenue, order counts by status, and top 5 customers by spend
- **Consistent error responses** — 404 / 400 with descriptive messages throughout
- **CORS enabled** — ready to be called from any frontend
- **Interactive Swagger UI** at `/docs`, auto-generated from code

---

## Architecture

```
HTTP Request
     │
     ▼
app/main.py          ← FastAPI route handlers (thin, no business logic)
     │
     ▼
app/resources/       ← Pydantic models + orchestration per domain
  CustomerResource
  OrderResource
  OrderDetailsResource
     │
     ▼
app/services/        ← Data access layer
  MySQLDataService   ← Parameterized SQL, single/composite PKs, pagination
     │
     ▼
MySQL (classicmodels schema on Railway)
```

---

## API Reference

### Root

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | API info |
| GET | `/health` | Health check |
| GET | `/stats` | Analytics: revenue, order counts, top customers |

### Customers

| Method | Path | Description |
|--------|------|-------------|
| GET | `/customers` | List customers (filter by `customerName`, `city`, `country`, `state`; paginate with `limit`/`offset`) |
| POST | `/customers` | Create a customer |
| GET | `/customers/{customerNumber}` | Get one customer |
| PUT | `/customers/{customerNumber}` | Update a customer |
| DELETE | `/customers/{customerNumber}` | Delete a customer |
| GET | `/customers/{customerNumber}/orders` | All orders for a customer |

### Orders

| Method | Path | Description |
|--------|------|-------------|
| GET | `/orders` | List orders (filter by `customerNumber`, `status`; paginate) |
| POST | `/orders` | Create an order |
| GET | `/orders/{orderNumber}` | Get one order |
| PUT | `/orders/{orderNumber}` | Update an order |
| DELETE | `/orders/{orderNumber}` | Delete an order |

### Order Details

| Method | Path | Description |
|--------|------|-------------|
| GET | `/orderdetails` | List order details (filter by `orderNumber`, `productCode`; paginate) |
| POST | `/orderdetails` | Create an order detail |
| GET | `/orders/{orderNumber}/orderdetails` | All line items for an order, joined with product name + line totals |
| GET | `/orders/{orderNumber}/orderdetails/{productCode}` | Single order detail |
| PUT | `/orders/{orderNumber}/orderdetails/{productCode}` | Update an order detail |
| DELETE | `/orders/{orderNumber}/orderdetails/{productCode}` | Delete an order detail |

---

## Quick Examples

```bash
# List US customers, 10 per page
curl "https://template-mauve-eight.vercel.app/customers?country=USA&limit=10"

# Get all orders for customer 103
curl "https://template-mauve-eight.vercel.app/customers/103/orders"

# Get order 10100's line items with product details and totals
curl "https://template-mauve-eight.vercel.app/orders/10100/orderdetails"

# Analytics snapshot
curl "https://template-mauve-eight.vercel.app/stats"
```

---

## Local Setup

```bash
git clone https://github.com/jonowrenn/W4111-Template_Web_Application
cd W4111-Template_Web_Application

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env with your MySQL credentials

python -m app.main
# → http://localhost:8000/docs
```

### Loading the ClassicModels data

```bash
python scripts/load_classicmodels.py
```

This downloads the ClassicModels SQL dump from mysqltutorial.org and imports it into your configured database automatically.

---

## Deployment

### Vercel (API)

```bash
npm i -g vercel
vercel login
vercel --prod
```

Set environment variables in the Vercel dashboard (or via `vercel env add`):

```
MYSQL_HOST=<your-db-host>
MYSQL_PORT=<port>
MYSQL_USER=<user>
MYSQL_PASSWORD=<password>
MYSQL_DATABASE=<database>
```

### Database (Railway)

1. Create a project at [railway.app](https://railway.app) (GitHub login)
2. Add a MySQL service
3. Enable TCP Proxy under Settings → Networking
4. Use the proxy host/port as `MYSQL_HOST` / `MYSQL_PORT`
5. Run `python scripts/load_classicmodels.py` to import the data

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| API framework | FastAPI + Uvicorn |
| Data validation | Pydantic v2 |
| Database | MySQL 8 (classicmodels schema) |
| DB driver | PyMySQL |
| Hosting — API | Vercel (Python runtime) |
| Hosting — DB | Railway |
| Config | python-dotenv / environment variables |

---

## Project Structure

```
app/
  main.py                    # FastAPI app, route definitions
  resources/
    AbstractBaseResource.py  # Base class for all resources
    CustomerResource.py      # Customer CRUD + Pydantic models
    OrderResource.py         # Order CRUD + Pydantic models
    OrderDetailsResource.py  # OrderDetail CRUD, composite PK, JOIN queries
    HarryPotterResource.py   # Template example (JSON-backed)
  services/
    AbstractBaseDataService.py  # Abstract data service interface
    MySQLDataService.py         # MySQL implementation with pagination + raw queries
    JSONFileDataService.py      # JSON file implementation (template example)
api/
  index.py                   # Vercel entry point
scripts/
  load_classicmodels.py      # One-command data import
tests/
  hw4_notebook.ipynb         # Demo notebook — runs all endpoints top to bottom
```
