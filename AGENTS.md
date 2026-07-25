# 维护约束

本仓库是 **Ubuntu/Debian + systemd** 环境下的 sing-box 网关和 Rule UI（从 Alpine/OpenRC 版 singbox-ui-alpine 移植而来）。任何代码修改都必须以生产系统维护标准处理，稳定性优先于功能速度。

## 第一原则

1. `sing-box` 不死是第一前提。
   - 不管用户在 Rule UI 里如何新增、删除、导入、切换或保存配置，都不能因为 UI 操作导致 `sing-box` 无法启动。
   - 所有会影响 `/etc/sing-box/config.json`、节点、分组、规则集、TProxy 或 DNS 监听的改动，都必须先生成临时配置并执行 `sing-box check`。
   - 只有 `sing-box check` 通过后，才允许把新配置落盘到正式路径。
   - 如果运行态重启、同步 TProxy、测速或后续应用失败，必须保留或恢复到上一个可启动状态。

2. 不能用“先写入再试试看”的方式改配置。
   - 配置写入必须具备可验证、可回滚的流程。
   - 对导入备份、批量修改、节点生成这类高风险入口，必须特别确认失败路径不会破坏现有服务。

3. 不能为了修一个点东打补丁。
   - 修改前先理解现有调用链、服务依赖、安装脚本、systemd 行为、前端刷新逻辑和回滚语义。
   - 如果一个问题会影响多个入口，要统一修复共享逻辑，不要只修当前触发路径。
   - 修改一个文件前，要评估它和 `scripts/`、`systemd/`、`singbox-rule-ui/`、`templates/` 之间的联动。

## 修改要求

1. 先理解，再修改。
   - 先读相关代码和脚本，确认真实根因。
   - 不凭猜测改生产路径、服务启动顺序、防火墙/TProxy、DNS 监听或 sing-box 配置结构。

2. 先收敛，再验证。
   - 改动范围要收敛到解决问题所需的最小集合。
   - 不做无关重构，不顺手改变既有行为。
   - 修改后必须至少做语法检查；涉及服务和安装流程时，还要在 Ubuntu/Debian + systemd 上实测安装、重启、接口和卸载路径。

3. 先校验，再落盘。
   - 影响 sing-box 配置的代码必须沿用或补齐 staged check、backup、rollback 机制。
   - 禁止绕过 `staged_check`、`check_config`、`rollback_apply` 等保护逻辑直接写正式配置。
   - 新增入口如果会写配置，必须接入同等级别的校验和回滚。

4. 稳定性第一。
   - UI 请求不能因为 systemd 重启链路被中途打断。
   - 服务依赖要避免不必要的级联停止；Rule UI 可以依赖网络和启动顺序，但不应让 `sing-box restart` 直接拖死 UI 请求（故 singbox-rule-ui.service 只 After 不 Requires sing-box）。
   - 53 端口、TProxy、规则集下载、定时任务和运行态刷新都要以可预期、可恢复为目标。

5. 可读、可追踪。
   - 关键行为改变要加中文注释，解释为什么这样做，尤其是回滚、延迟重启、端口冲突和 systemd 依赖相关逻辑。
   - 注释要解释维护意图，不写空泛描述。
   - 提交信息要说明真实修复点，不掩盖行为变化。

## 环境差异（相对 Alpine 版）

- **init 系统**：systemd（`systemctl`），不是 OpenRC。服务单元在 `systemd/*.service`，装到 `/etc/systemd/system/`，改动后必须 `systemctl daemon-reload`。
- **包管理**：apt（`apt-get` / `dpkg-query`），不是 apk。
- **定时任务**：`/etc/cron.d/sing-box-gateway`（每行含用户字段），cron 每分钟自动扫描；不是 `/etc/crontabs/root` + crond。app.py 写 cron 行时第 6 列是用户名。
- **53 端口**：Ubuntu/Debian 默认 systemd-resolved 占 `127.0.0.53:53`。install.sh 的 `disable_systemd_resolved_stub` 会自动关 stub listener 并把 `/etc/resolv.conf` 指向真实上游，卸载时按 `resolved-state` 恢复。
- **MTU/qdisc 持久化**：systemd oneshot unit（`singbox-mtu.service` / `singbox-qdisc.service`），不是 `/etc/local.d/*.start`。
- **failed 状态**：systemd 有 failed/start-limit，重启前 `systemctl reset-failed` 清除（Alpine 版是空壳）。

## 验证基线

修改后根据影响范围选择验证项，不能跳过明显相关的检查：

```sh
PYTHONPYCACHEPREFIX=/tmp/sb-ud-pycache python3 -m py_compile \
  singbox-rule-ui/app.py \
  scripts/monitor_runtime.py \
  scripts/refresh_runtime_config.py \
  scripts/sync_tproxy_setup.py \
  scripts/bootstrap_config.py

bash -n \
  scripts/install.sh \
  scripts/uninstall.sh \
  scripts/update-sing-box-rules-jsdelivr \
  scripts/sing-box-gateway-info \
  scripts/sysctl-performance.sh

sh -n \
  scripts/quick-install.sh \
  scripts/quick-install-proxy.sh

systemd-analyze verify systemd/*.service   # 有 systemd 的机器上
```

涉及安装、卸载、systemd、DNS 53 端口、TProxy、备份导入、规则更新或运行态重启时，还必须在 Ubuntu/Debian 测试机上做端到端验证：

1. 安装脚本可以完整跑通。
2. `sing-box`、`sing-box-tproxy`、`singbox-rule-ui` 都是 `active`。
3. `/api/state`、`/api/proxy`、`/api/maintenance` 返回 200。
4. 备份导出和导入不会中断 HTTP 响应，不会让服务进入 `failed`。
5. 卸载脚本行为符合预期，不残留会影响下次安装的服务状态；systemd-resolved 状态被正确恢复。

## 禁止事项

1. 禁止绕过 `sing-box check` 直接覆盖正式配置。
2. 禁止用临时 sleep、忽略错误、吞掉失败来假装成功。
3. 禁止只修前端提示而不修后端真实失败路径。
4. 禁止让第三方 DNS、TProxy、规则更新冲突在重启后反复出现却没有明确处理策略。
5. 禁止为了快速通过测试而移除回滚、校验、服务状态检查。
6. 禁止改动不相关文件或重排大段代码制造不可追踪 diff。

---

## 上游关系

| 仓库 | 说明 |
|------|------|
| `hanigege/singbox-ui-alpine` | 上游 Alpine/OpenRC 版。核心渲染逻辑、Rule UI、TProxy 的改动一般先在此发生，再移植到本仓库。 |
| `hanigege/sing-box-ui-ubuntu-debian` | 本仓库。Ubuntu/Debian + systemd 移植版。 |

从上游同步 Rule UI / 渲染 / TProxy 逻辑时，注意不要把 OpenRC/apk/crontabs 相关实现一起带过来——服务层、包管理、cron、53 端口处理在本仓库都是 systemd/apt 版本。前端静态文件（index.html、styles.css、app.js）的纯 UI 改动可直接同步。
