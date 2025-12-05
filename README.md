# AWS 多账号控制面板（Flask 版）

一个自部署的轻量面板，可在浏览器本地保存多个 AWS 账号配置，支持 SOCKS 代理检测、AK/SK 验证、生成临时控制台登录链接，以及基础的 EC2 / Lightsail 实例查看与控制。

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

访问：`http://your-server/`

## 使用说明
- **多配置管理**：左上角选择/新建/重命名/删除/保存配置。数据仅存储在浏览器 `localStorage`（key: `awsTempLinkProfiles`）。
- **测试 SOCKS**：填写 `socks5://...` 代理地址，点击“测试 SOCKS”，后端通过代理访问 `ip-api.com`。
- **测试 AWS 账号**：填写 AK/SK/Region（可选代理），调用 `sts.get_caller_identity` 验证有效性。
- **生成临时登录链接**：填写会话时长（900–43200 秒），调用 `GetFederationToken` + federation URL，返回可直接打开的控制台登录链接。
- **实例管理**：点击“加载实例”获取当前 Region 的 EC2 / Lightsail 列表。每行提供启动/停止/重启/换 IP 操作，操作前会弹出确认。

## 常见错误提示
- `密钥无效 / 权限不足`：AK/SK 无权限调用 STS 或实例操作，请检查 IAM 策略。
- `Region 无效`：Region 拼写错误或账号未启用对应区域。
- `代理不可用`：SOCKS 地址错误、网络不可达或认证失败，查看代理日志。
- `STS 调用异常`：可能因时间同步问题、网络问题或凭证被吊销。

## 可选环境变量
- `FLASK_DEBUG`：设为 `1/true` 启用调试。
- `DEFAULT_SESSION_DURATION`：控制默认会话时长（秒）。
- `HTTP_TIMEOUT`：HTTP/代理测试超时（秒）。
- `AWS_CONSOLE_DESTINATION`：控制台目标 URL，默认 `https://console.aws.amazon.com/`。
