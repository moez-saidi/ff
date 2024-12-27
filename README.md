# FastAPI Project with PostgreSQL and Alembic

## Project Overview

This is a **FastAPI** project with a **PostgreSQL** database and **Alembic** for migrations. The project is containerized using Docker and includes a basic setup for API endpoints, database models, and migrations.

---

## Features

- **FastAPI** for building APIs.
- **PostgreSQL** for the database.
- **Alembic** for migrations.
- **Docker Compose** for containerized deployment.
- **Auto-reload** during development.

---

## Getting Started

### Prerequisites

- Install [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/).
- Python 3.11
- precommit install

### Steps to Run

**Set Up Environment Variables:**

Create a .env file in the project root with the following:

```bash
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
POSTGRES_DB=your_db_name
POSTGRES_HOST=db
PGPORT=5432
POSTGRES_VERSION=17.2
```

**Run the Application:**

```bash
docker compose -p ff --env-file .env up -d --build
```
