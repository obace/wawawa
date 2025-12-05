## 目录结构
```
backend/
  app.py           # Flask 入口
  config.py        # 环境配置
  aws/             # boto3 封装（Session/STSes/EC2/Lightsail）
  routes/          # API 路由
templates/
  index.html       # 单页主界面
static/
  css/main.css
  js/main.js
requirements.txt
```

## 部署（Debian/Ubuntu 示例）
```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip nginx

# 拉取代码后，在项目根目录执行：
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 测试运行（开发用）
export FLASK_DEBUG=1
python backend/app.py

# 生产建议使用 gunicorn
gunicorn -b 0.0.0.0:8000 'backend.app:create_app()'
```

### systemd 服务示例 `/etc/systemd/system/aws-panel.service`
```ini
[Unit]
Description=AWS Panel via Gunicorn
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/aws-panel
Environment="PATH=/var/www/aws-panel/venv/bin"
ExecStart=/var/www/aws-panel/venv/bin/gunicorn -b 0.0.0.0:8000 'backend.app:create_app()'
Restart=always

[Install]
WantedBy=multi-user.target
```
```
sudo systemctl daemon-reload
sudo systemctl enable --now aws-panel
```

### nginx 反向代理示例
`/etc/nginx/sites-available/aws-panel`
```nginx
server {
    listen 80;
    server_name your-server-domain-or-ip;

    # 仅允许特定 IP 访问
    allow 1.2.3.4;
    deny all;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```
```
sudo ln -s /etc/nginx/sites-available/aws-panel /etc/nginx/sites-enabled/aws-panel
sudo nginx -t && sudo systemctl restart nginx
```
### 一键
sudo apt update && sudo apt install -y git python3-venv python3-pip && \
cd /opt && \
git clone https://github.com/obace/wawawa.git aws-panel && \
cd aws-panel && \
python3 -m venv venv && source venv/bin/activate && \
pip install -r requirements.txt && \
venv/bin/gunicorn -b 0.0.0.0:8000 --timeout 120 backend.app:app
