import urllib.parse
import os

mermaid_code = """graph TD
    Client["Developer Browser / Bruno API Client"] -->|Port 80 HTTP / 443 HTTPS| Nginx["Nginx Web Server & Reverse Proxy"]

    subgraph Web_Routing ["Virtual Host Routing"]
        Nginx -->|Unix Socket: /run/php/php8.5-fpm.sock| Laravel["Laravel App laravel.test"]
        Nginx -->|Unix Socket: /run/php/php8.5-fpm.sock| WP["WordPress wp.test"]
        Nginx -->|Unix Socket: /run/php/php8.5-fpm.sock| PMA["PHPMyAdmin localhost/phpmyadmin"]
        Nginx -->|HTTP Proxy: localhost:3000| NextJS["Node.js / Next.js / Vite Apps"]
    end

    subgraph Databases ["High-Performance Native Storage"]
        Laravel -->|Socket / Port 3306| MySQL["MySQL 8.4 Server"]
        Laravel -->|Socket / Port 5432| Postgres["PostgreSQL 18 Server"]
        Laravel -->|Port 6379| Redis["Redis 8.0 Cache & Queue Worker"]
        WP -->|Socket / Port 3306| MySQL
        PMA -->|Socket / Port 3306| MySQL
    end

    subgraph Management ["Management Cockpit & Tools"]
        DBeaver["DBeaver Community Edition"] -->|Native Local & SSH Tunneling| MySQL
        DBeaver -->|Native Local & SSH Tunneling| Postgres
        DBeaver -->|Native Local & SSH Tunneling| Redis
        DBeaver -.->|Remote Bastion / Private VPC| CloudDB["AWS RDS / DigitalOcean / Cloud DBs"]
    end
"""

# Mermaid.ink URL
encoded = urllib.parse.quote(mermaid_code)
image_url = f"https://mermaid.ink/img/{encoded}"

print("Image URL generated:")
print(image_url)

# Read index.md and replace mermaid code block with rendered image + details collapsible
with open('/home/user/developer-machine-handbook/index.md', 'r') as f:
    content = f.read()

target = """```mermaid
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
```"""

replacement = f"""![Master Architecture Diagram]({image_url})

<details>
<summary>🔍 Click to view raw Mermaid Diagram Code</summary>

```mermaid
{mermaid_code}
```
</details>"""

if target in content:
    content = content.replace(target, replacement)
    with open('/home/user/developer-machine-handbook/index.md', 'w') as f:
        f.write(content)
    with open('/home/user/dev-environment-audit/docs/THE_DEFINITIVE_DEVELOPER_HANDBOOK.md', 'w') as f:
        f.write(content)
    print("Replaced successfully in index.md and handbook doc.")
else:
    print("Target block not matched exactly, looking for mermaid block...")
