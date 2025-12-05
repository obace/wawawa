"""配额相关封装。"""

from botocore.exceptions import BotoCoreError, ClientError

from backend.aws.sessions import create_boto3_client


def get_spot_standard_quota(access_key: str, secret_key: str, region: str) -> float:
    """
    获取 EC2 Running On-Demand Standard (A, C, D, H, I, M, R, T, Z) 实例配额。
    Service Code: ec2, Quota Code: L-1216C47A
    """
    client = create_boto3_client("service-quotas", access_key, secret_key, region)
    try:
        resp = client.get_service_quota(ServiceCode="ec2", QuotaCode="L-1216C47A")
        return resp["Quota"]["Value"]
    except (ClientError, BotoCoreError) as exc:
        raise RuntimeError(f"获取 On-Demand 配额失败: {exc}") from exc
