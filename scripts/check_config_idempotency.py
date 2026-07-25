#!/usr/bin/env python3
import hashlib
import importlib.util
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP_PATH = ROOT / "singbox-rule-ui" / "app.py"


def load_app(workdir):
    spec = importlib.util.spec_from_file_location("rule_ui_app", APP_PATH)
    app = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(app)
    app.RULE_DIR = workdir / "custom-rules"
    app.MANAGER_DIR = workdir / "manager"
    app.CONFIG_PATH = workdir / "config.json"
    app.BASE_CONFIG_PATH = app.MANAGER_DIR / "base.json"
    app.NODES_PATH = app.MANAGER_DIR / "nodes.json"
    app.GROUPS_PATH = app.MANAGER_DIR / "groups.json"
    app.BACKUP_DIR = app.MANAGER_DIR / "backups"
    app.TOKEN_FILE = workdir / "rule-ui" / "token"
    # 本测试只验证渲染幂等性；固定运行态监听信息，避免依赖测试机是否有 Linux ip 命令。
    app.default_lan_ip = lambda: "10.20.20.6"
    app.assigned_ipv6_addresses = lambda: []
    return app


def sample_base_config():
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
                {"tag": "local-dns", "type": "udp", "server": "119.29.29.29", "server_port": 53},
                {"tag": "fakeip-dns", "type": "fakeip", "inet4_range": "28.0.0.0/8", "inet6_range": "2001:2::/64"},
            ],
            "rules": [{"inbound": ["dns-in"], "action": "hijack-dns"}],
        },
        "inbounds": [
            {"type": "tproxy", "tag": "tproxy-in", "listen": "::", "listen_port": 9888, "sniff": False},
            {"type": "direct", "tag": "dns-in", "listen": "10.20.20.6", "listen_port": 53},
        ],
        "outbounds": [],
        "route": {
            "auto_detect_interface": True,
            "default_domain_resolver": "remote-dns",
            "rule_set": [],
            "rules": [{"inbound": ["dns-in"], "action": "hijack-dns"}],
            "final": "direct",
        },
        "experimental": {
            "cache_file": {"enabled": True, "store_fakeip": True},
            "clash_api": {"external_controller": "10.20.20.6:9090", "secret": "test", "default_mode": "rule"},
        },
    }


def sample_nodes():
    return [
        {
            "enabled": True,
            "outbound": {
                "type": "hysteria2",
                "tag": "US-HY2",
                "server": "192.0.2.1",
                "server_port": 443,
                "password": "test",
                "tls": {"enabled": True, "server_name": "example.com", "insecure": True},
                "up_mbps": 20,
                "down_mbps": 100,
            },
        },
        {
            "enabled": True,
            "outbound": {
                "type": "vless",
                "tag": "US-VLESS",
                "server": "192.0.2.2",
                "server_port": 443,
                "uuid": "00000000-0000-4000-8000-000000000001",
                "packet_encoding": "xudp",
                "tls": {"enabled": True, "server_name": "example.com", "insecure": True},
            },
        },
    ]


def sample_groups():
    return {
        "proxy": {"default": "Auto", "interrupt_exist_connections": False},
        "auto": {
            "url": "https://www.gstatic.com/generate_204",
            "interval": "30s",
            "tolerance": 50,
            "interrupt_exist_connections": False,
        },
        "direct": {"type": "direct", "tag": "direct"},
        "block": {"type": "block", "tag": "block"},
        "fakeip": {
            "tag": "fakeip-dns",
            "inet4_range": "28.0.0.0/8",
            "inet6_range": "2001:2::/64",
            "block_quic": True,
            "ipv6_enabled": True,
        },
        "dns": {"local": "dnspod"},
        "ddns": {"dns": "local"},
        "telegram": {"capture_ips": True},
    }


def main():
    with tempfile.TemporaryDirectory(prefix="singbox-rule-ui-idempotency-") as temp_name:
        workdir = Path(temp_name)
        app = load_app(workdir)
        for path in (app.RULE_DIR, app.MANAGER_DIR, app.TOKEN_FILE.parent):
            path.mkdir(parents=True, exist_ok=True)
        for name in app.LISTS:
            app.write_json(app.rule_path(name), app.empty_rule_set())
        nodes = sample_nodes()
        groups = sample_groups()
        app.write_json(app.BASE_CONFIG_PATH, sample_base_config())
        app.write_json(app.NODES_PATH, nodes)
        app.write_json(app.GROUPS_PATH, groups)
        normalized_lists = {name: app.read_entries(name) for name in app.LISTS}
        rendered = []
        for _ in range(5):
            config = app.render_config(nodes=nodes, groups=groups, rule_dir=app.RULE_DIR, normalized_lists=normalized_lists)
            app.write_json(app.CONFIG_PATH, config)
            rendered.append(config)
        if any(rendered[0] != item for item in rendered[1:]):
            raise SystemExit("render_config is not idempotent")
        route_rules = len(rendered[-1].get("route", {}).get("rules", []))
        dns_rules = len(rendered[-1].get("dns", {}).get("rules", []))
        udp443_reject = sum(
            1
            for rule in rendered[-1].get("route", {}).get("rules", [])
            if isinstance(rule, dict) and rule.get("network") == "udp" and rule.get("port") == 443 and rule.get("action") == "reject"
        )
        digest = hashlib.sha256(json.dumps(rendered[-1], sort_keys=True).encode()).hexdigest()
        print(f"ok route_rules={route_rules} dns_rules={dns_rules} udp443_reject={udp443_reject} sha256={digest}")


if __name__ == "__main__":
    main()
