"""STS 相关封装：身份验证、生成临时控制台登录链接。"""

import json
from typing import Optional

import requests
from botocore.exceptions import BotoCoreError, ClientError

from backend import config
from backend.aws.sessions import create_boto3_client


def get_caller_identity(
    access_key: str,
    secret_key: str,
    region: str,
    proxy_url: Optional[str] = None,
):
    """调用 sts.get_caller_identity 验证 AK/SK 有效性。"""
    try:
        sts_client = create_boto3_client(
            "sts", access_key, secret_key, region, proxy_url
        )
        resp = sts_client.get_caller_identity()
        return {
            "account": resp.get("Account"),
            "arn": resp.get("Arn"),
            "user_id": resp.get("UserId"),
        }
    except (ClientError, BotoCoreError) as exc:
        raise RuntimeError(f"STS 调用失败: {exc}") from exc


def generate_console_login_url(
    access_key: str,
    secret_key: str,
    region: str,
    session_duration: int,
    proxy_url: Optional[str] = None,
):
    """
    生成 AWS 控制台的临时登录链接。
    不再支持代理，所有调用直连。
    """
    if not 900 <= session_duration <= 43200:
        raise ValueError("会话时长需在 900 - 43200 秒之间")

    try:
        sts_client = create_boto3_client(
            "sts", access_key, secret_key, region, proxy_url
        )
        token_resp = sts_client.get_federation_token(
            Name="temp-console-user",
            DurationSeconds=session_duration,
            Policy=json.dumps(
                {
                    "Version": "2012-10-17",
                    "Statement": [
                        {"Effect": "Allow", "Action": "*", "Resource": "*"}
                    ],
                }
            ),
        )
        creds = token_resp["Credentials"]
    except (ClientError, BotoCoreError) as exc:
        raise RuntimeError(f"获取临时凭证失败: {exc}") from exc

    session_json = json.dumps(
        {
            "sessionId": creds["AccessKeyId"],
            "sessionKey": creds["SecretAccessKey"],
            "sessionToken": creds["SessionToken"],
        }
    )

    try:
        token_url = "https://signin.aws.amazon.com/federation"
        token_resp = requests.get(
            token_url,
            params={"Action": "getSigninToken", "Session": session_json},
            timeout=config.HTTP_TIMEOUT,
            proxies=None,
        )
        token_resp.raise_for_status()
        signin_token = token_resp.json()["SigninToken"]
    except requests.RequestException as exc:
        raise RuntimeError(f"获取 SigninToken 失败: {exc}") from exc
    except (KeyError, ValueError) as exc:
        raise RuntimeError("解析 SigninToken 响应失败") from exc

    login_params = {
        "Action": "login",
        "Issuer": "aws-panel",
        "Destination": config.AWS_CONSOLE_DESTINATION,
        "SigninToken": signin_token,
    }
    login_url = requests.Request("GET", token_url, params=login_params).prepare().url
    return login_url
