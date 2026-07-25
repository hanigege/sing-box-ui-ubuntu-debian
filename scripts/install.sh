#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SING_BOX_BUNDLED_VERSION="${SING_BOX_BUNDLED_VERSION:-1.14.0-alpha.48-reF1nd}"
SING_BOX_ARCH="${SING_BOX_ARCH:-auto}"
INSTALL_DIR="/opt/singbox-rule-ui"
CONFIG_DIR="/etc/sing-box"
MANAGER_DIR="$CONFIG_DIR/manager"
RULE_DIR="$CONFIG_DIR/custom-rules"
INSTALL_STATE_FILE="$MANAGER_DIR/install-state"
RADVD_STATE_FILE="$MANAGER_DIR/radvd-state.before-sing-box"
RESOLVED_STATE_FILE="$MANAGER_DIR/resolved-state.before-sing-box"
LOG_DIR="/var/log/sing-box-gateway"
LOGROTATE_CONFIG="/etc/logrotate.d/sing-box-gateway"
SYSTEMD_DIR="/etc/systemd/system"
# Debian/Ubuntu 用 /etc/cron.d 片段代替 Alpine 的 /etc/crontabs/root；每行多一个用户字段。
CRON_FILE="/etc/cron.d/sing-box-gateway"
CRON_USER="root"
RESOLVED_DROPIN_DIR="/etc/systemd/resolved.conf.d"
RESOLVED_DROPIN="$RESOLVED_DROPIN_DIR/00-sing-box-gateway.conf"
# apt 依赖：iputils-ping 提供 ping（MTU 探测），cron 提供 /etc/cron.d 调度，其余对齐 Alpine 版功能集。
DEB_PACKAGES=(curl ca-certificates tar gzip python3 nftables iproute2 rsync util-linux coreutils cron logrotate iputils-ping)

need_root() {
  if [ "$(id -u)" -ne 0 ]; then
    echo "Please run as root." >&2
    exit 1
  fi
}

require_debian_family() {
  # 支持 Ubuntu 与 Debian（含衍生版）；依据 os-release 的 ID/ID_LIKE 判定，再确认 systemd 与 apt 齐全。
  local id="" id_like=""
  if [ -r /etc/os-release ]; then
    id="$(. /etc/os-release 2>/dev/null; echo "${ID:-}")"
    id_like="$(. /etc/os-release 2>/dev/null; echo "${ID_LIKE:-}")"
  fi
  case " $id $id_like " in
    *" debian "*|*" ubuntu "*) : ;;
    *)
      echo "This repository is the Ubuntu/Debian (systemd) build. Please run it on Ubuntu or Debian." >&2
      exit 1
      ;;
  esac
  if ! command -v apt-get >/dev/null 2>&1; then
    echo "apt-get is required (Debian/Ubuntu)." >&2
    exit 1
  fi
  if ! command -v systemctl >/dev/null 2>&1 || [ ! -d /run/systemd/system ]; then
    echo "systemd is required. This host does not appear to be running systemd as init." >&2
    exit 1
  fi
}

state_get() {
  local key="$1"
  [ -r "$INSTALL_STATE_FILE" ] || return 0
  awk -F= -v key="$key" '$1 == key { value = substr($0, length(key) + 2) } END { print value }' "$INSTALL_STATE_FILE"
}

state_set() {
  local key="$1" value="$2" tmp
  mkdir -p "$MANAGER_DIR"
  tmp="$(mktemp)"
  if [ -r "$INSTALL_STATE_FILE" ]; then
    awk -F= -v key="$key" '$1 != key { print }' "$INSTALL_STATE_FILE" > "$tmp"
  fi
  printf "%s=%s\n" "$key" "$value" >> "$tmp"
  install -m 0600 "$tmp" "$INSTALL_STATE_FILE"
  rm -f "$tmp"
}

pkg_installed() {
  dpkg-query -W -f='${Status}' "$1" 2>/dev/null | grep -q "install ok installed"
}

record_preinstall_state() {
  mkdir -p "$MANAGER_DIR"
  if [ "$(state_get state_version)" != "2" ]; then
    : > "$INSTALL_STATE_FILE"
    chmod 0600 "$INSTALL_STATE_FILE"
    state_set state_version 2
    state_set init_system systemd
    if [ -e /usr/local/bin/sing-box ]; then
      state_set sing_box_binary preexisting
    else
      state_set sing_box_binary absent
    fi
    for package in "${DEB_PACKAGES[@]}"; do
      if pkg_installed "$package"; then
        state_set "pkg_${package}" preexisting
      else
        state_set "pkg_${package}" absent
      fi
    done
    # 记录 53 端口现场，卸载时据此决定是否恢复 systemd-resolved stub listener。
    state_set port53_owners "$(port53_owners 2>/dev/null || true)"
  fi
}

install_packages() {
  local missing=() package
  for package in "${DEB_PACKAGES[@]}"; do
    if ! pkg_installed "$package"; then
      missing+=("$package")
    fi
  done
  if [ "${#missing[@]}" -eq 0 ]; then
    echo "Debian/Ubuntu dependencies already installed."
    return
  fi
  # 覆盖安装不能因外部索引临时 TLS/网络失败而中断；仅在确有缺失依赖时联网安装。
  echo "Installing missing packages: ${missing[*]}"
  DEBIAN_FRONTEND=noninteractive apt-get update -qq || true
  DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends "${missing[@]}"
}

enable_radvd_requested() {
  case "${SING_BOX_GATEWAY_ENABLE_RADVD:-${RULE_UI_ENABLE_RADVD:-0}}" in
    1|true|TRUE|yes|YES|on|ON) return 0 ;;
    *) return 1 ;;
  esac
}

unit_exists() {
  systemctl list-unit-files "$1.service" >/dev/null 2>&1 && \
    systemctl cat "$1.service" >/dev/null 2>&1
}

unit_enabled() {
  systemctl is-enabled "$1" >/dev/null 2>&1
}

unit_active() {
  systemctl is-active "$1" >/dev/null 2>&1
}

disable_unrequested_radvd() {
  if enable_radvd_requested; then
    return
  fi
  if unit_exists radvd; then
    if [ ! -e "$RADVD_STATE_FILE" ]; then
      {
        if unit_enabled radvd; then
          printf "enabled=enabled\n"
        else
          printf "enabled=disabled\n"
        fi
        printf "active=%s\n" "$(unit_active radvd && echo active || echo inactive)"
      } > "$RADVD_STATE_FILE"
    fi
    # 旁路网关默认不广播 IPv6 RA，避免本机抢走上游路由器的默认网关角色。
    systemctl stop radvd >/dev/null 2>&1 || true
    systemctl disable radvd >/dev/null 2>&1 || true
    echo "IPv6 router advertisement is disabled by default; radvd was stopped and disabled."
  fi
}

detect_arch() {
  local arch="${1:-${SING_BOX_ARCH}}"
  if [ "$arch" = "auto" ] || [ -z "$arch" ]; then
    arch="$(uname -m)"
  fi
  case "$arch" in
    x86_64|amd64) echo "amd64" ;;
    aarch64|arm64) echo "Unsupported architecture: $arch — reF1nd binary only available for amd64. See third_party/sing-box/ for available builds." >&2; exit 1 ;;
    *) echo "Unsupported architecture: $arch" >&2; exit 1 ;;
  esac
}

choose_sing_box_runtime() {
  # 安装阶段不读取终端输入；架构保持 auto，由 uname -m 自动选择仓库内固定版本包。
  SING_BOX_ARCH="${SING_BOX_ARCH:-auto}"
  echo "sing-box binary: bundled ${SING_BOX_BUNDLED_VERSION} (repository-tested, arch: $(detect_arch))"
}

install_sing_box() {
  local arch singbox_dir binary tmp current_version backup
  arch="$(detect_arch)"
  singbox_dir="$PROJECT_DIR/third_party/sing-box/v${SING_BOX_BUNDLED_VERSION}"
  binary="$singbox_dir/sing-box-ref1nd-linux-${arch}"
  if [ ! -r "$binary" ]; then
    echo "Bundled reF1nd sing-box binary not found: $binary" >&2
    exit 1
  fi
  tmp="$(mktemp -d)"
  trap "rm -rf '$tmp'" EXIT
  if command -v /usr/local/bin/sing-box >/dev/null 2>&1; then
    current_version="$(/usr/local/bin/sing-box version 2>/dev/null | head -n 1 || true)"
    if [ -n "$current_version" ] && printf "%s" "$current_version" | grep -q "$SING_BOX_BUNDLED_VERSION"; then
      echo "sing-box already installed: $current_version"
      state_set sing_box_binary installed
      state_set sing_box_bundled_version "$SING_BOX_BUNDLED_VERSION"
      return
    fi
    backup="/usr/local/bin/sing-box.bak-gateway-$(date +%Y%m%d-%H%M%S)"
    cp -a /usr/local/bin/sing-box "$backup"
    echo "Backed up existing sing-box to $backup"
    state_set sing_box_binary replaced
    state_set sing_box_binary_backup "$backup"
  else
    state_set sing_box_binary installed
  fi
  echo "Installing bundled reF1nd sing-box ${SING_BOX_BUNDLED_VERSION} (${arch})"
  install -m 0755 "$binary" /usr/local/bin/sing-box
  state_set sing_box_bundled_version "$SING_BOX_BUNDLED_VERSION"
}

install_files() {
  mkdir -p "$INSTALL_DIR" "$CONFIG_DIR" "$MANAGER_DIR" "$RULE_DIR" "$LOG_DIR" "$SYSTEMD_DIR" /usr/local/bin /usr/local/sbin
  rsync -a --delete "$PROJECT_DIR/singbox-rule-ui/" "$INSTALL_DIR/"
  install -m 0755 "$PROJECT_DIR/scripts/sing-box-gateway-info" /usr/local/bin/sing-box-gateway-info
  install -m 0755 "$PROJECT_DIR/scripts/uninstall.sh" /usr/local/bin/sing-box-gateway-uninstall
  install -m 0755 "$PROJECT_DIR/scripts/refresh_runtime_config.py" /usr/local/sbin/refresh-sing-box-runtime-config
  install -m 0755 "$PROJECT_DIR/scripts/monitor_runtime.py" /usr/local/sbin/monitor-sing-box-runtime
  install -m 0755 "$PROJECT_DIR/scripts/update-sing-box-rules-jsdelivr" /usr/local/sbin/update-sing-box-rules-jsdelivr
  install -m 0755 "$PROJECT_DIR/scripts/sync_tproxy_setup.py" /usr/local/sbin/refresh-sing-box-tproxy-setup
  install -m 0644 "$PROJECT_DIR/systemd/sing-box.service" "$SYSTEMD_DIR/sing-box.service"
  install -m 0644 "$PROJECT_DIR/systemd/sing-box-tproxy.service" "$SYSTEMD_DIR/sing-box-tproxy.service"
  install -m 0644 "$PROJECT_DIR/systemd/singbox-rule-ui.service" "$SYSTEMD_DIR/singbox-rule-ui.service"
  # systemd 需要 daemon-reload 才能识别新/改动的 unit 文件。
  systemctl daemon-reload
}

install_logrotate_config() {
  mkdir -p "$(dirname "$LOGROTATE_CONFIG")"
  # append: 日志和 crontab 都会长期追加写入；用 copytruncate 让重启服务也能收敛日志大小。
  cat > "$LOGROTATE_CONFIG" <<'EOF'
/var/log/sing-box-gateway/*.log {
    size 5M
    rotate 6
    missingok
    notifempty
    compress
    delaycompress
    copytruncate
    create 0640 root root
}
EOF
  chmod 0644 "$LOGROTATE_CONFIG"
}

bootstrap_config() {
  python3 "$PROJECT_DIR/scripts/bootstrap_config.py"
}

install_initial_rules() {
  RULE_UPDATE_RESTART=0 RULE_UPDATE_LOCK_WAIT="${RULE_UPDATE_LOCK_WAIT:-300}" /usr/local/sbin/update-sing-box-rules-jsdelivr || true
  verify_required_rules || true
}

verify_required_rules() {
  local missing=0 path
  for path in \
    /etc/sing-box/rules/geosite/speedtest.srs \
    /etc/sing-box/rules/geosite/telegram.srs \
    /etc/sing-box/rules/geosite/geolocation-!cn.srs \
    /etc/sing-box/rules/geosite/cn.srs \
    /etc/sing-box/rules/geosite/icloud@cn.srs \
    /etc/sing-box/rules/geosite/apple@cn.srs \
    /etc/sing-box/rules/geosite/geolocation-cn.srs \
    /etc/sing-box/rules/geoip/cn.srs \
    /etc/sing-box/rules/geoip/telegram.srs; do
    if [ ! -s "$path" ]; then
      echo "WARN: missing rule file: $path — will retry via cron" >&2
      missing=1
    fi
  done
  if [ "$missing" -ne 0 ]; then
    echo "WARN: some rule files are missing; cron will retry the update. Services are still being enabled." >&2
  fi
  return 0
}

port53_conflicts() {
  python3 - <<'PY'
import ipaddress
import json
import re
import subprocess
from pathlib import Path

config = json.loads(Path("/etc/sing-box/config.json").read_text(encoding="utf-8"))
targets = set()
for inbound in config.get("inbounds", []) or []:
    if isinstance(inbound, dict) and inbound.get("listen_port") == 53:
        listen = str(inbound.get("listen") or "").strip()
        if listen:
            targets.add(listen)

if not targets:
    raise SystemExit(0)

def normalize(address):
    address = address.strip("[]")
    if "%" in address:
        address = address.split("%", 1)[0]
    try:
        return str(ipaddress.ip_address(address))
    except ValueError:
        return address

targets = {normalize(item) for item in targets}
wildcards = {"0.0.0.0", "::", "*"}
conflicts = set()
for command in (["ss", "-H", "-lunp", "sport = :53"], ["ss", "-H", "-ltnp", "sport = :53"]):
    result = subprocess.run(command, text=True, capture_output=True)
    for line in result.stdout.splitlines():
        owner_match = re.search(r'users:\(\("([^"]+)"', line)
        owner = owner_match.group(1) if owner_match else "unknown"
        pid_match = re.search(r"pid=(\d+)", line)
        pid = pid_match.group(1) if pid_match else ""
        cmdline = ""
        if pid:
            try:
                cmdline = Path(f"/proc/{pid}/cmdline").read_bytes().replace(b"\0", b" ").decode("utf-8", "replace")
            except OSError:
                cmdline = ""
        if owner == "sing-box" or "/usr/local/bin/sing-box" in cmdline or " sing-box run " in cmdline:
            continue
        parts = line.split()
        if len(parts) < 5:
            continue
        local = parts[4]
        if local.startswith("["):
            address = local.rsplit("]:", 1)[0].lstrip("[")
        else:
            address = local.rsplit(":", 1)[0]
        address = normalize(address)
        if address in wildcards or address in targets:
            conflicts.add(owner)

if conflicts:
    print(",".join(sorted(conflicts)))
PY
}

port53_owners() {
  python3 - <<'PY'
import re
import subprocess
from pathlib import Path

owners = set()
result = subprocess.run(["ss", "-H", "-ltnup", "sport = :53"], text=True, capture_output=True)
for line in result.stdout.splitlines():
    owner_match = re.search(r'users:\(\("([^"]+)"', line)
    owner = owner_match.group(1) if owner_match else "unknown"
    pid_match = re.search(r"pid=(\d+)", line)
    pid = pid_match.group(1) if pid_match else ""
    if pid:
        try:
            cmdline = Path(f"/proc/{pid}/cmdline").read_bytes().replace(b"\0", b" ").decode("utf-8", "replace")
            if "/usr/local/bin/sing-box" in cmdline or " sing-box run " in cmdline:
                owner = "sing-box"
        except OSError:
            pass
    owners.add(owner)
print(",".join(sorted(owners)))
PY
}

disable_systemd_resolved_stub() {
  # Ubuntu/Debian 默认 systemd-resolved 在 127.0.0.53:53 起 stub listener，会占用 sing-box 的 DNS 入站。
  # 处理策略：记录原状态 → 关闭 DNSStubListener → 把 /etc/resolv.conf 指向 resolved 的真实上游解析文件。
  # 卸载时据 resolved-state 恢复。仅在 resolved 确实活跃且占用 53 时执行。
  if ! unit_active systemd-resolved; then
    return 1
  fi
  if [ ! -e "$RESOLVED_STATE_FILE" ]; then
    {
      printf "stub_listener_was=%s\n" "$(grep -E '^\s*DNSStubListener=' /etc/systemd/resolved.conf 2>/dev/null | tail -1 | sed 's/.*=//' | tr -d ' ' || true)"
      if [ -L /etc/resolv.conf ]; then
        printf "resolv_conf_type=symlink\n"
        printf "resolv_conf_target=%s\n" "$(readlink /etc/resolv.conf)"
      elif [ -e /etc/resolv.conf ]; then
        printf "resolv_conf_type=file\n"
      else
        printf "resolv_conf_type=absent\n"
      fi
    } > "$RESOLVED_STATE_FILE"
    chmod 0600 "$RESOLVED_STATE_FILE"
  fi
  mkdir -p "$RESOLVED_DROPIN_DIR"
  cat > "$RESOLVED_DROPIN" <<'EOF'
# Managed by sing-box-gateway-ui installer: sing-box needs :53 for its DNS inbound.
# Disabling the stub listener frees 127.0.0.53:53. Removed on uninstall.
[Resolve]
DNSStubListener=no
EOF
  chmod 0644 "$RESOLVED_DROPIN"
  systemctl restart systemd-resolved >/dev/null 2>&1 || true
  # 关闭 stub 后 /etc/resolv.conf 若仍指向 stub-resolv.conf，本机自身解析会断；改指向 resolved 汇总的真实上游。
  if [ -e /run/systemd/resolve/resolv.conf ]; then
    ln -sf /run/systemd/resolve/resolv.conf /etc/resolv.conf
    echo "systemd-resolved stub listener disabled; /etc/resolv.conf now points to upstream (via resolved)."
  else
    echo "systemd-resolved stub listener disabled." 
  fi
  return 0
}

ensure_dns_port_available() {
  echo "正在检查 53 端口，确保 sing-box DNS 可以启动..."
  all_owners="$(port53_owners)"
  if [ -z "$all_owners" ]; then
    echo "53 端口当前未被占用。"
  else
    echo "53 端口当前占用进程: $all_owners"
  fi
  owner="$(port53_conflicts)"
  if [ -z "$owner" ]; then
    echo "53 端口检查通过。"
    return
  fi
  if printf "%s" "$owner" | grep -q "sing-box"; then
    echo "53 端口已由 sing-box 使用，继续安装。"
    return
  fi
  # Ubuntu/Debian 上最常见的占用者就是 systemd-resolved；自动关闭它的 stub listener 释放 53。
  if printf "%s" "$owner" | grep -q "systemd-resolve"; then
    echo "检测到 systemd-resolved 占用 53，正在关闭其 stub listener..."
    if disable_systemd_resolved_stub; then
      sleep 1
      owner="$(port53_conflicts)"
      if [ -z "$owner" ] || printf "%s" "$owner" | grep -q "sing-box"; then
        echo "53 端口已释放，检查通过。"
        return
      fi
    fi
  fi
  echo "53 端口仍被占用: $owner" >&2
  echo "请先停止占用 53 的服务（如 dnsmasq/bind9），或调整它的监听端口；否则重启后仍会再次抢占 53。" >&2
  exit 1
}

install_tproxy_setup() {
  python3 "$PROJECT_DIR/scripts/sync_tproxy_setup.py"
}

install_cron_jobs() {
  mkdir -p "$(dirname "$CRON_FILE")"
  # Debian/Ubuntu 用 /etc/cron.d 片段：每行含用户字段。UI 改计划时只重写规则更新块，监控块由本函数固定写入。
  cat > "$CRON_FILE" <<EOF
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
# BEGIN sing-box-gateway-ui rule update
# UI 只调整规则自动更新的 cron 触发时间；执行脚本保持仓库内受控路径。
20 4 * * 0 $CRON_USER /usr/local/sbin/update-sing-box-rules-jsdelivr >> /var/log/sing-box-gateway/rule-update.log 2>&1
# END sing-box-gateway-ui rule update
# BEGIN sing-box-gateway-ui runtime monitor
*/2 * * * * $CRON_USER /usr/local/sbin/monitor-sing-box-runtime >> /var/log/sing-box-gateway/runtime-monitor.log 2>&1
# END sing-box-gateway-ui runtime monitor
EOF
  chmod 0644 "$CRON_FILE"
  # cron 每分钟扫描 /etc/cron.d，确保 cron 已启用并在运行。
  systemctl enable cron >/dev/null 2>&1 || true
  systemctl restart cron >/dev/null 2>&1 || systemctl start cron >/dev/null 2>&1 || true
}

enable_services() {
  systemctl enable sing-box-tproxy >/dev/null 2>&1 || true
  systemctl enable sing-box >/dev/null 2>&1 || true
  systemctl enable singbox-rule-ui >/dev/null 2>&1 || true
  # 覆盖安装后显式重启，确保新 unit 和新二进制立即生效。启动顺序由 unit 依赖控制。
  restart_systemd_service sing-box-tproxy
  restart_systemd_service sing-box
  restart_systemd_service singbox-rule-ui
}

refresh_tproxy_after_start() {
  # 安装阶段已生成 TProxy 脚本和 sysctl；这里仅重启确认服务状态，避免新机空刷新留下 .bak 垃圾。
  restart_systemd_service sing-box-tproxy
}

restart_systemd_service() {
  local service="$1"
  # 覆盖安装时旧进程可能刚退出触发 start-limit；先清 failed 状态再重启。
  systemctl reset-failed "$service" >/dev/null 2>&1 || true
  if systemctl restart "$service"; then
    return 0
  fi
  systemctl stop "$service" >/dev/null 2>&1 || true
  sleep 1
  systemctl reset-failed "$service" >/dev/null 2>&1 || true
  systemctl start "$service" || true
  if systemctl is-active "$service" >/dev/null 2>&1; then
    return 0
  fi
  echo "Failed to start systemd service: $service" >&2
  return 1
}

detect_optimal_mtu() {
  local gw="$1"
  # Probe path MTU to gateway with DF bit (requires iputils ping)
  for mtu in 1500 1492 1464 1440 1400; do
    if ping -c 1 -M do -s "$((mtu - 28))" -W 2 "$gw" >/dev/null 2>&1; then
      echo "$mtu"
      return 0
    fi
  done
  echo "1500"  # fallback
}

ensure_mtu_standard() {
  local iface current detected mtu_unit
  iface="$(ip -4 route show default 2>/dev/null | awk '/default/ { print $5; exit }')"
  [ -z "$iface" ] && { echo "No default route — skip MTU adjustment."; return 0; }
  current="$(cat "/sys/class/net/$iface/mtu" 2>/dev/null || echo "1500")"

  if [ -n "${SING_BOX_MTU:-}" ]; then
    detected="$SING_BOX_MTU"
    echo "Using SING_BOX_MTU=$detected (from environment)."
  elif [ "$current" -gt 1500 ]; then
    echo "Detected $iface MTU=$current (unusually high) — probing optimal MTU..."
    detected="$(detect_optimal_mtu "$(ip -4 route show default | awk '/default/ { print $3; exit }')")"
  elif command -v ping >/dev/null && ping -c 1 -M do -s 1472 -W 2 "$(ip -4 route show default | awk '/default/ { print $3; exit }')" >/dev/null 2>&1; then
    echo "$iface MTU $current — path MTU 1500 validated, no change needed."
    return 0
  else
    echo "$iface MTU $current — probing path MTU (likely PPPoE)..."
    detected="$(detect_optimal_mtu "$(ip -4 route show default | awk '/default/ { print $3; exit }')")"
  fi

  [ "$current" = "$detected" ] && { echo "$iface MTU already $detected — no change needed."; return 0; }

  echo "Adjusting $iface MTU: $current → $detected"
  if ip link set dev "$iface" mtu "$detected" 2>/dev/null; then
    echo "  MTU adjusted immediately."
  else
    echo "  WARN: could not adjust MTU immediately (will retry at boot)." >&2
  fi
  # 用 systemd oneshot unit 持久化 MTU（替代 Alpine 的 /etc/local.d）。
  mtu_unit="$SYSTEMD_DIR/singbox-mtu.service"
  cat > "$mtu_unit" <<UNITEOF
[Unit]
Description=sing-box gateway: set $iface MTU to $detected
After=network-online.target
Wants=network-online.target
Before=sing-box-tproxy.service sing-box.service

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/sbin/ip link set dev $iface mtu $detected

[Install]
WantedBy=multi-user.target
UNITEOF
  systemctl daemon-reload
  systemctl enable singbox-mtu.service >/dev/null 2>&1 || true
  echo "  Persisted via singbox-mtu.service (applied at boot)."
}

setup_performance_qdisc() {
  # 复用 sysctl-performance.sh 的 systemd 分支：tcp_notsent_lowat + fq qdisc + 持久化 unit。
  bash "$PROJECT_DIR/scripts/sysctl-performance.sh" || echo "WARN: performance qdisc setup had issues (non-fatal)." >&2
}

pre_upgrade_cleanup() {
  # 停止旧服务、清理旧文件，确保新版本文件覆盖不受残留影响。
  # 原则：不炸网络（不删 nftables/路由）、不阻断安装（全部 || true）。
  echo "Stopping existing services for clean upgrade..."
  for s in singbox-rule-ui sing-box sing-box-tproxy; do
    systemctl stop "$s" >/dev/null 2>&1 || true
    systemctl reset-failed "$s" >/dev/null 2>&1 || true
  done
  # 移除旧版 systemd unit（install_files 会重新装新的），兼容早期可能残留的 OpenRC init 脚本。
  rm -f "$SYSTEMD_DIR/sing-box.service" "$SYSTEMD_DIR/sing-box-tproxy.service" "$SYSTEMD_DIR/singbox-rule-ui.service"
  rm -f /etc/init.d/sing-box /etc/init.d/sing-box-tproxy /etc/init.d/singbox-rule-ui
  rm -f /etc/local.d/set-mtu-*.start
  rm -f /etc/sysctl.d/99-sing-box-tproxy.conf "$LOGROTATE_CONFIG"
  systemctl daemon-reload >/dev/null 2>&1 || true
  echo "Cleanup done."
}

main() {
  case "${1:-install}" in
    install|"") ;;
    uninstall|remove)
      exec bash "$PROJECT_DIR/scripts/uninstall.sh" "${@:2}"
      ;;
    purge)
      exec bash "$PROJECT_DIR/scripts/uninstall.sh" --purge "${@:2}"
      ;;
    *)
      echo "Unknown action: $1" >&2
      echo "Usage: sudo bash scripts/install.sh [install|uninstall|purge]" >&2
      exit 1
      ;;
  esac
  need_root
  require_debian_family
  record_preinstall_state
  choose_sing_box_runtime
  install_packages
  pre_upgrade_cleanup
  install_files
  install_logrotate_config
  bootstrap_config
  install_sing_box
  install_initial_rules
  disable_unrequested_radvd
  install_tproxy_setup
  ensure_dns_port_available
  /usr/local/bin/sing-box check -c /etc/sing-box/config.json || echo "WARN: config check had issues (likely missing rule files); cron will retry the update." >&2
  install_cron_jobs
  enable_services
  refresh_tproxy_after_start
  ensure_mtu_standard
  setup_performance_qdisc
  echo
  echo "Installed on Ubuntu/Debian (systemd)."
  echo "Host resolver: if systemd-resolved held :53, its stub listener was disabled and /etc/resolv.conf repointed to upstream."
  echo "Interface MTU was auto-detected; set via SING_BOX_MTU env var to override."
  sing-box-gateway-info
}

main "$@"
