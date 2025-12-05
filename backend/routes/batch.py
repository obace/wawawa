from flask import Blueprint, jsonify, request
from backend.aws import ec2

batch_bp = Blueprint("batch", __name__)


@batch_bp.route("/batch_delete_ec2", methods=["POST"])
def batch_delete_ec2():
    data = request.get_json(force=True, silent=True) or {}
    accounts = data.get("accounts") or []
    regions_override = data.get("regions") or None

    if not accounts:
        return jsonify({"ok": False, "error": "accounts 不能为空"})

    results = []
    for idx, acct in enumerate(accounts, start=1):
        name = acct.get("name") or f"acct-{idx}"
        access_key = acct.get("access_key")
        secret_key = acct.get("secret_key")
        region = acct.get("region")
        if not all([access_key, secret_key]):
            results.append({"name": name, "ok": False, "error": "缺少 access_key/secret_key"})
            continue

        # 目标 Region：优先前端传入列表；否则若账号带 region 用它；否则查全部可用 Region
        target_regions = regions_override or ([region] if region else [])
        if not target_regions:
            try:
                target_regions = ec2.list_all_regions(access_key, secret_key, region or "us-east-1", proxy_url=None)
            except Exception as exc:  # noqa: BLE001
                results.append({"name": name, "ok": False, "error": f"获取 Region 失败: {exc}"})
                continue
        if not target_regions:
            results.append({"name": name, "ok": False, "error": "未指定 region"})
            continue

        acct_summary = {"name": name, "ok": True, "regions": []}
        for reg in target_regions:
            try:
                terminated = ec2.terminate_all_instances(access_key, secret_key, reg, proxy_url=None)
                acct_summary["regions"].append({"region": reg, "terminated": terminated})
            except Exception as exc:  # noqa: BLE001
                acct_summary["ok"] = False
                acct_summary["regions"].append({"region": reg, "error": str(exc), "terminated": []})
        results.append(acct_summary)

    overall_ok = all(item.get("ok") for item in results if isinstance(item, dict))
    return jsonify({"ok": overall_ok, "results": results})
