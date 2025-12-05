import os

# 简单的配置模块，方便后续通过环境变量调整行为

# 是否开启 Flask 调试
DEBUG = os.getenv("FLASK_DEBUG", "false").lower() in ("1", "true", "yes")

# STS 默认会话时长（秒），可在表单里覆盖
DEFAULT_SESSION_DURATION = int(os.getenv("DEFAULT_SESSION_DURATION", "3600"))

# 代理/HTTP 请求默认超时时间
HTTP_TIMEOUT = float(os.getenv("HTTP_TIMEOUT", "8"))

# 公网 IP 查询接口
IP_INFO_ENDPOINT = os.getenv("IP_INFO_ENDPOINT", "http://ip-api.com/json/")

# AWS 联邦登录的目标控制台主页，可按需修改
AWS_CONSOLE_DESTINATION = os.getenv(
    "AWS_CONSOLE_DESTINATION", "https://console.aws.amazon.com/"
)
