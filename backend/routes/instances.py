from flask import Blueprint, jsonify, request

from backend.aws import ec2, lightsail, quotas, userdata

instances_bp = Blueprint("instances", __name__)


@instances_bp.route("/instances", methods=["POST"])
def list_instances():
    data = request.get_json(force=True, silent=True) or {}
    access_key = data.get("access_key")
    secret_key = data.get("secret_key")
    region = data.get("region")
    proxy_url = None  # 已禁用代理
    if not all([access_key, secret_key, region]):
        return jsonify({"ok": False, "error": "参数缺失：access_key/secret_key/region"})

    try:
        ec2_list = ec2.list_instances(access_key, secret_key, region, proxy_url)
        ls_list = lightsail.list_instances(access_key, secret_key, region, proxy_url)
        return jsonify({"ok": True, "ec2": ec2_list, "lightsail": ls_list})
    except Exception as exc:  # noqa: BLE001
        return jsonify({"ok": False, "error": str(exc)})


@instances_bp.route("/instance_action", methods=["POST"])
def instance_action():
    data = request.get_json(force=True, silent=True) or {}
    typ = data.get("type")
    action = data.get("action")
    access_key = data.get("access_key")
    secret_key = data.get("secret_key")
    region = data.get("region")
    proxy_url = None

    if not all([typ, action, access_key, secret_key, region]):
        return jsonify({"ok": False, "error": "参数缺失"})

    try:
        if typ == "ec2":
            instance_id = data.get("instance_id")
            if not instance_id:
                return jsonify({"ok": False, "error": "缺少 instance_id"})
            if action == "start":
                ec2.start_instances([instance_id], access_key, secret_key, region, proxy_url)
                msg = "EC2 实例已启动"
            elif action == "stop":
                ec2.stop_instances([instance_id], access_key, secret_key, region, proxy_url)
                msg = "EC2 实例已停止"
            elif action == "reboot":
                ec2.reboot_instances([instance_id], access_key, secret_key, region, proxy_url)
                msg = "EC2 实例已重启"
            elif action == "change_ip":
                ec2.change_instance_ip(instance_id, access_key, secret_key, region, proxy_url)
                msg = "EC2 实例公网 IP 已更换"
            else:
                return jsonify({"ok": False, "error": "未知操作"})
        elif typ == "lightsail":
            name = data.get("name")
            if not name:
                return jsonify({"ok": False, "error": "缺少实例 name"})
            if action == "start":
                lightsail.start_instance(name, access_key, secret_key, region, proxy_url)
                msg = "Lightsail 实例已启动"
            elif action == "stop":
                lightsail.stop_instance(name, access_key, secret_key, region, proxy_url)
                msg = "Lightsail 实例已停止"
            elif action == "reboot":
                lightsail.reboot_instance(name, access_key, secret_key, region, proxy_url)
                msg = "Lightsail 实例已重启"
            elif action == "change_ip":
                lightsail.change_instance_ip(name, access_key, secret_key, region, proxy_url)
                msg = "Lightsail 实例公网 IP 已更换"
            else:
                return jsonify({"ok": False, "error": "未知操作"})
        else:
            return jsonify({"ok": False, "error": "未知实例类型"})

        return jsonify({"ok": True, "message": msg})
    except Exception as exc:  # noqa: BLE001
        return jsonify({"ok": False, "error": str(exc)})


@instances_bp.route("/quota", methods=["POST"])
def spot_quota():
    data = request.get_json(force=True, silent=True) or {}
    access_key = data.get("access_key")
    secret_key = data.get("secret_key")
    region = data.get("region")
    proxy_url = None
    if not all([access_key, secret_key, region]):
        return jsonify({"ok": False, "error": "参数缺失：access_key/secret_key/region"})
    try:
        value = quotas.get_spot_standard_quota(access_key, secret_key, region)
        return jsonify({"ok": True, "value": value})
    except Exception as exc:  # noqa: BLE001
        return jsonify({"ok": False, "error": str(exc)})


@instances_bp.route("/create_instance", methods=["POST"])
def create_instance():
    data = request.get_json(force=True, silent=True) or {}
    typ = data.get("type")
    access_key = data.get("access_key")
    secret_key = data.get("secret_key")
    region = data.get("region")
    proxy_url = None
    instance_type = data.get("instance_type")
    ami_id = data.get("ami_id")
    name = data.get("name") or None
    password = data.get("password")
    volume_size = data.get("volume_size")
    user_data = ""
    if not all([typ, access_key, secret_key, region, instance_type]):
        return jsonify({"ok": False, "error": "缺少必要参数"})
    try:
        if typ == "ec2":
            os_type = userdata.infer_os_type_from_ami(ami_id)
            user_data = userdata.build_user_data(os_type, password)
            instance_id = ec2.create_ec2_instance(
                access_key, secret_key, region, instance_type, ami_id, proxy_url, name, user_data, volume_size
            )
            return jsonify({"ok": True, "message": f"EC2 已创建：{instance_id}"})
        elif typ == "lightsail":
            bundle_id = data.get("bundle_id")
            blueprint_id = data.get("blueprint_id") or "amazon_linux_2023"
            os_type = userdata.infer_os_type_from_blueprint(blueprint_id)
            user_data = userdata.build_user_data(os_type, password)
            if not name:
                return jsonify({"ok": False, "error": "创建 Lightsail 需要 name"})
            if not bundle_id:
                return jsonify({"ok": False, "error": "缺少 bundle_id"})
            lightsail.create_instance(
                name=name,
                bundle_id=bundle_id,
                blueprint_id=blueprint_id,
                access_key=access_key,
                secret_key=secret_key,
                region=region,
                proxy_url=proxy_url,
                user_data=user_data,
            )
            return jsonify({"ok": True, "message": f"Lightsail 实例已创建：{name}"})
        else:
            return jsonify({"ok": False, "error": "未知实例类型"})
    except Exception as exc:  # noqa: BLE001
        return jsonify({"ok": False, "error": str(exc)})
