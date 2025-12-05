from flask import Blueprint, jsonify, request

from backend import config
from backend.aws import sts

console_bp = Blueprint("console", __name__)


@console_bp.route("/generate_console_link", methods=["POST"])
def generate_console_link():
    data = request.get_json(force=True, silent=True) or {}
    access_key = data.get("access_key")
    secret_key = data.get("secret_key")
    region = data.get("region")
    proxy_url = None  # SOCKS 功能已禁用
    session_duration = int(
        data.get("session_duration") or config.DEFAULT_SESSION_DURATION
    )

    if not all([access_key, secret_key, region]):
        return jsonify({"ok": False, "error": "参数缺失：access_key/secret_key/region"})

    try:
        url = sts.generate_console_login_url(
            access_key, secret_key, region, session_duration, proxy_url
        )
        return jsonify({"ok": True, "url": url})
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)})
    except Exception as exc:  # noqa: BLE001
        return jsonify({"ok": False, "error": f"生成链接失败: {exc}"})
