# Developer Backup & Restore Playbook

A practical backup workflow for developer configurations, project source code, and local databases.

## 1. What to Back Up vs. Exclude

| Category | Back Up | Exclude |
| :--- | :--- | :--- |
| **Configs** | `/etc/nginx/sites-available`, `~/.bashrc`, `~/.ssh/config` | Ephemeral sockets (`/run/`) |
| **Databases** | Plain SQL dumps (`mysqldump`, `pg_dumpall`) | Raw binary data (`/var/lib/mysql`) |
| **Code** | Git repository remotes, custom `.env.example` | `node_modules/`, `vendor/`, `.venv/` |

## 2. Backup Script
Save as `~/bin/backup-dev.sh`:
```bash
#!/bin/bash
set -euo pipefail

DEST="$HOME/backups/$(date +%F_%H%M%S)"
mkdir -p "$DEST"

echo "Backing up Nginx sites..."
sudo tar -czf "$DEST/nginx.tar.gz" /etc/nginx/sites-available

echo "Backing up dotfiles..."
tar -czf "$DEST/dotfiles.tar.gz" -C "$HOME" .bashrc .gitconfig .ssh/config 2>/dev/null || true

echo "Dumping MySQL..."
sudo mysqldump --all-databases --single-transaction --quick | gzip > "$DEST/mysql.sql.gz"

echo "Dumping PostgreSQL..."
sudo -u postgres pg_dumpall | gzip > "$DEST/postgres.sql.gz"

echo "Backup created at: $DEST"
```

## 3. Restoration
```bash
# Restore MySQL
gunzip < mysql.sql.gz | sudo mysql

# Restore PostgreSQL
gunzip < postgres.sql.gz | sudo -u postgres psql
```
