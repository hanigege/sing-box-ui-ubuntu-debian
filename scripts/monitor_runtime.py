#!/usr/bin/env python3
import ipaddress
import json
import os
import subprocess
import sys
import time
from pathlib import Path


APP_DIR = Path(os.environ.get("RULE_UI_APP_DIR", "/opt/singbox-rule-ui"))
CONFIG_PATH = Path(os.environ.get("RULE_UI_SING_BOX_CONFIG", "/etc/sing-box/config.json"))
REFRESH_CONFIG = Path(os.environ.get("RULE_UI_REFRESH_CONFIG", "/usr/local/sbin/refresh-sing-box-runtime-config"))
SING_BOX_BIN = Path(os.environ.get("RULE_UI_SING_BOX_BIN", "/usr/local/bin/sing-box"))
SING_BOX_SERVICE = os.environ.get("RULE_UI_SING_BOX_SERVICE", "sing-box")
TPROXY_SERVICE = os.environ.get("RULE_UI_TPROXY_SERVICE", "sing-box-tproxy")
UI_SERVICE = os.environ.get("RULE_UI_SERVICE", "singbox-rule-ui")


def run(command, timeout=30):
    result = subprocess.run(command, text=True, capture_output=True, timeout=timeout)
    return {"command": command, "code": result.returncode, "stdout": result.stdout.strip(), "stderr": result.stderr.strip()}


def default_lan_ip():
    result = run(["ip", "-o", "-4", "route", "get", "1.1.1.1"], timeout=8)
    parts = result["stdout"].split()
    if "src" not in parts:
        return ""
    return parts[parts.index("src") + 1]


def load_config():
    if not CONFIG_PATH.exists():
        return {}
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def service_active(name):
    # systemd 版：is-active 判定，输出单词 active 即活跃。
    result = run(["systemctl", "is-active", name], timeout=8)
    return result["code"] == 0 and (result["stdout"] or result["stderr"]).strip().lower() == "active"


def config_matches_runtime(config, lan_ip, ipv6_listener):
    dns4_ok = False
    dns6_ok = not ipv6_listener
    for inbound in config.get("inbounds", []) or []:
        if not isinstance(inbound, dict):
            continue
        if inbound.get("tag") == "dns-in":
            dns4_ok = inbound.get("listen") == lan_ip
        if inbound.get("tag") == "dns-in-v6":
            dns6_ok = inbound.get("listen") == ipv6_listener
    controller = str(config.get("experimental", {}).get("clash_api", {}).get("external_controller", ""))
    controller_host = controller.rsplit(":", 1)[0] if ":" in controller else controller
    return dns4_ok and dns6_ok and controller_host == lan_ip


def ipv6_prefixes_covered(current, scripted):
    scripted_networks = []
    for item in scripted:
        try:
            network = ipaddress.ip_network(item, strict=False)
        except ValueError:
            continue
        if network.version == 6:
            scripted_networks.append(network)
    for item in current:
        try:
            network = ipaddress.ip_network(item, strict=False)
        except ValueError:
            continue
        # 脚本里可能用 fc00::/7 这类汇总网段保护 ULA；判断覆盖关系，避免把等价保护误判成需要重启。
        if network.version == 6 and not any(network.subnet_of(scripted) for scripted in scripted_networks):
            return False
    return True


def restart_service(name):
    return run(["systemctl", "restart", name], timeout=60)


def main():
    started = time.strftime("%Y-%m-%d %H:%M:%S")
    actions = []
    sys.path.insert(0, str(APP_DIR))
    import app

    lan_ip = default_lan_ip()
    iface = app.first_default_interface()
    current_v6 = app.current_ipv6_prefixes(iface)
    script_v6 = app.script_ipv6_prefixes(app.TPROXY_SCRIPT)
    ipv6_listener = app.preferred_ipv6_listener(lan_ip) if lan_ip else ""

    config = load_config()
    config_needs_refresh = bool(lan_ip and not config_matches_runtime(config, lan_ip, ipv6_listener))
    tproxy_needs_refresh = bool(not script_v6 or not ipv6_prefixes_covered(current_v6, script_v6))

    if config_needs_refresh:
        # IPv4 地址或 IPv6 DNS 监听地址发生变化时，先重渲染配置并校验，成功后才重启 sing-box。
        actions.append({"refreshConfig": run([str(REFRESH_CONFIG)], timeout=30)})
        check = run([str(SING_BOX_BIN), "check", "-c", str(CONFIG_PATH)], timeout=30)
        actions.append({"singBoxCheck": check})
        if check["code"] == 0:
            actions.append({"restartSingBox": restart_service(SING_BOX_SERVICE)})

    if tproxy_needs_refresh or not service_active(TPROXY_SERVICE):
        # TProxy 捕获边界依赖当前网卡和 IPv6 前缀；只在前缀不一致或服务异常时刷新。
        actions.append({"restartTproxy": restart_service(TPROXY_SERVICE)})

    if not service_active(SING_BOX_SERVICE):
        actions.append({"restartSingBoxInactive": restart_service(SING_BOX_SERVICE)})

    if not service_active(UI_SERVICE):
        actions.append({"restartUiInactive": restart_service(UI_SERVICE)})

    summary = {
        "startedAt": started,
        "lanIp": lan_ip,
        "interface": iface,
        "currentIpv6Prefixes": current_v6,
        "scriptIpv6Prefixes": script_v6,
        "ipv6Listener": ipv6_listener,
        "configNeedsRefresh": config_needs_refresh,
        "tproxyNeedsRefresh": tproxy_needs_refresh,
        "actions": actions,
    }
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
