## 建立 Webhook 的 systemd Service

```bash
sudo nano /etc/systemd/system/glance-webhook.service
```

```
[Unit]
Description=Glance Dashboard Webhook Server
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/glance
ExecStart=/usr/bin/python3 /home/pi/glance/webhook-server.py
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable glance-webhook
sudo systemctl start glance-webhook
sudo systemctl status glance-webhook
```

## 設定 Cron 自動更新

```bash
crontab -e
```

```bash
0 2 * * * /home/pi/glance/scripts/deploy.sh
```

```bash
sudo visudo
```

```
pie ALL=(ALL) NOPASSWD: /usr/bin/docker
```

