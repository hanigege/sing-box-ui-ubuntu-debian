#!/usr/bin/env python3
import ipaddress
import json
import os
import secrets
import subprocess
import tempfile
from pathlib import Path


CONFIG_DIR = Path("/etc/sing-box")
MANAGER_DIR = CONFIG_DIR / "manager"
RULE_DIR = CONFIG_DIR / "custom-rules"
CONFIG_PATH = CONFIG_DIR / "config.json"
BASE_CONFIG_PATH = MANAGER_DIR / "base.json"
NODES_PATH = MANAGER_DIR / "nodes.json"
GROUPS_PATH = MANAGER_DIR / "groups.json"
DEFAULT_FAKE4 = "28.0.0.0/8"
DEFAULT_FAKE6 = "2001:2::/64"
DEFAULT_INTERRUPT_EXIST_CONNECTIONS = False
INITIAL_NODES_FILE = os.environ.get("SING_BOX_INITIAL_NODES_FILE", "")
# 仓库根目录（bootstrap_config.py 在 scripts/ 下，上溯一层即为仓库根）。
REPO_DIR = Path(__file__).resolve().parent.parent
PRESET_RULES_DIR = REPO_DIR / "templates" / "custom-rules"


def default_lan_ip():
    try:
        out = subprocess.check_output(["ip", "-o", "-4", "route", "get", "1.1.1.1"], text=True)
        parts = out.split()
        if "src" in parts:
            return parts[parts.index("src") + 1]
    except Exception:
        pass
    return "0.0.0.0"


def empty_rule_set():
    return {"version": 3, "rules": []}


def normalize_cidr(value, label):
    try:
        return str(ipaddress.ip_network(value, strict=True))
    except ValueError as exc:
        # FakeIP 网段会同时写入 DNS、路由和 TProxy；必须要求网络地址，不能把主机地址静默修正成网段。
        raise ValueError(f"{label} must be a network CIDR, for example 28.0.0.0/8") from exc


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    # 初装会生成正式配置和 UI 状态文件，使用原子替换保证中断后不会留下半截 JSON。
    content = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))
    temp_path = Path(temp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, path)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def template_nodes():
    return [
        {
            "enabled": True,
            "outbound": {
                "type": "hysteria2",
                "tag": "TEMPLATE-HY2",
                "server": "198.51.100.10",
                "server_port": 443,
                "password": "change-me-hysteria2-password",
                "tls": {"enabled": True, "server_name": "example.com", "insecure": True},
                "obfs": {"type": "salamander", "password": "change-me-obfs-password"},
                "up_mbps": 20,
                "down_mbps": 100,
            },
        },
        {
            "enabled": True,
            "outbound": {
                "type": "vless",
                "tag": "TEMPLATE-VLESS",
                "server": "203.0.113.10",
                "server_port": 443,
                "uuid": "00000000-0000-4000-8000-000000000001",
                "packet_encoding": "xudp",
                "tcp_fast_open": True,
                "tls": {
                    "enabled": True,
                    "server_name": "example.com",
                    "insecure": True,
                    "utls": {"enabled": True, "fingerprint": "chrome"},
                },
            },
        },
    ]


def initial_nodes_from_file():
    if not INITIAL_NODES_FILE:
        return None
    path = Path(INITIAL_NODES_FILE)
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list) or not data:
        raise ValueError("SING_BOX_INITIAL_NODES_FILE must contain a non-empty node list")
    for index, node in enumerate(data, 1):
        if not isinstance(node, dict) or not isinstance(node.get("outbound"), dict):
            raise ValueError(f"Node {index} is missing outbound")
        outbound = node["outbound"]
        if not outbound.get("tag") or outbound.get("type") not in {"hysteria2", "vless"}:
            raise ValueError(f"Node {index} must have a supported outbound type and tag")
        node.setdefault("enabled", True)
    return data


def local_rule_set(tag, path, format_="source"):
    return {"type": "local", "tag": tag, "format": format_, "path": path}


def base_config(lan_ip, ui_secret, fake4, fake6, ipv6_dns_listen):
    dns_inbounds = ["dns-in"]
    inbounds = [
        {"type": "tproxy", "tag": "tproxy-in", "listen": "::", "listen_port": 9888, "sniff": False},
        {"type": "direct", "tag": "dns-in", "listen": lan_ip, "listen_port": 53},
    ]
    if ipv6_dns_listen:
        dns_inbounds.append("dns-in-v6")
        inbounds.append({"type": "direct", "tag": "dns-in-v6", "listen": ipv6_dns_listen, "listen_port": 53})
    return {
        "log": {"level": "warning"},
        "dns": {
            "servers": [
                {
                    "tag": "remote-dns",
                    "type": "https",
                    "server": "1.1.1.1",
                    "server_port": 443,
                    "path": "/dns-query",
                    "tls": {"server_name": "cloudflare-dns.com"},
                    "detour": "Proxy",
                },
                {
                    "tag": "local-dns",
                    "type": "udp",
                    "server": "119.29.29.29",
                    "server_port": 53,
                    # 国内直连域名优先使用 DNSPod UDP，当前 sing-box 版本没有 DNS 上游并发/自动备用组；223.5.5.5 只作为手动回退参考，不能伪装成自动备份。
                },
                {
                    "tag": "ddns-remote-dns",
                    "type": "udp",
                    "server": "1.1.1.1",
                    "server_port": 53,
                    "detour": "Proxy",
                    # DDNS 的代理解析只需要从代理出口查真实地址；不要复用 remote-dns 的 DoH 长连接，避免直连 DDNS 业务被 DNS 旧连接拖住。
                },
                {"tag": "fakeip-dns", "type": "fakeip", "inet4_range": fake4, "inet6_range": fake6},
            ],
            "rules": [
                {"rule_set": "custom-blacklist", "action": "reject"},
                # 白名单既然要直连，DNS 也必须返回真实地址；否则 LAN 兜底 FakeIP 会让 IPv6 外测继续进入代理链路。
                {"rule_set": "custom-whitelist", "action": "route", "server": "local-dns", "rewrite_ttl": 60},
                {"rule_set": "custom-greylist", "action": "route", "server": "fakeip-dns", "rewrite_ttl": 60, "query_type": ["A", "AAAA"]},
                {"rule_set": "custom-ddns", "action": "route", "server": "local-dns", "rewrite_ttl": 60},
                {"inbound": dns_inbounds, "rule_set": "custom-ddns", "action": "route", "server": "local-dns", "rewrite_ttl": 60},
                {"inbound": dns_inbounds, "rule_set": ["geosite-cn", "geosite-geolocation-cn", "geosite-icloud@cn", "geosite-apple@cn"], "action": "route", "server": "local-dns", "rewrite_ttl": 60},
                {"inbound": dns_inbounds, "rule_set": ["geosite-geolocation-!cn"], "action": "route", "server": "fakeip-dns", "rewrite_ttl": 60, "query_type": ["A", "AAAA"]},
                {"inbound": dns_inbounds, "query_type": ["A", "AAAA"], "action": "route", "server": "fakeip-dns", "rewrite_ttl": 60},
                # 局域网 AD/mDNS/单标签主机名探测不送上游，避免无意义 timeout/error 刷屏。
                {"inbound": dns_inbounds, "domain_suffix": ["local"], "domain_regex": [r"^[^.]+$", r"^_(ldap|gc)\._tcp\..+"], "action": "reject"},
                {"rule_set": ["geosite-cn", "geosite-geolocation-cn", "geosite-icloud@cn", "geosite-apple@cn"], "action": "route", "server": "local-dns", "rewrite_ttl": 60},
                {"rule_set": ["geosite-geolocation-!cn"], "action": "route", "server": "remote-dns", "rewrite_ttl": 60},
            ],
        },
        "inbounds": inbounds,
        "outbounds": [],
        "route": {
            "auto_detect_interface": True,
            "default_domain_resolver": "remote-dns",
            "rule_set": [
                local_rule_set("geosite-geolocation-!cn", "/etc/sing-box/rules/geosite/geolocation-!cn.srs", "binary"),
                local_rule_set("geosite-cn", "/etc/sing-box/rules/geosite/cn.srs", "binary"),
                local_rule_set("geosite-geolocation-cn", "/etc/sing-box/rules/geosite/geolocation-cn.srs", "binary"),
                local_rule_set("geosite-icloud@cn", "/etc/sing-box/rules/geosite/icloud@cn.srs", "binary"),
                local_rule_set("geosite-apple@cn", "/etc/sing-box/rules/geosite/apple@cn.srs", "binary"),
                local_rule_set("geosite-speedtest", "/etc/sing-box/rules/geosite/speedtest.srs", "binary"),
                local_rule_set("geosite-telegram", "/etc/sing-box/rules/geosite/telegram.srs", "binary"),
                local_rule_set("geoip-cn", "/etc/sing-box/rules/geoip/cn.srs", "binary"),
                local_rule_set("geoip-telegram", "/etc/sing-box/rules/geoip/telegram.srs", "binary"),
                local_rule_set("custom-whitelist", "/etc/sing-box/custom-rules/whitelist.json"),
                local_rule_set("custom-blacklist", "/etc/sing-box/custom-rules/blacklist.json"),
                local_rule_set("custom-greylist", "/etc/sing-box/custom-rules/greylist.json"),
                local_rule_set("custom-ddns", "/etc/sing-box/custom-rules/ddns.json"),
            ],
            "rules": [
                {"inbound": dns_inbounds, "action": "hijack-dns"},
                # FakeIP 视频连接可能在路由阶段被还原成域名；用 reject 表达预期拒绝，避免 block 出站把正常 QUIC 回落记录成 ERROR。
                {
                    "network": "udp",
                    "port": 443,
                    "domain_suffix": ["googlevideo.com", "youtube.com", "youtube-nocookie.com", "ytimg.com", "ggpht.com", "googleusercontent.com"],
                    "action": "reject",
                },
                # 同时保留 CIDR 保护，覆盖尚未还原域名的 FakeIP UDP/443；不能扩大到全部 UDP，否则会影响游戏和语音。
                {"network": "udp", "port": 443, "ip_cidr": [fake4, fake6], "action": "reject"},
                {"inbound": "tproxy-in", "action": "sniff", "sniffer": ["tls", "http"], "timeout": "300ms"},
                {"rule_set": "custom-blacklist", "outbound": "block"},
                {"rule_set": "custom-whitelist", "outbound": "direct"},
                {"rule_set": "custom-ddns", "outbound": "direct"},
                {"rule_set": "custom-greylist", "outbound": "Proxy"},
                # 测速流量会主动打满带宽，默认直连，避免压垮代理节点影响游戏和实时业务。
                {"rule_set": ["geosite-speedtest"], "outbound": "direct"},
                # Telegram 客户端可能直接连接官方 IP 段，域名和 IP 规则都要在 FakeIP 捕获前送代理。
                # 拆成两条 OR 规则而非 AND：裸 IP 连接没有域名，AND 会导致规则失败掉到 direct。
                {"rule_set": "geosite-telegram", "outbound": "Proxy"},
                {"rule_set": "geoip-telegram", "outbound": "Proxy"},
                {"ip_cidr": [fake4, fake6], "outbound": "Proxy"},
                {"ip_is_private": True, "outbound": "direct"},
                {"rule_set": ["geosite-geolocation-!cn"], "outbound": "Proxy"},
                {"rule_set": ["geosite-cn", "geosite-geolocation-cn", "geosite-icloud@cn", "geosite-apple@cn", "geoip-cn"], "outbound": "direct"},
            ],
            "final": "direct",
        },
        "experimental": {
            "cache_file": {"enabled": True, "store_fakeip": True},
            "clash_api": {
                "external_controller": f"{lan_ip}:9090",
                "secret": ui_secret,
                "default_mode": "rule",
            },
        },
    }


def main():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    MANAGER_DIR.mkdir(parents=True, exist_ok=True)
    RULE_DIR.mkdir(parents=True, exist_ok=True)
    # 一键安装不做任何命令行交互：先用可启动的简单配置落地，节点和高级参数交给 UI 修改。
    lan_ip = default_lan_ip()
    fake4 = DEFAULT_FAKE4
    fake6 = DEFAULT_FAKE6
    ipv6_dns = ""
    fake4 = normalize_cidr(fake4, "FakeIP IPv4 range")
    fake6 = normalize_cidr(fake6, "FakeIP IPv6 range")
    nodes = initial_nodes_from_file()
    if nodes is None:
        nodes = template_nodes()
    secret = secrets.token_urlsafe(24)
    base = base_config(lan_ip, secret, fake4, fake6, ipv6_dns)
    default_node = nodes[0]["outbound"]["tag"]
    groups = {
        # 初装默认不打断既有连接，避免 urltest 切换节点时让游戏/语音长连接掉线重连。
        "proxy": {"default": default_node, "interrupt_exist_connections": DEFAULT_INTERRUPT_EXIST_CONNECTIONS},
        "auto": {
            "url": "https://www.gstatic.com/generate_204",
            "interval": "30s",
            "tolerance": 50,
            "interrupt_exist_connections": DEFAULT_INTERRUPT_EXIST_CONNECTIONS,
        },
        "direct": {"type": "direct", "tag": "direct"},
        "block": {"type": "block", "tag": "block"},
        "fakeip": {"tag": "fakeip-dns", "inet4_range": fake4, "inet6_range": fake6, "block_quic": True},
        "dns": {"local": "dnspod"},
        "ddns": {"dns": "local"},
    }
    # 首次安装预置黑白灰名单模板，让新装机即带常用规则，无需手动配置。
    # 覆盖安装时保留用户已配置的规则，不覆盖；ddns 无模板，创建空规则集。
    for name in ("whitelist", "blacklist", "greylist", "ddns"):
        rule_path = RULE_DIR / f"{name}.json"
        if rule_path.is_file():
            continue
        preset_path = PRESET_RULES_DIR / f"{name}.json"
        if preset_path.is_file():
            write_json(rule_path, json.loads(preset_path.read_text(encoding="utf-8")))
        else:
            write_json(rule_path, empty_rule_set())
    write_json(BASE_CONFIG_PATH, base)
    write_json(NODES_PATH, nodes)
    write_json(GROUPS_PATH, groups)
    token_path = CONFIG_DIR / "rule-ui" / "token"
    token_path.parent.mkdir(parents=True, exist_ok=True)
    token_path.write_text(secrets.token_urlsafe(32) + "\n", encoding="utf-8")
    token_path.chmod(0o600)
    import sys
    sys.path.insert(0, "/opt/singbox-rule-ui")
    from app import render_config
    write_json(CONFIG_PATH, render_config(nodes=nodes, groups=groups, rule_dir=RULE_DIR))


if __name__ == "__main__":
    main()
