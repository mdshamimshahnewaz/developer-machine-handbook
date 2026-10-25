# Production-Like Local Django & ASGI/WSGI Deployment

For advanced workflows requiring local testing of production app servers (Gunicorn/Uvicorn) with systemd.

## 1. Systemd Service Unit
Create `/etc/systemd/system/django-app.service`:
```ini
[Unit]
Description=Gunicorn daemon for Django Application
After=network.target postgresql.service

[Service]
User=user
Group=user
WorkingDirectory=/home/user/projects/my-api
ExecStart=/home/user/projects/my-api/.venv/bin/gunicorn \
    --workers 3 \
    --bind 127.0.0.1:8000 \
    config.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now django-app
```

## 2. Nginx Reverse Proxy Block
In `/etc/nginx/sites-available/api.local.conf`:
```nginx
server {
    listen 80;
    server_name api.local;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /home/user/projects/my-api/staticfiles/;
    }
}
```

## 3. Production Deployment Checks
```bash
uv run python manage.py check --deploy
```
