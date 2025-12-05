from flask import Blueprint, jsonify, request

from backend.aws import sts

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/check_aws", methods=["POST"])
def check_aws():
    data = request.get_json(force=True, silent=True) or {}
    access_key = data.get("access_key")
    secret_key = data.get("secret_key")
    region = data.get("region")
    proxy_url = None  # SOCKS 功能已禁用

    if not all([access_key, secret_key, region]):
        return jsonify({"ok": False, "error": "参数缺失：access_key/secret_key/region"})

    try:
        identity = sts.get_caller_identity(access_key, secret_key, region, proxy_url)
        return jsonify({"ok": True, **identity})
    except Exception as exc:  # noqa: BLE001
        return jsonify({"ok": False, "error": str(exc)})
