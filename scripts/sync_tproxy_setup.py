#!/usr/bin/env python3
import os
import sys
import tempfile
from pathlib import Path


APP_DIR = Path("/opt/singbox-rule-ui")


def main():
    sys.path.insert(0, str(APP_DIR))
    from app import TPROXY_SCRIPT, TPROXY_SYSCTL, load_groups, load_nodes, render_radvd_conf, render_tproxy_script, render_tproxy_sysctl, run_command, sync_radvd, tproxy_bypass_sets
    enable_radvd = os.environ.get("SING_BOX_GATEWAY_ENABLE_RADVD", os.environ.get("RULE_UI_ENABLE_RADVD", "0")).lower() in ("1", "true", "yes", "on")

    nodes = load_nodes()
    groups = load_groups()
    sets = tproxy_bypass_sets(nodes=nodes, groups=groups)
    script = render_tproxy_script(nodes=nodes, groups=groups)

    with tempfile.TemporaryDirectory(prefix="tproxy-install-") as temp_name:
        temp_dir = Path(temp_name)
        script_path = temp_dir / "sing-box-tproxy-setup"
        sysctl_path = temp_dir / "99-sing-box-tproxy.conf"
        script_path.write_text(script, encoding="utf-8")
        script_path.chmod(0o755)
        sysctl_path.write_text(render_tproxy_sysctl(sets["interface"]), encoding="utf-8")
        radvd_conf = render_radvd_conf(sets["interface"]) if enable_radvd else ""
        check = run_command(["bash", "-n", str(script_path)], timeout=8)
        if check["code"] != 0:
            sys.stderr.write(check["stderr"] or check["stdout"] or "TProxy script syntax check failed\n")
            return check["code"] or 1
        TPROXY_SCRIPT.parent.mkdir(parents=True, exist_ok=True)
        TPROXY_SYSCTL.parent.mkdir(parents=True, exist_ok=True)
        TPROXY_SCRIPT.write_text(script_path.read_text(encoding="utf-8"), encoding="utf-8")
        TPROXY_SCRIPT.chmod(0o755)
        TPROXY_SYSCTL.write_text(sysctl_path.read_text(encoding="utf-8"), encoding="utf-8")

    print(f"TProxy setup installed for interface {sets['interface']}.")
    if radvd_conf:
        radvd = sync_radvd(sets["interface"])
        if radvd.get("code") != 0:
            sys.stderr.write(radvd.get("stderr") or radvd.get("stdout") or "radvd sync failed\n")
            return radvd.get("code") or 1
        print("IPv6 router advertisement enabled for LAN clients.")
    else:
        print("IPv6 router advertisement is disabled by default.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
