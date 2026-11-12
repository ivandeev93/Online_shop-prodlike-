# Online Shop API

A backend REST API for an online store built with **FastAPI**, **PostgreSQL**, and **SQLAlchemy**. The project follows a layered architecture and uses Docker Compose for local development and deployment.

## Features

- JWT authentication and token refresh
- Role-based access control (buyer, seller, admin)
- Product and category management
- Product search and filtering
- Shopping cart management
- Order checkout and order history
- Product reviews and rating calculation
- Product image upload
- Database migrations with Alembic

## Tech Stack

- **Language:** Python 3.11
- **Framework:** FastAPI
- **Database:** PostgreSQL 16
- **ORM:** SQLAlchemy 2.0 (async)
- **Migrations:** Alembic
- **Authentication:** JWT
- **Password hashing:** bcrypt
- **Containerization:** Docker, Docker Compose
- **ASGI server:** Uvicorn

## Architecture

The application uses a layered architecture:

```text
API → Services → Repositories → Database
```

- **API layer** — handles HTTP requests, response schemas, and dependencies.
- **Service layer** — contains business logic and application rules.
- **Repository layer** — handles database queries and persistence.
- **Models** — define database entities and relationships.

This separation makes the application easier to maintain, test, and extend.

## Project Structure

```text
.
├── alembic/
│   └── versions/
├── app/
│   ├── api/
│   ├── core/
│   ├── exceptions/
│   ├── models/
│   ├── repositories/
│   ├── services/
│   ├── auth.py
│   ├── config.py
│   ├── main.py
│   └── schemas.py
├── .dockerignore
├── .env.example
├── .gitignore
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## Getting Started

### Requirements

- Docker
- Docker Compose

### 1. Clone the repository

```bash
git clone https://github.com/ivandeev93/Online_shop-prodlike-.git
cd Online_shop-prodlike-
```

### 2. Configure environment variables

Create your local `.env` file:

```bash
cp .env.example .env
```

On Windows PowerShell, use:

```powershell
Copy-Item .env.example .env
```

Update the values in `.env`:

```env
DATABASE_URL=postgresql+asyncpg://shop_user:change_me@localhost:5432/online_shop

POSTGRES_USER=shop_user
POSTGRES_PASSWORD=change_me
POSTGRES_DB=online_shop

SECRET_KEY=replace_with_a_long_random_secret_key
```

Use a strong, unique password and secret key. Do not commit your `.env` file.

### 3. Build the Docker image

```bash
docker compose build
```

### 4. Start the database

```bash
docker compose up -d db
```

### 5. Apply database migrations

```bash
docker compose run --rm web alembic upgrade head
```

### 6. Start the application

```bash
docker compose up -d
```

The API will be available at:

```text
http://localhost:8000
```

## API Documentation

FastAPI automatically generates interactive API documentation.

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Database Migrations

Apply all available migrations:

```bash
docker compose run --rm web alembic upgrade head
```

Generate a new migration:

```bash
docker compose run --rm web alembic revision --autogenerate -m "migration_message"
```

## Main API Endpoints

| Module | Method | Endpoint | Description |
|---|---|---|---|
| Users | POST | `/users/` | Register a user |
| Users | POST | `/users/token` | Authenticate |
| Users | POST | `/users/refresh-token` | Refresh access token |
| Products | GET | `/products/` | List products |
| Products | POST | `/products/` | Create a product |
| Products | GET | `/products/{product_id}` | Get product details |
| Categories | GET | `/categories/` | List categories |
| Cart | GET | `/cart/` | Get shopping cart |
| Cart | POST | `/cart/items` | Add an item |
| Orders | POST | `/orders/checkout` | Create an order |
| Orders | GET | `/orders/` | Get user orders |
| Reviews | POST | `/reviews/` | Create a review |
| Reviews | GET | `/reviews/products/{product_id}/reviews/` | Get product reviews |

For the complete list of endpoints and request schemas, see Swagger UI.

## Docker Services

The application runs with two main services:

- **web** — FastAPI application.
- **db** — PostgreSQL database.

Docker Compose also configures persistent volumes for PostgreSQL data and uploaded media files, as well as a database health check.

## License

This project is intended for educational and portfolio purposes.