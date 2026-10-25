# Ubuntu Compatibility Table

| Feature | Ubuntu 24.04 LTS | Ubuntu 26.04 LTS |
|---------|----------------|----------------|
| **PHP** | `php8.2` and `php8.2-fpm` (default in repo) | `php8.5` and `php8.5-fpm` (default in repo) |
| **PostgreSQL** | `postgresql-16` (available in the official repo) | `postgresql-18` (available in the official repo) |
| **MySQL** | `mysql-server-8.4` (default package) | `mysql-server-8.4` (default package) |
| **Nginx** | `nginx` (same package) | `nginx` (same package) |
| **Redis** | `redis-server` (same) | `redis-server` (same) |
| **Docker (optional)** | `docker-ce`, `docker-compose-plugin` (available) | `docker-ce`, `docker-compose-plugin` (available) |

> **Note:** All versioned packages are the ones provided by the Ubuntu official repositories. No third‑party PPAs are required for the core stack.
