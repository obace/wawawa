"""Lightsail 实例的基础操作封装。"""

from typing import List, Optional
from uuid import uuid4

from botocore.exceptions import BotoCoreError, ClientError

from backend.aws.sessions import create_boto3_client


def _ls_client(access_key, secret_key, region, proxy_url):
    return create_boto3_client("lightsail", access_key, secret_key, region, proxy_url)


def list_instances(
    access_key: str, secret_key: str, region: str, proxy_url: Optional[str] = None
) -> List[dict]:
    """列出 Lightsail 实例的基础信息。"""
    client = _ls_client(access_key, secret_key, region, proxy_url)
    result = []
    try:
        paginator = client.get_paginator("get_instances")
        for page in paginator.paginate():
            for inst in page.get("instances", []):
                result.append(
                    {
                        "name": inst.get("name"),
                        "state": inst.get("state", {}).get("name"),
                        "public_ip": inst.get("publicIpAddress"),
                        "private_ip": inst.get("privateIpAddress"),
                    }
                )
    except (ClientError, BotoCoreError) as exc:
        raise RuntimeError(f"列出 Lightsail 实例失败: {exc}") from exc
    return result


def start_instance(name, access_key, secret_key, region, proxy_url=None):
    client = _ls_client(access_key, secret_key, region, proxy_url)
    try:
        client.start_instance(instanceName=name)
    except (ClientError, BotoCoreError) as exc:
        raise RuntimeError(f"启动 Lightsail 实例失败: {exc}") from exc


def stop_instance(name, access_key, secret_key, region, proxy_url=None):
    client = _ls_client(access_key, secret_key, region, proxy_url)
    try:
        client.stop_instance(instanceName=name)
    except (ClientError, BotoCoreError) as exc:
        raise RuntimeError(f"停止 Lightsail 实例失败: {exc}") from exc


def reboot_instance(name, access_key, secret_key, region, proxy_url=None):
    client = _ls_client(access_key, secret_key, region, proxy_url)
    try:
        client.reboot_instance(instanceName=name)
    except (ClientError, BotoCoreError) as exc:
        raise RuntimeError(f"重启 Lightsail 实例失败: {exc}") from exc


def change_instance_ip(name, access_key, secret_key, region, proxy_url=None):
    """
    使用 Lightsail 的静态 IP 接口更换公网 IP。
    简化流程：为实例创建新的静态 IP，并在成功绑定后释放旧的静态 IP（如果存在）。
    """
    client = _ls_client(access_key, secret_key, region, proxy_url)
    old_static_ip = None
    try:
        # 找到当前绑定的静态 IP 名称（如果有）
        ips = client.get_static_ips().get("staticIps", [])
        for ip in ips:
            if ip.get("attachedTo") == name:
                old_static_ip = ip.get("name")
                break

        # 创建新的静态 IP
        new_ip_name = f"{name}-ip-{uuid4().hex[:8]}"
        client.create_static_ip(staticIpName=new_ip_name)
        # 绑定到实例
        client.attach_static_ip(staticIpName=new_ip_name, instanceName=name)

        # 释放旧静态 IP（如有）
        if old_static_ip:
            try:
                client.release_static_ip(staticIpName=old_static_ip)
            except (ClientError, BotoCoreError):
                # 如果释放失败，不阻断主要流程
                pass
    except (ClientError, BotoCoreError) as exc:
        raise RuntimeError(f"更换 Lightsail 公网 IP 失败: {exc}") from exc


def create_instance(
    name: str,
    bundle_id: str,
    blueprint_id: str,
    access_key: str,
    secret_key: str,
    region: str,
    proxy_url: Optional[str] = None,
    user_data: Optional[str] = None,
):
    """
    创建 Lightsail 实例，使用 Amazon Linux 2023 blueprint，
    并开放全部端口。
    """
    client = _ls_client(access_key, secret_key, region, proxy_url)
    availability_zone = f"{region}a"
    try:
        client.create_instances(
            instanceNames=[name],
            availabilityZone=availability_zone,
            blueprintId=blueprint_id,
            bundleId=bundle_id,
            userData=user_data or "",
        )
        # 开放所有端口
        client.open_instance_public_ports(
            portInfo={
                "fromPort": 0,
                "toPort": 65535,
                "protocol": "all",
            },
            instanceName=name,
        )
    except (ClientError, BotoCoreError) as exc:
        raise RuntimeError(f"创建 Lightsail 实例失败: {exc}") from exc
