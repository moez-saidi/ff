# FastAPI Project with PostgreSQL and Alembic

## 🚀 Project Overview

This project is built with **FastAPI**, **PostgreSQL**, and **Alembic** to provide a scalable and efficient API. It is fully containerized using **Docker Compose** and includes automatic reloading during development.

---

## ✨ Features

- ⚡ **FastAPI** - High-performance web framework for APIs.
- 🗄️ **PostgreSQL** - Powerful, open-source relational database.
- 🔄 **Alembic** - Database migration management.
- 🐳 **Docker Compose** - Containerized deployment.
- 🔁 **Auto-reload** - Automatically refreshes during development.

---

## 🛠️ Getting Started

### 📌 Prerequisites

Ensure you have the following installed:

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- Python **3.11**
- Pre-commit hooks (`pre-commit install`)

---

### 📄 Environment Configuration

Create a **`.env`** file in the project root with the following variables:

```ini
# PostgreSQL Configuration
POSTGRES_USER=db_user
POSTGRES_PASSWORD=db_pass
POSTGRES_DB=db
POSTGRES_HOST=postgresdb
PGPORT=5432
POSTGRES_VERSION=17.2

# Security
SECRET_KEY=your_secret_key_used_for_jwt

# RabbitMQ Configuration
RABBITMQ_DEFAULT_USER=guest
RABBITMQ_DEFAULT_PASS=guest_pass
RABBITMQ_PORT=5672
```

---

## 🚀 Running the Application

### 🔹 Start the Application

```bash
docker compose -p ff --env-file .env up -d --build
```

### 🔹 Stop and Remove Containers

```bash
docker compose -p ff --env-file .env down -v
```

---

## 📌 Additional Notes

- Ensure your `.env` file is correctly configured before starting the application.
- You can modify the `docker-compose.yml` file to adjust container settings.
- Logs can be viewed using:

  ```bash
  docker logs -f <container_name>
  ```

- To run database migrations with Alembic:

  ```bash
  alembic upgrade head
  ```

---

## 📜 License

This project is licensed under the **MIT License**.

---

## 💡 Contributing

Contributions are welcome! Feel free to fork this repository, make improvements, and submit a pull request.

---

## 📞 Contact

For questions or support, please open an issue or reach out to the maintainer.

---

