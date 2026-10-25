# Troubleshooting & Service Management Reference

Quick diagnostics commands when local services experience conflicts or fail to boot.

## 1. Port Conflicts (Port 80, 3306, 5432, 6379)
Find out which process holds a port:
```bash
sudo ss -tulpn | grep -E ':80|:3306|:5432|:6379'
```
- If **Apache** is occupying port 80:
  ```bash
  sudo systemctl stop apache2 && sudo systemctl disable apache2
  ```
- If a **Docker container** is occupying port 3306 or 80:
  ```bash
  docker ps
  docker stop <container_name>
  ```

## 2. Service Logs
Inspect live systemd service journals:
```bash
# Nginx logs
sudo journalctl -u nginx -n 50 --no-pager
sudo nginx -t

# PHP-FPM logs
sudo journalctl -u php*-fpm -n 50 --no-pager

# MySQL logs
sudo journalctl -u mysql -n 50 --no-pager

# PostgreSQL logs
sudo journalctl -u postgresql -n 50 --no-pager
```

## 3. Safe Cache Maintenance
Avoid `rm -rf ~/.cache/*`. Use tool-specific commands:
```bash
npm cache clean --force
composer clear-cache
uv cache prune
pip cache purge 2>/dev/null || true
```
