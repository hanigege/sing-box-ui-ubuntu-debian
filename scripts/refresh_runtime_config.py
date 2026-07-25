#!/usr/bin/env python3
import json
import ipaddress
import os
import subprocess
import sys
import tempfile
from pathlib import Path


CONFIG_PATH = Path("/etc/sing-box/config.json")
APP_DIR = Path("/opt/singbox-rule-ui")
SING_BOX_BIN = Path("/usr/local/bin/sing-box")


def default_lan_ip():
    out = subprocess.check_output(["ip", "-o", "-4", "route", "get", "1.1.1.1"], text=True)
    parts = out.split()
    if "src" not in parts:
        raise RuntimeError("cannot detect LAN IPv4 address")
    return parts[parts.index("src") + 1]


def assigned_ipv6_addresses():
    try:
        out = subprocess.check_output(["ip", "-o", "-6", "addr", "show", "scope", "global"], text=True)
    except Exception:
        return []
    addresses = []
    for line in out.splitlines():
        parts = line.split()
        if "inet6" not in parts:
            continue
        value = parts[parts.index("inet6") + 1].split("/", 1)[0]
        try:
            addresses.append(ipaddress.IPv6Address(value))
        except ValueError:
            continue
    return addresses


def preferred_ipv6_listener(lan_ip):
    addresses = assigned_ipv6_addresses()
    if not addresses:
        return ""
    expected_candidates = []
    try:
        last_octet = int(ipaddress.IPv4Address(lan_ip).packed[-1])
        suffix = str(last_octet)
        expected_candidates = [
            ipaddress.IPv6Address(f"fd88::{suffix}{suffix}"),
            ipaddress.IPv6Address(f"fd88::{suffix * 4}") if len(suffix) == 1 else None,
        ]
    except Exception:
        expected_candidates = []
    for expected in expected_candidates:
        if expected and expected in addresses:
            return str(expected)

    def score(address):
        text = str(address)
        if address.is_private and "ff:fe" not in text:
            return 0
        if address.is_private:
            return 1
        return 2

    return str(sorted(addresses, key=score)[0])


def remove_inbound_tag(config, tag):
    for section in ("dns", "route"):
        for rule in config.get(section, {}).get("rules", []) or []:
            if not isinstance(rule, dict):
                continue
            inbound = rule.get("inbound")
            if isinstance(inbound, list) and tag in inbound:
                inbound[:] = [item for item in inbound if item != tag]
                if len(inbound) == 1:
                    rule["inbound"] = inbound[0]
            elif inbound == tag:
                rule.pop("inbound", None)


def add_inbound_tag(config, tag):
    for section in ("dns", "route"):
        for rule in config.get(section, {}).get("rules", []) or []:
            if not isinstance(rule, dict):
                continue
            inbound = rule.get("inbound")
            if inbound is None:
                continue
            if isinstance(inbound, list):
                if tag not in inbound:
                    inbound.append(tag)
            elif inbound == "dns-in":
                rule["inbound"] = ["dns-in", tag]


def render_managed_config():
    sys.path.insert(0, str(APP_DIR))
    from app import RULE_DIR, load_groups, load_nodes, render_config

    return render_config(nodes=load_nodes(), groups=load_groups(), rule_dir=RULE_DIR)


def apply_runtime_listeners(config, lan_ip, ipv6_listen):
    changed = False
    inbounds = config.get("inbounds", []) or []
    kept_inbounds = []
    for inbound in inbounds:
        if not isinstance(inbound, dict):
            kept_inbounds.append(inbound)
            continue
        if inbound.get("tag") == "dns-in" and inbound.get("listen") != lan_ip:
            inbound["listen"] = lan_ip
            changed = True
        if inbound.get("tag") == "dns-in-v6":
            if ipv6_listen:
                if inbound.get("listen") != ipv6_listen:
                    inbound["listen"] = ipv6_listen
                    changed = True
            else:
                remove_inbound_tag(config, "dns-in-v6")
                changed = True
                continue
        kept_inbounds.append(inbound)
    if kept_inbounds != inbounds:
        config["inbounds"] = kept_inbounds
    if ipv6_listen and not any(isinstance(item, dict) and item.get("tag") == "dns-in-v6" for item in kept_inbounds):
        config.setdefault("inbounds", []).append({"type": "direct", "tag": "dns-in-v6", "listen": ipv6_listen, "listen_port": 53})
        add_inbound_tag(config, "dns-in-v6")
        changed = True

    clash = config.setdefault("experimental", {}).setdefault("clash_api", {})
    controller = f"{lan_ip}:9090"
    if clash.get("external_controller") != controller:
        clash["external_controller"] = controller
        changed = True
    return changed


def atomic_write_text(path, text):
    # 这是服务启动前的运行态刷新步骤，正式配置必须原子替换，避免启动前写坏 config.json。
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))
    temp_path = Path(temp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, path)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def check_rendered_config(path, text):
    # 运行态刷新同样遵守“先 check 再落盘”：正式 config.json 只有在 sing-box 能解析时才会被替换。
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.check-", suffix=".tmp", dir=str(path.parent))
    temp_path = Path(temp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        result = subprocess.run([str(SING_BOX_BIN), "check", "-c", str(temp_path)], text=True, capture_output=True, timeout=30)
        if result.returncode != 0:
            message = (result.stderr or result.stdout or "sing-box check failed").strip()
            raise RuntimeError(message)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def main():
    if not CONFIG_PATH.exists():
        return 0
    lan_ip = default_lan_ip()
    ipv6_listen = preferred_ipv6_listener(lan_ip)
    previous = CONFIG_PATH.read_text(encoding="utf-8")
    config = render_managed_config()
    listener_changed = apply_runtime_listeners(config, lan_ip, ipv6_listen)
    rendered = json.dumps(config, indent=2, ensure_ascii=False) + "\n"
    if rendered != previous:
        check_rendered_config(CONFIG_PATH, rendered)
        atomic_write_text(CONFIG_PATH, rendered)
        print(f"Rendered sing-box config and updated listeners for {lan_ip}.")
    elif listener_changed:
        print(f"Updated sing-box listeners for {lan_ip}.")
    else:
        print(f"sing-box config already rendered and listeners match {lan_ip}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
