#!/bin/sh
set -eu

# ⚠️ `curl ... | sh` 的固有缺陷：管道左侧 curl 失败（网络 reset、DNS 污染、
# 反代挂掉）时 sh 读到空输入或半截脚本，仍然退出码 0，用户看到「装完了」但
# 什么都没发生；截断更危险——前半段可能已经改了系统状态。
# 防线一：main 函数包裹全部逻辑，末尾才调用。脚本被截断时 main 定义不完整或
# 调用行缺失，sh 会报语法错/什么都不执行，而不是执行半截安装。
# 防线二：README 推荐先落盘再执行的两步式命令，让 curl 的非零退出码可见。
main() {
REPO="${SING_BOX_GATEWAY_REPO:-hanigege/sing-box-ui-ubuntu-debian}"
REF="${SING_BOX_GATEWAY_REF:-main}"
ACTION="${1:-install}"

if ! command -v curl >/dev/null 2>&1 && ! command -v wget >/dev/null 2>&1; then
  echo "缺少 curl/wget，请先安装 curl：apt-get install -y curl ca-certificates" >&2
  exit 1
fi

if [ "${SING_BOX_GATEWAY_DRY_RUN:-0}" != "1" ] && [ "$(id -u)" -ne 0 ]; then
  echo "请用 root 权限运行，例如：" >&2
  echo "  curl -fsSL https://raw.githubusercontent.com/${REPO}/${REF}/scripts/quick-install.sh | sh" >&2
  exit 1
fi

tmp="$(mktemp -d)"
cleanup() {
  rm -rf "$tmp"
}
trap cleanup EXIT

archive="$tmp/source.tar.gz"
src="$tmp/source"

download_first() {
  output="$1"
  shift
  for url in "$@"; do
    [ -n "$url" ] || continue
    echo "尝试下载: $url"
    # 每个 URL 先 curl 后 wget 双试：curl 存在但因 TLS/ca-certificates 等原因
    # 失败时，仍能回落到 wget(不同实现，可能成功)。用 if 而非 elif——
    # elif 会让「curl 存在但失败」直接跳过 wget，白丢一次重试机会。
    if command -v curl >/dev/null 2>&1; then
      if curl -fL --connect-timeout 10 --max-time 120 "$url" -o "$output"; then
        return 0
      fi
    fi
    if command -v wget >/dev/null 2>&1; then
      if wget -T 120 -O "$output" "$url"; then
        return 0
      fi
    fi
  done
  return 1
}

echo "正在下载 sing-box-ui-ubuntu-debian ${REPO}@${REF}..."
archive_url="https://github.com/${REPO}/archive/refs/heads/${REF}.tar.gz"
download_first "$archive" "$archive_url"
mkdir -p "$src"
tar -xzf "$archive" -C "$src" --strip-components=1

if [ "${SING_BOX_GATEWAY_DRY_RUN:-0}" = "1" ]; then
  test -f "$src/scripts/install.sh"
  test -f "$src/scripts/bootstrap_config.py"
  test -f "$src/scripts/uninstall.sh"
  test -f "$src/systemd/sing-box.service"
  echo "一键安装链路检查通过。"
  echo "安装器位置: $src/scripts/install.sh"
  exit 0
fi

case "$ACTION" in
  install|"")
    target="$src/scripts/install.sh"
    args=""
    ;;
  uninstall|remove)
    target="$src/scripts/uninstall.sh"
    args="--yes"
    ;;
  purge)
    target="$src/scripts/uninstall.sh"
    args="--purge --yes"
    ;;
  *)
    echo "未知操作: $ACTION" >&2
    echo "可用操作: install, uninstall, purge" >&2
    exit 1
    ;;
esac

if [ "$ACTION" = "install" ] || [ -z "$ACTION" ]; then
  export SING_BOX_GATEWAY_ASSUME_DEFAULTS=1
fi

if ! command -v bash >/dev/null 2>&1; then
  if command -v apt-get >/dev/null 2>&1; then
    DEBIAN_FRONTEND=noninteractive apt-get update -qq || true
    DEBIAN_FRONTEND=noninteractive apt-get install -y bash
  else
    echo "缺少 bash，且当前系统没有 apt-get；请在 Ubuntu/Debian 上运行本安装器。" >&2
    exit 1
  fi
fi

# shellcheck disable=SC2086
exec bash "$target" $args
}

# 完整性哨兵：只有脚本被完整读入时才会执行到这一行。
main "$@"
