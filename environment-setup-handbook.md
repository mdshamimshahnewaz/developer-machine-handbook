---
layout: default
title: "Ubuntu Developer Workstation Setup Guide"
description: "A Practical, Step-by-Step Developer Workstation Guide for Ubuntu 26.04 & 24.04 LTS"
permalink: /environment-setup-handbook/
---

# 🚀 Ubuntu Developer Workstation Setup Guide
### A Practical, Step-by-Step Guide for Ubuntu 26.04 & 24.04 LTS

This guide provides a straightforward, copy-paste friendly walkthrough for configuring a clean Ubuntu developer workstation. 

**Default Philosophy:** Native Linux installation (fastest disk I/O, direct hardware execution, zero container overhead). Docker remains completely optional.

---

## 📑 9-Step Setup Overview

1. [Step 1: Update Ubuntu and Install Essential Tools](#step-1-update-ubuntu-and-install-essential-tools)
2. [Step 2: Configure Git and SSH](#step-2-configure-git-and-ssh)
3. [Step 3: Install PHP, Composer, and Laravel Tooling](#step-3-install-php-composer-and-laravel-tooling)
4. [Step 4: Install Python, uv, Django, and DRF Tooling](#step-4-install-python-uv-django-and-drf-tooling)
5. [Step 5: Install Node.js and Frontend Tooling](#step-5-install-nodejs-and-frontend-tooling)
6. [Step 6: Install MySQL and PostgreSQL](#step-6-install-mysql-and-postgresql)
7. [Step 7: Install Nginx and Configure Local Development](#step-7-install-nginx-and-configure-local-development)
8. [Step 8: Install Optional Redis and AI/ML Tools](#step-8-install-optional-redis-and-aiml-tools)
9. [Step 9: Verify Environment and Troubleshoot Common Problems](#step-9-verify-environment-and-troubleshoot-common-problems)

---

## Step 1: Update Ubuntu and Install Essential Tools

**Why it's needed:** Build compilers, curl, archive utilities, and search tools are required to compile native language extensions (PECL, node-gyp, Python wheels) and navigate code efficiently.

### Commands
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y build-essential curl wget git zip unzip \
    software-properties-common ca-certificates gnupg lsb-release \
    fzf jq ripgrep pkg-config htop
```

### Verification
```bash
gcc --version
git --version
rg --version
```
*Expected result:* Outputs version numbers for GCC compiler, Git, and Ripgrep.

---

## Step 2: Configure Git and SSH

**Why it's needed:** Ed25519 SSH keys provide secure authentication with GitHub and GitLab without storing plaintext passwords or personal access tokens in files.

### Commands
```bash
# 1. Generate an Ed25519 key (replace with your email)
ssh-keygen -t ed25519 -C "developer@example.com" -f ~/.ssh/id_ed25519

# 2. Configure SSH agent to use the key automatically
mkdir -p ~/.ssh && chmod 700 ~/.ssh
cat << 'EOF' >> ~/.ssh/config
Host *
    AddKeysToAgent yes
    IdentityFile ~/.ssh/id_ed25519
EOF
chmod 600 ~/.ssh/config

# 3. Configure Git global identity
git config --global user.name "Your Name"
git config --global user.email "developer@example.com"
git config --global init.defaultBranch main
git config --global pull.rebase true
```

### Verification
Display your **public** key and add it to [GitHub SSH Keys](https://github.com/settings/keys):
```bash
cat ~/.ssh/id_ed25519.pub
```
> **Warning:** Never share or commit your private key (`~/.ssh/id_ed25519`). Only copy the `.pub` file contents.

Test connection:
```bash
ssh -T git@github.com
```
*Expected result:* `Hi <username>! You've successfully authenticated...`

---

## Step 3: Install PHP, Composer, and Laravel Tooling

**Why it's needed:** Powers Laravel and modern PHP development using high-performance FastCGI Process Manager (PHP-FPM) communicating over Unix sockets.

### Commands
Ubuntu 26.04 provides **PHP 8.5** and Ubuntu 24.04 provides **PHP 8.2**. This snippet automatically detects your release and installs the appropriate native stack:

```bash
UBUNTU_VER=$(lsb_release -rs)
if [[ "$UBUNTU_VER" == "24.04" ]]; then
    PHP_PKG="8.2"
else
    PHP_PKG="8.5"
fi

sudo apt install -y php${PHP_PKG}-cli php${PHP_PKG}-fpm \
    php${PHP_PKG}-mysql php${PHP_PKG}-pgsql php${PHP_PKG}-sqlite3 \
    php${PHP_PKG}-redis php${PHP_PKG}-curl php${PHP_PKG}-gd \
    php${PHP_PKG}-mbstring php${PHP_PKG}-xml php${PHP_PKG}-zip \
    php${PHP_PKG}-bcmath php${PHP_PKG}-intl composer

# Enable and start PHP-FPM service
sudo systemctl enable --now php${PHP_PKG}-fpm

# Standardize socket symlink for Nginx virtual hosts
sudo ln -sf /run/php/php${PHP_PKG}-fpm.sock /run/php/php-fpm.sock

# Install Laravel installer globally
composer global require laravel/installer

# Add Composer bin to PATH if not already present
if ! grep -q 'composer' ~/.bashrc; then
    echo 'export PATH="$HOME/.config/composer/vendor/bin:$PATH"' >> ~/.bashrc
    source ~/.bashrc
fi
```

### Verification
```bash
php -v
composer --version
laravel --version
ls -la /run/php/php-fpm.sock
```
*Expected result:* PHP version, Composer version, Laravel installer version, and an active Unix socket file.

---

## Step 4: Install Python, uv, Django, and DRF Tooling

**Why it's needed:** Per PEP 668, modern Ubuntu environments restrict direct `pip install` into system Python. We use **Astral `uv`**, a fast Rust-based tool, to manage isolated virtual environments and locked dependencies.

### Commands
```bash
# 1. Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env

# 2. Quick-start a Django REST Framework project
mkdir -p ~/projects/my-api && cd ~/projects/my-api
uv init --app
uv venv .venv
source .venv/bin/activate

# 3. Add Django, DRF, PostgreSQL driver, and code-quality tools
uv add django djangorestframework psycopg[binary] python-dotenv
uv add --dev ruff pytest pytest-django
uv lock
```

### Verification
```bash
uv --version
uv run ruff --version
uv run python -c "import django, rest_framework; print('Django:', django.__version__, '| DRF:', rest_framework.__version__)"
```
*Expected result:* Displays `uv`, `ruff`, and versions of Django & DRF inside the isolated `.venv`.

> 💡 *Need local Gunicorn or systemd services for Django?* See [Production Django Deployment Reference](file:///home/user/developer-machine-handbook/docs/production-django-deployment.md).

---

## Step 5: Install Node.js and Frontend Tooling

**Why it's needed:** Frontend apps (React, Vue, Vite, Next.js) need Node.js and package managers. **Fast Node Manager (`fnm`)** lets you switch Node versions instantly without shell startup slowdown.

### Commands
```bash
# 1. Install fnm
curl -fsSL https://fnm.vercel.app/install | bash

# 2. Add fnm to ~/.bashrc safely
if ! grep -q 'fnm env' ~/.bashrc; then
    cat << 'EOF' >> ~/.bashrc

# Fast Node Manager
export PATH="$HOME/.local/share/fnm:$PATH"
eval "`fnm env --use-on-cd --shell bash`"
EOF
    source ~/.bashrc
fi

# 3. Install Node.js LTS and enable corepack (pnpm)
fnm install --lts
fnm default lts-latest
corepack enable
```

### Verification
```bash
node -v
npm -v
pnpm -v
```
*Expected result:* Displays Node LTS (v24.x+ or v22.x+), npm, and pnpm versions.

---

## Step 6: Install MySQL and PostgreSQL

**Why it's needed:** Relational persistence for Laravel (MySQL/PostgreSQL) and Django (PostgreSQL).

### Commands
```bash
# Install MySQL & PostgreSQL
sudo apt install -y mysql-server postgresql postgresql-contrib
sudo systemctl enable --now mysql postgresql
```

### Creating Dedicated Application Users (Practical Security)
> **Important:** Never use administrative root accounts in your application `.env` files. Ubuntu MySQL uses secure `auth_socket` for local root by default. Create dedicated users instead:

```bash
# 1. Create a MySQL database and dedicated project user
sudo mysql -e "
CREATE DATABASE IF NOT EXISTS app_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'app_user'@'localhost' IDENTIFIED BY 'LocalDevSecret123!';
GRANT ALL PRIVILEGES ON app_db.* TO 'app_user'@'localhost';
FLUSH PRIVILEGES;
"

# 2. Create a PostgreSQL database and dedicated project user
sudo -u postgres psql -c "
CREATE DATABASE app_db;
CREATE USER app_user WITH ENCRYPTED PASSWORD 'LocalDevSecret123!';
GRANT ALL PRIVILEGES ON DATABASE app_db TO app_user;
" 2>/dev/null || true
```

### Verification
```bash
# Test MySQL user login
mysql -u app_user -p'LocalDevSecret123!' -e "SHOW DATABASES;"

# Test PostgreSQL user login
PGPASSWORD='LocalDevSecret123!' psql -U app_user -h localhost -d app_db -c "\l"
```
*Expected result:* Lists databases accessible by `app_user` for both MySQL and Postgres.

> 💡 *GUI Client Recommendation:* Install **DBeaver Community Edition** for a single graphical interface supporting both MySQL and PostgreSQL.

---

## Step 7: Install Nginx and Configure Local Development

**Why it's needed:** Nginx serves as the reverse proxy on port 80/443, routing traffic to Laravel PHP-FPM sockets, Node.js dev servers, or Django APIs with friendly `.test` or `.local` domains.

### Commands
```bash
# Check if port 80 is free (stop Apache if it was previously installed)
if sudo ss -tulpn | grep -q ':80.*apache2'; then
    sudo systemctl stop apache2 && sudo systemctl disable apache2
fi

sudo apt install -y nginx
sudo systemctl enable --now nginx
```

### Creating a Simple Laravel Virtual Host
Create `/etc/nginx/sites-available/app.test.conf`:
```nginx
server {
    listen 80;
    server_name app.test;
    root /home/user/projects/sample-app/public;

    index index.php index.html;

    location / {
        try_files $uri $uri/ /index.php?$query_string;
    }

    location ~ \.php$ {
        fastcgi_pass unix:/run/php/php-fpm.sock;
        fastcgi_param SCRIPT_FILENAME $realpath_root$fastcgi_script_name;
        include fastcgi_params;
    }
}
```

Enable site safely:
```bash
sudo ln -sf /etc/nginx/sites-available/app.test.conf /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

### Verification
```bash
curl -I http://localhost
```
*Expected result:* `HTTP/1.1 200 OK` (Welcome to nginx).

---

## Step 8: Install Optional Redis and AI/ML Tools

**Why it's needed:** Optional in-memory caching and background queues for Laravel/Django, and local LLM execution.

### Redis Setup (Optional)
```bash
sudo apt install -y redis-server
sudo systemctl enable --now redis-server

# Verify Redis is bound safely to localhost (127.0.0.1)
grep "^bind" /etc/redis/redis.conf
redis-cli ping
```
*Expected result:* Outputs `PONG`.

### Local AI/ML & LLM Runner (Optional)
Run models like Llama 3 or Qwen locally with **Ollama** (zero container overhead):
```bash
# Install Ollama native binary
curl -fsSL https://ollama.com/install.sh | sh

# Pull and run a lightweight model
ollama run llama3.2:1b
```

> 💡 *Using NVIDIA GPUs or CUDA?* See [AI/ML & GPU Acceleration Reference](file:///home/user/developer-machine-handbook/docs/ai-ml-gpu-setup.md).

### Docker (Optional)
If you require Docker for isolated third-party tools:
```bash
sudo apt install -y docker-ce docker-compose-plugin
sudo usermod -aG docker $USER
```
*Docker remains strictly optional; all core tools above run natively.*

---

## Step 9: Verify Environment and Troubleshoot Common Problems

### One-Line Health Check Cheatsheet
Run this single block to check all your core development services:

```bash
echo "=== 1. Active Services ==="
systemctl is-active nginx mysql postgresql redis-server

echo "=== 2. Listening Ports (Must be 127.0.0.1 for DBs) ==="
sudo ss -tulpn | grep -E ':80|:3306|:5432|:6379'

echo "=== 3. Runtimes ==="
php -v | head -n 1
uv --version
node -v
```

### Common Fixes

| Issue | Quick Diagnostic & Fix |
| :--- | :--- |
| **Nginx fails to start** | Check port conflict: `sudo ss -tulpn \| grep :80`. Test syntax: `sudo nginx -t`. |
| **PHP 502 Bad Gateway** | Confirm socket path matches: `ls -la /run/php/php*-fpm.sock` and `/run/php/php-fpm.sock`. |
| **MySQL Access Denied** | Use `sudo mysql` for admin tasks; use application user `mysql -u app_user -p` for projects. |
| **Disk Space Low** | Inspect sizes: `du -sh ~/.cache ~/.npm ~/.config`. Safe clean: `npm cache clean --force && uv cache prune`. |

---

## 📚 Advanced References (Progressive Disclosure)

When you need deeper configurations, refer to these dedicated pages:
- 🔒 [Advanced Security & Network Hardening](file:///home/user/developer-machine-handbook/docs/advanced-security-networking.md) (UFW rules, SSH bastion tunnels, loopback bindings)
- 💾 [Developer Backup & Restore Playbook](file:///home/user/developer-machine-handbook/docs/backup-and-restore.md) (Nginx sites, dotfiles, and database dumps)
- 🐍 [Production-Like Django Deployment](file:///home/user/developer-machine-handbook/docs/production-django-deployment.md) (Gunicorn, systemd services, and deploy checks)
- 🤖 [AI/ML & GPU Acceleration](file:///home/user/developer-machine-handbook/docs/ai-ml-gpu-setup.md) (NVIDIA drivers, CUDA, PyTorch setup, model caching)
- 🔧 [Troubleshooting & Service Management](file:///home/user/developer-machine-handbook/docs/troubleshooting-service-management.md) (Port diagnosis, journalctl, rollback)

---
*Maintained in the [developer-machine-handbook](https://github.com/mdshamimshahnewaz/developer-machine-handbook) repository.*
