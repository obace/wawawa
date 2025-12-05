"""EC2 实例的基础操作封装。"""

from typing import List, Optional
from uuid import uuid4

from botocore.exceptions import BotoCoreError, ClientError

from backend.aws.sessions import create_boto3_client


def _ec2_client(access_key, secret_key, region, proxy_url):
    return create_boto3_client("ec2", access_key, secret_key, region, proxy_url)


def list_all_regions(
    access_key: str, secret_key: str, region: str = "us-east-1", proxy_url: Optional[str] = None
) -> List[str]:
    """返回当前账号可用的全部 Region 名称列表。"""
    client = _ec2_client(access_key, secret_key, region, proxy_url)
    try:
        resp = client.describe_regions(AllRegions=False)
        return [r.get("RegionName") for r in resp.get("Regions", []) if r.get("RegionName")]
    except (ClientError, BotoCoreError) as exc:
        raise RuntimeError(f"获取 Region 列表失败: {exc}") from exc

def list_instances(
    access_key: str, secret_key: str, region: str, proxy_url: Optional[str] = None
) -> List[dict]:
    """列出当前 region 下的实例，提取 Name 标签与 IP 信息。"""
    client = _ec2_client(access_key, secret_key, region, proxy_url)
    instances = []
    try:
        paginator = client.get_paginator("describe_instances")
        for page in paginator.paginate():
            for reservation in page.get("Reservations", []):
                for inst in reservation.get("Instances", []):
                    name_tag = next(
                        (
                            t["Value"]
                            for t in inst.get("Tags", [])
                            if t.get("Key") == "Name"
                        ),
                        "",
                    )
                    instances.append(
                        {
                            "instance_id": inst.get("InstanceId"),
                            "name": name_tag,
                            "state": inst.get("State", {}).get("Name"),
                            "public_ip": inst.get("PublicIpAddress"),
                            "private_ip": inst.get("PrivateIpAddress"),
                        }
                    )
    except (ClientError, BotoCoreError) as exc:
        raise RuntimeError(f"列出 EC2 实例失败: {exc}") from exc
    return instances


def start_instances(
    instance_ids, access_key, secret_key, region, proxy_url: Optional[str] = None
):
    client = _ec2_client(access_key, secret_key, region, proxy_url)
    try:
        client.start_instances(InstanceIds=instance_ids)
    except (ClientError, BotoCoreError) as exc:
        raise RuntimeError(f"启动实例失败: {exc}") from exc


def stop_instances(
    instance_ids, access_key, secret_key, region, proxy_url: Optional[str] = None
):
    client = _ec2_client(access_key, secret_key, region, proxy_url)
    try:
        client.stop_instances(InstanceIds=instance_ids)
    except (ClientError, BotoCoreError) as exc:
        raise RuntimeError(f"停止实例失败: {exc}") from exc


def reboot_instances(
    instance_ids, access_key, secret_key, region, proxy_url: Optional[str] = None
):
    client = _ec2_client(access_key, secret_key, region, proxy_url)
    try:
        client.reboot_instances(InstanceIds=instance_ids)
    except (ClientError, BotoCoreError) as exc:
        raise RuntimeError(f"重启实例失败: {exc}") from exc


def change_instance_ip(
    instance_id: str,
    access_key: str,
    secret_key: str,
    region: str,
    proxy_url: Optional[str] = None,
):
    """
    为实例分配新的 EIP 并关联。
    简化处理：若发现旧 EIP 的 allocation id，会在成功关联新 EIP 后释放旧的。
    """
    client = _ec2_client(access_key, secret_key, region, proxy_url)
    old_allocation_id = None
    try:
        desc = client.describe_instances(InstanceIds=[instance_id])
        for r in desc.get("Reservations", []):
            for inst in r.get("Instances", []):
                for iface in inst.get("NetworkInterfaces", []):
                    assoc = iface.get("Association")
                    if assoc and assoc.get("AllocationId"):
                        old_allocation_id = assoc["AllocationId"]
                        break
        alloc = client.allocate_address(Domain="vpc")
        new_allocation_id = alloc["AllocationId"]
        client.associate_address(
            InstanceId=instance_id,
            AllocationId=new_allocation_id,
            AllowReassociation=True,
        )
        if old_allocation_id:
            try:
                client.release_address(AllocationId=old_allocation_id)
            except (ClientError, BotoCoreError):
                pass
    except (ClientError, BotoCoreError) as exc:
        raise RuntimeError(f"更换公网 IP 失败: {exc}") from exc


def get_spot_quota(
    access_key: str, secret_key: str, region: str, proxy_url: Optional[str] = None
) -> float:
    """
    查询 EC2 Running On-Demand Standard (A,C,D,H,I,M,R,T,Z) 配额。
    使用 Service Quotas 接口，配额代码为 L-1216C47A。
    """
    client = create_boto3_client("service-quotas", access_key, secret_key, region, proxy_url)
    try:
        resp = client.get_service_quota(ServiceCode="ec2", QuotaCode="L-1216C47A")
        return resp["Quota"]["Value"]
    except (ClientError, BotoCoreError) as exc:
        raise RuntimeError(f"获取 On-Demand 配额失败: {exc}") from exc


def create_ec2_instance(
    access_key: str,
    secret_key: str,
    region: str,
    instance_type: str,
    ami_id: Optional[str] = None,
    proxy_url: Optional[str] = None,
    name: Optional[str] = None,
    user_data: Optional[str] = None,
    volume_size: Optional[int] = None,
) -> str:
    """
    创建一台 EC2 实例，默认使用 Amazon Linux 2023 最新 AMI，放在默认 VPC/子网内，
    并创建一个安全组放通全部端口（0-65535，0.0.0.0/0）。
    """
    ec2_client = _ec2_client(access_key, secret_key, region, proxy_url)
    ssm_client = create_boto3_client("ssm", access_key, secret_key, region, proxy_url)

    try:
        if ami_id and ami_id.startswith("ssm:"):
            param_name = ami_id.replace("ssm:", "", 1)
            ami_param = ssm_client.get_parameter(Name=param_name)
            image_id = ami_param["Parameter"]["Value"]
        elif ami_id:
            image_id = ami_id
        else:
            ami_param = ssm_client.get_parameter(
                Name="/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-6.1-x86_64"
            )
            image_id = ami_param["Parameter"]["Value"]
    except (ClientError, BotoCoreError) as exc:
        raise RuntimeError(f"获取 AMI 失败: {exc}") from exc

    try:
        vpcs = ec2_client.describe_vpcs(Filters=[{"Name": "isDefault", "Values": ["true"]}]).get(
            "Vpcs", []
        )
        if not vpcs:
            raise RuntimeError("未找到默认 VPC，无法自动创建实例")
        vpc_id = vpcs[0]["VpcId"]
        subnets = ec2_client.describe_subnets(Filters=[{"Name": "vpc-id", "Values": [vpc_id]}]).get(
            "Subnets", []
        )
        if not subnets:
            raise RuntimeError("未找到默认子网，无法自动创建实例")
        subnet_id = subnets[0]["SubnetId"]
    except (ClientError, BotoCoreError) as exc:
        raise RuntimeError(f"获取 VPC/子网信息失败: {exc}") from exc

    sg_id = None
    try:
        sg_name = f"open-all-{uuid4().hex[:8]}"
        sg_resp = ec2_client.create_security_group(
            GroupName=sg_name,
            Description="Open all ports (auto-created by panel)",
            VpcId=vpc_id,
        )
        sg_id = sg_resp["GroupId"]
        ec2_client.authorize_security_group_ingress(
            GroupId=sg_id,
            IpPermissions=[
                {
                    "IpProtocol": "-1",
                    "IpRanges": [{"CidrIp": "0.0.0.0/0", "Description": "Open all"}],
                }
            ],
        )
    except (ClientError, BotoCoreError) as exc:
        raise RuntimeError(f"创建安全组失败: {exc}") from exc

    try:
        tags = []
        if name:
            tags.append({"Key": "Name", "Value": name})
        block_device = {
            "DeviceName": "/dev/xvda",
            "Ebs": {
                "DeleteOnTermination": True,
                "VolumeType": "gp3",
            },
        }
        if volume_size:
            block_device["Ebs"]["VolumeSize"] = int(volume_size)
        resp = ec2_client.run_instances(
            ImageId=image_id,
            InstanceType=instance_type,
            MinCount=1,
            MaxCount=1,
            SecurityGroupIds=[sg_id],
            SubnetId=subnet_id,
            UserData=user_data or "",
            BlockDeviceMappings=[block_device],
            TagSpecifications=[
                {
                    "ResourceType": "instance",
                    "Tags": tags,
                }
            ]
            if tags
            else [],
        )
        instance_id = resp["Instances"][0]["InstanceId"]
        return instance_id
    except (ClientError, BotoCoreError) as exc:
        raise RuntimeError(f"创建 EC2 实例失败: {exc}") from exc


def terminate_all_instances(
    access_key: str,
    secret_key: str,
    region: str,
    proxy_url: Optional[str] = None,
) -> List[str]:
    """终止当前 region 下所有非终止状态的实例，返回被终止的实例 ID 列表。"""
    client = _ec2_client(access_key, secret_key, region, proxy_url)
    instance_ids: List[str] = []
    try:
        paginator = client.get_paginator("describe_instances")
        for page in paginator.paginate(
            Filters=[
                {
                    "Name": "instance-state-name",
                    "Values": ["pending", "running", "stopping", "stopped"],
                }
            ]
        ):
            for reservation in page.get("Reservations", []):
                for inst in reservation.get("Instances", []):
                    inst_id = inst.get("InstanceId")
                    if inst_id:
                        instance_ids.append(inst_id)
        if instance_ids:
            client.terminate_instances(InstanceIds=instance_ids)
    except (ClientError, BotoCoreError) as exc:
        raise RuntimeError(f"终止实例失败: {exc}") from exc
    return instance_ids
