# sing-box-reF1nd 魔改版（Ubuntu / Debian · systemd 版）

本仓库是 [singbox-ui-alpine](https://github.com/hanigege/singbox-ui-alpine)（Alpine/OpenRC 版）向 **Ubuntu / Debian + systemd** 的移植版本。核心渲染逻辑、Rule UI、TProxy、回滚校验机制完全一致，只把服务层从 OpenRC 换成 systemd、包管理从 apk 换成 apt，并处理了 Ubuntu/Debian 上 systemd-resolved 占用 53 端口的问题。

## 功能

- 一键安装 `sing-box` 二进制、systemd 服务、TProxy、cron 定时任务和 Web UI
- 默认使用仓库内置并校验过的 reF1nd 增强版 `sing-box v1.14.0-alpha.48-reF1nd` 静态二进制（`amd64`）
- 9091 规则 UI 管理白名单、黑名单、灰名单、DDNS、代理节点、实时连接、日志和运行规则
- 保存前执行 `sing-box check`，失败不覆盖正式配置；规则和主配置使用原子替换
- 重启失败自动回滚上一份可用配置，优先保证正在运行的 `sing-box` 可恢复
- Auto 默认每 30 秒自动测速并重选可用节点，urltest 选中节点变化时中断旧连接
- TProxy 自动检测默认网卡、本机网段和 IPv6 前缀
- 节点服务器 IP 自动加入 TProxy bypass，避免代理链路被透明代理套住
- Telegram 官方 IP 捕获列表支持在线更新和手动校验编辑
- LAN 侧 DNS 指向本机时，sing-box 监听 53 端口处理 DNS 查询，降低 IPv4/IPv6 明文 DNS 泄漏
- 规则更新由系统 `cron`（`/etc/cron.d`）管理，运行状态自愈每 2 分钟检查一次
- `sing-box-gateway-info` 一键查看 9091 访问地址和 Rule UI token

## 支持系统

当前安装器面向 Ubuntu / Debian + systemd：

- Ubuntu 22.04 / 24.04 / 25.04 及衍生版
- Debian 11 / 12 及衍生版
- `x86_64/amd64`（仓库内置 reF1nd 二进制仅提供 amd64）

需要 root 权限，且系统以 systemd 作为 init。Alpine/OpenRC 环境请使用原版仓库 [singbox-ui-alpine](https://github.com/hanigege/singbox-ui-alpine)。

## reF1nd 魔改版 一键安装 {v1.14.0-alpha.48-reF1nd}

提供两个并行的安装入口，按网络环境选一个即可。两个入口走不同的安装脚本，最终效果一致：

```sh
# 入口一：直连 GitHub（推荐，海外或能直连 GitHub raw 的机器）
curl -fsSL https://raw.githubusercontent.com/hanigege/sing-box-ui-ubuntu-debian/main/scripts/quick-install.sh | sh
```

```sh
# 入口二：ghproxy.net 反代（境内或 GitHub 直连不稳定的机器）
# 脚本内置 ghproxy.net、gh-proxy.com、gh.llkk.cc 多级镜像加速和直连回退。
curl -fsSL https://ghproxy.net/https://raw.githubusercontent.com/hanigege/sing-box-ui-ubuntu-debian/main/scripts/quick-install-proxy.sh | sh
```

安装器自动安装 apt 依赖：`curl`、`ca-certificates`、`tar`、`gzip`、`python3`、`nftables`、`iproute2`、`rsync`、`util-linux`、`coreutils`、`cron`、`logrotate`、`iputils-ping`。仓库内置的 `sing-box` 是 reF1nd 增强版 `v1.14.0-alpha.48-reF1nd` 静态二进制。卸载时默认保留 apt 包，避免连带移除系统基础依赖。

如果安装在 Proxmox VE 的 Ubuntu/Debian LXC 里，一键安装只负责容器内的 sing-box、TProxy、systemd 服务和 Rule UI，不会改 PVE 宿主机配置。高并发或高带宽场景建议安装后继续看下面的“Proxmox VE / LXC 可选优化”。

## 53 端口和 DNS

Ubuntu/Debian 默认启用 `systemd-resolved`，它会在 `127.0.0.53:53`（部分版本还有 `127.0.0.54:53`）起 stub listener，占用 sing-box 需要的 53 端口。安装器的处理策略：

- 检查 sing-box 将要监听的 53 地址
- 53 未占用则继续安装
- 已由 sing-box 占用则认为是覆盖安装，继续
- **占用者是 `systemd-resolved` 时：自动记录原状态 → 写入 `/etc/systemd/resolved.conf.d/00-sing-box-gateway.conf` 关闭 `DNSStubListener` → 把 `/etc/resolv.conf` 指向 resolved 汇总的真实上游解析文件**，释放 53 后继续安装
- 占用者是 `dnsmasq`/`bind9`/`unbound`/`adguardhome` 等第三方 DNS 时：停止安装并提示，需先手动释放端口

卸载时会按记录删除 drop-in、还原 `/etc/resolv.conf` 软链并重启 `systemd-resolved`，恢复 stub listener。

客户端 DNS 只有最终进入 sing-box，白名单、黑名单、灰名单、FakeIP 和域名分流规则才会完整生效。实现方式可以是：

- 在客户端手动把 DNS 指向 sing-box 机器的内网 IPv4
- 在前端软路由上把客户端 DNS 转发到 sing-box
- 在前端软路由上劫持客户端 53 端口 DNS 到 sing-box

没有配置真实代理节点前，不建议把客户端 DNS 指向 sing-box，否则国外网站可能解析成 FakeIP 但代理不可用。

## systemd 服务

安装后会创建：

- `/etc/systemd/system/sing-box-tproxy.service`
- `/etc/systemd/system/sing-box.service`
- `/etc/systemd/system/singbox-rule-ui.service`

常用检查命令：

```bash
systemctl status sing-box
systemctl status sing-box-tproxy
systemctl status singbox-rule-ui
systemctl list-unit-files 'sing-box*' 'singbox*'
sing-box-gateway-info
```

服务日志同时进 journald 和文件：

- `/var/log/sing-box-gateway/sing-box.log`
- `/var/log/sing-box-gateway/rule-ui.log`
- `/var/log/sing-box-gateway/rule-update.log`
- `/var/log/sing-box-gateway/runtime-monitor.log`

查看 journald：`journalctl -u sing-box -f`。安装器会写入 `/etc/logrotate.d/sing-box-gateway`，对文件日志按单文件 5M 触发轮转，保留 6 份压缩归档。

## 自动维护

安装器会写入 `/etc/cron.d/sing-box-gateway`：

- 每周日 04:20 更新分流规则
- 每 2 分钟运行 `/usr/local/sbin/monitor-sing-box-runtime`

Rule UI 的维护页可以调整分流规则自动更新周期和执行时间。保存后 UI 会更新 `/etc/cron.d/sing-box-gateway` 中由本项目标记包围的规则更新块（cron.d 格式含用户字段），并 reload `cron`。手动“立即更新分流规则”成功后，也会把下一次自动更新从本次完成时间重新顺延一个周期。这些动作只改变触发计划，不改变 `/usr/local/sbin/update-sing-box-rules-jsdelivr` 更新脚本，也不会修改 sing-box 主配置。

## IPv6 RA

安装器默认不启用 `radvd`，也不会把这台机器广播成 LAN 默认 IPv6 网关。如果目标机之前已经安装并启用了 `radvd`，安装器会在未显式 opt-in 时执行：

```bash
systemctl stop radvd
systemctl disable radvd
```

如果你确实需要让本机广播 IPv6 默认网关，可以自行 `apt-get install radvd`，并在运行安装器、UI 或同步脚本时显式设置：

```bash
SING_BOX_GATEWAY_ENABLE_RADVD=1 /usr/local/sbin/refresh-sing-box-runtime-config
```

生产网络里不建议在多台旁路机上同时启用 RA 广播。一般更稳的做法是：前端软路由继续作为默认网关，只把 FakeIP 网段或指定流量路由到 sing-box 机器。

### PPPoE / RouterOS IPv6 MTU

如果前端软路由通过 PPPoE 拨号，WAN MTU 通常是 `1492`，但 LAN 侧 IPv6 RA 如果不显式广播 MTU，客户端会按以太网默认 `1500` 发送 IPv6。大 TLS ClientHello 或 HTTP/2 请求可能在 PPPoE 出口被 IPv6 分片，部分 CDN/中间网络会丢弃分片，表现为：

- 淘宝、天猫、支付宝等页面主体能打开，但订单、购物车、接口数据或部分图片一直加载
- `ping -6` 正常，普通小页面正常，但某些 HTTPS 接口间歇性超时
- DNS 已经返回真实国内 IPv4/IPv6，不是 FakeIP 或白名单问题

根因修复是在**前端默认 IPv6 网关**上把 LAN RA MTU 设置为实际 WAN MTU。MikroTik RouterOS 示例：

```routeros
/interface/print detail where name~"pppoe|bridge"
/ipv6/nd/print detail
/ipv6/nd/set [find interface=bridge1] mtu=1492
/ipv6/nd/print detail where interface=bridge1
```

如果你的 LAN 接口不是 `bridge1`，请替换成实际接口名；如果 PPPoE MTU 不是 `1492`，请使用 `/interface/print detail` 里 `pppoe-out` 的 `actual-mtu`。改完后，让客户端重新获取 RA：断开/重连 Wi-Fi、重启网卡，或等待下一次 RA。

sing-box 所在的机器本身也是 LAN IPv6 客户端。如果它已经在线并仍显示 `mtu 1500`，可以立即把默认网卡 MTU 调成同一个值来验证：

```bash
ip link show dev eth0
ip link set dev eth0 mtu 1492
curl -6 -m 6 -o /dev/null -w '%{http_code} %{time_total} %{remote_ip}\n' https://h5api.m.taobao.com/
```

安装器会自动探测默认网卡的最优 MTU，并用 systemd oneshot unit（`singbox-mtu.service`）持久化。可用 `SING_BOX_MTU=<值>` 环境变量强制指定。原则是 LAN 客户端看到的 IPv6 MTU 不要大于 PPPoE 出口实际 MTU。

## TProxy 转发模式

默认按“非网关 TProxy + FakeIP 入口”部署：上游路由器继续做默认网关，只把 FakeIP 或灰名单 CIDR 路由到这台机器。安装器和 UI 生成的 `/etc/sysctl.d/99-sing-box-tproxy.conf` 只保留 TProxy/FakeIP 必需参数，例如 `ip_nonlocal_bind`、`rp_filter` 和当前网卡的 IPv6 RA 接收项，不会默认开启 `net.ipv4.ip_forward` 或 IPv6 forwarding。

如果第三方设备的默认网关或明确路由已经指向本机，需要让本机作为代理网关，再显式开启：

```bash
SING_BOX_GATEWAY_ENABLE_FORWARDING=1 systemctl restart sing-box-tproxy
```

如果要持久启用，可以创建 systemd drop-in 写入该环境变量：
`systemctl edit sing-box-tproxy`，加入 `[Service]` 段的 `Environment=SING_BOX_GATEWAY_ENABLE_FORWARDING=1`，再重启服务。这个开关只影响容器内转发类 sysctl。

## 性能优化

安装器会调用 `scripts/sysctl-performance.sh` 写入 `tcp_notsent_lowat` 并在默认出口网卡上尝试附加 `fq` qdisc（用 `singbox-qdisc.service` 持久化，内核不支持时自动跳过）。BBR、缓冲区等更激进的调参默认不捆绑，建议按实际链路手动测试后写入 `/etc/sysctl.d/*.conf`。

## Proxmox VE / LXC 可选优化

这部分只适合 Proxmox VE 宿主机上的 Ubuntu/Debian LXC。它不是一键安装器的一部分，因为 PVE 宿主机和 LXC 配置属于容器外部边界，安装脚本不应该从容器内自动修改宿主机。

> 注意：LXC 容器内 systemd 可写的 sysctl 项受限，部分 `net.*` 全局参数需要在 PVE 宿主机侧统一配置。判断是否在 LXC：`grep -q container=lxc /proc/1/environ && echo LXC`。

### PVE 宿主机网络参数

在 PVE 宿主机上追加或确认 `/etc/sysctl.conf`：

```conf
net.core.default_qdisc = fq
net.ipv4.tcp_congestion_control = bbr
net.core.somaxconn = 32768
net.ipv4.tcp_max_syn_backlog = 16384
net.core.netdev_max_backlog = 65536
net.core.rmem_max = 134217728
net.core.wmem_max = 134217728
net.ipv4.tcp_rmem = 4096 87380 67108864
net.ipv4.tcp_wmem = 4096 65536 67108864
fs.file-max = 2097152
fs.nr_open = 2097152
```

应用并检查：`sysctl -p && sysctl net.ipv4.tcp_congestion_control net.core.default_qdisc`。

### PVE 放宽指定 LXC 的 nofile

```bash
pct list
nano /etc/pve/lxc/<CTID>.conf   # 追加：lxc.prlimit.nofile: 1048576:1048576
pct reboot <CTID>
```

进入 LXC 验证：`cat /proc/$(pidof sing-box)/limits | grep 'Max open files'`，正常应看到 `1048576`。

## 访问入口

安装完成后输出 9091 规则 UI 地址和 Rule UI token。忘记也没关系，在网关机器上运行：

```bash
sing-box-gateway-info
```

默认入口：`http://<网关IP>:9091/`。9090 Clash API 保留给 9091 后端读取连接、日志和运行规则；浏览器日常管理只需要进入 9091，并使用 Rule UI token 登录。

## 一键卸载

已安装机器优先使用本地卸载器：

```bash
/usr/local/bin/sing-box-gateway-uninstall --yes
```

默认卸载会停止并禁用本项目 systemd 服务，清理 TProxy nft/routing 运行规则，移除 `/etc/cron.d/sing-box-gateway`，按安装前记录恢复 `radvd` 和 `systemd-resolved` 状态，并删除本项目安装的 UI、辅助脚本、运行配置、规则缓存和 `/etc/sing-box`。

如果 `/usr/local/bin/sing-box` 是本安装器新增的，默认会删除；如果安装前已经存在，则默认保留。

卸载器默认不删除 apt 依赖包。确实要删除安装器新增依赖时，显式设置：

```bash
SING_BOX_GATEWAY_REMOVE_DEPS=1 /usr/local/bin/sing-box-gateway-uninstall --yes
```

如果没有安装状态记录，但仍确认要删除 `/usr/local/bin/sing-box`，可以使用 purge：

```bash
/usr/local/bin/sing-box-gateway-uninstall --purge --yes
```

## Git 安装

适合想修改脚本或参与开发的用户：

```bash
apt-get update && apt-get install -y git curl ca-certificates
git clone https://github.com/hanigege/sing-box-ui-ubuntu-debian.git
cd sing-box-ui-ubuntu-debian
bash scripts/install.sh
```

本地卸载（交互式确认，静默模式加 `--yes`）：

```bash
bash scripts/install.sh uninstall        # 标准卸载，有确认提示
bash scripts/install.sh uninstall --yes  # 静默卸载
bash scripts/install.sh purge --yes      # 静默强制删除 /usr/local/bin/sing-box
```

## 安全

不要把以下内容提交到公开仓库：节点密码、UUID、Reality public key / short id、UI token、真实服务器 IP、私有域名。本仓库只保存安装逻辑和通用模板，不包含任何可用代理节点或私人配置。
