"""统一封装 boto3 Session / Client 创建（直连模式，无代理）。"""
from typing import Optional

import boto3
from botocore.config import Config

from backend import config


def _build_boto3_session(access_key: str, secret_key: str, region: str) -> boto3.Session:
    return boto3.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region,
    )


def create_boto3_client(
    service: str,
    access_key: str,
    secret_key: str,
    region: str,
    proxy_url: Optional[str] = None,
) -> boto3.client:
    """
    创建指定 service 的 boto3 client，始终直连（proxies=None）。
    proxy_url 参数保留但不使用。
    """
    session = _build_boto3_session(access_key, secret_key, region)

    client_config = Config(
        proxies=None,
        connect_timeout=config.HTTP_TIMEOUT,
        read_timeout=config.HTTP_TIMEOUT,
        retries={"max_attempts": 3, "mode": "standard"},
        region_name=region,
    )

    return session.client(service_name=service, config=client_config)
