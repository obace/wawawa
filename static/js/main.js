const LS_KEY = "awsTempLinkProfiles";

const REGION_OPTIONS = [
    ["us-east-1", "美国东部(弗吉尼亚北部) us-east-1"],
    ["us-east-2", "美国东部(俄亥俄) us-east-2"],
    ["us-west-1", "美国西部(加利福尼亚北部) us-west-1"],
    ["us-west-2", "美国西部(俄勒冈) us-west-2"],
    ["af-south-1", "非洲(开普敦) af-south-1"],
    ["ap-east-1", "亚太地区(香港) ap-east-1"],
    ["ap-south-1", "亚太地区(孟买) ap-south-1"],
    ["ap-south-2", "亚太地区(海得拉巴) ap-south-2"],
    ["ap-southeast-1", "亚太地区(新加坡) ap-southeast-1"],
    ["ap-southeast-2", "亚太地区(悉尼) ap-southeast-2"],
    ["ap-southeast-3", "亚太地区(雅加达) ap-southeast-3"],
    ["ap-southeast-4", "亚太地区(墨尔本) ap-southeast-4"],
    ["ap-northeast-1", "亚太地区(东京) ap-northeast-1"],
    ["ap-northeast-2", "亚太地区(首尔) ap-northeast-2"],
    ["ap-northeast-3", "亚太地区(大阪) ap-northeast-3"],
    ["ca-central-1", "加拿大(中部) ca-central-1"],
    ["eu-central-1", "欧洲(法兰克福) eu-central-1"],
    ["eu-central-2", "欧洲(苏黎世) eu-central-2"],
    ["eu-west-1", "欧洲(爱尔兰) eu-west-1"],
    ["eu-west-2", "欧洲(伦敦) eu-west-2"],
    ["eu-west-3", "欧洲(巴黎) eu-west-3"],
    ["eu-north-1", "欧洲(斯德哥尔摩) eu-north-1"],
    ["eu-south-1", "欧洲(米兰) eu-south-1"],
    ["eu-south-2", "欧洲(西班牙) eu-south-2"],
    ["il-central-1", "以色列(特拉维夫) il-central-1"],
    ["me-south-1", "中东(巴林) me-south-1"],
    ["me-central-1", "中东(阿联酋) me-central-1"],
    ["sa-east-1", "南美洲(圣保罗) sa-east-1"],
];

// EC2 规格：T2/T3 全系列（x86_64），以及 T4g 作为 arm 备选
const EC2_INSTANCE_TYPES = {
    x86_64: [
        { value: "t2.nano", label: "t2.nano · 1vCPU/0.5GiB" },
        { value: "t2.micro", label: "t2.micro · 1vCPU/1GiB" },
        { value: "t2.small", label: "t2.small · 1vCPU/2GiB" },
        { value: "t2.medium", label: "t2.medium · 2vCPU/4GiB" },
        { value: "t2.large", label: "t2.large · 2vCPU/8GiB" },
        { value: "t2.xlarge", label: "t2.xlarge · 4vCPU/16GiB" },
        { value: "t2.2xlarge", label: "t2.2xlarge · 8vCPU/32GiB" },
        { value: "t3.nano", label: "t3.nano · 2vCPU/0.5GiB" },
        { value: "t3.micro", label: "t3.micro · 2vCPU/1GiB" },
        { value: "t3.small", label: "t3.small · 2vCPU/2GiB" },
        { value: "t3.medium", label: "t3.medium · 2vCPU/4GiB" },
        { value: "t3.large", label: "t3.large · 2vCPU/8GiB" },
        { value: "t3.xlarge", label: "t3.xlarge · 4vCPU/16GiB" },
        { value: "t3.2xlarge", label: "t3.2xlarge · 8vCPU/32GiB" },
    ],
    arm64: [
        { value: "t4g.nano", label: "t4g.nano · 2vCPU/0.5GiB" },
        { value: "t4g.micro", label: "t4g.micro · 2vCPU/1GiB" },
        { value: "t4g.small", label: "t4g.small · 2vCPU/2GiB" },
        { value: "t4g.medium", label: "t4g.medium · 2vCPU/4GiB" },
        { value: "t4g.large", label: "t4g.large · 2vCPU/8GiB" },
        { value: "t4g.xlarge", label: "t4g.xlarge · 4vCPU/16GiB" },
        { value: "t4g.2xlarge", label: "t4g.2xlarge · 8vCPU/32GiB" },
    ],
};

// EC2 AMI 列表，按架构区分，含 Windows
const EC2_AMIS = {
    x86_64: [
        { value: "ssm:/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-6.1-x86_64", label: "Amazon Linux 2023 x86_64 (SSM 最新)" },
        { value: "ssm:/aws/service/canonical/ubuntu/server/22.04/stable/current/amd64/hvm/ebs-gp2/ami-id", label: "Ubuntu 22.04 x86_64 (SSM 最新)" },
        { value: "ssm:/aws/service/debian/debian-12/amd64/latest/image_id", label: "Debian 12 x86_64 (SSM 最新)" },
        { value: "ssm:/aws/service/ami-windows-latest/Windows_Server-2019-English-Full-Base", label: "Windows Server 2019 (SSM 最新)" },
        { value: "ssm:/aws/service/ami-windows-latest/Windows_Server-2022-English-Full-Base", label: "Windows Server 2022 (SSM 最新)" },
    ],
    arm64: [
        { value: "ssm:/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-6.1-arm64", label: "Amazon Linux 2023 arm64 (SSM 最新)" },
        { value: "ssm:/aws/service/canonical/ubuntu/server/22.04/stable/current/arm64/hvm/ebs-gp2/ami-id", label: "Ubuntu 22.04 arm64 (SSM 最新)" },
        { value: "ssm:/aws/service/debian/debian-12/arm64/latest/image_id", label: "Debian 12 arm64 (SSM 最新)" },
    ],
};

// Lightsail 套餐（全系列）
const LIGHTSAIL_BUNDLES = [
    { id: "nano_2_0", label: "Nano · 512MB / 1vCPU / 20GB 磁盘" },
    { id: "micro_2_0", label: "Micro · 1GB / 1vCPU / 40GB 磁盘" },
    { id: "small_2_0", label: "Small · 2GB / 1vCPU / 60GB 磁盘" },
    { id: "medium_2_0", label: "Medium · 4GB / 2vCPU / 80GB 磁盘" },
    { id: "large_2_0", label: "Large · 8GB / 2vCPU / 160GB 磁盘" },
    { id: "xlarge_2_0", label: "XLarge · 16GB / 4vCPU / 320GB 磁盘" },
    { id: "2xlarge_2_0", label: "2XLarge · 32GB / 8vCPU / 640GB 磁盘" },
];

// Lightsail 镜像，区分架构，含 Windows
const LIGHTSAIL_BLUEPRINTS = {
    x86_64: [
        { id: "amazon_linux_2023", label: "Amazon Linux 2023 x86_64" },
        { id: "ubuntu_22_04", label: "Ubuntu 22.04 x86_64" },
        { id: "debian_12", label: "Debian 12 x86_64" },
        { id: "windows_server_2019", label: "Windows Server 2019" },
        { id: "windows_server_2022", label: "Windows Server 2022" },
    ],
    arm64: [
        { id: "amazon_linux_2023_arm64", label: "Amazon Linux 2023 arm64" },
        { id: "ubuntu_22_04_arm64", label: "Ubuntu 22.04 arm64" },
        { id: "debian_12_arm64", label: "Debian 12 arm64" },
    ],
};

function setStatus(id, text, type = "") {
    const el = document.getElementById(id);
    if (!el) return;
    el.textContent = text;
    el.className = "proxy-status";
    if (type === "success") el.classList.add("success");
    if (type === "fail") el.classList.add("fail");
    if (type === "warn") el.classList.add("warn");
}

function loadStore() {
    try {
        const raw = localStorage.getItem(LS_KEY);
        if (!raw) return { profiles: {}, current: "" };
        return JSON.parse(raw);
    } catch (e) {
        return { profiles: {}, current: "" };
    }
}

function saveStore(store) {
    localStorage.setItem(LS_KEY, JSON.stringify(store));
}

function populateRegions() {
    const select = document.getElementById("region");
    select.innerHTML = "";
    REGION_OPTIONS.forEach(([value, label]) => {
        const opt = document.createElement("option");
        opt.value = value;
        opt.textContent = label;
        select.appendChild(opt);
    });
    const manage = document.getElementById("manage-region");
    if (manage) {
        manage.innerHTML = "";
        REGION_OPTIONS.forEach(([value, label]) => {
            const opt = document.createElement("option");
            opt.value = value;
            opt.textContent = label;
            manage.appendChild(opt);
        });
    }
    const createRegion = document.getElementById("create-region");
    if (createRegion) {
        createRegion.innerHTML = "";
        REGION_OPTIONS.forEach(([value, label]) => {
            const opt = document.createElement("option");
            opt.value = value;
            opt.textContent = label;
            createRegion.appendChild(opt);
        });
    }
}

function populateInstanceTypes() {
    const typeSelect = document.getElementById("create-type");
    const archSelect = document.getElementById("create-arch");
    const instanceSelect = document.getElementById("create-instance-type");
    const bundleSelect = document.getElementById("create-bundle");
    const amiSelect = document.getElementById("create-ami");
    const blueprintSelect = document.getElementById("create-blueprint");
    const arch = archSelect.value || "x86_64";
    instanceSelect.innerHTML = "";
    bundleSelect.innerHTML = "";
    amiSelect.innerHTML = "";
    blueprintSelect.innerHTML = "";
    if (typeSelect.value === "ec2") {
        (EC2_INSTANCE_TYPES[arch] || []).forEach((t) => {
            const opt = document.createElement("option");
            opt.value = t.value;
            opt.textContent = t.label || t.value;
            instanceSelect.appendChild(opt);
        });
        (EC2_AMIS[arch] || []).forEach((a) => {
            const opt = document.createElement("option");
            opt.value = a.value;
            opt.textContent = a.label;
            amiSelect.appendChild(opt);
        });
        bundleSelect.disabled = true;
        blueprintSelect.disabled = true;
    } else {
        LIGHTSAIL_BUNDLES.forEach((b) => {
            const opt = document.createElement("option");
            opt.value = b.id;
            opt.textContent = b.label;
            bundleSelect.appendChild(opt);
        });
        (LIGHTSAIL_BLUEPRINTS[arch] || []).forEach((b) => {
            const opt = document.createElement("option");
            opt.value = b.id;
            opt.textContent = b.label;
            blueprintSelect.appendChild(opt);
        });
        bundleSelect.disabled = false;
        blueprintSelect.disabled = false;
        instanceSelect.innerHTML = "";
        const opt = document.createElement("option");
        opt.value = "lightsail";
        opt.textContent = "由套餐决定";
        instanceSelect.appendChild(opt);
        amiSelect.innerHTML = "";
        const opt2 = document.createElement("option");
        opt2.value = "lightsail";
        opt2.textContent = "由镜像选择决定";
        amiSelect.appendChild(opt2);
    }
}

function getFormData() {
    return {
        access_key: document.getElementById("access-key").value.trim(),
        secret_key: document.getElementById("secret-key").value.trim(),
        region: document.getElementById("region").value.trim(),
        session_duration: Number(document.getElementById("session-duration").value),
    };
}

function setFormData(data) {
    document.getElementById("access-key").value = data.access_key || "";
    document.getElementById("secret-key").value = data.secret_key || "";
    const regionSelect = document.getElementById("region");
    if (data.region && !REGION_OPTIONS.find(([v]) => v === data.region)) {
        const opt = document.createElement("option");
        opt.value = data.region;
        opt.textContent = `${data.region} (自定义)`;
        regionSelect.appendChild(opt);
    }
    regionSelect.value = data.region || REGION_OPTIONS[0][0];
    const manageRegion = document.getElementById("manage-region");
    if (manageRegion) {
        manageRegion.value = regionSelect.value;
    }
    document.getElementById("session-duration").value = data.session_duration || 3600;
}

function renderProfiles(store) {
    const select = document.getElementById("profile-select");
    const nameInput = document.getElementById("profile-name-input");
    select.innerHTML = "";
    const names = Object.keys(store.profiles);
    if (!names.length) {
        const opt = document.createElement("option");
        opt.value = "";
        opt.textContent = "未保存";
        select.appendChild(opt);
        nameInput.value = "";
        return;
    }
    names.forEach((name) => {
        const opt = document.createElement("option");
        opt.value = name;
        opt.textContent = name;
        if (name === store.current) {
            opt.selected = true;
            setFormData(store.profiles[name]);
            nameInput.value = name;
        }
        select.appendChild(opt);
    });
}

function updateCurrentLabels(store) {
    document.getElementById("current-profile-name").textContent =
        store.current || "未选择";
    const manageRegion = document.getElementById("manage-region");
    const regionValue = manageRegion && manageRegion.value ? manageRegion.value : document.getElementById("region").value;
    document.getElementById("current-region").textContent = regionValue || "-";
}

function parseBatchAccounts(text) {
    const lines = (text || "").split(/\n+/).map((l) => l.trim()).filter(Boolean);
    const accounts = [];
    lines.forEach((line, idx) => {
        const parts = line.split(/\s+/).filter(Boolean);
        if (parts.length < 2) return;
        let name = "";
        let ak = "";
        let sk = "";
        if (parts.length >= 3) {
            [name, ak, sk] = parts;
        } else {
            [ak, sk] = parts;
            name = `acct-${idx + 1}`;
        }
        accounts.push({ name, access_key: ak, secret_key: sk });
    });
    return accounts;
}

async function apiPost(url, body) {
    const resp = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
    });
    return resp.json();
}

function initProfileActions() {
    const select = document.getElementById("profile-select");
    const nameInput = document.getElementById("profile-name-input");
    populateRegions();
    populateInstanceTypes();
    let store = loadStore();
    renderProfiles(store);
    updateCurrentLabels(store);

    document.getElementById("create-type").addEventListener("change", populateInstanceTypes);
    document.getElementById("create-arch").addEventListener("change", populateInstanceTypes);

    select.addEventListener("change", () => {
        const name = select.value;
        if (store.profiles[name]) {
            store.current = name;
            setFormData(store.profiles[name]);
            nameInput.value = name;
            saveStore(store);
            updateCurrentLabels(store);
            setStatus("profile-result", `已切换到配置：${name}`, "success");
        }
    });

    document.getElementById("new-profile").addEventListener("click", () => {
        const name = nameInput.value.trim();
        if (!name) {
            setStatus("profile-result", "请先在“配置名称”填写名称", "warn");
            return;
        }
        store.profiles[name] = getFormData();
        store.current = name;
        saveStore(store);
        renderProfiles(store);
        select.value = name;
        updateCurrentLabels(store);
        setStatus("profile-result", "新配置已创建", "success");
    });

    document.getElementById("rename-profile").addEventListener("click", () => {
        if (!store.current) {
            setStatus("profile-result", "未选择配置，无法重命名", "warn");
            return;
        }
        const newName = nameInput.value.trim();
        if (!newName) {
            setStatus("profile-result", "请先在“配置名称”填写新名称", "warn");
            return;
        }
        store.profiles[newName] = store.profiles[store.current];
        delete store.profiles[store.current];
        store.current = newName;
        saveStore(store);
        renderProfiles(store);
        select.value = newName;
        updateCurrentLabels(store);
        setStatus("profile-result", "配置已重命名", "success");
    });

    document.getElementById("delete-profile").addEventListener("click", () => {
        if (!store.current) {
            setStatus("profile-result", "未选择配置，无法删除", "warn");
            return;
        }
        if (nameInput.value.trim() !== store.current) {
            setStatus("profile-result", "请在“配置名称”中填写当前配置名以确认删除", "warn");
            return;
        }
        delete store.profiles[store.current];
        store.current = Object.keys(store.profiles)[0] || "";
        saveStore(store);
        renderProfiles(store);
        nameInput.value = store.current || "";
        updateCurrentLabels(store);
        setStatus("profile-result", "配置已删除", "success");
    });

    document.getElementById("save-profile").addEventListener("click", () => {
        const name = nameInput.value.trim();
        if (!name) {
            setStatus("profile-result", "请在“配置名称”填写后再保存", "warn");
            return;
        }
        store.profiles[name] = getFormData();
        store.current = name;
        saveStore(store);
        renderProfiles(store);
        select.value = name;
        updateCurrentLabels(store);
        setStatus("profile-result", "配置已保存/覆盖", "success");
    });
}

function bindActions() {
    document.getElementById("test-aws").addEventListener("click", async () => {
        const payload = getFormData();
        setStatus("aws-result", "测试中...");
        try {
            const res = await apiPost("/check_aws", payload);
            if (res.ok) {
                setStatus(
                    "aws-result",
                    `验证成功：Account=${res.account}，UserId=${res.user_id}，Arn=${res.arn}`,
                    "success"
                );
            } else {
                setStatus("aws-result", `验证失败：${res.error}`, "fail");
            }
        } catch (e) {
            setStatus("aws-result", `请求失败：${e}`, "fail");
        }
    });

    document.getElementById("fetch-quota").addEventListener("click", async () => {
        const payload = getFormData();
        setStatus("quota-result", "查询中...");
        try {
            const res = await apiPost("/quota", payload);
            if (res.ok) {
                setStatus("quota-result", `On-Demand 标准实例配额：${res.value}`, "success");
            } else {
                setStatus("quota-result", `查询失败：${res.error}`, "fail");
            }
        } catch (e) {
            setStatus("quota-result", `请求失败：${e}`, "fail");
        }
    });

    document.getElementById("generate-link").addEventListener("click", async () => {
        const payload = getFormData();
        setStatus("link-result", "生成中...");
        try {
            const res = await apiPost("/generate_console_link", payload);
            if (res.ok) {
                document.getElementById("console-url").textContent = res.url;
                document.getElementById("open-console").href = res.url;
                setStatus("link-result", "登录链接已生成", "success");
            } else {
                setStatus("link-result", `生成失败：${res.error}`, "fail");
            }
        } catch (e) {
            setStatus("link-result", `请求失败：${e}`, "fail");
        }
    });

    document.getElementById("copy-link").addEventListener("click", async () => {
        const url = document.getElementById("console-url").textContent;
        if (!url.startsWith("http")) {
            setStatus("link-result", "还没有可复制的链接", "warn");
            return;
        }
        try {
            if (navigator.clipboard && window.isSecureContext) {
                await navigator.clipboard.writeText(url);
            } else {
                const ta = document.createElement("textarea");
                ta.value = url;
                document.body.appendChild(ta);
                ta.select();
                document.execCommand("copy");
                document.body.removeChild(ta);
            }
            setStatus("link-result", "链接已复制到剪贴板", "success");
        } catch (e) {
            setStatus("link-result", "复制失败，请手动复制", "fail");
        }
    });

    document.getElementById("batch-delete").addEventListener("click", async () => {
        const accounts = parseBatchAccounts(document.getElementById("batch-accounts").value);
        if (!accounts.length) {
            setStatus("batch-result", "请先填写账号列表（至少 AK/SK）", "warn");
            return;
        }
        setStatus("batch-result", "批量删除中...");
        try {
            const res = await apiPost("/batch_delete_ec2", { accounts });
            if (res.ok) {
                const lines = (res.results || []).map((a) => {
                    const regions = a.regions || [];
                    const nonZero = regions.filter((r) => (r.terminated || []).length > 0);
                    if (!nonZero.length) {
                        return `${a.name}：全部区域 0 个实例`;
                    }
                    const parts = nonZero.map(
                        (r) => `${r.region} 删除 ${(r.terminated || []).length} 个实例`
                    );
                    return `${a.name}：${parts.join("，")}，其余区域 0`;
                });
                const block = [`删除完成：`, ...lines].join("\n");
                const el = document.getElementById("batch-result");
                if (el) {
                    el.textContent = block;
                    el.className = "batch-result success";
                }
            } else {
                const el = document.getElementById("batch-result");
                if (el) {
                    el.textContent = `执行失败：${res.error}`;
                    el.className = "batch-result fail";
                }
            }
        } catch (e) {
            const el = document.getElementById("batch-result");
            if (el) {
                el.textContent = `请求失败：${e}`;
                el.className = "batch-result fail";
            }
        }
    });

    document.getElementById("create-instance-btn").addEventListener("click", async () => {
        const payload = getFormData();
        const typ = document.getElementById("create-type").value;
        const createRegion = document.getElementById("create-region");
        if (createRegion && createRegion.value) {
            payload.region = createRegion.value;
        }
        const arch = document.getElementById("create-arch").value;
        const instance_type = document.getElementById("create-instance-type").value;
        const bundle_id = document.getElementById("create-bundle").value;
        const blueprint_id = document.getElementById("create-blueprint").value;
        const ami_id = document.getElementById("create-ami").value;
        const name = document.getElementById("create-name").value.trim();
        const password = document.getElementById("create-password").value.trim();
        const volume_size = Number(document.getElementById("create-volume").value) || undefined;
        const body = {
            ...payload,
            type: typ,
            arch,
            instance_type,
            bundle_id,
            blueprint_id,
            ami_id,
            name,
            password,
            volume_size,
        };
        setStatus("create-result", "创建中...");
        try {
            const res = await apiPost("/create_instance", body);
            if (res.ok) {
                setStatus("create-result", res.message || "实例创建成功", "success");
            } else {
                setStatus("create-result", `创建失败：${res.error}`, "fail");
            }
        } catch (e) {
            setStatus("create-result", `请求失败：${e}`, "fail");
        }
    });

    document.getElementById("load-instances").addEventListener("click", loadInstances);
}

async function loadInstances() {
    const payload = getFormData();
    const manageRegionSelect = document.getElementById("manage-region");
    if (manageRegionSelect && manageRegionSelect.value) {
        payload.region = manageRegionSelect.value;
    }
    setStatus("instances-result", "加载中...");
    try {
        const res = await apiPost("/instances", payload);
        if (!res.ok) {
            setStatus("instances-result", `加载失败：${res.error}`, "fail");
            return;
        }
        renderEC2(res.ec2 || []);
        renderLightsail(res.lightsail || []);
        setStatus("instances-result", "实例列表已更新", "success");
        const store = loadStore();
        updateCurrentLabels(store);
    } catch (e) {
        setStatus("instances-result", `请求失败：${e}`, "fail");
    }
}

function renderEC2(list) {
    const tbody = document.getElementById("ec2-table-body");
    tbody.innerHTML = "";
    list.forEach((item) => {
        const tr = document.createElement("tr");
        const stateClass = item.state === "running" ? "running" : "stopped";
        tr.innerHTML = `
            <td class="mono">${item.instance_id}</td>
            <td>${item.name || "-"}</td>
            <td><span class="badge ${stateClass}">${item.state}</span></td>
            <td>${item.public_ip || "-"}</td>
            <td>${item.private_ip || "-"}</td>
            <td class="actions"></td>
        `;
        const actions = tr.querySelector(".actions");
        actions.appendChild(actionButton("启动", () => instanceAction("ec2", "start", { instance_id: item.instance_id })));
        actions.appendChild(actionButton("停止", () => instanceAction("ec2", "stop", { instance_id: item.instance_id })));
        actions.appendChild(actionButton("重启", () => instanceAction("ec2", "reboot", { instance_id: item.instance_id })));
        actions.appendChild(actionButton("换 IP", () => instanceAction("ec2", "change_ip", { instance_id: item.instance_id })));
        tbody.appendChild(tr);
    });
}

function renderLightsail(list) {
    const tbody = document.getElementById("lightsail-table-body");
    tbody.innerHTML = "";
    list.forEach((item) => {
        const tr = document.createElement("tr");
        const stateClass = item.state === "running" ? "running" : "stopped";
        tr.innerHTML = `
            <td class="mono">${item.name}</td>
            <td><span class="badge ${stateClass}">${item.state}</span></td>
            <td>${item.public_ip || "-"}</td>
            <td>${item.private_ip || "-"}</td>
            <td class="actions"></td>
        `;
        const actions = tr.querySelector(".actions");
        actions.appendChild(actionButton("启动", () => instanceAction("lightsail", "start", { name: item.name })));
        actions.appendChild(actionButton("停止", () => instanceAction("lightsail", "stop", { name: item.name })));
        actions.appendChild(actionButton("重启", () => instanceAction("lightsail", "reboot", { name: item.name })));
        actions.appendChild(actionButton("换 IP", () => instanceAction("lightsail", "change_ip", { name: item.name })));
        tbody.appendChild(tr);
    });
}

function actionButton(text, handler) {
    const btn = document.createElement("button");
    btn.textContent = text;
    btn.addEventListener("click", handler);
    return btn;
}

async function instanceAction(type, action, extra) {
    const payload = { ...getFormData(), type, action, ...extra };
    const manageRegionSelect = document.getElementById("manage-region");
    if (manageRegionSelect && manageRegionSelect.value) {
        payload.region = manageRegionSelect.value;
    }
    setStatus("instances-result", `正在执行 ${action}...`);
    try {
        const res = await apiPost("/instance_action", payload);
        if (res.ok) {
            setStatus("instances-result", res.message || "操作成功", "success");
            loadInstances();
        } else {
            setStatus("instances-result", `操作失败：${res.error}`, "fail");
        }
    } catch (e) {
        setStatus("instances-result", `请求失败：${e}`, "fail");
    }
}

document.addEventListener("DOMContentLoaded", () => {
    initProfileActions();
    bindActions();
});
