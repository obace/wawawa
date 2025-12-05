"""根据 OS 类型生成初始化脚本，用于设置 root/Administrator 密码，并从镜像猜测 OS。"""

from typing import Optional


def build_user_data(os_type: str, password: Optional[str]) -> str:
    """
    os_type 支持：
    - debian
    - ubuntu
    - windows
    返回 cloud-init / powershell 脚本字符串。
    """
    if not password:
        return ""

    if os_type == "debian":
        return f"""#!/bin/bash
echo root:{password} | sudo chpasswd root
sudo sed -i 's/^#\\?PermitRootLogin.*/PermitRootLogin yes/g' /etc/ssh/sshd_config
sudo sed -i 's/^#\\?PasswordAuthentication.*/PasswordAuthentication yes/g' /etc/ssh/sshd_config
sudo service ssh restart || sudo service sshd restart
"""
    if os_type == "ubuntu":
        return f"""#!/bin/bash
echo root:{password} | sudo chpasswd root
sudo sed -i 's/^#\\?PermitRootLogin.*/PermitRootLogin yes/g' /etc/ssh/sshd_config
sudo sed -i 's/^#\\?PasswordAuthentication.*/PasswordAuthentication yes/g' /etc/ssh/sshd_config
sudo rm -rf /etc/ssh/sshd_config.d/*
sudo systemctl restart ssh || sudo systemctl restart sshd
"""
    if os_type == "windows":
        return f"""<powershell>
secedit /export /cfg c:\\secpol.cfg
(Get-Content c:\\secpol.cfg) -replace "PasswordComplexity = 1", "PasswordComplexity = 0" | Set-Content c:\\secpol.cfg
secedit /configure /db c:\\windows\\security\\local.sdb /cfg c:\\secpol.cfg /areas SECURITYPOLICY
Remove-Item c:\\secpol.cfg
net user Administrator {password}
</powershell>
"""
    return ""


def infer_os_type_from_ami(ami_id: Optional[str]) -> str:
    """简单根据 ami/ssm 名称猜测 OS 类型。"""
    if not ami_id:
        return ""
    lower = ami_id.lower()
    if "windows" in lower:
        return "windows"
    if "ubuntu" in lower:
        return "ubuntu"
    if "debian" in lower:
        return "debian"
    if "al2023" in lower or "amazon-linux" in lower:
        # Amazon Linux 按类 Linux 处理
        return "debian"
    return ""


def infer_os_type_from_blueprint(blueprint: Optional[str]) -> str:
    if not blueprint:
        return ""
    lower = blueprint.lower()
    if "windows" in lower:
        return "windows"
    if "ubuntu" in lower:
        return "ubuntu"
    if "debian" in lower:
        return "debian"
    if "amazon_linux" in lower:
        return "debian"
    return ""
