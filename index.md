# 📘 The Definitive Full-Stack Developer Machine Handbook
### A Complete, Deep-Dive Native Architecture & Setup Guide for Ubuntu (Linux)

> **Document Type:** Production-Grade Developer Reference & Manual  
> **Target OS:** Ubuntu 24.04 LTS / 26.04 LTS (`resolute`)  
> **Philosophy:** Pure Native Execution (Zero-Docker Overhead, Bare-Metal Performance, Maximum Stability)  
> **Target Audience:** Professional Full-Stack Software Engineers, Laravel/PHP Developers, Frontend Engineers, and Systems Tinkerers  
> **Generated Timestamp:** 2026-10-25 23:15 UTC+6  

---

## 📑 Table of Contents

1. [Architectural Philosophy: Why Native Bare-Metal Over Docker?](#1-architectural-philosophy-why-native-bare-metal-over-docker)
2. [Master Architecture Map & Port Allocations](#2-master-architecture-map--port-allocations)
3. [Section 1: The Foundation — Build Utilities, System Tooling & Shell](#3-section-1-the-foundation--build-utilities-system-tooling--shell)
4. [Section 2: The Gateway — Nginx Web Server & Reverse Proxy](#4-section-2-the-gateway--nginx-web-server--reverse-proxy)
5. [Section 3: The Engine — PHP, PHP-FPM, Composer & Laravel Ecosystem](#5-section-3-the-engine--php-php-fpm-composer--laravel-ecosystem)
6. [Section 4: The Storage Tier — MySQL Server 8.4 LTS](#6-section-4-the-storage-tier--mysql-server-84-lts)
7. [Section 5: The Enterprise Data Engine — PostgreSQL 18](#7-section-5-the-enterprise-data-engine--postgresql-18)
8. [Section 6: The Ultra-Fast In-Memory Layer — Redis 8.0](#8-section-6-the-ultra-fast-in-memory-layer--redis-80)
9. [Section 7: The Single-Pane Database Cockpit — DBeaver Community Edition](#9-section-7-the-single-pane-database-cockpit--dbeaver-community-edition)
10. [Section 8: The Frontend Runtime — FNM, Node.js LTS, NPM & PNPM](#10-section-8-the-frontend-runtime--fnm-nodejs-lts-npm--pnpm)
11. [Section 9: The Next-Gen Python Toolchain — Astral UV](#11-section-9-the-next-gen-python-toolchain--astral-uv)
12. [Section 10: The Offline-First API Client — Bruno](#12-section-10-the-offline-first-api-client--bruno)
13. [Section 11: Production Integration Recipe — Running WordPress, Laravel, PHPMyAdmin & Next.js Side-by-Side](#13-section-11-production-integration-recipe--running-wordpress-laravel-phpmyadmin--nextjs-side-by-side)
14. [Section 12: Daily Operations, Troubleshooting & Maintenance Playbook](#14-section-12-daily-operations-troubleshooting--maintenance-playbook)

---

## 1. Architectural Philosophy: Why Native Bare-Metal Over Docker?

In modern web development, containerization with Docker is ubiquitous. However, for a dedicated personal development workstation, running your primary runtime and database servers directly on the Linux host (Bare-Metal Native) provides unmatched advantages that containers cannot match:

### The Docker Tax vs. Native Bare-Metal

| Comparison Metric | Native Host (Systemd + Bare-Metal) 🏆 | Docker Desktop / Docker Engine |
| :--- | :--- | :--- |
| **Filesystem I/O Speed** | **Direct NVMe speed (Zero overhead)**. `vendor/` and `node_modules` file indexing happens at native kernel speeds. | OverlayFS filesystem abstraction adds significant latency when scanning 50,000+ tiny files in modern frameworks. |
| **RAM & Idle Resource Consumption** | **Virtually Zero (~120–250 MB total idle RAM)** for PHP-FPM, Nginx, MySQL, and Redis combined. | Docker daemon, containerd, rootless proxies, and virtual network bridges consume 2.0 to 4.5 GB RAM at idle. |
| **CPU & Battery Health** | CPU cycles execute raw instructions on bare hardware. Laptop runs significantly cooler with doubled battery longevity. | Constant virtualization polling, socket bridges, and background container health checks throttle battery. |
| **Networking & Port Mapping** | All services communicate via lightning-fast **Unix Domain Sockets** (`/run/php/php-fpm.sock`, `/var/run/mysqld/mysqld.sock`) or `localhost`. | Requires NAT, iptables packet forwarding, virtual bridge networks (`docker0`), and subnet routing. |
| **Developer Ergonomics** | Simple system commands (`systemctl status`, `mysql -u root`, `redis-cli ping`). CLI tools discover runtimes immediately. | Requires typing verbose commands like `docker exec -it <container> php artisan ...` or maintaining brittle volumes. |

> **Conclusion:** By operating natively on Ubuntu Linux, you harness the raw power of the OS that actually powers 90%+ of production cloud servers. You write code against the genuine Linux environment, eliminating subtle "works on my machine" container abstraction bugs.

---

## 2. Master Architecture Map & Port Allocations

Below is the bird's-eye architectural blueprint of how all native components connect and communicate on your workstation:

```mermaid
graph TD
    Client["🌐 Developer Browser / Bruno API Client"] -->|Port 80 (HTTP) / 443 (HTTPS)| Nginx["Nginx Reverse Proxy & Web Server"]

    subgraph Web_Routing ["Nginx Virtual Host Routing"]
        Nginx -->|Unix Socket: /run/php/php8.5-fpm.sock| Laravel["🚀 Laravel App (laravel.test)"]
        Nginx -->|Unix Socket: /run/php/php8.5-fpm.sock| WP["📝 WordPress (wp.test)"]
        Nginx -->|Unix Socket: /run/php/php8.5-fpm.sock| PMA["🗄️ PHPMyAdmin (localhost/phpmyadmin)"]
        Nginx -->|HTTP Proxy: localhost:3000| NextJS["⚡ Node.js / Next.js / Vite Apps"]
    end

    subgraph Databases ["High-Performance Native Storage"]
        Laravel -->|Socket / Port 3306| MySQL["🐬 MySQL 8.4 Server"]
        Laravel -->|Socket / Port 5432| Postgres["🐘 PostgreSQL 18 Server"]
        Laravel -->|Port 6379| Redis["⚡ Redis 8.0 Cache & Queue Worker"]
        WP -->|Socket / Port 3306| MySQL
        PMA -->|Socket / Port 3306| MySQL
    end

    subgraph Management ["Management Cockpit & Tools"]
        DBeaver["🦅 DBeaver Community Edition"] -->|Native Local & SSH Tunneling| MySQL
        DBeaver -->|Native Local & SSH Tunneling| Postgres
        DBeaver -->|Native Local & SSH Tunneling| Redis
        DBeaver -.->|Remote Bastion / Private VPC| CloudDB["☁️ AWS RDS / DigitalOcean / Cloud DBs"]
    end
```

### Official Host Port & Socket Allocations

| Component | Protocol / Binding | Port / Socket Path | Default Access Role |
| :--- | :--- | :--- | :--- |
| **Nginx Web Server** | TCP (IPv4 / IPv6) | `0.0.0.0:80`, `0.0.0.0:443` | Main entrance for all web traffic |
| **PHP 8.5 FPM** | Unix Domain Socket | `/run/php/php8.5-fpm.sock` | Blazing-fast IPC between Nginx and PHP |
| **MySQL Server** | TCP & Unix Socket | `127.0.0.1:3306` & `/var/run/mysqld/mysqld.sock` | Local relational data for WordPress/Laravel |
| **PostgreSQL 18** | TCP & Unix Socket | `127.0.0.1:5432` & `/var/run/postgresql/.s.PGSQL.5432` | Enterprise relational database |
| **Redis Server** | TCP (Loopback) | `127.0.0.1:6379` | Fast key-value caching, session storage & queues |
| **Node.js (Next/Vite)** | TCP (Loopback) | `127.0.0.1:3000` (up to 5173) | Frontend dev servers reverse-proxied by Nginx |
| **DBeaver CE** | GUI Application | Standalone Desktop Window | Connects directly to local sockets or remote SSH tunnels |

---

## 3. Section 1: The Foundation — Build Utilities, System Tooling & Shell

### 1.1 What Is It and Why Do You Need It?
Before compiling any native extensions (like PECL modules for PHP, native C++ bindings for Node.js `node-gyp`, or Python binary wheels), the operating system requires an industrial-grade toolchain. 
- **`build-essential`**: A canonical Ubuntu metapackage that bundles the GNU Compiler Collection (`gcc`, `g++`), `make`, and standard C header libraries (`libc6-dev`).
- **`fzf` & `ripgrep` (`rg`)**: The fastest search and fuzzy-finding tools available in the Unix world, allowing instant traversal of millions of lines of code.
- **`jq`**: Lightweight command-line JSON processor indispensable for parsing API responses.

### 1.2 Installation Guide
Execute in your terminal:
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y build-essential curl wget git zip unzip                     software-properties-common ca-certificates gnupg                     lsb-release fzf jq ripgrep pkg-config
```

### 1.3 How to Verify Installation
```bash
# Verify compiler
gcc --version
make --version

# Verify version control & utilities
git --version
fzf --version
rg --version
```
*Expected Output:* You should see version numbers for GCC (version 15+), Make, Git (version 2.50+), and Ripgrep.

---

## 4. Section 2: The Gateway — Nginx Web Server & Reverse Proxy

### 2.1 What Is Nginx?
**Nginx** (pronounced *engine-ex*) is an asynchronous, event-driven HTTP web server, reverse proxy, and load balancer. Developed by Igor Sysoev to solve the "C10K problem" (handling 10,000 concurrent connections on a single machine), Nginx processes requests non-blockingly inside worker loops rather than spawning heavy threads per request.

### 2.2 Why Nginx Over Apache (Comprehensive Comparison)

| Dimension | Nginx (Selected Choice) 🏆 | Apache 2 (Alternative) |
| :--- | :--- | :--- |
| **Architecture** | **Event-Driven, Asynchronous Non-blocking I/O**. A single worker thread handles thousands of connections. | **Process / Thread Driven** (`mpm_prefork` or `mpm_event`). Spawns heavy threads/processes per connection. |
| **RAM Footprint** | Extremely lightweight (~5–10 MB RAM under load). | Heavier (~30–100 MB+ RAM under load due to modules loaded in memory). |
| **Static File Delivery** | Serves static assets (CSS, JS, Images, Videos) **200% to 300% faster** via kernel `sendfile` bypass. | Slower, overhead of traversing `.htaccess` files on every directory level. |
| **Modern Reverse Proxying** | Native first-class reverse proxy for Node.js, Next.js, Python FastAPI, and Unix Sockets. | Requires enabling and configuring `mod_proxy`, `mod_proxy_http`, and complex rewrite chains. |
| **Configuration Style** | Clean, declarative blocks (`server { listen 80; ... }`). Centralized in `/etc/nginx/`. | Scattered configuration with `.htaccess` overrides in every directory, causing disk-check latency. |

> **Why we did not choose Apache:** Apache's `.htaccess` scanning slows down directory reads. In our initial audit, Apache caused a port-80 conflict that crashed Nginx. Standardizing on Nginx provides unified reverse proxying, faster page loads, and uniform server blocks across all your projects.

### 2.3 Installation Guide
```bash
sudo apt install -y nginx

# Ensure Nginx starts automatically on boot
sudo systemctl enable nginx

# Start the service immediately
sudo systemctl start nginx
```

### 2.4 How to Verify Nginx is Working
```bash
# 1. Check system service status
sudo systemctl status nginx --no-pager

# 2. Check that port 80 is actively listening
sudo ss -tulpn | grep :80

# 3. Test HTTP request locally via curl
curl -I http://localhost
```
*Expected Output:*
```text
HTTP/1.1 200 OK
Server: nginx/...
Content-Type: text/html
```
Open your browser and navigate to `http://localhost`. You will be greeted with the famous **"Welcome to nginx!"** landing page.

### 2.5 Operational Management Cheatsheet
| Action | Command | Purpose |
| :--- | :--- | :--- |
| **Start Service** | `sudo systemctl start nginx` | Starts the Nginx master and worker daemons |
| **Stop Service** | `sudo systemctl stop nginx` | Stops Nginx completely, freeing ports 80/443 |
| **Restart Service** | `sudo systemctl restart nginx` | Hard restart (drops existing connections) |
| **Graceful Reload** | `sudo systemctl reload nginx` | Re-reads configuration files without zero downtime |
| **Syntax Test** | `sudo nginx -t` | **CRITICAL:** Tests config files for syntax errors before reloading |
| **View Live Access Logs** | `sudo tail -f /var/log/nginx/access.log` | Monitors real-time browser requests |
| **View Error Logs** | `sudo tail -f /var/log/nginx/error.log` | Debugs connection errors and 502 Bad Gateway |

---

## 5. Section 3: The Engine — PHP, PHP-FPM, Composer & Laravel Ecosystem

### 3.1 What Is PHP-FPM and Composer?
- **PHP (Hypertext Preprocessor)**: The web programming language powering ~75% of the internet, including Laravel and WordPress.
- **PHP-FPM (FastCGI Process Manager)**: Instead of running PHP embedded inside the web server (which was how the slow Apache `mod_php` worked), PHP-FPM runs as an independent high-performance daemon. Nginx hands off raw PHP scripts to PHP-FPM via a ultra-fast **Unix Domain Socket** (`.sock`), receives the generated HTML, and streams it back to the client.
- **Composer**: The industry-standard dependency manager for PHP, analogous to NPM for Node.js.
- **Laravel**: The premier PHP web framework offering elegant MVC architecture, Eloquent ORM, and enterprise-grade robustness.

### 3.2 Installation Guide
Ubuntu 26.04 provides **PHP 8.5** natively. We install PHP-FPM alongside the complete suite of extensions required by both Laravel and WordPress:

```bash
# 1. Install PHP CLI, FPM, and all essential modules
sudo apt install -y php-cli php-fpm php-mysql php-pgsql php-sqlite3                     php-redis php-curl php-gd php-mbstring php-xml                     php-zip php-bcmath php-intl php-soap

# 2. Enable and start PHP-FPM daemon
sudo systemctl enable --now php8.5-fpm 2>/dev/null || sudo systemctl enable --now php*-fpm

# 3. Install Composer globally
sudo apt install -y composer

# 4. Install the official Laravel Global Installer
composer global require laravel/installer

# 5. Persist Composer binary path to your shell environment
if ! grep -q 'composer/vendor/bin' ~/.bashrc; then
    echo 'export PATH="$HOME/.config/composer/vendor/bin:$PATH"' >> ~/.bashrc
    source ~/.bashrc
fi
```

### 3.3 How to Verify Installation
```bash
# 1. Check PHP version
php -v

# 2. Check loaded modules
php -m | grep -E "redis|pdo_mysql|pdo_pgsql|mbstring|curl|gd"

# 3. Check PHP-FPM Unix Socket exists
ls -la /run/php/php*-fpm.sock

# 4. Check Composer & Laravel CLI
composer --version
laravel --version
```
*Expected Output:*
- PHP version reports `8.5.x` (or latest LTS).
- The Unix socket `/run/php/php8.5-fpm.sock` is active with `srw-rw----` permissions.
- `laravel --version` displays `Laravel Installer 5.x+`.

### 3.4 Operational Management Cheatsheet
| Action | Command | Purpose |
| :--- | :--- | :--- |
| **Check FPM Status** | `sudo systemctl status php8.5-fpm` | Verifies worker pools and memory consumption |
| **Restart FPM Workers** | `sudo systemctl restart php8.5-fpm` | Flushes OPcache and reloads PHP runtime extensions |
| **Edit PHP-FPM Config** | `sudo nano /etc/php/8.5/fpm/php.ini` | Tune `upload_max_filesize`, `memory_limit`, etc. |
| **Edit FPM Pool Settings** | `sudo nano /etc/php/8.5/fpm/pool.d/www.conf` | Adjust child process allocation (`pm.max_children`) |

---

## 6. Section 4: The Storage Tier — MySQL Server 8.4 LTS

### 4.1 What Is It and Why Do You Need It?
**MySQL** is the world's most widely adopted open-source relational database management system (RDBMS). It is the mandatory, battle-tested persistence layer for **WordPress**, and remains one of the top choices for **Laravel** web applications. Ubuntu 26.04 ships with the modern **MySQL 8.4 Long-Term Support (LTS)** release.

### 4.2 Installation & Hardening Guide
```bash
# 1. Install MySQL Server and client libraries
sudo apt install -y mysql-server mysql-client

# 2. Enable and start MySQL service
sudo systemctl enable --now mysql

# 3. Secure Root Account and Set Password
# In Ubuntu, MySQL root defaults to 'auth_socket' (requiring sudo).
# We configure native password authentication for easy DBeaver & CLI access:
sudo mysql -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'RootPass123!';"
sudo mysql -e "FLUSH PRIVILEGES;"
```
*(Replace `RootPass123!` with your preferred master local development password).*

### 4.3 How to Verify MySQL is Working
```bash
# 1. Verify service status
sudo systemctl status mysql --no-pager

# 2. Check local listening port 3306
sudo ss -tulpn | grep :3306

# 3. Log in via CLI client
mysql -u root -p'RootPass123!' -e "SELECT VERSION(), CURRENT_USER();"
```
*Expected Output:* You should see `8.4.x-0ubuntu...` and `root@localhost`.

### 4.4 Operational Management Cheatsheet
| Action | Command | Purpose |
| :--- | :--- | :--- |
| **Start Service** | `sudo systemctl start mysql` | Starts the MySQL server daemon (`mysqld`) |
| **Stop Service** | `sudo systemctl stop mysql` | Shuts down MySQL gracefully and flushes tables |
| **Restart Service** | `sudo systemctl restart mysql` | Full reboot of database daemon |
| **Database Directory** | `/var/lib/mysql` | Raw InnoDB data files and tablespaces |
| **Configuration File** | `/etc/mysql/mysql.conf.d/mysqld.cnf` | Tune `max_connections`, `innodb_buffer_pool_size` |

---

## 7. Section 5: The Enterprise Data Engine — PostgreSQL 18

### 7.1 What Is It and Why Do You Need It?
**PostgreSQL** is an advanced, enterprise-grade open-source object-relational database system known for reliability, feature robustness, and performance. It excels at complex queries, JSONB document manipulation, geospatial data (PostGIS), and transactional integrity. In modern Laravel and Python applications, PostgreSQL is frequently the preferred database engine over MySQL.

### 7.2 Installation & Configuration Guide
Ubuntu 26.04 includes the cutting-edge **PostgreSQL 18**:
```bash
# 1. Install PostgreSQL 18 and common contrib modules
sudo apt install -y postgresql postgresql-contrib

# 2. Enable and start the PostgreSQL cluster
sudo systemctl enable --now postgresql

# 3. Configure a password for the default 'postgres' superuser
# This allows DBeaver to connect over localhost:5432
sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD 'PostgresPass123!';"
```
*(Replace `PostgresPass123!` with your desired local password).*

### 7.3 How to Verify PostgreSQL is Working
```bash
# 1. Check systemd service status
sudo systemctl status postgresql --no-pager

# 2. Check local port 5432
sudo ss -tulpn | grep :5432

# 3. Execute query using psql client
PGPASSWORD='PostgresPass123!' psql -h localhost -U postgres -c "SELECT version();"
```
*Expected Output:* You will see `PostgreSQL 18.x ... on x86_64-pc-linux-gnu`.

### 7.4 Operational Management Cheatsheet
| Action | Command | Purpose |
| :--- | :--- | :--- |
| **Start Cluster** | `sudo systemctl start postgresql` | Starts all active PostgreSQL clusters |
| **Stop Cluster** | `sudo systemctl stop postgresql` | Gracefully closes connections and stops daemon |
| **Restart Cluster** | `sudo systemctl restart postgresql` | Full daemon restart |
| **Access Interactive Shell** | `sudo -u postgres psql` | Direct root administrative shell |
| **Config Directory** | `/etc/postgresql/18/main/` | Houses `postgresql.conf` and `pg_hba.conf` |

---

## 8. Section 6: The Ultra-Fast In-Memory Layer — Redis 8.0

### 8.1 What Is It and Why Do You Need It?
**Redis** (Remote Dictionary Server) is an open-source, in-memory data structure store used as a distributed database, cache, and message broker. 
- In **Laravel**, Redis acts as the high-speed backend for session storage, cache tagging (`Cache::remember`), and real-time asynchronous queue processing (`php artisan queue:work`).
- In **WordPress**, Redis Object Cache accelerates page generation by up to 1000% by caching query results in RAM.

### 8.2 Installation Guide
```bash
# 1. Install Redis Server and CLI tools
sudo apt install -y redis-server redis-tools

# 2. Enable and start Redis
sudo systemctl enable --now redis-server
```

### 8.3 How to Verify Redis is Working
```bash
# 1. Check service status
sudo systemctl status redis-server --no-pager

# 2. Send ping to Redis daemon
redis-cli ping
```
*Expected Output:* `PONG`.

### 8.4 Operational Management Cheatsheet
| Action | Command | Purpose |
| :--- | :--- | :--- |
| **Test Latency** | `redis-cli --latency` | Measures network/socket latency in milliseconds |
| **Flush All Cache** | `redis-cli flushall` | **CAUTION:** Instantly purges all in-memory keys |
| **Monitor Live Commands** | `redis-cli monitor` | Streams every query executed by Laravel/WP live |
| **Configuration File** | `/etc/redis/redis.conf` | Tune `maxmemory` and eviction policies |

---

## 9. Section 7: The Single-Pane Database Cockpit — DBeaver Community Edition

### 9.1 What Is DBeaver CE?
**DBeaver Community Edition** is a universal, open-source multi-platform database management tool built on the Eclipse platform. It supports any database with a JDBC driver, including MySQL, PostgreSQL, SQLite, Redis, Oracle, and cloud warehouses.

### 9.2 Why DBeaver Replaces BOTH pgAdmin and MySQL Workbench

| Feature / Scenario | DBeaver CE (Unified Champion) 🏆 | pgAdmin 4 | MySQL Workbench |
| :--- | :--- | :--- | :--- |
| **Supported Engines** | **Universal** (MySQL, Postgres, MariaDB, Redis, SQLite, DuckDB, MongoDB). | PostgreSQL only. | MySQL only. |
| **Remote Database Access (SSH Tunneling)** | **Built-in Zero-Config SSH Bastion Support**. Connects to private VPC cloud databases using private keys (`.pem`/`id_rsa`). | Web-based interface; complex SSH setup. | Basic SSH tunneling; prone to connection drops. |
| **Cross-Database Data Transfer** | **Drag & Drop ETL**: Copy tables directly from remote MySQL into local PostgreSQL. | Not possible. | Not possible. |
| **RAM & Overhead** | Single native desktop process (~200 MB). | Spawns heavy Python WSGI backend web server. | Heavy Snap sandbox container (~300 MB+). |
| **ER Diagrams & Visual Query Builder** | Automatic ERD generation for any database with one click. | Basic ERD for Postgres. | MySQL only. |

> **The Verdict:** DBeaver eliminates software bloat. Instead of running two separate single-engine GUI tools, DBeaver gives you an enterprise cockpit that manages both your local databases and your remote cloud clusters.

### 9.3 Installation Guide
```bash
# 1. Download and trust official DBeaver GPG keyring
sudo mkdir -p /etc/apt/keyrings
wget -O - https://dbeaver.io/debs/dbeaver.gpg.key | sudo gpg --dearmor -o /etc/apt/keyrings/dbeaver.gpg 2>/dev/null || true

# 2. Add repository source
echo "deb [signed-by=/etc/apt/keyrings/dbeaver.gpg] https://dbeaver.io/debs/dbeaver-ce /" | sudo tee /etc/apt/sources.list.d/dbeaver.list

# 3. Update index and install DBeaver CE
sudo apt update
sudo apt install -y dbeaver-ce
```

### 9.4 Pro-Tip: Connecting to Remote Databases Behind a Firewall / Bastion
To connect to an AWS RDS or remote database not exposed to the public internet:
1. Open DBeaver $ightarrow$ **New Database Connection** $ightarrow$ Choose **MySQL** or **PostgreSQL**.
2. In the **Main** tab, enter the database host (e.g. `127.0.0.1` or the private RDS VPC endpoint) and credentials.
3. Switch to the **SSH** tab:
   - Check **"Use SSH Tunnel"**.
   - **Host/IP:** Enter your public Bastion server / VPS IP.
   - **Username:** `ubuntu` (or your server user).
   - **Authentication Method:** Select **Public Key** and browse to your private key (`~/.ssh/id_rsa` or `key.pem`).
4. Click **Test Connection**. DBeaver securely tunnels the connection over encrypted SSH!

---

## 10. Section 8: The Frontend Runtime — FNM, Node.js LTS, NPM & PNPM

### 10.1 What Is FNM (Fast Node Manager)?
**FNM** is a blazing-fast Node.js version manager built in Rust. It serves as a modern replacement for legacy `nvm` (Node Version Manager). Unlike `nvm` which adds 500ms+ of lag to every new shell startup due to heavy bash scripting, FNM loads in under **5 milliseconds** and supports automatic `.nvmrc` version switching.

### 10.2 Installation Guide
```bash
# 1. Install FNM binary
curl -fsSL https://fnm.vercel.app/install | bash

# 2. Activate FNM environment in current shell session
export PATH="$HOME/.local/share/fnm:$PATH"
eval "`fnm env`"

# 3. Install latest Long-Term Support (LTS) Node.js release
fnm install --lts

# 4. Set as default global runtime
fnm default lts-latest

# 5. Install high-performance package managers globally
npm install -g pnpm yarn
```

### 10.3 How to Verify Installation
```bash
node -v
npm -v
pnpm -v
```
*Expected Output:*
- Node.js reports active LTS version (e.g. `v22.x` or `v24.x`).
- NPM and PNPM CLI tools are active in your path.

---

## 11. Section 9: The Next-Gen Python Toolchain — Astral UV

### 11.1 What Is Astral UV?
**`uv`** is an extremely fast Python package and project manager developed by Astral (creators of Ruff), written in Rust. It is engineered as a 10x-100x faster drop-in replacement for `pip`, `pip-tools`, `virtualenv`, and `poetry`.

### 11.2 Why UV?
- **Global Interpreter Safety:** Modern Ubuntu versions enforce PEP 668 (`externally-managed-environment`), preventing risky `sudo pip install` from breaking the OS.
- `uv` creates isolated virtual environments instantaneously (in ~15 milliseconds).
- Resolves and installs complex Python packages (Django, FastAPI, Pandas) in seconds from local caches.

### 11.3 Installation & Quickstart
```bash
# 1. Install UV standalone binary
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc

# 2. Verify
uv --version
```

### How to use for a new Python project:
```bash
mkdir my-python-app && cd my-python-app
uv venv                       # Instantly creates a pristine .venv
source .venv/bin/activate     # Activate virtual environment
uv pip install fastapi uvicorn django  # Ultra-fast package installation
```

---

## 12. Section 10: The Offline-First API Client — Bruno

### 12.1 What Is Bruno?
**Bruno** is an open-source, fast, git-friendly desktop API client designed to challenge Postman and Insomnia.

### 12.2 Why Bruno Instead of Postman?

| Evaluation Point | Bruno ([usebruno.com](https://usebruno.com)) 🏆 | Postman |
| :--- | :--- | :--- |
| **Privacy & Security** | **100% Offline-First**. Collections live on your filesystem as `.bru` text files. Zero company data leaks. | Forces cloud accounts. Requests and secrets sync to Postman's third-party cloud. |
| **Git Collaboration** | Commit API requests directly into your git repository alongside your Laravel/Node source code. | Trapped in proprietary cloud workspaces; requires paid tiers for team sharing. |
| **Performance & Weight** | Lightweight, instantaneous launch, minimal memory usage. | Bloated Electron container consuming 1+ GB RAM and displaying frequent sign-in modals. |
| **Cost** | 100% Open-Source (MIT License). Free forever for personal and commercial use. | Freemium paywalls on runner limits and team seats. |

### 12.3 Installation Guide
```bash
# 1. Add official Bruno repository keyring
sudo mkdir -p /etc/apt/keyrings
gpg --keyserver keyserver.ubuntu.com --recv-keys 9FA6017ECABE0266 2>/dev/null || true
gpg --export 9FA6017ECABE0266 | sudo tee /etc/apt/keyrings/bruno.gpg > /dev/null

# 2. Add apt source list
echo "deb [signed-by=/etc/apt/keyrings/bruno.gpg] http://debian.usebruno.com/ bruno stable" | sudo tee /etc/apt/sources.list.d/bruno.list

# 3. Update index and install Bruno
sudo apt update
sudo apt install -y bruno
```

---

## 13. Section 11: Production Integration Recipe — Running WordPress, Laravel, PHPMyAdmin & Next.js Side-by-Side

Now that all native components are in place, here is the exact production configuration to run all your development stacks simultaneously on Nginx without collisions.

### Step 1: Configure Local Hostnames
Map your local development domains in `/etc/hosts`:
```bash
sudo bash -c 'cat << EOF >> /etc/hosts
127.0.0.1   laravel.test
127.0.0.1   wp.test
127.0.0.1   app.test
EOF'
```

---

### Recipe A: Modern Laravel 11/12 Nginx Server Block
Create file `/etc/nginx/sites-available/laravel.test`:
```nginx
server {
    listen 80;
    listen [::]:80;
    server_name laravel.test;
    root /home/user/Development/my-laravel-project/public;

    add_header X-Frame-Options "SAMEORIGIN";
    add_header X-Content-Type-Options "nosniff";

    index index.php index.html;
    charset utf-8;

    location / {
        try_files $uri $uri/ /index.php?$query_string;
    }

    location = /favicon.ico { access_log off; log_not_found off; }
    location = /robots.txt  { access_log off; log_not_found off; }

    error_page 404 /index.php;

    location ~ \.php$ {
        fastcgi_pass unix:/run/php/php8.5-fpm.sock;
        fastcgi_param SCRIPT_FILENAME $realpath_root$fastcgi_script_name;
        include fastcgi_params;
        fastcgi_hide_header X-Powered-By;
    }

    location ~ /\.(?!well-known).* {
        deny all;
    }
}
```

---

### Recipe B: WordPress Nginx Server Block
Create file `/etc/nginx/sites-available/wp.test`:
```nginx
server {
    listen 80;
    server_name wp.test;
    root /var/www/html/wordpress;

    index index.php index.html;

    location / {
        try_files $uri $uri/ /index.php?$args;
    }

    location ~ \.php$ {
        include snippets/fastcgi-php.conf;
        fastcgi_pass unix:/run/php/php8.5-fpm.sock;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        include fastcgi_params;
    }

    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires max;
        log_not_found off;
    }
}
```

---

### Recipe C: PHPMyAdmin Sub-Path Setup (`http://localhost/phpmyadmin`)
Add the following location block inside `/etc/nginx/sites-available/default`:
```nginx
location /phpmyadmin {
    root /usr/share/;
    index index.php index.html index.htm;

    location ~ ^/phpmyadmin/(.+\.php)$ {
        try_files $uri =404;
        root /usr/share/;
        fastcgi_pass unix:/run/php/php8.5-fpm.sock;
        fastcgi_index index.php;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        include fastcgi_params;
    }

    location ~* ^/phpmyadmin/(.+\.(jpg|jpeg|gif|css|png|js|ico|html|xml|txt))$ {
        root /usr/share/;
    }
}
```

---

### Recipe D: Reverse-Proxying Node.js / Next.js / Vite (`app.test`)
Create file `/etc/nginx/sites-available/app.test`:
```nginx
server {
    listen 80;
    server_name app.test;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### Enable Sites & Reload:
```bash
sudo ln -s /etc/nginx/sites-available/laravel.test /etc/nginx/sites-enabled/
sudo ln -s /etc/nginx/sites-available/wp.test /etc/nginx/sites-enabled/
sudo ln -s /etc/nginx/sites-available/app.test /etc/nginx/sites-enabled/

# ALWAYS verify syntax before reload:
sudo nginx -t

# Reload Nginx:
sudo systemctl reload nginx
```

---

## 14. Section 12: Daily Operations, Troubleshooting & Maintenance Playbook

### Diagnostic & Health Check Scripts

Keep these one-liners handy to inspect your entire development environment in seconds:

#### 1. Instant Service Health Check
```bash
systemctl is-active nginx php8.5-fpm mysql postgresql redis-server
```
*Expected Output:*
```text
active
active
active
active
active
```

#### 2. Port Binding Audit
```bash
sudo ss -tulpn | grep -E "nginx|php|mysql|postgres|redis"
```

#### 3. Resolving "502 Bad Gateway" in Nginx
A 502 Bad Gateway means Nginx cannot talk to the PHP-FPM socket. Follow these diagnostic steps:
1. Verify PHP-FPM is running: `sudo systemctl status php8.5-fpm`
2. Check socket path permissions: `ls -l /run/php/php8.5-fpm.sock`
3. Inspect live Nginx error logs: `sudo tail -n 20 /var/log/nginx/error.log`

#### 4. Resolving MySQL "Access Denied for user 'root'@'localhost'"
If password authentication fails, log in via system socket and reset:
```bash
sudo mysql -u root
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'YourNewPassword!';
FLUSH PRIVILEGES;
EXIT;
```

#### 5. Safe System Maintenance & Cache Cleanup
Run once a month to keep your workstation lean:
```bash
# Clean package manager cache
sudo apt autoremove --purge -y
sudo apt clean

# Clean NPM and Composer caches
npm cache clean --force 2>/dev/null || true
composer clear-cache 2>/dev/null || true

# Check NVMe disk usage
df -h /
```

---

### 🎉 Summary & Architecture Certificate
With this architecture in place, your workstation is configured to world-class software engineering standards:
- **Zero virtualization overhead** (pure native speed).
- **Zero port collisions** (Nginx fully orchestrates port 80/443).
- **Unified database management** with DBeaver CE.
- **Privacy-first API development** with Bruno.
- **Independent multi-runtime support** with FNM, UV, and PHP-FPM.
