# 📋 HANDBOOK AUDIT REPORT

**Generated on:** 2026-10-25

---

## Overview
The audit was performed on a fresh Ubuntu 26.04 workstation (`resolute`) with the current **developer‑machine‑handbook** repository checked out at `~/developer-machine-handbook`.  All data was collected read‑only; no changes were made to the system.

| Category | Items Found |
|----------|-------------|
| **Operating System** | Ubuntu 26.04.1 LTS (kernel 7.0.0‑38‑generic) |
| **CPU / Memory / Disk** | 8 cores, 14 GiB RAM, 468 GiB disk (≈14 % used) |
| **Package Managers** | `apt` (full list in `dpkg_list.tsv`), `snap` (list in `snap_list.txt`), `flatpak` (none detected) |
| **Installed Services (running)** | Nginx, MySQL, PostgreSQL, Redis, Docker, Docker‑compose, php‑fpm, php‑8.5‑fpm, gdm, cups, fwupd, etc. |
| **Manually installed apt packages** | 154 packages (see `apt_manual.txt`). Notable examples: `docker-ce`, `docker-compose-plugin`, `brave-browser`, `code`, `dbeaver-ce`, `php8.5`, `nginx`, `mysql-server`, `postgresql-18`, `redis-server`, `gitkraken`, `bitwarden`, `chatgpt` (Snap), `antigravity` (Snap) |
| **Global language runtimes** | Python 3.14, Node v24.19 (via FNM), PHP 8.5, Java 25.0.4.1, Composer 2.9.5 |
| **Global packages** | npm (11.17), Composer packages (see `composer_global.json`), pip packages (see `pip_list.json`) |
| **Cache footprint** | `~7.2 GiB` in `~/.cache`, `~1.4 GiB` in `~/.local/share`, `~1.5 GiB` in `~/.npm` |

---

## 🔴 Critical Security Issues
| Issue | Description | Recommendation |
|-------|-------------|----------------|
| **Root MySQL authentication** | The handbook assumes a password‑based `root` login (`mysql -u root -p`). On Ubuntu 26.04 the default `auth_socket` plugin disables password auth, which can lead to a failed login or insecure manual password changes. | Use `auth_socket` for local root access; create a dedicated application user with a strong password for Laravel/WordPress. |
| **Hard‑coded service ports** | Multiple services listen on default ports (e.g., MySQL 3306, PostgreSQL 5432, Redis 6379). The handbook does not advise firewall hardening. | Add a step to enable `ufw` and allow only necessary ports (80/443 for Nginx, 3306/5432/6379 for local development or restrict to `127.0.0.1`). |
| **Installed Docker while promoting “no‑Docker”** | Docker engine (`docker-ce`, `docker-compose-plugin`) is installed but the handbook’s philosophy is native‑only. This creates potential confusion and port conflicts (Docker may expose its own 80/443). | Either remove Docker from the base setup or clearly document it as an *optional* component with an explicit opt‑out flag. |
| **Large cache directories** | `~/.cache` (7.2 GiB) and `~/.npm` (1.5 GiB) contain artefacts that can grow unchecked, especially AI model caches. | Add a cleanup section that explains safe cache pruning (`rm -rf ~/.cache/*` after confirming nothing essential) and encourage periodic review. |

---

## ⚠️ Incorrect / Broken Instructions
| Section | Problem | Fix |
|--------|---------|-----|
| **2. Nginx Installation** | The handbook runs `sudo apt install -y nginx` but does not ensure the default Apache package is purged, leading to port‑80 conflicts (observed in the audit). | Add `sudo apt purge -y apache2` **before** installing Nginx, or at least warn the user to stop Apache. |
| **3. PHP Version** | Commands reference `php8.5` and `php8.5-fpm`. Ubuntu 24.04 ships only PHP 8.2, so the guide will fail on that distro. | Use conditional logic: `if [[ $(lsb_release -rs) == "24.04" ]]; then sudo apt install -y php8.2 php8.2-fpm; else sudo apt install -y php8.5 php8.5-fpm; fi`. |
| **5. PostgreSQL Installation** | The guide installs `postgresql-18` (available only on Ubuntu 26.04). No fallback for 24.04. | Provide an alternative `postgresql` package for LTS releases (e.g., `postgresql-16`). |
| **7. Composer Global Packages** | The handbook lists Composer packages but does not lock versions, risking future breakage. | Add a `composer.lock` generation step (`composer global require --prefer-dist ... && composer global dump-autoload --optimize`) and store the lock file. |
| **12. Frontend Runtime** | The guide recommends `fnm` but the audit shows the `fnm` binary is placed under `/run/user/...` without an installation step. | Include an explicit `curl -fsSL https://fnm.vercel.app/install | bash` command and add `$HOME/.fnm` to `PATH`. |

---

## 📦 Important Missing Capabilities
| Missing Feature | Why It Matters | Suggested Addition |
|----------------|----------------|-------------------|
| **Git SSH key generation & GitHub setup** | Developers need secure push credentials. | Add a “Generate SSH keys, add to GitHub” subsection under **Foundation**. |
| **Ubuntu 24.04 compatibility guide** | Handbook claims dual‑support but many commands are version‑specific. | Provide a table of package name differences and conditional install scripts. |
| **Backup & restore workflow** | No guidance on protecting configuration files (`/etc/nginx/sites-available`, `.env`). | Add a simple `tar -czvf backup_$(date +%F).tar.gz /etc/nginx /var/www ~/projects` step. |
| **Testing utilities** | No mention of `phpunit`, `pytest`, or `jest` for verifying project health. | Include a “Run project tests” checklist for each stack. |
| **System monitoring** | No instructions for `htop`, `glances`, or `systemd-analyze`. | Add an optional “Performance monitoring” section. |

---

## 🔧 Improvements / Optional Enhancements
| Enhancement | Benefit |
|------------|---------|
| **Add a summary table** at the top of the handbook listing all installed components, versions, and whether they are *required* or *optional*. |
| **Introduce a `scripts/` directory** with idempotent installer scripts (`install_base.sh`, `install_php.sh`, `install_python.sh`). |
| **Provide a `verify.sh` script** that runs `nginx -t`, `php -v`, `mysqladmin ping`, `psql -c '\l'`, and reports success/failure. |
| **Add a comparison table** between Nginx and Apache (already present, but expand with memory/CPU benchmarks from the audit). |
| **Create a `PROFILES.md`** describing modular installation profiles (Base, PHP/Laravel, Python/Django, Frontend, Full Stack). |
| **Document cache sizes** and give a one‑line command to clean each (`rm -rf ~/.cache/*`, `npm cache clean --force`, `pip cache purge`). |

---

## 📑 Next Steps
1. **Integrate the audit findings** into the handbook:
   - Update the Nginx section to purge Apache first.
   - Add version‑conditional PHP/PostgreSQL install blocks.
   - Insert a security tip about MySQL `auth_socket`.
2. **Add the missing sections** listed above (SSH keys, backups, testing, monitoring).
3. **Commit the new file** (`docs/HANDBOOK_AUDIT.md`) to the repository.
4. **Regenerate the site** (`bundle exec jekyll build && git push`) and verify the live page updates.
5. **Optional**: run the `verify.sh` script on a clean VM to ensure all commands succeed.

---

*The audit is intentionally exhaustive but non‑destructive.  All recommendations are safe to apply on a fresh Ubuntu installation.*
