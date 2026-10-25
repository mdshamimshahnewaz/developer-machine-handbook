# Advanced Security & Network Hardening Reference

This guide covers advanced security considerations for developers running local services or connecting to remote cloud environments.

## 1. Localhost Service Bindings
Local development databases (MySQL, PostgreSQL, Redis) must bind strictly to `127.0.0.1` (loopback) so they cannot be accessed over local Wi-Fi or Ethernet:
- **MySQL:** In `/etc/mysql/mysql.conf.d/mysqld.cnf`: `bind-address = 127.0.0.1`
- **PostgreSQL:** In `/etc/postgresql/<version>/main/postgresql.conf`: `listen_addresses = 'localhost'`
- **Redis:** In `/etc/redis/redis.conf`: `bind 127.0.0.1 -::1`

Verify listening sockets:
```bash
sudo ss -tulpn | grep LISTEN
```

## 2. UFW Firewall Setup
For developer workstations connecting to untrusted networks:
```bash
# Set safe defaults
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow essential web and SSH traffic
sudo ufw allow 22/tcp comment 'SSH'
sudo ufw allow 80/tcp comment 'Nginx HTTP'
sudo ufw allow 443/tcp comment 'Nginx HTTPS'

# Enable firewall
sudo ufw enable
```

> **Rule:** Never open MySQL (3306), PostgreSQL (5432), or Redis (6379) in UFW.

## 3. Remote Database Access via SSH Bastion Tunnels
When managing remote production databases (e.g. AWS RDS, DigitalOcean Managed DB):
1. Keep the cloud database port private (not exposed to `0.0.0.0/0`).
2. Use **DBeaver Community Edition**'s built-in **SSH Tunnel** tab.
3. Connect through your cloud jumpbox/bastion host using your SSH key.
