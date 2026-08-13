const translations = {
  en: {
    title: "Sing-box",
    loading: "Loading",
    ready: "Ready",
    restart: "Restart",
    restartHint: "Use only when you need to reload sing-box without changing rules.",
    restartSingbox: "Restart sing-box",
    restartTproxy: "Restart TProxy",
    restartingTproxy: "Restarting TProxy",
    restartingSingbox: "Restarting sing-box",
    singboxRestarted: "sing-box restarted",
    tproxyRestarted: "TProxy restarted",
    tproxyRestartFailed: "TProxy restart failed. sing-box is still running.",
    save: "Save",
    saveHint: "Save runs a staged sing-box check first. If it passes, rules are saved and sing-box restarts. If it fails, nothing is changed.",
    add: "Add",
    accessToken: "Access Token",
    pasteToken: "Paste token",
    unlock: "Unlock",
    logout: "Logout",
    loggedOut: "Logged out",
    filter: "Filter",
    loaded: "Loaded",
    tokenRequired: "Token required",
    changed: "Changed",
    noChanges: "No unsaved changes",
    saving: "Saving",
    savingWithCheck: "Checking staged rules. If it passes, rules will be saved and sing-box will restart.",
    savedAndRestarted: "Check passed. Rules saved and sing-box restarted.",
    savedAlert: "Saved successfully. sing-box and TProxy are ready.",
    restarting: "Checking before restart",
    restarted: "Config check passed and sing-box restarted",
    checkFailed: "Config check failed. Nothing was restarted.",
    saveBlocked: "Config check failed. Rules were not saved and sing-box was not restarted.",
    changesBlocked: "Config check failed. Changes were not saved and sing-box was not restarted.",
    restartFailed: "Restart failed",
    noMatches: "No matching entries",
    noEntries: "No entries",
    entries: "entries",
    matchHelp: "Match examples",
    remove: "Remove",
    service: "Service",
    memory: "Memory",
    updated: "System time",
    singBoxVersion: "sing-box",
    nodes: "Nodes",
    nodesNote: "Managed outbounds",
    enabled: "Enabled",
    disabled: "Disabled",
    deleteNode: "Delete node",
    addNode: "Add node",
    updateNode: "Update node",
    cancelEdit: "Cancel",
    editCancelled: "Edit cancelled",
    transportBbr: "System BBR / TCP",
    transportBrutal: "Brutal mux",
    transportBbrBadge: "System BBR",
    transportBrutalBadge: "Brutal",
    allowInsecure: "Allow insecure TLS",
    defaultProxy: "Default proxy",
    activeProxy: "Active proxy",
    autoSelected: "Auto selected",
    autoStatusUnavailable: "Auto status unavailable",
    setDefault: "Set default",
    defaultSaved: "Saved default",
    activeNow: "Active now",
    pendingDefault: "Default changed. It takes effect immediately; save persists it for the next start.",
    proxySwitchFailed: "Runtime proxy switch failed. Save can still persist the config.",
    switchingProxy: "Switching node\u2026",
    proxySwitched: "Node switched (no restart, existing connections kept)",
    persistFailed: "Not persisted",
    delay: "Delay",
    delayUnknown: "Not tested",
    delayFailed: "Failed",
    refreshDelay: "Refresh delay",
    refreshMaintenance: "Refresh",
    refreshingMaintenance: "Refreshing",
    maintenanceRefreshed: "Refreshed",
    runtime: "Runtime",
    runtimeNote: "Connections, logs and active rules",
    refreshingRuntime: "Refreshing runtime",
    runtimeRefreshed: "Runtime refreshed",
    runtimeUnavailable: "Runtime API unavailable",
    runtimeViewConnections: "Connections",
    runtimeViewLogs: "Logs",
    runtimeViewRules: "Rules",
    noRuntimeRows: "No runtime data",
    waitingRuntimeLogs: "Waiting for logs",
    idleRuntimeLogs: "No new log lines. Current level only shows warning/error.",
    startLogs: "Start logs",
    stopLogs: "Stop logs",
    logsStreaming: "Streaming logs",
    logsStopped: "Logs stopped",
    logLevelSaved: "Log level updated",
    connectionHost: "Host",
    connectionType: "Type",
    connectionRoute: "Route",
    connectionChain: "Proxy chain",
    connectionTraffic: "Traffic",
    logIndex: "No.",
    rulePayload: "Payload",
    ruleTarget: "Target",
    restartUi: "Restart UI",
    restartingUi: "Restarting UI",
    uiRestartScheduled: "UI restart requested. The page will reconnect shortly.",
    uiRestartReady: "UI restarted and reconnected",
    uiRestartManualRefresh: "UI restart was requested. If the page does not update, refresh the browser.",
    actionDone: "Done",
    actionFailed: "Failed",
    updateRules: "Update rule sets",
    saveRuleSchedule: "Save schedule",
    savingRuleSchedule: "Saving schedule",
    ruleScheduleSaved: "Rule update schedule saved",
    ruleScheduleTitle: "Auto update schedule",
    ruleScheduleNote: "Applies to the system /etc/cron.d schedule. A successful manual update reschedules the next automatic run from that update time.",
    ruleScheduleFrequency: "Frequency",
    ruleScheduleDaily: "Daily",
    ruleScheduleWeekly: "Weekly",
    ruleScheduleTime: "Time",
    ruleScheduleDelay: "Random delay (minutes)",
    syncTproxy: "Sync TProxy",
    exportBackup: "Export backup",
    importBackup: "Import backup",
    exportingBackup: "Exporting backup",
    importingBackup: "Importing backup",
    backupExported: "Backup exported",
    backupImported: "Backup imported and sing-box restarted",
    backupExportedAlert: "Backup exported successfully.",
    backupImportedAlert: "Backup imported successfully. sing-box and TProxy are ready.",
    backupImportFailed: "Backup import failed. Existing config is still in use.",
    updatingRules: "Updating rule sets",
    updatingTelegramCidr: "Updating Telegram IP ranges",
    savingTelegramCidr: "Saving Telegram IP ranges",
    ruleUpdateRunning: "Updating now. Please wait.",
    ruleUpdateSlow: "Update is slow. Existing rule files are still in use.",
    syncingTproxy: "Syncing TProxy",
    rulesUpdated: "Rule sets updated safely",
    tproxySynced: "TProxy synced safely",
    tproxySyncFailed: "TProxy sync failed. sing-box is still running.",
    telegramCidrUpdated: "Telegram IP ranges updated and TProxy synced",
    telegramCidrSaved: "Telegram IP ranges saved and TProxy synced",
    telegramCidrUpdateFailed: "Telegram IP range update failed. Existing list is still in use.",
    maintenance: "Maintenance",
    maintenanceNote: "Rule-set updates and TProxy status",
    backupTitle: "Backup and restore",
    backupNote: "Export or restore the UI-managed rules, nodes, and routing settings.",
    changeTokenTitle: "Change access token",
    changeTokenNote: "Set a custom login token (at least 6 characters, no spaces).",
    changeToken: "Change token",
    newTokenPlaceholder: "New token",
    changingToken: "Changing...",
    tokenChanged: "Access token updated",
    tokenTooShort: "Token must be at least 6 characters",
    maintenanceOverview: "Maintenance overview",
    configHealthTitle: "Config health",
    configHealthStatus: "Config health",
    configHealthOk: "No duplicate managed rules",
    configHealthWarn: "Duplicate or excessive managed rules detected",
    configHealthSummary: "Health summary",
    configHealthTierNote: "Tiers: Excellent · Normal · Problem",
    configHealthGreat: "Excellent",
    configHealthNormal: "Running normally",
    configHealthProblem: "Problem found",
    configHealthReasonDuplicateRules: "duplicate rules",
    configHealthReasonUdp443Rules: "too many UDP/443 reject rules",
    configHealthReasonRouteOrder: "route order is wrong",
    configHealthReasonFakeipRoute: "FakeIP route is missing",
    configHealthReasonLocalDns: "local DNS is missing",
    configHealthReasonRouteFinal: "fallback route is not direct",
    configHealthReasonMtuNotIdeal: "MTU is not standard (expected 1500 or 1492)",
    activeLocalDns: "Active local DNS",
    activeFakeip: "Active FakeIP",
    routeFinal: "Fallback route",
    routeOrderStatus: "Route order",
    fakeipRouteStatus: "FakeIP route",
    interfaceMtu: "Interface MTU",
    routeOrderOk: "Proxy rules visible",
    routeOrderWarn: "Bare direct before proxy",
    fakeipRouteOk: "Ready",
    fakeipRouteWarn: "Missing",
    routeRuleCount: "Route rules",
    dnsRuleCount: "DNS rules",
    ruleSetCount: "Rule sets",
    outboundCount: "Outbounds",
    udp443RejectCount: "UDP/443 reject rules",
    ruleUpdateTitle: "Rule-set updates",
    ruleUpdateDetails: "Rule update status",
    updatedRules: "Updated",
    keptRules: "Optional cache",
    skippedRules: "Skipped",
    errorDetails: "Needs attention",
    finalResult: "Final",
    ruleFinalUpdated: "Rule sets updated and checked",
    ruleFinalChecked: "Rule sets checked",
    ruleFinalSkippedSafe: "Using local rule cache; gateway cannot reach rule source directly",
    tproxySummaryTitle: "TProxy summary",
    tproxyDetailsTitle: "TProxy details",
    updateHealthOk: "Core rule sets are current. Optional service IP lists kept their cached copies.",
    optionalCacheOk: "Optional service IP lists are unavailable upstream, so cached copies are used. No action needed.",
    updatedCount: "Updated files",
    optionalCount: "Cached optional files",
    noUpdateDetails: "No update details yet",
    tproxyTitle: "TProxy gateway",
    nextUpdate: "Next update",
    lastUpdate: "Last update",
    updateResult: "Result",
    updateScript: "Script",
    timerStatus: "Timer",
    tproxyService: "TProxy service",
    defaultInterface: "Default interface",
    currentIpv6Prefix: "Local IPv6 LAN prefixes",
    currentIpv4Prefix: "Local IPv4 LAN prefix",
    scriptIpv6Prefix: "IPv6 destinations not intercepted",
    plannedBypass4: "IPv4 destinations not intercepted",
    plannedBypass6: "IPv6 destinations not intercepted",
    fakeipRanges: "FakeIP ranges",
    plannedProxy4: "IPv4 destinations captured",
    plannedProxy6: "IPv6 destinations captured",
    telegramCaptureStatus: "Telegram IP capture",
    telegramCidrTitle: "Telegram IP ranges",
    telegramCidrLoading: "Loading Telegram CIDR status.",
    telegramCidrSummary: "Source: {source} · IPv4 {count4} · IPv6 {count6} · Updated: {updated}",
    telegramCidrFallback: "using built-in fallback",
    telegramCidrNever: "not saved yet",
    telegramCidrHelp: "Online update downloads, validates, saves, and applies the list in one step. Use manual save only after editing the text box.",
    updateTelegramCidr: "Update and apply online",
    saveTelegramCidr: "Save manual list",
    nodeServerIps: "Node server addresses",
    tproxyPolicy: "LAN/private and node server IPs bypass TProxy. LAN DNS port 53 is redirected to sing-box DNS. FakeIP, explicit Greylist IP/CIDR, and enabled Telegram IP ranges are captured by TProxy.",
    prefixMismatch: "IPv6 bypass prefix should be regenerated for this host.",
    healthy: "OK",
    unknown: "Unknown",
    testingDelay: "Testing node delay",
    delayUpdated: "Delay updated",
    autoTitle: "Auto",
    autoNote: "Urltest re-tests every node each interval and picks the lowest latency; a candidate must beat the current one by more than the tolerance to take over.",
    autoUrl: "Test URL",
    autoInterval: "Interval",
    autoTolerance: "Tolerance (ms)",
    autoIdleTimeout: "Idle timeout",
    autoIdleNote: "Idle timeout: once no traffic goes through the Auto group for this long, periodic testing stops and resumes automatically on the next connection \u2014 resource saving only, it does not affect node selection. Tolerance is the anti-flapping threshold: a candidate must be at least this many ms faster to take over. Idle timeout must be greater than or equal to the interval, otherwise sing-box refuses to start.",
    nodeClockNote: "2022-blake3 has a 30-second replay window: if this gateway's clock differs from the server by more than 30s, the node connects but transfers 0 B/s. Make sure an NTP daemon is running on this host (e.g. apt install chrony, or systemctl enable --now systemd-timesyncd).",
    nodeSsFormatNote: "Shadowsocks fill-in: method 2022-blake3-aes-256-gcm needs a 44-char base64 key from `ssservice genkey` (NOT a plain password). For Caddy/WebSocket disguise: plugin=v2ray-plugin, plugin_opts=mode=websocket;tls;host=YOUR_DOMAIN;path=/YOUR_PATH. Both fields are required — leaving plugin empty silently removes the disguise (node breaks).",
    interruptConnections: "Interrupt old connections",
    localDnsTitle: "China DNS",
    localDnsNote: "Choose one local-dns upstream. sing-box does not run these in parallel.",
    localDnsUpstream: "Upstream",
    customDnsServer: "Custom Server",
    customDnsPort: "Custom Port",
    refreshDnsDelay: "Refresh DNS delay",
    dnsDelayUpdated: "DNS delay updated",
    dnsDelayEmpty: "DNS delay has not been tested",
    dnsDelayFailed: "Failed",
    dnsMode: "DNS mode",
    ddnsLocalDns: "Local DNS",
    ddnsRemoteDns: "Proxy DNS",
    ddnsLocalSummary: "Local DNS + direct",
    ddnsRemoteSummary: "Proxy DNS + direct",
    ddnsLocalHint: ["Lookup: use local DNS.", "Connect: keep direct routing."],
    ddnsRemoteHint: ["Lookup: use remote DNS through Proxy to avoid local DNS pollution.", "Connect: keep direct routing after the IP is resolved."],
    fakeipTitle: "FakeIP",
    fakeipNote: "Match this range with the upstream router.",
    fakeipV4: "IPv4 range",
    fakeipV6: "IPv6 range",
    fakeipIpv6Enabled: "Enable IPv6 FakeIP / AAAA",
    fakeipIpv6Help: "Return IPv6 FakeIP answers for matched domains only when the upstream router sends the IPv6 FakeIP range back to sing-box.",
    fakeipQuicPolicy: "FakeIP QUIC protection is always on",
    fakeipQuicPolicyHelp: "UDP/443 to FakeIP ranges is blocked so browsers fall back to TCP, reducing QUIC long connections that can occupy proxy bandwidth and connection tracking. Real game and voice UDP are not affected.",
    telegramCaptureIps: "Proxy Telegram official IP ranges",
    socks5Title: "SOCKS5",
    socks5Note: "Enable SOCKS5 inbound for LAN clients. Port 0 disables it.",
    socks5Port: "SOCKS5 Port",
    telegramPolicy: "Telegram IP capture",
    telegramPolicyHelp: "Telegram clients may connect to official IPs directly. This keeps those explicit service ranges in TProxy without capturing all public IP traffic.",
    editingNode: "Editing node",
    nodeSelected: "Node loaded into the form",
    nodeDeleteBlocked: "This node is still referenced by the active default. Choose another default first.",
    duplicateNode: "Invalid or duplicate tag",
    placeholders: {
      domain: "login.example.com",
      domain_suffix: "example.com",
      domain_keyword: "google",
      domain_regex: "^api[0-9]+\\.example\\.com$",
      ip_cidr: "203.0.113.0/24",
    },
    // 批量编辑框提示。按当前表允许的类型动态拼接，见 renderListHint()
    textareaHint: {
      format: "One entry per line, format:",
      types: "Supported types:",
      fallback:
        "A line without a type prefix uses the type selected above, so pasting {example} is added as {applied}.",
      caseNote: "Type prefixes are case-insensitive; the Chinese labels shown in the dropdown also work.",
      regexNote:
        "Regex values keep their original case ([^a-zA-Z0-9._-] is stored as typed). Every other type is lowercased, and a trailing dot is dropped.",
      ipv6Note:
        "IPv6 must use an explicit ip_cidr: prefix, otherwise the part before the first colon looks like a prefix.",
      cidrNote: "ip_cidr must be a real network address: use 192.168.1.0/24, not 192.168.1.5/24.",
      urlNote: "Paste bare domains only. A full URL such as https://example.com/path is rejected.",
      fallbackShort: "or paste bare domains to use the type selected above",
    },
    typeHelp: {
      domain: { use: "match one exact domain", example: "login.example.com" },
      domain_suffix: { use: "match this domain and all subdomains", example: "example.com" },
      domain_keyword: { use: "match domains containing this word", example: "google" },
      domain_regex: { use: "match domains with a pattern, such as api1 or api23", example: "^api[0-9]+\\.example\\.com$" },
      ip_cidr: { use: "match a real destination IP range; for Greylist, the upstream router must also route that IPv4/IPv6 CIDR to sing-box", example: "203.0.113.0/24" },
    },
    listTypeHelp: {
      whitelist: "Direct: suffix is usually enough; IP/CIDR is useful for game servers and other traffic that no longer carries a domain.",
      blacklist: "Block: suffix blocks a site family; IP/CIDR blocks known destination ranges.",
      greylist: "Proxy: suffix is safest. IP/CIDR can capture literal IP traffic into TProxy, but RouterOS/upstream routing must send the same IPv4 CIDR to sing-box-v4 or IPv6 CIDR to sing-box-v6.",
      ddns: "DDNS only needs exact host or suffix. Keyword and regex are hidden to avoid accidental broad matches.",
    },
    greylistRouteNotice: "Proxy: suffix is safest. IP/CIDR requires two sides: this UI adds the CIDR to sing-box TProxy capture, and RouterOS/upstream routing must also send that exact IPv4/IPv6 CIDR to the sing-box gateway or the policy table that uses it. Protected LAN and node server ranges are rejected.",
    lists: {
      whitelist: { title: "Whitelist", note: "Direct routing" },
      blacklist: { title: "Blacklist", note: "Blocked routing" },
      greylist: { title: "Greylist", note: "Forced proxy" },
      ddns: { title: "Local DDNS", note: "Local DNS and direct routing" },
      nodes: { title: "Nodes", note: "Add, delete, and enable outbounds" },
      runtime: { title: "Runtime", note: "Connections, logs and active rules" },
      maintenance: { title: "Maintenance", note: "Rule-set updates and TProxy status" },
    },
    types: {
      domain: "Domain",
      domain_suffix: "Suffix",
      domain_keyword: "Keyword",
      domain_regex: "Regex",
      ip_cidr: "IP/CIDR",
    },
  },
  zh: {
    title: "Sing-box",
    loading: "加载中",
    ready: "就绪",
    restart: "重启",
    restartHint: "仅在没有改规则、但需要重新加载 sing-box 时使用。",
    restartSingbox: "重启 sing-box",
    restartTproxy: "重启 TProxy",
    restartingTproxy: "正在重启 TProxy",
    restartingSingbox: "正在重启 sing-box",
    singboxRestarted: "sing-box 已重启",
    tproxyRestarted: "TProxy 已重启",
    tproxyRestartFailed: "TProxy 重启失败，sing-box 仍在运行。",
    save: "保存",
    saveHint: "保存会先用临时规则检测 sing-box 配置；通过才保存并重启，失败不会改正式规则。",
    add: "添加",
    accessToken: "访问令牌",
    pasteToken: "粘贴 token",
    unlock: "解锁",
    logout: "退出",
    loggedOut: "已退出",
    filter: "筛选",
    loaded: "已加载",
    tokenRequired: "需要 token",
    changed: "有未保存修改",
    noChanges: "没有未保存修改",
    saving: "正在保存",
    savingWithCheck: "正在检测临时规则；通过后才会保存并重启 sing-box",
    savedAndRestarted: "检测通过，规则已保存，sing-box 已重启",
    savedAlert: "保存成功，sing-box 和 TProxy 已就绪。",
    restarting: "重启前检测中",
    restarted: "检测通过，sing-box 已重启",
    checkFailed: "配置检测失败，没有执行重启",
    saveBlocked: "配置检测失败，规则未保存，也未重启 sing-box",
    changesBlocked: "配置检测失败，修改未保存，也未重启 sing-box",
    restartFailed: "重启失败",
    noMatches: "没有匹配条目",
    noEntries: "没有条目",
    entries: "条",
    matchHelp: "匹配示例",
    remove: "删除",
    service: "服务",
    memory: "内存",
    updated: "系统时间",
    singBoxVersion: "sing-box",
    nodes: "节点",
    nodesNote: "受管理的出站节点",
    enabled: "启用",
    disabled: "停用",
    deleteNode: "删除节点",
    addNode: "添加节点",
    updateNode: "更新节点",
    cancelEdit: "取消编辑",
    editCancelled: "已取消编辑",
    transportBbr: "系统 BBR / TCP",
    transportBrutal: "Brutal 复用",
    transportBbrBadge: "系统 BBR",
    transportBrutalBadge: "Brutal",
    allowInsecure: "允许不安全 TLS",
    defaultProxy: "默认代理",
    activeProxy: "当前生效",
    autoSelected: "Auto 选中",
    autoStatusUnavailable: "Auto 状态不可用",
    setDefault: "设为默认",
    defaultSaved: "已保存默认",
    activeNow: "当前生效",
    pendingDefault: "默认节点已切换并立即生效；保存只是让它在下次启动时保持",
    proxySwitchFailed: "运行态切换失败；仍可保存配置让它持久化生效",
    switchingProxy: "正在切换节点\u2026",
    proxySwitched: "节点已切换（无需重启，现有连接不断）",
    persistFailed: "未能持久化",
    delay: "延迟",
    delayUnknown: "未检测",
    delayFailed: "失败",
    refreshDelay: "刷新延迟",
    refreshMaintenance: "刷新状态",
    refreshingMaintenance: "正在刷新",
    maintenanceRefreshed: "已刷新",
    runtime: "运行状态",
    runtimeNote: "连接、日志与运行规则",
    refreshingRuntime: "正在刷新运行状态",
    runtimeRefreshed: "运行状态已刷新",
    runtimeUnavailable: "运行态 API 不可用",
    runtimeViewConnections: "连接",
    runtimeViewLogs: "日志",
    runtimeViewRules: "规则",
    noRuntimeRows: "暂无运行数据",
    waitingRuntimeLogs: "正在接收日志",
    idleRuntimeLogs: "暂无新日志；当前级别只显示 warning/error。",
    startLogs: "开始日志",
    stopLogs: "停止日志",
    logsStreaming: "正在接收日志",
    logsStopped: "日志已停止",
    logLevelSaved: "日志级别已更新",
    connectionHost: "目标",
    connectionType: "类型",
    connectionRoute: "路由",
    connectionChain: "代理链",
    connectionTraffic: "流量",
    logIndex: "序号",
    rulePayload: "匹配条件",
    ruleTarget: "出站",
    restartUi: "重启 UI",
    restartingUi: "正在重启 UI",
    uiRestartScheduled: "UI 正在重启，页面稍后会自动恢复。",
    uiRestartReady: "UI 已重启并恢复连接",
    uiRestartManualRefresh: "UI 重启请求已发送；如果页面没有变化，可以手动刷新浏览器。",
    actionDone: "完成",
    actionFailed: "失败",
    updateRules: "立即更新分流规则",
    saveRuleSchedule: "保存更新时间",
    savingRuleSchedule: "正在保存更新时间",
    ruleScheduleSaved: "分流规则自动更新时间已保存",
    ruleScheduleTitle: "自动更新设置",
    ruleScheduleNote: "只调整系统 /etc/cron.d 计划；手动更新成功后，会从本次更新时间重新顺延下一次自动更新。",
    ruleScheduleFrequency: "更新周期",
    ruleScheduleDaily: "每天",
    ruleScheduleWeekly: "每周",
    ruleScheduleTime: "执行时间",
    ruleScheduleDelay: "随机延迟（分钟）",
    syncTproxy: "同步 TProxy",
    exportBackup: "导出备份",
    importBackup: "导入备份",
    exportingBackup: "正在导出备份",
    importingBackup: "正在导入备份",
    backupExported: "备份已导出",
    backupImported: "备份已导入，sing-box 已重启",
    backupExportedAlert: "备份导出成功。",
    backupImportedAlert: "备份导入成功，sing-box 和 TProxy 已就绪。",
    backupImportFailed: "备份导入失败，当前配置仍在使用。",
    updatingRules: "正在更新分流规则",
    updatingTelegramCidr: "正在更新 Telegram IP 网段",
    savingTelegramCidr: "正在保存 Telegram IP 网段",
    ruleUpdateRunning: "正在更新，请稍候。",
    ruleUpdateSlow: "更新较慢，旧规则仍在使用，不影响 sing-box。",
    syncingTproxy: "正在同步 TProxy",
    rulesUpdated: "分流规则已安全更新",
    tproxySynced: "TProxy 已安全同步",
    tproxySyncFailed: "TProxy 同步失败，sing-box 仍在运行。",
    telegramCidrUpdated: "Telegram IP 网段已更新，TProxy 已同步",
    telegramCidrSaved: "Telegram IP 网段已保存，TProxy 已同步",
    telegramCidrUpdateFailed: "Telegram IP 网段更新失败，旧列表仍在使用。",
    maintenance: "维护",
    maintenanceNote: "规则集更新与 TProxy 状态",
    backupTitle: "备份与恢复",
    backupNote: "导出或恢复 UI 管理的规则、节点和分流设置。",
    changeTokenTitle: "修改访问密码",
    changeTokenNote: "设置自定义登录密码（至少 6 位，不含空格）。",
    changeToken: "修改密码",
    newTokenPlaceholder: "新密码",
    changingToken: "修改中...",
    tokenChanged: "访问密码已更新",
    tokenTooShort: "密码至少需要 6 位",
    maintenanceOverview: "维护概览",
    configHealthTitle: "配置健康",
    configHealthStatus: "配置健康",
    configHealthOk: "未发现重复受管理规则",
    configHealthWarn: "发现重复或过量受管理规则",
    configHealthSummary: "健康总评",
    configHealthTierNote: "三级：状态极佳 · 运行正常 · 发现问题",
    configHealthGreat: "状态极佳",
    configHealthNormal: "运行正常",
    configHealthProblem: "发现问题",
    configHealthReasonDuplicateRules: "存在重复规则",
    configHealthReasonUdp443Rules: "UDP/443 拒绝规则过多",
    configHealthReasonRouteOrder: "路由顺序异常",
    configHealthReasonFakeipRoute: "FakeIP 路由缺失",
    configHealthReasonLocalDns: "本地 DNS 缺失",
    configHealthReasonRouteFinal: "兜底出口不是 direct",
    configHealthReasonMtuNotIdeal: "MTU 非标准值（预期 1500 或 1492）",
    activeLocalDns: "当前本地 DNS",
    activeFakeip: "当前 FakeIP",
    routeFinal: "兜底出口",
    routeOrderStatus: "路由顺序",
    fakeipRouteStatus: "FakeIP 路由",
    interfaceMtu: "网卡 MTU",
    routeOrderOk: "代理规则可命中",
    routeOrderWarn: "裸直连挡在代理前",
    fakeipRouteOk: "已就绪",
    fakeipRouteWarn: "缺失",
    routeRuleCount: "路由规则数",
    dnsRuleCount: "DNS 规则数",
    ruleSetCount: "规则集数",
    outboundCount: "出站数",
    udp443RejectCount: "UDP/443 拒绝规则数",
    ruleUpdateTitle: "分流规则更新",
    ruleUpdateDetails: "规则更新状态",
    updatedRules: "已更新",
    keptRules: "可选规则缓存",
    skippedRules: "已跳过",
    errorDetails: "需要处理",
    finalResult: "最终结果",
    ruleFinalUpdated: "分流规则已更新并通过检查",
    ruleFinalChecked: "分流规则已通过检查",
    ruleFinalSkippedSafe: "已使用本地规则缓存；网关机当前无法直连规则源",
    tproxySummaryTitle: "TProxy 摘要",
    tproxyDetailsTitle: "TProxy 详情",
    updateHealthOk: "核心分流规则已更新；可选服务 IP 列表沿用缓存，不影响正常分流。",
    optionalCacheOk: "这些可选服务 IP 上游暂时没有文件，已自动沿用旧缓存，无需处理。",
    updatedCount: "更新文件数",
    optionalCount: "沿用缓存数",
    noUpdateDetails: "暂无更新明细",
    tproxyTitle: "TProxy 旁路网关",
    nextUpdate: "下次自动更新",
    lastUpdate: "上次触发",
    updateResult: "更新结果",
    updateScript: "脚本",
    timerStatus: "定时器",
    tproxyService: "TProxy 服务",
    defaultInterface: "默认网卡",
    currentIpv6Prefix: "本机 IPv6 局域网段",
    currentIpv4Prefix: "本机 IPv4 局域网段",
    scriptIpv6Prefix: "不接管的 IPv6 目标",
    plannedBypass4: "不接管的 IPv4 目标",
    plannedBypass6: "不接管的 IPv6 目标",
    fakeipRanges: "FakeIP 网段",
    plannedProxy4: "已捕获 IPv4 目标",
    plannedProxy6: "已捕获 IPv6 目标",
    telegramCaptureStatus: "Telegram IP 捕获",
    telegramCidrTitle: "Telegram IP 网段",
    telegramCidrLoading: "正在读取 Telegram CIDR 状态。",
    telegramCidrSummary: "来源：{source} · IPv4 {count4} 条 · IPv6 {count6} 条 · 更新时间：{updated}",
    telegramCidrFallback: "正在使用内置兜底列表",
    telegramCidrNever: "尚未保存",
    telegramCidrHelp: "在线更新会自动下载、校验、保存并应用；只有手动改了文本框，才需要点保存手动列表。",
    updateTelegramCidr: "在线更新并应用",
    saveTelegramCidr: "保存手动列表",
    nodeServerIps: "节点服务器地址",
    tproxyPolicy: "内网、本机和节点服务器 IP 会绕过 TProxy；LAN DNS 53 端口会转给 sing-box；FakeIP、灰名单 IP/CIDR 和启用的 Telegram 官方 IP 网段会进入 TProxy。",
    prefixMismatch: "IPv6 绕过前缀和当前机器不一致，打包安装时应自动生成。",
    healthy: "正常",
    unknown: "未知",
    testingDelay: "正在检测节点延迟",
    delayUpdated: "延迟已更新",
    autoTitle: "Auto 自动选择",
    autoNote: "urltest 每隔「检测间隔」重测所有节点，选延迟最低的；候选节点要比当前节点快出「切换容差」才会接替。",
    autoUrl: "测速链接",
    autoInterval: "检测间隔",
    autoTolerance: "切换容差（毫秒）",
    autoIdleTimeout: "空闲停测",
    autoIdleNote: "空闲停测：Auto 组连续这么久没有流量经过时停止周期测速，下次有连接自动恢复——只省资源，不影响选路。切换容差是防抖阈值：候选节点要比当前节点快这么多毫秒才会接替，设 0 会在延迟抖动时反复横跳。空闲停测必须不小于检测间隔，否则 sing-box 拒绝启动。",
    nodeClockNote: "2022-blake3 有 30 秒防重放窗口：本网关与服务端时钟相差超过 30 秒，节点会「能连上但 0 B/s」。请确保本机有 NTP 在跑（如 apt install chrony，或 systemctl enable --now systemd-timesyncd）。",
    nodeSsFormatNote: "Shadowsocks 填写格式：加密方式选 2022-blake3-aes-256-gcm 时，密码必须是 `ssservice genkey -m 2022-blake3-aes-256-gcm` 生成的 44 字符 base64 key（不能填普通字符串密码）。WS 伪装版：插件填 v2ray-plugin，插件参数填 mode=websocket;tls;host=你的域名;path=/你的暗号。这两项必填——插件留空保存会被静默删掉，节点会退回直连而连不上。",
    interruptConnections: "切换时中断旧连接",
    localDnsTitle: "国内 DNS",
    localDnsNote: "为国内直连域名选择一个 local-dns 上游；sing-box 不会并发查询这些 DNS。",
    localDnsUpstream: "上游",
    customDnsServer: "自定义服务器",
    customDnsPort: "自定义端口",
    refreshDnsDelay: "刷新 DNS 延时",
    dnsDelayUpdated: "DNS 延时已更新",
    dnsDelayEmpty: "还没有检测 DNS 延时",
    dnsDelayFailed: "失败",
    dnsMode: "解析方式",
    ddnsLocalDns: "本地解析",
    ddnsRemoteDns: "代理解析",
    ddnsLocalSummary: "本地解析 + 直连",
    ddnsRemoteSummary: "代理解析 + 直连",
    ddnsLocalHint: ["查 IP：使用本地 DNS。", "连接：拿到 IP 后仍保持直连。"],
    ddnsRemoteHint: ["查 IP：使用国外 DNS，并经代理节点发起解析，绕开本地 DNS 污染。", "连接：拿到 IP 后仍按 DDNS 规则直连，不走代理。"],
    fakeipTitle: "FakeIP",
    fakeipNote: "需要和前端软路由里的 FakeIP 网段保持一致",
    fakeipV4: "IPv4 网段",
    fakeipV6: "IPv6 网段",
    fakeipIpv6Enabled: "启用 IPv6 FakeIP / AAAA",
    fakeipIpv6Help: "只有当前端路由器已把 IPv6 FakeIP 网段送回 sing-box 时，才建议开启 AAAA FakeIP 响应。",
    fakeipQuicPolicy: "FakeIP QUIC 保护固定开启",
    fakeipQuicPolicyHelp: "系统会固定拦截发往 FakeIP 网段的 UDP/443，让浏览器回落到 TCP，减少 QUIC 长连接占满代理带宽和连接表；真实游戏/语音 UDP 不受影响。",
    telegramCaptureIps: "代理 Telegram 官方 IP 网段",
    socks5Title: "SOCKS5",
    socks5Note: "为局域网客户端启用 SOCKS5 入站代理。设置 0 关闭。",
    socks5Port: "SOCKS5 端口",
    telegramPolicy: "Telegram IP 捕获",
    telegramPolicyHelp: "Telegram 客户端可能直接连接官方 IP。开启后只把这些明确服务网段加入 TProxy，不扩大到全部公网 IP。",
    editingNode: "正在编辑节点",
    nodeSelected: "已把节点参数填入上方表单",
    nodeDeleteBlocked: "这个节点仍是当前默认选择，请先切换默认节点。",
    duplicateNode: "节点名称无效或重复",
    placeholders: {
      domain: "home.example.com",
      domain_suffix: "example.com",
      domain_keyword: "google",
      domain_regex: "^api[0-9]+\\.example\\.com$",
      ip_cidr: "203.0.113.0/24",
    },
    // 批量编辑框提示。按当前表允许的类型动态拼接，见 renderListHint()
    textareaHint: {
      format: "每行一个条目，格式：",
      types: "支持的类型：",
      fallback: "不写类型前缀则自动使用上方下拉框选中的类型，例如粘贴 {example} 会添加为 {applied}。",
      caseNote: "类型前缀不区分大小写，也可以直接用下拉框里的中文名称（如 域名后缀:）。",
      regexNote:
        "正则的大小写会原样保留（[^a-zA-Z0-9._-] 存进去还是这样）；其余类型统一转小写，并去掉结尾的点。",
      ipv6Note: "IPv6 必须显式写 ip_cidr: 前缀，否则第一个冒号前的内容会被当成类型前缀。",
      cidrNote: "ip_cidr 必须是真实网段：写 192.168.1.0/24，不能写 192.168.1.5/24。",
      urlNote: "只能粘贴纯域名，带协议的完整网址（如 https://example.com/path）会被拒绝。",
      fallbackShort: "也可以直接粘贴纯域名，会使用上方选中的类型",
    },
    typeHelp: {
      domain: { use: "只匹配这个完整域名", example: "home.example.com" },
      domain_suffix: { use: "匹配该域名及其所有子域名", example: "example.com" },
      domain_keyword: { use: "域名里包含这个关键词就匹配", example: "google" },
      domain_regex: { use: "按一条表达式匹配有规律的域名，如 api1、api23", example: "^api[0-9]+\\.example\\.com$" },
      ip_cidr: { use: "匹配真实目标 IP 网段；灰名单使用 IP/CIDR 时，上游路由器也必须把同一段 IPv4/IPv6 送到 sing-box", example: "203.0.113.0/24" },
    },
    listTypeHelp: {
      whitelist: "白名单用于强制直连；游戏服务器这类进入连接阶段只剩 IP 的流量，可以用 IP/CIDR。",
      blacklist: "黑名单用于强制阻断；后缀适合整站，IP/CIDR 适合已知目标网段。",
      greylist: "灰名单用于强制代理；后缀最稳。IP/CIDR 可捕获字面量 IP 流量进 TProxy，但 RouterOS/上游路由也必须把同一段 IPv4 指到 sing-box-v4、IPv6 指到 sing-box-v6。",
      ddns: "DDNS 只保留完整域名和域名后缀；关键词/正则容易误伤，已隐藏。",
    },
    greylistRouteNotice: "灰名单用于强制代理；后缀最稳。IP/CIDR 需要两边同时配置：这里会把该网段加入 sing-box TProxy 捕获，RouterOS/上游路由也必须把同一段 IPv4/IPv6 指向 sing-box 网关，或指向使用该网关的策略路由表。内网和节点服务器网段会被后端拒绝。",
    lists: {
      whitelist: { title: "白名单", note: "强制直连" },
      blacklist: { title: "黑名单", note: "强制阻断" },
      greylist: { title: "灰名单", note: "强制代理" },
      ddns: { title: "本地 DDNS", note: "本地 DNS + 直连" },
      nodes: { title: "节点", note: "添加、删除、启停出站节点" },
      runtime: { title: "运行状态", note: "连接、日志与运行规则" },
      maintenance: { title: "维护", note: "规则集更新与 TProxy 状态" },
    },
    types: {
      domain: "完整域名",
      domain_suffix: "域名后缀",
      domain_keyword: "关键词",
      domain_regex: "正则",
      ip_cidr: "IP/CIDR",
    },
  },
};

let token = localStorage.getItem("ruleUiToken") || "";
let lang = localStorage.getItem("ruleUiLang") || ((navigator.language || "").toLowerCase().startsWith("zh") ? "zh" : "en");
let state = { lists: { whitelist: [], blacklist: [], greylist: [], ddns: [] }, nodes: [], groups: {}, meta: {} };
let maintenance = {};
let runtime = { connections: [], rules: [], logLevel: "warn", logLines: [], logIdle: false };
let runtimeProxy = { now: null, available: false };
let delays = {};
let dnsDelays = {};
let dnsDelayHost = "";
let active = "nodes";
let dirty = false;
let busy = false;
let editingNodeTag = null;
let editingNodeSnapshot = "";
let nodeEditChanged = false;
let metaUpdatedAt = null;
let metaRefreshInFlight = false;
let delayRefreshInFlight = false;
let dnsDelayRefreshInFlight = false;
let logStreamController = null;
let runtimePollTimer = null;
const actionButtonTimers = {};

const $ = (id) => document.getElementById(id);
const t = (key) => translations[lang][key] || translations.en[key] || key;
const allEntryTypes = ["domain_suffix", "domain", "domain_keyword", "domain_regex", "ip_cidr"];
const listEntryTypes = {
  whitelist: allEntryTypes,
  blacklist: allEntryTypes,
  greylist: allEntryTypes,
  ddns: ["domain_suffix", "domain"],
};

function setStatus(text, tone = "") {
  const node = $("status");
  node.textContent = text;
  node.className = `status ${tone}`;
}

function setBusy(value) {
  busy = value;
  updateButtons();
}

function setDirty(value) {
  dirty = value;
  updateButtons();
}

function updateButtons() {
  $("logoutBtn").disabled = busy;
  $("refreshMaintenanceBtn").disabled = busy;
  $("restartSingboxBtn").disabled = busy;
  $("restartTproxyBtn").disabled = busy;
  $("restartUiBtn").disabled = busy;
  $("syncTproxyBtn").disabled = busy;
  $("exportBackupBtn").disabled = busy;
  $("importBackupBtn").disabled = busy;
  $("changeTokenBtn").disabled = busy;
  $("updateRulesBtn").disabled = busy;
  $("updateTelegramCidrBtn").disabled = busy;
  $("saveTelegramCidrBtn").disabled = busy;
  $("runtimeLogLevel").disabled = busy;
  $("saveBtn").disabled = busy || !dirty;
  $("nodeSubmit").disabled = busy || Boolean(editingNodeTag && !nodeEditChanged);
  const scheduleSave = $("saveRuleScheduleBtn");
  if (scheduleSave) scheduleSave.disabled = busy || !ruleScheduleChanged();
}

function currentRuleScheduleForm() {
  const frequency = $("ruleScheduleFrequencyInput");
  const timeInput = $("ruleScheduleTimeInput");
  const delayInput = $("ruleScheduleDelayInput");
  if (!frequency || !timeInput || !delayInput) return null;
  const [hour = "", minute = ""] = timeInput.value.split(":");
  return {
    frequency: frequency.value,
    hour: Number(hour),
    minute: Number(minute),
    randomizedDelayMinutes: Number(delayInput.value),
  };
}

function ruleScheduleChanged() {
  const current = currentRuleScheduleForm();
  if (!current) return false;
  return ruleScheduleChangedFor(maintenance?.ruleUpdate?.schedule || {});
}

function ruleScheduleChangedFor(schedule) {
  const current = currentRuleScheduleForm();
  if (!current) return false;
  return (
    current.frequency !== (schedule.frequency || "weekly") ||
    current.hour !== (Number.isInteger(schedule.hour) ? schedule.hour : 4) ||
    current.minute !== (Number.isInteger(schedule.minute) ? schedule.minute : 20) ||
    current.randomizedDelayMinutes !== scheduleDelayMinutes(schedule)
  );
}

function scheduleDelayMinutes(schedule = {}) {
  if (Number.isInteger(schedule.randomizedDelayMinutes)) return schedule.randomizedDelayMinutes;
  if (Number.isInteger(schedule.randomizedDelayHours)) return schedule.randomizedDelayHours * 60;
  return 0;
}

function setActionButton(id, textKey, tone = "") {
  const button = $(id);
  clearTimeout(actionButtonTimers[id]);
  button.textContent = t(textKey);
  button.classList.remove("working", "done", "failed");
  if (tone) button.classList.add(tone);
}

function pulseActionButton(id, textKey) {
  setActionButton(id, textKey, "working");
}

function finishActionButton(id, textKey, tone = "done", resetKey = null) {
  setActionButton(id, textKey, tone);
  actionButtonTimers[id] = setTimeout(() => {
    if (resetKey) setActionButton(id, resetKey);
    else applyLanguage();
  }, 1600);
}

async function api(path, options = {}) {
  const headers = { ...(options.headers || {}) };
  if (token) headers.Authorization = `Bearer ${token}`;
  if (options.body && !headers["Content-Type"]) headers["Content-Type"] = "application/json";
  const response = await fetch(path, { ...options, headers });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    const updateMessage = [body.update?.stderr, body.update?.stdout].filter(Boolean).join("\n");
    const telegramMessage = (body.telegramCidrUpdate?.errors || []).join("; ");
    // 后端维护入口会把脚本 stdout/stderr 放在不同字段；统一提取，避免 UI 只显示 HTTP 500 而看不到真实失败原因。
    throw new Error(updateMessage || telegramMessage || body.check?.stderr || body.error || `HTTP ${response.status}`);
  }
  return body;
}

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

async function waitForUiReconnect(timeoutMs = 12000) {
  const deadline = Date.now() + timeoutMs;
  await sleep(900);
  while (Date.now() < deadline) {
    try {
      return await api("/api/maintenance");
    } catch (error) {
      await sleep(700);
    }
  }
  return null;
}

function showLogin() {
  $("login").classList.remove("hidden");
  $("app").classList.add("hidden");
  $("tokenInput").value = token;
  $("tokenInput").focus();
}

function showApp() {
  $("login").classList.add("hidden");
  $("app").classList.remove("hidden");
}

function logout() {
  token = "";
  localStorage.removeItem("ruleUiToken");
  state = { lists: { whitelist: [], blacklist: [], greylist: [], ddns: [] }, nodes: [], groups: {}, meta: {} };
  maintenance = {};
  runtime = { connections: [], rules: [], logLevel: "warn", logLines: [], logIdle: false };
  stopRuntimeLogs(false);
  stopRuntimePolling();
  runtimeProxy = { now: null, available: false };
  delays = {};
  dnsDelays = {};
  dnsDelayHost = "";
  metaUpdatedAt = null;
  setDirty(false);
  $("tokenInput").value = "";
  showLogin();
  renderMeta();
  setStatus(t("loggedOut"), "ok");
}

async function load() {
  try {
    state = await api("/api/state");
    metaUpdatedAt = new Date();
    await loadProxyInfo(false);
    setDirty(false);
    showApp();
    render();
    // 重新登录时 logout() 已清空 maintenance/runtime 缓存；若当前停留在这两个 tab，
    // render() 只会画出空数据(网卡 MTU 未知等)。与 tab 切换逻辑对齐，登录后按当前页补拉。
    if (active === "maintenance") refreshMaintenance().catch(() => {});
    if (active === "runtime") refreshRuntime();
    setStatus(t("loaded"), "ok");
    refreshDnsDelays({ silent: true }).catch(() => {});
  } catch (error) {
    showLogin();
    setStatus(error.message === "Unauthorized" ? t("tokenRequired") : error.message, "bad");
  }
}

async function refreshMeta() {
  if (!token || $("app").classList.contains("hidden")) return;
  if (metaRefreshInFlight) return;
  metaRefreshInFlight = true;
  try {
    const latest = await api("/api/state");
    state.meta = latest.meta || state.meta;
    metaUpdatedAt = new Date();
    renderMeta();
  } catch (error) {
    // A missed telemetry refresh should never interrupt rule or node editing.
  } finally {
    metaRefreshInFlight = false;
  }
}

async function refreshDnsDelays(options = {}) {
  if (dnsDelayRefreshInFlight) return;
  if (!$("app").classList.contains("hidden")) syncNodeSettingsFromForm();
  const silent = Boolean(options.silent);
  dnsDelayRefreshInFlight = true;
  if (!silent) {
    setBusy(true);
    pulseActionButton("refreshDnsDelayBtn", "refreshDnsDelay");
    setStatus(t("refreshDnsDelay"));
  }
  try {
    const params = new URLSearchParams();
    const groupsDns = state.groups?.dns || {};
    if (groupsDns.local_custom_server) params.set("custom_server", groupsDns.local_custom_server);
    if (groupsDns.local_custom_port) params.set("custom_port", String(groupsDns.local_custom_port));
    const suffix = params.toString() ? `?${params.toString()}` : "";
    const result = await api(`/api/dns-delays${suffix}`);
    if (result.state) state = result.state;
    dnsDelays = result.dnsDelays?.items || {};
    dnsDelayHost = result.dnsDelays?.host || "";
    render();
    if (!silent) {
      finishActionButton("refreshDnsDelayBtn", "actionDone", "done", "refreshDnsDelay");
      setStatus(t("dnsDelayUpdated"), "ok");
    }
  } catch (error) {
    if (!silent) {
      finishActionButton("refreshDnsDelayBtn", "actionFailed", "failed", "refreshDnsDelay");
      setStatus(error.message, "bad");
    }
  } finally {
    dnsDelayRefreshInFlight = false;
    if (!silent) setBusy(false);
    render();
  }
}

async function loadProxyInfo(testDelay = false) {
  try {
    const result = await api(testDelay ? "/api/delays?test=1" : "/api/proxy");
    applyProxyPayload(result);
    return result;
  } catch (error) {
    runtimeProxy = { now: null, available: false, error: error.message };
    return null;
  }
}

function applyProxyPayload(result) {
  if (result.proxy) {
    runtimeProxy = {
      now: result.proxy.ok ? result.proxy.data?.now || null : null,
      autoNow: result.proxy.ok ? result.proxy.data?.autoNow || null : null,
      autoError: result.proxy.ok ? result.proxy.data?.autoError || "" : "",
      available: Boolean(result.proxy.ok),
      error: result.proxy.ok ? "" : result.proxy.error,
    };
  }
  const delayPayload = result.delays?.delays || {};
  delays = { ...delays, ...delayPayload };
}

function applyLanguage() {
  document.documentElement.lang = lang === "zh" ? "zh-CN" : "en";
  document.title = t("title");
  $("brandLink").textContent = t("title");
  $("langSelect").value = lang;
  document.querySelectorAll("[data-i18n]").forEach((node) => {
    node.textContent = t(node.dataset.i18n);
  });
  document.querySelectorAll("[data-i18n-placeholder]").forEach((node) => {
    node.placeholder = t(node.dataset.i18nPlaceholder);
  });
  document.querySelectorAll(".tab").forEach((tab) => {
    tab.textContent = translations[lang].lists[tab.dataset.list].title;
  });
  $("saveBtn").title = t("saveHint");
  $("logoutBtn").textContent = t("logout");
  $("restartSingboxBtn").textContent = t("restartSingbox");
  $("restartSingboxBtn").title = t("restartHint");
  $("restartTproxyBtn").textContent = t("restartTproxy");
  $("refreshDelayBtn").textContent = t("refreshDelay");
  $("refreshDnsDelayBtn").textContent = t("refreshDnsDelay");
  $("refreshMaintenanceBtn").textContent = t("refreshMaintenance");
  $("restartUiBtn").textContent = t("restartUi");
  $("syncTproxyBtn").textContent = t("syncTproxy");
  $("updateRulesBtn").textContent = t("updateRules");
  $("runtimeView").querySelector('option[value="connections"]').textContent = t("runtimeViewConnections");
  $("runtimeView").querySelector('option[value="logs"]').textContent = t("runtimeViewLogs");
  $("runtimeView").querySelector('option[value="rules"]').textContent = t("runtimeViewRules");
  $("runtimeLogLevel").querySelector('option[value="error"]').textContent = "error";
  $("runtimeLogLevel").querySelector('option[value="warn"]').textContent = "warning";
  $("runtimeLogLevel").querySelector('option[value="info"]').textContent = "info";
  $("runtimeLogLevel").querySelector('option[value="debug"]').textContent = "debug";
  $("nodeSubmit").textContent = editingNodeTag ? t("updateNode") : t("addNode");
  $("nodeCancel").textContent = t("cancelEdit");
  $("nodeTransportMode").querySelector('option[value="bbr"]').textContent = t("transportBbr");
  $("nodeTransportMode").querySelector('option[value="brutal"]').textContent = t("transportBrutal");
  // 批量编辑框的 placeholder 和提示是运行时拼出来的，切换语言时要一起重画
  renderListHint();
}

function goNodes() {
  if ($("app").classList.contains("hidden")) return;
  active = "nodes";
  $("searchInput").value = "";
  setStatus(t("ready"));
  render();
}

function renderMeta() {
  const memory = state.meta?.memory?.rss || "unknown";
  const bytes = state.meta?.memory?.rssBytes || 0;
  let memoryTone = "good";
  if (bytes > 512 * 1024 * 1024) memoryTone = "bad";
  else if (bytes > 256 * 1024 * 1024) memoryTone = "warn";
  $("meta").innerHTML = "";
  const serviceStatus = state.meta.service || "unknown";
  const service = document.createElement("span");
  service.className = `meta-pill service-pill ${serviceStatus === "active" ? "good" : "bad"}`;
  const servicePulse = document.createElement("span");
  servicePulse.className = "memory-pulse";
  const serviceText = document.createElement("span");
  serviceText.textContent = `${t("service")}: ${serviceStatus}`;
  service.append(servicePulse, serviceText);
  const memoryPill = document.createElement("span");
  memoryPill.className = `meta-pill memory-pill ${memoryTone}`;
  const pulse = document.createElement("span");
  pulse.className = "memory-pulse";
  const memoryText = document.createElement("span");
  memoryText.textContent = `${t("memory")}: ${memory}`;
  memoryPill.append(pulse, memoryText);
  const versionPill = document.createElement("span");
  versionPill.className = "meta-pill version-pill";
  versionPill.textContent = `${t("singBoxVersion")}: ${state.meta?.singBoxVersion || "unknown"}`;
  // 配置目录对用户无操作价值（路径固定为 /etc/sing-box），移除该 pill 收敛顶栏信息量
  $("meta").append(service, memoryPill, versionPill);
  if (metaUpdatedAt) {
    const updated = document.createElement("span");
    updated.className = "meta-pill meta-updated time-pill";
    updated.textContent = `${t("updated")}: ${metaUpdatedAt.toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    })}`;
    $("meta").append(updated);
  }
}

function render() {
  applyLanguage();
  renderMeta();
  renderTypeOptions();
  document.querySelectorAll(".tab").forEach((tab) => {
    tab.classList.toggle("active", tab.dataset.list === active);
  });
  $("ruleEditor").classList.toggle("hidden", active === "nodes" || active === "maintenance" || active === "runtime");
  $("nodeEditor").classList.toggle("hidden", active !== "nodes");
  $("maintenanceEditor").classList.toggle("hidden", active !== "maintenance");
  $("runtimeEditor").classList.toggle("hidden", active !== "runtime");
  if (active === "runtime") {
    renderRuntime();
    updateButtons();
    return;
  }
  if (active === "maintenance") {
    renderMaintenance();
    updateButtons();
    return;
  }
  if (active === "nodes") {
    renderNodes();
    updateButtons();
    return;
  }
 const items = state.lists[active] || [];
 const listInfo = translations[lang].lists[active];
 const note = active === "ddns" ? t(ddnsDnsMode() === "remote" ? "ddnsRemoteSummary" : "ddnsLocalSummary") : listInfo.note;
 $("listTitle").textContent = listInfo.title;
 $("listSummary").textContent = `${items.length} ${t("entries")} · ${note}`;

  // 列表视图：用 textarea 替代逐行显示，方便批量粘贴、删除和管理
  renderListTextarea(items);

  // 列表视图隐藏搜索框（用 textarea 的浏览器原生查找即可）
  $("searchInput").style.display = "none";

  const rows = $("rows");
  rows.innerHTML = "";
  rows.appendChild(renderMatchHelp());
  if (active === "ddns") rows.appendChild(renderDdnsControls());
  updateButtons();
}

function formatMaintenanceValue(value) {
  if (Array.isArray(value)) return value.length ? value.join(", ") : t("unknown");
  return value || t("unknown");
}

function statusTone(value) {
  return value === "active" || value === "success" || value === true ? "good" : "warn";
}

function renderMaintenanceItem(label, value, tone = "") {
  const row = document.createElement("div");
  row.className = `maintenance-item ${tone}`;
  const name = document.createElement("span");
  name.textContent = label;
  const detail = document.createElement("strong");
  detail.textContent = formatMaintenanceValue(value);
  row.append(name, detail);
  return row;
}

function renderRuleUpdateSchedule(schedule = {}) {
  const panel = document.createElement("section");
  panel.className = "rule-schedule-panel";

  const head = document.createElement("div");
  const title = document.createElement("h3");
  title.textContent = t("ruleScheduleTitle");
  const note = document.createElement("p");
  note.textContent = t("ruleScheduleNote");
  head.append(title, note);

  const form = document.createElement("div");
  form.className = "rule-schedule-form";

  const frequencyLabel = document.createElement("label");
  const frequencyText = document.createElement("span");
  frequencyText.textContent = t("ruleScheduleFrequency");
  const frequency = document.createElement("select");
  frequency.id = "ruleScheduleFrequencyInput";
  for (const [value, labelKey] of [["weekly", "ruleScheduleWeekly"], ["daily", "ruleScheduleDaily"]]) {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = t(labelKey);
    option.selected = (schedule.frequency || "weekly") === value;
    frequency.appendChild(option);
  }
  frequencyLabel.append(frequencyText, frequency);

  const timeLabel = document.createElement("label");
  const timeText = document.createElement("span");
  timeText.textContent = t("ruleScheduleTime");
  const timeInput = document.createElement("input");
  timeInput.id = "ruleScheduleTimeInput";
  timeInput.type = "time";
  timeInput.value = `${String(Number.isInteger(schedule.hour) ? schedule.hour : 4).padStart(2, "0")}:${String(Number.isInteger(schedule.minute) ? schedule.minute : 20).padStart(2, "0")}`;
  timeLabel.append(timeText, timeInput);

  const delayLabel = document.createElement("label");
  const delayText = document.createElement("span");
  delayText.textContent = t("ruleScheduleDelay");
  const delayInput = document.createElement("input");
  delayInput.id = "ruleScheduleDelayInput";
  delayInput.type = "number";
  delayInput.min = "0";
  delayInput.max = "180";
  delayInput.step = "1";
  delayInput.value = String(scheduleDelayMinutes(schedule));
  delayLabel.append(delayText, delayInput);
  for (const control of [frequency, timeInput, delayInput]) {
    // 自动更新时间是独立的 crond 配置，输入变化要立即反映保存状态，避免用户误以为无法保存。
    control.addEventListener("input", updateButtons);
    control.addEventListener("change", updateButtons);
  }

  form.append(frequencyLabel, timeLabel, delayLabel);
  const save = document.createElement("button");
  save.id = "saveRuleScheduleBtn";
  save.type = "button";
  save.textContent = t("saveRuleSchedule");
  save.disabled = busy || !ruleScheduleChangedFor(schedule);
  save.addEventListener("click", saveRuleUpdateSchedule);
  form.appendChild(save);

  panel.append(head, form);
  return panel;
}

function formatNodeServers(items) {
  if (!Array.isArray(items) || !items.length) return [];
  return items.map((item) => {
    const tag = item.tag ? `${item.tag}: ` : "";
    if (item.address) {
      return item.server === item.address ? `${tag}${item.address}` : `${tag}${item.server} -> ${item.address}`;
    }
    return `${tag}${item.server} -> ${item.error || t("unknown")}`;
  });
}

function renderMaintenanceCard(titleText, items, note = "") {
  const card = document.createElement("section");
  card.className = "maintenance-card";
  const title = document.createElement("h3");
  title.textContent = titleText;
  card.appendChild(title);
  for (const item of items) {
    card.appendChild(renderMaintenanceItem(item[0], item[1], item[2] || ""));
  }
  if (note) {
    const warning = document.createElement("p");
    warning.className = "maintenance-note";
    warning.textContent = note;
    card.appendChild(warning);
  }
  return card;
}

function renderMaintenanceOverview(items) {
  const card = document.createElement("section");
  card.className = "maintenance-overview-card";
  const title = document.createElement("h3");
  title.textContent = t("maintenanceOverview");
  const grid = document.createElement("div");
  grid.className = "maintenance-overview-grid";
  for (const item of items) {
    const tile = document.createElement("div");
    tile.className = `maintenance-overview-tile ${item[2] || ""}`.trim();
    const label = document.createElement("span");
    label.textContent = item[0];
    const value = document.createElement("strong");
    value.textContent = formatMaintenanceValue(item[1]);
    tile.append(label, value);
    grid.appendChild(tile);
  }
  card.append(title, grid);
  return card;
}

function renderHealthSummaryBanner(configHealth) {
  const summary = configHealth?.summary || {};
  const banner = document.createElement("section");
  banner.className = `health-summary-banner ${summary.tone || (configHealth?.ok === false ? "warn" : "good")}`.trim();
  const marker = document.createElement("span");
  marker.className = "health-summary-marker";
  marker.setAttribute("aria-hidden", "true");
  const body = document.createElement("div");
  const label = document.createElement("span");
  label.className = "health-summary-label";
  label.textContent = t("configHealthSummary");
  const value = document.createElement("strong");
  value.textContent = formatHealthSummary(summary);
  const note = document.createElement("div");
  note.className = "health-summary-tier-note";
  note.textContent = t("configHealthTierNote");
  body.append(label, value, note);
  banner.append(marker, body);
  return banner;
}

function formatLocalDnsStatus(item) {
  if (!item || !item.server) return t("unknown");
  return `${item.server}${item.port ? `:${item.port}` : ""}`;
}

function formatFakeipStatus(item) {
  if (!item) return t("unknown");
  return [item.inet4Range, item.inet6Range].filter(Boolean).join(" · ") || t("unknown");
}

function formatHealthSummary(summary) {
  const level = summary?.level || "problem";
  if (level === "great") return t("configHealthGreat");
  if (level === "normal") {
    const reasons = (summary?.reasons || [])
      .map((reason) => t(`configHealthReason${reason.split("_").map((part) => part[0].toUpperCase() + part.slice(1)).join("")}`))
      .filter(Boolean);
    return reasons.length ? `${t("configHealthNormal")}（${reasons.join("、")}）` : t("configHealthNormal");
  }
  const reasons = (summary?.reasons || [])
    .map((reason) => t(`configHealthReason${reason.split("_").map((part) => part[0].toUpperCase() + part.slice(1)).join("")}`))
    .filter(Boolean);
  return reasons.length ? `${t("configHealthProblem")}：${reasons.join("、")}` : t("configHealthProblem");
}

function compactRuleMessages(items) {
  if (!Array.isArray(items) || !items.length) return t("unknown");
  return items
    .map((item) => String(item).replace(/^downloaded\s+/, "").replace(/^installed\s+/, "").replace(/\s+via\s+https?:\/\/\S+$/, ""))
    .join(", ");
}

function ruleNames(items) {
  if (!Array.isArray(items) || !items.length) return "";
  return items
    .map((item) => {
      const match = String(item).match(/(?:for|downloaded|installed)\s+([a-z0-9@!_./-]+\.srs)/i);
      return match ? match[1] : "";
    })
    .filter(Boolean)
    .filter((item, index, arr) => arr.indexOf(item) === index)
    .join(", ");
}

function formatRuleFinal(summary) {
  const status = summary?.status || summary?.final || "";
  if (status === "updated") return t("ruleFinalUpdated");
  if (status === "checked") return t("ruleFinalChecked");
  if (status === "skipped_safe") return t("ruleFinalSkippedSafe");
  const text = String(summary?.final || "");
  if (text.includes("skipped this update safely")) return t("ruleFinalSkippedSafe");
  if (text.includes("config checked")) return t("ruleFinalChecked");
  return text || t("unknown");
}

function isRuleCacheSafe(summary) {
  return (summary?.status || summary?.final || "") === "skipped_safe";
}

function renderMaintenanceDetails(titleText, items, note = "") {
  const details = document.createElement("details");
  details.className = "maintenance-details";
  const summary = document.createElement("summary");
  const title = document.createElement("span");
  title.className = "maintenance-summary-title";
  title.textContent = titleText;
  summary.appendChild(title);
  details.appendChild(summary);
  const body = document.createElement("div");
  body.className = "maintenance-details-body";
  for (const item of items) {
    body.appendChild(renderMaintenanceItem(item[0], item[1], item[2] || ""));
  }
  if (note) {
    const warning = document.createElement("p");
    warning.className = "maintenance-note";
    warning.textContent = note;
    body.appendChild(warning);
  }
  details.appendChild(body);
  return details;
}

function formatLocalDateTime(unixSeconds, fallback = "") {
  const timestamp = Number(unixSeconds);
  if (!Number.isFinite(timestamp) || timestamp <= 0) return fallback;
  const date = new Date(timestamp * 1000);
  const parts = new Intl.DateTimeFormat([], {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
    timeZoneName: "shortOffset",
  }).formatToParts(date);
  const values = Object.fromEntries(parts.filter((part) => part.type !== "literal").map((part) => [part.type, part.value]));
  // 后端保存的是 Unix 时间戳；这里按浏览器时区显示，避免服务器 UTC 时间和用户本地时间混在一起。
  return `${values.year}-${values.month}-${values.day} ${values.hour}:${values.minute}:${values.second} ${values.timeZoneName || ""}`.trim();
}

function formatTelegramCidrSummary(data) {
  const updated = formatLocalDateTime(data?.updatedAtUnix, data?.updatedAt || t("telegramCidrNever"));
  const source = data?.fallback ? t("telegramCidrFallback") : data?.source || t("unknown");
  return t("telegramCidrSummary")
    .replace("{source}", source)
    .replace("{count4}", String(data?.count4 ?? 0))
    .replace("{count6}", String(data?.count6 ?? 0))
    .replace("{updated}", updated);
}

function renderTelegramCidrPanel() {
  const data = maintenance?.telegramCidr || maintenance?.tproxy?.planned?.telegramCidr || {};
  $("telegramCidrSummary").textContent = formatTelegramCidrSummary(data);
  if (document.activeElement !== $("telegramCidrText")) {
    $("telegramCidrText").value = (data.cidrs || []).join("\n");
  }
  $("updateTelegramCidrBtn").textContent = t("updateTelegramCidr");
  $("saveTelegramCidrBtn").textContent = t("saveTelegramCidr");
}

function renderMaintenance() {
  const info = maintenance || {};
  const rule = info.ruleUpdate || {};
  const tproxy = info.tproxy || {};
  const configHealth = info.configHealth || {};
  $("maintenanceTitle").textContent = t("maintenance");
  $("maintenanceSummary").textContent = t("maintenanceNote");
  const rows = $("maintenanceRows");
  rows.innerHTML = "";
  rows.appendChild(renderRuleUpdateSchedule(rule.schedule || {}));
  const summary = rule.summary || {};
  const hasDetails = Boolean((summary.updated || []).length || (summary.kept || []).length || (summary.skipped || []).length || (summary.errors || []).length || summary.final);
  const keptCount = (summary.kept || []).length;
  const errorCount = (summary.errors || []).length;
  const finalTone = errorCount ? "bad" : isRuleCacheSafe(summary) ? "warn" : summary.requiredOk ? "good" : summary.final ? "soft" : "";
  const ruleDetailItems = [
    [t("finalResult"), hasDetails ? formatRuleFinal(summary) : t("noUpdateDetails"), hasDetails ? finalTone : ""],
    [t("updatedCount"), String((summary.updated || []).length), "good"],
    [t("nextUpdate"), rule.next],
    [t("lastUpdate"), rule.last],
    [t("updateScript"), rule.scriptExists ? rule.script : t("unknown"), rule.scriptExists ? "good" : "bad"],
  ];
  if (keptCount) {
    ruleDetailItems.push([t("optionalCount"), `${keptCount} · ${ruleNames(summary.kept)}`, "soft"]);
    ruleDetailItems.push([t("keptRules"), t("optionalCacheOk"), "soft"]);
  }
  if (errorCount) {
    ruleDetailItems.push([t("errorDetails"), compactRuleMessages(summary.errors), "bad"]);
  }

  const updateResult = rule.result || rule.serviceState;

  const overview = renderMaintenanceOverview([
    [t("interfaceMtu"), configHealth.interfaceMtu || t("unknown"), String(configHealth.interfaceMtu) === "1492" || String(configHealth.interfaceMtu) === "1500" ? "good compact" : "soft compact"],
    [t("updateResult"), updateResult, statusTone(updateResult)],
    [t("nextUpdate"), rule.next, rule.next ? "good compact" : ""],
  ]);
  overview.insertBefore(renderHealthSummaryBanner(configHealth), overview.children[1] || null);
  rows.appendChild(overview);

  // 维护页按折叠分组纵向排列，标题只保留箭头和名称，避免右侧状态字干扰扫读。
  rows.appendChild(renderMaintenanceDetails(t("tproxyDetailsTitle"), [
    [t("tproxyService"), tproxy.serviceActive, statusTone(tproxy.serviceActive)],
    [t("defaultInterface"), tproxy.defaultInterface],
    [t("currentIpv4Prefix"), tproxy.currentIpv4Prefixes],
    [t("currentIpv6Prefix"), tproxy.currentIpv6Prefixes],
    [t("fakeipRanges"), [tproxy.planned?.fakeip4, tproxy.planned?.fakeip6].filter(Boolean)],
    [t("telegramCaptureStatus"), tproxy.planned?.telegramCaptureIps ? t("enabled") : t("disabled"), tproxy.planned?.telegramCaptureIps ? "good" : "warn"],
    [t("telegramCidrTitle"), formatTelegramCidrSummary(info.telegramCidr || tproxy.planned?.telegramCidr || {}), (info.telegramCidr || {}).fallback ? "warn" : "good"],
    [t("plannedProxy4"), tproxy.planned?.proxy4],
    [t("plannedProxy6"), tproxy.planned?.proxy6],
    [t("nodeServerIps"), formatNodeServers(tproxy.outboundServers) || tproxy.outboundServerIps],
    [t("scriptIpv6Prefix"), tproxy.scriptIpv6Prefixes, tproxy.ipv6PrefixMatches ? "good" : "warn"],
    [t("plannedBypass4"), tproxy.planned?.bypass4],
    [t("plannedBypass6"), tproxy.planned?.bypass6],
  ], `${t("tproxyPolicy")}${tproxy.ipv6PrefixMatches === false ? ` ${t("prefixMismatch")}` : ""}`));
  rows.appendChild(renderMaintenanceDetails(t("configHealthTitle"), [
    [t("configHealthStatus"), configHealth.ok === false ? t("configHealthWarn") : t("configHealthOk"), configHealth.ok === false ? "warn" : "good"],
    [t("activeLocalDns"), formatLocalDnsStatus(configHealth.localDns), configHealth.localDns?.server ? "good" : "warn"],
    [t("activeFakeip"), formatFakeipStatus(configHealth.fakeip), configHealth.fakeipRouteOk === false ? "warn" : "good"],
    [t("fakeipRouteStatus"), configHealth.fakeipRouteOk === false ? t("fakeipRouteWarn") : t("fakeipRouteOk"), configHealth.fakeipRouteOk === false ? "warn" : "good"],
    [t("routeOrderStatus"), configHealth.routeOrderOk === false ? t("routeOrderWarn") : t("routeOrderOk"), configHealth.routeOrderOk === false ? "warn" : "good"],
    [t("routeFinal"), configHealth.routeFinal || t("unknown"), configHealth.routeFinal === "direct" ? "good" : "warn"],
    [t("interfaceMtu"), configHealth.interfaceMtu || t("unknown"), String(configHealth.interfaceMtu) === "1492" || String(configHealth.interfaceMtu) === "1500" ? "good" : "soft"],
    [t("routeRuleCount"), configHealth.routeRules ?? 0],
    [t("dnsRuleCount"), configHealth.dnsRules ?? 0],
    [t("ruleSetCount"), configHealth.ruleSets ?? 0],
    [t("outboundCount"), configHealth.outbounds ?? 0],
    [t("udp443RejectCount"), configHealth.udp443RejectRules ?? 0, Number(configHealth.udp443RejectRules || 0) > 2 ? "warn" : "good"],
    [t("configHealthSummary"), formatHealthSummary(configHealth.summary), configHealth.summary?.tone || (configHealth.ok === false ? "warn" : "good")],
  ]));
  rows.appendChild(renderMaintenanceDetails(t("ruleUpdateTitle"), ruleDetailItems));
  renderTelegramCidrPanel();
}

function formatBytes(value) {
  const bytes = Number(value || 0);
  if (bytes >= 1024 * 1024) return `${(bytes / 1024 / 1024).toFixed(1)} MiB`;
  if (bytes >= 1024) return `${(bytes / 1024).toFixed(1)} KiB`;
  return `${bytes} B`;
}

function formatRate(value) {
  const bytes = Number(value || 0);
  if (bytes >= 1024 * 1024) return `${(bytes / 1024 / 1024).toFixed(1)} MB/s`;
  if (bytes >= 1024) return `${(bytes / 1024).toFixed(1)} kB/s`;
  return `${bytes} B/s`;
}

function runtimeCard(title, meta, detail) {
  const card = document.createElement("section");
  card.className = "runtime-card";
  const head = document.createElement("div");
  head.className = "runtime-card-head";
  const name = document.createElement("strong");
  name.textContent = title || t("unknown");
  const small = document.createElement("small");
  small.textContent = meta || "";
  head.append(name, small);
  const body = document.createElement("p");
  body.textContent = detail || "";
  card.append(head, body);
  return card;
}

function renderRuntimeConnections(rows) {
  if (!rows.length) return renderRuntimeEmpty();
  const table = document.createElement("div");
  table.className = "runtime-table connections-table";
  const header = document.createElement("div");
  header.className = "runtime-table-row runtime-table-head";
  [t("connectionHost"), t("connectionType"), t("connectionRoute"), t("connectionChain")].forEach((label) => {
    const cell = document.createElement("span");
    cell.textContent = label;
    header.appendChild(cell);
  });
  table.appendChild(header);
  for (const item of rows) {
    const metadata = item.metadata || {};
    const host = `${metadata.host || metadata.destinationIP || ""}${metadata.destinationPort ? `:${metadata.destinationPort}` : ""}` || t("unknown");
    const chain = Array.isArray(item.chains) ? item.chains.join(" -> ") : "";
    const row = document.createElement("div");
    row.className = "runtime-table-row";
    const hostCell = document.createElement("strong");
    hostCell.textContent = host;
    const type = document.createElement("span");
    type.className = "runtime-type-pill";
    type.textContent = `${metadata.type || ""}${metadata.network ? ` | ${metadata.network}` : ""}` || t("unknown");
    const rule = document.createElement("span");
    rule.textContent = item.rule || t("unknown");
    const chainCell = document.createElement("span");
    chainCell.textContent = chain || t("unknown");
    row.append(hostCell, type, rule, chainCell);
    table.appendChild(row);
  }
  return table;
}

function renderRuntimeRules(rows) {
  if (!rows.length) return renderRuntimeEmpty();
  const frag = document.createDocumentFragment();
  rows.forEach((item, index) => {
    const card = document.createElement("section");
    card.className = "runtime-rule-card";
    const head = document.createElement("div");
    head.className = "runtime-rule-head";
    const no = document.createElement("span");
    no.className = "runtime-rule-no";
    no.textContent = `#${index + 1}`;
    const payload = document.createElement("strong");
    payload.textContent = item.payload || t("unknown");
    const target = document.createElement("span");
    const proxy = item.proxy || t("unknown");
    const targetKey = String(proxy).match(/\(([^)]+)\)/)?.[1] || proxy;
    target.className = `runtime-rule-target ${String(targetKey).toLowerCase().replace(/[^a-z0-9_-]+/g, "-")}`;
    target.textContent = targetKey;
    const raw = document.createElement("small");
    raw.textContent = `${t("ruleTarget")}: ${proxy}`;
    head.append(no, payload, target);
    card.append(head, raw);
    frag.appendChild(card);
  });
  return frag;
}

function renderRuntimeLogs() {
  if (!runtime.logLines.length) return renderRuntimeEmpty(logStreamController ? (runtime.logIdle ? t("idleRuntimeLogs") : t("waitingRuntimeLogs")) : t("noRuntimeRows"));
  const list = document.createElement("div");
  list.className = "runtime-log-list";
  runtime.logLines.forEach((raw, index) => {
    let level = "info";
    let payload = raw;
    try {
      const item = JSON.parse(raw);
      level = item.type || level;
      payload = item.payload || raw;
    } catch (error) {
      const match = raw.match(/"type":"([^"]+)".*"payload":"(.*)"}/);
      if (match) {
        level = match[1];
        payload = match[2];
      } else {
        const plainLevel = raw.match(/\b(ERROR|WARN|WARNING|INFO|DEBUG|TRACE|FATAL|PANIC)\b/i);
        if (plainLevel) level = plainLevel[1].toLowerCase();
      }
    }
    const row = document.createElement("div");
    row.className = "runtime-log-row";
    const no = document.createElement("span");
    no.className = "runtime-log-no";
    no.textContent = String(Math.max(1, runtime.logLines.length - index));
    const badge = document.createElement("span");
    badge.className = `runtime-log-level ${level}`;
    badge.textContent = level;
    const message = document.createElement("code");
    message.textContent = payload;
    row.append(no, badge, message);
    list.appendChild(row);
  });
  return list;
}

function renderRuntimeEmpty(message = t("noRuntimeRows")) {
  const empty = document.createElement("div");
  empty.className = message === t("waitingRuntimeLogs") ? "runtime-waiting" : "empty";
  if (message === t("waitingRuntimeLogs")) {
    const pulse = document.createElement("span");
    pulse.className = "runtime-waiting-pulse";
    const text = document.createElement("strong");
    text.textContent = message;
    empty.append(pulse, text);
  } else {
    empty.textContent = message;
  }
  return empty;
}

function renderRuntime() {
  $("runtimeTitle").textContent = t("runtime");
  $("runtimeSummary").textContent = t("runtimeNote");
  const view = $("runtimeView").value || "connections";
  $("runtimeLogLevel").classList.toggle("hidden", view !== "logs");
  $("runtimeLogLevel").value = runtime.logLevel === "warning" ? "warn" : runtime.logLevel || "warn";
  const rows = $("runtimeRows");
  rows.innerHTML = "";
  if (view === "connections") rows.appendChild(renderRuntimeConnections(runtime.connections || []));
  else if (view === "rules") rows.appendChild(renderRuntimeRules(runtime.rules || []));
  else rows.appendChild(renderRuntimeLogs());
}

async function changeRuntimeLogLevel() {
  const level = $("runtimeLogLevel").value;
  setBusy(true);
  setStatus(t("refreshingRuntime"));
  try {
    const result = await api("/api/runtime/log-level", { method: "POST", body: JSON.stringify({ level }) });
    if (!result.ok) throw new Error(result.error || t("actionFailed"));
    runtime.logLevel = result.level || level;
    if (result.state) state = result.state;
    stopRuntimeLogs(false);
    render();
    setStatus(t("logLevelSaved"), "ok");
    setTimeout(() => {
      if (active === "runtime" && $("runtimeView").value === "logs" && !logStreamController) startRuntimeLogs();
    }, 1200);
  } catch (error) {
    setStatus(error.message, "bad");
    $("runtimeLogLevel").value = runtime.logLevel === "warning" ? "warn" : runtime.logLevel || "warn";
  } finally {
    setBusy(false);
  }
}

function stopRuntimePolling() {
  if (runtimePollTimer) {
    clearInterval(runtimePollTimer);
    runtimePollTimer = null;
  }
}

function ensureRuntimePolling() {
  stopRuntimePolling();
  if (active !== "runtime" || $("runtimeView").value !== "connections") return;
  runtimePollTimer = setInterval(() => {
    if (!busy && active === "runtime" && $("runtimeView").value === "connections") {
      refreshRuntime({ quiet: true });
    }
  }, 2500);
}

async function refreshRuntime(options = {}) {
  const view = $("runtimeView").value || "connections";
  if (view === "logs") {
    renderRuntime();
    if (!logStreamController) startRuntimeLogs();
    return;
  }
  if (!options.quiet) setStatus(t("refreshingRuntime"));
  try {
    const result = await api(`/api/runtime/${view}`);
    if (!result.runtime?.ok) throw new Error(result.runtime?.error || t("runtimeUnavailable"));
    if (view === "connections") runtime.connections = result.runtime.data?.connections || [];
    if (view === "rules") runtime.rules = result.runtime.data?.rules || [];
    runtime.logLevel = result.logLevel || runtime.logLevel;
    render();
    if (view === "connections") ensureRuntimePolling();
    if (!options.quiet) setStatus(t("runtimeRefreshed"), "ok");
  } catch (error) {
    if (!options.quiet) setStatus(error.message, "bad");
  } finally {
  }
}

function stopRuntimeLogs(updateStatus = true) {
  if (logStreamController) {
    logStreamController.abort();
    logStreamController = null;
  }
  if (updateStatus) {
    render();
    setStatus(t("logsStopped"), "ok");
  }
}

async function startRuntimeLogs() {
  stopRuntimeLogs(false);
  runtime.logLines = [];
  runtime.logIdle = false;
  const controller = new AbortController();
  logStreamController = controller;
  render();
  setStatus(t("logsStreaming"), "ok");
  const idleTimer = setTimeout(() => {
    if (logStreamController === controller && !runtime.logLines.length) {
      runtime.logIdle = true;
      if (active === "runtime" && $("runtimeView").value === "logs") renderRuntime();
    }
  }, 6000);
  try {
    const headers = {};
    if (token) headers.Authorization = `Bearer ${token}`;
    const level = runtime.logLevel === "warning" ? "warn" : runtime.logLevel || "warn";
    const response = await fetch(`/api/runtime/logs?level=${encodeURIComponent(level)}`, { headers, signal: controller.signal });
    if (!response.ok) throw new Error(`${t("runtimeUnavailable")}: HTTP ${response.status}`);
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    while (logStreamController === controller) {
      const { value, done } = await reader.read();
      if (done) break;
      const text = decoder.decode(value, { stream: true });
      runtime.logLines.push(...text.split(/\r?\n/).filter(Boolean));
      runtime.logLines = runtime.logLines.slice(-300);
      runtime.logIdle = false;
      if (active === "runtime" && $("runtimeView").value === "logs") renderRuntime();
    }
  } catch (error) {
    if (error.name !== "AbortError") setStatus(error.message, "bad");
  } finally {
    clearTimeout(idleTimer);
    if (logStreamController === controller) logStreamController = null;
    if (active === "runtime") renderRuntime();
  }
}

async function refreshMaintenance() {
  setBusy(true);
  pulseActionButton("refreshMaintenanceBtn", "refreshingMaintenance");
  setStatus(t("refreshingMaintenance"));
  try {
    const result = await api("/api/maintenance");
    maintenance = result.maintenance || {};
    if (result.state) state = result.state;
    render();
    finishActionButton("refreshMaintenanceBtn", "actionDone", "done", "refreshMaintenance");
    setStatus(t("maintenanceRefreshed"), "ok");
  } catch (error) {
    finishActionButton("refreshMaintenanceBtn", "actionFailed", "failed", "refreshMaintenance");
    setStatus(error.message, "bad");
  } finally {
    setBusy(false);
  }
}

async function updateRuleSets() {
  setBusy(true);
  pulseActionButton("updateRulesBtn", "updatingRules");
  setStatus(t("updatingRules"));
  maintenance.ruleUpdate = maintenance.ruleUpdate || {};
  maintenance.ruleUpdate.result = t("updatingRules");
  maintenance.ruleUpdate.summary = { updated: [], kept: [], skipped: [], errors: [], final: t("ruleUpdateRunning") };
  render();
  try {
    const result = await api("/api/rules/update", { method: "POST", body: "{}" });
    maintenance = result.maintenance || maintenance;
    if (result.update?.summary) {
      maintenance.ruleUpdate = maintenance.ruleUpdate || {};
      maintenance.ruleUpdate.summary = result.update.summary;
      maintenance.ruleUpdate.result = result.update.code === 0 ? "success" : result.update.code === 124 ? "slow" : "failed";
      maintenance.ruleUpdate.log = [result.update.stdout, result.update.stderr].filter(Boolean).join("\n");
    }
    if (result.state) state = result.state;
    render();
    if (result.update?.code !== 0) {
      if (result.update?.code === 124) {
        finishActionButton("updateRulesBtn", "actionDone", "done", "updateRules");
        setStatus(t("ruleUpdateSlow"), "ok");
      } else {
        finishActionButton("updateRulesBtn", "actionFailed", "failed", "updateRules");
        setStatus(result.update?.stderr || t("restartFailed"), "bad");
      }
      return;
    }
    finishActionButton("updateRulesBtn", "actionDone", "done", "updateRules");
    setStatus(t("rulesUpdated"), "ok");
  } catch (error) {
    finishActionButton("updateRulesBtn", "actionFailed", "failed", "updateRules");
    setStatus(error.message, "bad");
  } finally {
    setBusy(false);
  }
}

async function saveRuleUpdateSchedule() {
  const [hour = "", minute = ""] = $("ruleScheduleTimeInput").value.split(":");
  const payload = {
    frequency: $("ruleScheduleFrequencyInput").value,
    hour,
    minute,
    randomizedDelayMinutes: $("ruleScheduleDelayInput").value,
  };
  setBusy(true);
  pulseActionButton("saveRuleScheduleBtn", "savingRuleSchedule");
  setStatus(t("savingRuleSchedule"));
  try {
    const result = await api("/api/rules/schedule", { method: "POST", body: JSON.stringify(payload) });
    maintenance = result.maintenance || maintenance;
    if (result.state) state = result.state;
    render();
    if (!result.scheduleUpdate?.ok) {
      finishActionButton("saveRuleScheduleBtn", "actionFailed", "failed", "saveRuleSchedule");
      setStatus(result.scheduleUpdate?.restart?.stderr || result.scheduleUpdate?.daemonReload?.stderr || t("actionFailed"), "bad");
      return;
    }
    finishActionButton("saveRuleScheduleBtn", "actionDone", "done", "saveRuleSchedule");
    setStatus(t("ruleScheduleSaved"), "ok");
  } catch (error) {
    finishActionButton("saveRuleScheduleBtn", "actionFailed", "failed", "saveRuleSchedule");
    setStatus(error.message, "bad");
  } finally {
    setBusy(false);
  }
}

async function updateTelegramCidr() {
  setBusy(true);
  pulseActionButton("updateTelegramCidrBtn", "updatingTelegramCidr");
  setStatus(t("updatingTelegramCidr"));
  try {
    const result = await api("/api/telegram-cidr/update", { method: "POST", body: "{}" });
    maintenance = result.maintenance || maintenance;
    if (result.state) state = result.state;
    render();
    if (!result.telegramCidrUpdate?.ok) {
      finishActionButton("updateTelegramCidrBtn", "actionFailed", "failed", "updateTelegramCidr");
      setStatus((result.telegramCidrUpdate?.errors || []).join("; ") || t("telegramCidrUpdateFailed"), "bad");
      return;
    }
    finishActionButton("updateTelegramCidrBtn", "actionDone", "done", "updateTelegramCidr");
    setStatus(t("telegramCidrUpdated"), "ok");
  } catch (error) {
    finishActionButton("updateTelegramCidrBtn", "actionFailed", "failed", "updateTelegramCidr");
    setStatus(error.message, "bad");
  } finally {
    setBusy(false);
  }
}

async function saveTelegramCidr() {
  setBusy(true);
  pulseActionButton("saveTelegramCidrBtn", "savingTelegramCidr");
  setStatus(t("savingTelegramCidr"));
  try {
    const result = await api("/api/telegram-cidr/save", {
      method: "POST",
      body: JSON.stringify({ cidrs: $("telegramCidrText").value }),
    });
    maintenance = result.maintenance || maintenance;
    if (result.state) state = result.state;
    render();
    if (result.tproxySync?.code !== 0) {
      finishActionButton("saveTelegramCidrBtn", "actionFailed", "failed", "saveTelegramCidr");
      setStatus(result.tproxySync?.stderr || t("tproxySyncFailed"), "bad");
      return;
    }
    finishActionButton("saveTelegramCidrBtn", "actionDone", "done", "saveTelegramCidr");
    setStatus(t("telegramCidrSaved"), "ok");
  } catch (error) {
    finishActionButton("saveTelegramCidrBtn", "actionFailed", "failed", "saveTelegramCidr");
    setStatus(error.message, "bad");
  } finally {
    setBusy(false);
  }
}

async function syncTproxy() {
  setBusy(true);
  pulseActionButton("syncTproxyBtn", "syncingTproxy");
  setStatus(t("syncingTproxy"));
  try {
    const result = await api("/api/tproxy/sync", { method: "POST", body: "{}" });
    maintenance = result.maintenance || maintenance;
    if (result.state) state = result.state;
    render();
    if (result.sync?.code !== 0) {
      finishActionButton("syncTproxyBtn", "actionFailed", "failed", "syncTproxy");
      setStatus(result.sync?.stderr || t("tproxySyncFailed"), "bad");
      return;
    }
    finishActionButton("syncTproxyBtn", "actionDone", "done", "syncTproxy");
    setStatus(t("tproxySynced"), "ok");
  } catch (error) {
    finishActionButton("syncTproxyBtn", "actionFailed", "failed", "syncTproxy");
    setStatus(`${t("tproxySyncFailed")} ${error.message}`, "bad");
  } finally {
    setBusy(false);
  }
}

async function exportBackup() {
  setBusy(true);
  pulseActionButton("exportBackupBtn", "exportingBackup");
  setStatus(t("exportingBackup"));
  try {
    const headers = {};
    if (token) headers.Authorization = `Bearer ${token}`;
    const response = await fetch("/api/backup/export", { headers });
    if (!response.ok) {
      const body = await response.json().catch(() => ({}));
      throw new Error(body.error || `HTTP ${response.status}`);
    }
    const blob = await response.blob();
    const disposition = response.headers.get("Content-Disposition") || "";
    const match = disposition.match(/filename="([^"]+)"/);
    const filename = match ? match[1] : `sing-box-gateway-ui-backup-${Date.now()}.json`;
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
    finishActionButton("exportBackupBtn", "actionDone", "done", "exportBackup");
    setStatus(t("backupExported"), "ok");
    window.alert(t("backupExportedAlert"));
  } catch (error) {
    finishActionButton("exportBackupBtn", "actionFailed", "failed", "exportBackup");
    setStatus(error.message, "bad");
  } finally {
    setBusy(false);
  }
}

function chooseBackupFile() {
  $("backupFileInput").value = "";
  $("backupFileInput").click();
}

async function changeAccessToken() {
  const newToken = $("newTokenInput").value.trim();
  if (newToken.length < 6) {
    setStatus(t("tokenTooShort"), "bad");
    return;
  }
  setBusy(true);
  pulseActionButton("changeTokenBtn", "changingToken");
  try {
    const result = await api("/api/token/change", {
      method: "POST",
      body: JSON.stringify({ token: newToken }),
    });
    // 后端已落盘新 token；立即同步内存与 localStorage，否则下一个请求就会 401。
    token = result.token;
    localStorage.setItem("ruleUiToken", token);
    $("newTokenInput").value = "";
    finishActionButton("changeTokenBtn", "actionDone", "done", "changeToken");
    setStatus(t("tokenChanged"), "ok");
  } catch (error) {
    finishActionButton("changeTokenBtn", "actionFailed", "failed", "changeToken");
    setStatus(error.message, "bad");
  } finally {
    setBusy(false);
  }
}

async function importBackupFromFile(event) {
  const file = event.target.files && event.target.files[0];
  event.target.value = "";
  if (!file) return;
  setBusy(true);
  pulseActionButton("importBackupBtn", "importingBackup");
  setStatus(t("importingBackup"));
  try {
    const payload = JSON.parse(await file.text());
    const result = await api("/api/backup/import", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    state = result.state;
    maintenance = result.maintenance || maintenance;
    // 导入成功后运行态由后端后台重启应用；先清掉旧缓存，再延迟刷新，避免当前 fetch 被 OpenRC 重启链路打断。
    runtimeProxy = { now: null, available: false };
    delays = {};
    applyProxyPayload(result);
    setDirty(false);
    render();
    if (result.tproxySync && result.tproxySync.code !== 0) {
      finishActionButton("importBackupBtn", "actionFailed", "failed", "importBackup");
      setStatus(`${t("backupImported")}；${t("tproxySyncFailed")}`, "bad");
      return;
    }
    finishActionButton("importBackupBtn", "actionDone", "done", "importBackup");
    setStatus(t("backupImported"), "ok");
    window.alert(t("backupImportedAlert"));
    if (result.applyScheduled) {
      refreshMaintenance().catch(() => {});
      pollDelaysAfterImport();
    } else if (!result.delays) loadProxyInfo(false).then(() => render()).catch(() => {});
  } catch (error) {
    finishActionButton("importBackupBtn", "actionFailed", "failed", "importBackup");
    setStatus(error.message || t("backupImportFailed"), "bad");
  } finally {
    setBusy(false);
  }
}

async function pollDelaysAfterImport(maxAttempts = 5, interval = 3500) {
  for (let i = 0; i < maxAttempts; i++) {
    if (i > 0) await sleep(interval);
    try {
      await loadProxyInfo(false);
      render();
      const hasDelays = Object.values(delays).some((d) => d?.ok && typeof d.delay === "number");
      if (hasDelays) return;
    } catch (e) {}
  }
  try {
    await loadProxyInfo(true);
    await loadProxyInfo(false);
    render();
  } catch (e) {}
}

function allowedEntryTypes() {
  return listEntryTypes[active] || allEntryTypes;
}

function renderTypeOptions() {
  const select = $("typeInput");
  const current = allowedEntryTypes().includes(select.value) ? select.value : allowedEntryTypes()[0];
  select.innerHTML = "";
  for (const type of allowedEntryTypes()) {
    const option = document.createElement("option");
    option.value = type;
    option.textContent = translations[lang].types[type];
    option.selected = type === current;
    select.appendChild(option);
  }
  updateValueHint();
  renderListHint();
}

// renderListHint - 按当前表允许的类型生成 textarea 的 placeholder 和下方提示。
// 之前这段是 index.html 里的硬编码中文，有三个问题：
//   1. ddns 表只支持 domain_suffix/domain，却照样列出 5 种类型，照着填后端直接拒；
//   2. 英文界面下也显示中文；
//   3. 没有说明"正则保留大小写、其余转小写"和 IPv6 需显式前缀，用户容易踩坑。
function renderListHint() {
  const hint = $("listTextareaHint");
  const ta = $("listTextarea");
  if (!hint || !ta) return;
  const types = allowedEntryTypes();
  const dict = translations[lang];
  const h = dict.textareaHint || {};
  const labels = dict.types || {};
  const ph = dict.placeholders || {};
  const defaultType = ($("typeInput") && $("typeInput").value) || types[0];

  // placeholder：每种允许的类型给一行示例，用英文前缀（解析器和后端的规范写法）
  const lines = types.map((type) => `${type}: ${ph[type] || "example.com"}`);
  lines.push(h.fallbackShort || (lang === "zh" ? "也可以直接粘贴纯域名" : "or paste bare domains"));
  ta.placeholder = lines.join("\n");

  // 提示正文：只列当前表允许的类型
  const typeList = types.map((type) => `<code>${type}</code>（${labels[type] || type}）`).join("、");
  const example = `<code>${ph[defaultType] || "google.com"}</code>`;
  const applied = `<code>${defaultType}: ${ph[defaultType] || "google.com"}</code>`;
  const fallback = String(h.fallback || "")
    .replace("{example}", example)
    .replace("{applied}", applied);

  const parts = [
    `${h.format || ""} <code>type: value</code>。`,
    `${h.types || ""}${typeList}。`,
    fallback,
    h.caseNote,
  ];
  // 只有该表允许对应类型时才提示相关注意事项，避免 ddns 显示用不上的说明
  if (types.includes("domain_regex")) parts.push(h.regexNote);
  if (types.includes("ip_cidr")) parts.push(h.ipv6Note, h.cidrNote);
  parts.push(h.urlNote);
  hint.innerHTML = parts.filter(Boolean).join(" ");
}


function updateValueHint() {
  const type = $("typeInput").value || allowedEntryTypes()[0];
  $("valueInput").placeholder = translations[lang].placeholders[type] || "example.com";
}

function renderMatchHelp() {
  const box = document.createElement("section");
  box.className = "match-help";
  const title = document.createElement("strong");
  title.textContent = t("matchHelp");
  const listNote = document.createElement("p");
  listNote.className = "route-notice";
  listNote.textContent = active === "greylist" ? translations[lang].greylistRouteNotice : translations[lang].listTypeHelp[active];
  const examples = document.createElement("div");
  examples.className = "match-examples";
  for (const type of allowedEntryTypes()) {
    const item = document.createElement("span");
    const label = document.createElement("b");
    label.textContent = translations[lang].types[type];
    const help = translations[lang].typeHelp[type];
    const detail = document.createElement("small");
    detail.textContent = `${help.use}; ${lang === "zh" ? "例如" : "example"}: ${help.example}`;
    item.append(label, detail);
    examples.appendChild(item);
  }
  box.append(title, listNote);
  box.appendChild(examples);
  return box;
}

function ddnsDnsMode() {
  state.groups.ddns = state.groups.ddns || {};
  return state.groups.ddns.dns === "remote" ? "remote" : "local";
}

function renderDdnsControls() {
  const panel = document.createElement("section");
  panel.className = "ddns-mode";
  const copy = document.createElement("div");
  const title = document.createElement("strong");
  title.textContent = t("dnsMode");
  const hint = document.createElement("div");
  hint.className = "ddns-hint";
  const lines = translations[lang][ddnsDnsMode() === "remote" ? "ddnsRemoteHint" : "ddnsLocalHint"];
  for (const line of lines) {
    const item = document.createElement("p");
    item.textContent = line;
    hint.appendChild(item);
  }
  copy.append(title, hint);
  const switcher = document.createElement("div");
  switcher.className = "segment";
  [
    ["local", t("ddnsLocalDns")],
    ["remote", t("ddnsRemoteDns")],
  ].forEach(([mode, label]) => {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = label;
    button.className = ddnsDnsMode() === mode ? "active" : "";
    button.addEventListener("click", () => setDdnsDnsMode(mode));
    switcher.appendChild(button);
  });
  panel.append(copy, switcher);
  return panel;
}

function setDdnsDnsMode(mode) {
  state.groups.ddns = state.groups.ddns || {};
  if (state.groups.ddns.dns === mode) return;
  state.groups.ddns.dns = mode;
  markChanged();
  render();
}

function nodeTags() {
  return (state.nodes || []).map((node) => node.outbound.tag);
}

function enabledNodeTags() {
  return (state.nodes || []).filter((node) => node.enabled !== false).map((node) => node.outbound.tag);
}

function renderDefaultSelect() {
  const select = $("proxyDefault");
  const current = state.groups?.proxy?.default || "Auto";
  const options = ["Auto", ...enabledNodeTags()];
  select.innerHTML = "";
  for (const tag of options) {
    const option = document.createElement("option");
    option.value = tag;
    const autoTag = autoDisplayTag();
    const label = tag === "Auto" && autoTag ? `Auto -> ${autoTag}` : tag;
    option.textContent = `${t("defaultProxy")}: ${label}`;
    option.selected = tag === current;
    select.appendChild(option);
  }
}

function currentDefault() {
  return state.groups?.proxy?.default || "Auto";
}

function formatDelay(tag) {
  const item = delays[tag];
  if (!item) return t("delayUnknown");
  if (item.delay === null || item.delay === undefined) return item.error ? t("delayFailed") : t("delayUnknown");
  return `${item.delay} ms`;
}

function delayTone(tag) {
  const item = delays[tag];
  if (!item || item.delay === null || item.delay === undefined) return "unknown";
  if (item.delay <= 180) return "good";
  if (item.delay <= 450) return "warn";
  return "bad";
}

function autoDisplayTag() {
  // Auto 的真实选择只能以 Clash API 的 Auto.now 为准；延迟 history 只用于展示，不能推断当前出站。
  return runtimeProxy.autoNow || "";
}

function dnsChoices() {
  return state.meta?.dnsChoices || {};
}

function currentLocalDns() {
  state.groups.dns = state.groups.dns || {};
  if (!state.groups.dns.local || !dnsChoices()[state.groups.dns.local]) state.groups.dns.local = "alidns";
  return state.groups.dns.local;
}

function dnsChoiceDisplay(key, item) {
  if (key !== "custom_dns") return `${item.label} · ${item.server}`;
  const groupsDns = state.groups?.dns || {};
  const server = groupsDns.local_custom_server || "223.5.5.5";
  const port = Number(groupsDns.local_custom_port || 53);
  return `${item.label} · ${server}${port && port !== 53 ? `:${port}` : ""}`;
}

function renderLocalDnsSettings() {
  const select = $("localDnsSelect");
  const current = currentLocalDns();
  select.innerHTML = "";
  for (const [key, item] of Object.entries(dnsChoices())) {
    const option = document.createElement("option");
    option.value = key;
    option.textContent = dnsChoiceDisplay(key, item);
    select.appendChild(option);
  }
  select.value = current;
  const rows = $("dnsDelayRows");
  rows.innerHTML = "";
  const choices = Object.entries(dnsChoices());
  if (!choices.length) {
    rows.textContent = t("dnsDelayEmpty");
    return;
  }
  for (const [key, item] of choices) {
    const measured = dnsDelays[key];
    const row = document.createElement("div");
    row.className = `dns-delay-row ${key === current ? "selected" : ""} ${measured?.ok ? "good" : measured ? "bad" : ""}`;
    const name = document.createElement("strong");
    name.textContent = dnsChoiceDisplay(key, item);
    const value = document.createElement("span");
    value.className = "dns-delay-value";
    const delayEl = document.createElement("span");
    delayEl.className = "dns-delay-ms";
    const hostEl = document.createElement("span");
    hostEl.className = "dns-delay-host";
    if (!measured) {
      delayEl.textContent = t("dnsDelayEmpty");
    } else if (measured.ok) {
      delayEl.textContent = `${measured.delay} ms`;
      hostEl.textContent = dnsDelayHost || "";
    } else {
      delayEl.textContent = `${t("dnsDelayFailed")}: ${measured.error || t("unknown")}`;
    }
    value.append(delayEl, hostEl);
    row.append(name, value);
    rows.appendChild(row);
  }
  const fields = $("customDnsFields");
  const serverInput = $("customDnsServer");
  const portInput = $("customDnsPort");
  serverInput.value = (state.groups.dns || {}).local_custom_server || "223.5.5.5";
  portInput.value = (state.groups.dns || {}).local_custom_port || 53;
  if (current === "custom_dns") {
    fields.classList.remove("hidden");
  } else {
    fields.classList.add("hidden");
  }
}

function activeProxyLabel() {
  if (!runtimeProxy.now) return "";
  const autoTag = autoDisplayTag();
  if (runtimeProxy.now === "Auto" && autoTag) return `Auto -> ${autoTag}`;
  return runtimeProxy.now;
}

function renderNodes() {
  const nodes = state.nodes || [];
  state.groups.proxy = state.groups.proxy || {};
  state.groups.auto = state.groups.auto || {};
  state.groups.dns = state.groups.dns || {};
  state.groups.fakeip = state.groups.fakeip || {};
  state.groups.telegram = state.groups.telegram || {};
  if (document.activeElement !== $("autoUrl")) $("autoUrl").value = state.groups.auto.url || "https://www.gstatic.com/generate_204";
  if (document.activeElement !== $("autoInterval")) $("autoInterval").value = state.groups.auto.interval || "30s";
  // 官方语义：idle_timeout 是「空闲超时后停止周期测速」（省资源，见 protocol/group/urltest.go
  // loopCheck），不是重新测速；tolerance 才是节点接替的防抖阈值（Select 里 minDelay > delay+tolerance）。
  if (document.activeElement !== $("autoIdleTimeout")) $("autoIdleTimeout").value = state.groups.auto.idle_timeout || "30m";
  if (document.activeElement !== $("autoTolerance")) {
    $("autoTolerance").value = state.groups.auto.tolerance ?? 50;
  }
  $("interruptConnections").checked =
    state.groups.proxy.interrupt_exist_connections === true || state.groups.auto.interrupt_exist_connections === true;
  renderLocalDnsSettings();
  if (document.activeElement !== $("fakeipV4")) $("fakeipV4").value = state.groups.fakeip.inet4_range || "28.0.0.0/8";
  if (document.activeElement !== $("fakeipV6")) $("fakeipV6").value = state.groups.fakeip.inet6_range || "2001:2::/64";
  $("fakeipIpv6Enabled").checked = state.groups.fakeip.ipv6_enabled !== false;
  $("telegramCaptureIps").checked = state.groups.telegram.capture_ips !== false;
  state.groups.socks5 = state.groups.socks5 || {};
  if (document.activeElement !== $("socks5Port")) $("socks5Port").value = state.groups.socks5.port || 0;
  $("nodeTitle").textContent = t("nodes");
  $("nodeSummary").textContent = editingNodeTag
    ? `${t("editingNode")}: ${editingNodeTag}`
    : `${nodes.length} ${t("entries")} · ${t("defaultProxy")}: ${currentDefault()}${activeProxyLabel() ? ` · ${t("activeProxy")}: ${activeProxyLabel()}` : ""}`;
  $("nodeSubmit").textContent = editingNodeTag ? t("updateNode") : t("addNode");
  $("nodeCancel").classList.toggle("hidden", !editingNodeTag);
  renderDefaultSelect();
  const _r = $("nodeRows");
  const rows = _r.cloneNode(false);
  if (!nodes.length) {
    const empty = document.createElement("div");
    empty.className = "empty";
    empty.textContent = t("noEntries");
    rows.appendChild(empty);
    _r.replaceWith(rows);
    return;
  }
  const autoCard = document.createElement("div");
  autoCard.className = `node-card auto-card ${currentDefault() === "Auto" ? "default" : ""} ${runtimeProxy.now === "Auto" ? "runtime" : ""}`;
  const autoTitle = document.createElement("div");
  autoTitle.className = "node-title";
  const autoName = document.createElement("strong");
  const autoTag = autoDisplayTag();
  autoName.textContent = autoTag ? `Auto -> ${autoTag}` : "Auto";
  const autoMeta = document.createElement("span");
  autoMeta.textContent = autoTag ? `${t("autoSelected")}: ${autoTag}` : "urltest · automatic best node";
  const autoBadges = document.createElement("div");
  autoBadges.className = "node-badges";
  if (currentDefault() === "Auto") {
    const saved = document.createElement("span");
    saved.className = "node-pill saved";
    saved.textContent = t("defaultSaved");
    autoBadges.appendChild(saved);
  }
  if (autoTag) {
    const activeBadge = document.createElement("span");
    activeBadge.className = `node-pill ${runtimeProxy.now === "Auto" ? "active" : "auto-selected"}`;
    activeBadge.textContent = `${runtimeProxy.now === "Auto" ? t("activeNow") : t("autoSelected")}: ${autoTag}`;
    autoBadges.appendChild(activeBadge);
  }
  if (runtimeProxy.now === "Auto" && runtimeProxy.autoError) {
    const errorBadge = document.createElement("span");
    errorBadge.className = "node-pill bad";
    errorBadge.textContent = t("autoStatusUnavailable");
    autoBadges.appendChild(errorBadge);
  }
  autoTitle.append(autoName, autoMeta, autoBadges);
  const autoActions = document.createElement("div");
  autoActions.className = "node-actions";
  const autoDefaultButton = document.createElement("button");
  autoDefaultButton.type = "button";
  autoDefaultButton.className = "secondary-btn";
  autoDefaultButton.textContent = currentDefault() === "Auto" ? t("defaultSaved") : t("setDefault");
  autoDefaultButton.disabled = currentDefault() === "Auto" || busy;
  autoDefaultButton.addEventListener("click", (event) => {
    event.stopPropagation();
    chooseDefault("Auto");
  });
  autoActions.appendChild(autoDefaultButton);
  autoCard.append(autoTitle, autoActions);
  rows.appendChild(autoCard);
  for (const node of nodes) {
    const outbound = node.outbound;
    const isEnabled = node.enabled !== false;
    const isDefault = currentDefault() === outbound.tag;
    const isRuntime = runtimeProxy.now === outbound.tag;
    const isAutoRuntime = runtimeProxy.now === "Auto" && autoDisplayTag() === outbound.tag;
    const card = document.createElement("div");
    card.className = `node-card ${editingNodeTag === outbound.tag ? "selected" : ""} ${isDefault ? "default" : ""} ${isAutoRuntime ? "runtime" : ""} ${!isEnabled ? "disabled" : ""}`;
    card.addEventListener("click", () => selectNode(outbound.tag));
    const title = document.createElement("div");
    title.className = "node-title";
    const name = document.createElement("strong");
    name.textContent = outbound.tag;
    const meta = document.createElement("span");
    meta.textContent = `${outbound.type} · ${outbound.server}:${outbound.server_port}`;
    const badges = document.createElement("div");
    badges.className = "node-badges";
    const delay = document.createElement("span");
    delay.className = `node-pill delay ${delayTone(outbound.tag)}`;
    delay.textContent = `${t("delay")}: ${formatDelay(outbound.tag)}`;
    badges.appendChild(delay);
    if (outbound.type === "vless") {
      const transport = document.createElement("span");
      transport.className = `node-pill ${outbound.multiplex?.brutal?.enabled ? "warn" : "saved"}`;
      transport.textContent = outbound.multiplex?.brutal?.enabled ? t("transportBrutalBadge") : t("transportBbrBadge");
      badges.appendChild(transport);
    }
    if (isDefault) {
      const saved = document.createElement("span");
      saved.className = "node-pill saved";
      saved.textContent = t("defaultSaved");
      badges.appendChild(saved);
    }
    if (isRuntime) {
      const activeBadge = document.createElement("span");
      activeBadge.className = "node-pill active";
      activeBadge.textContent = t("activeNow");
      badges.appendChild(activeBadge);
    }
    if (isAutoRuntime) {
      const autoBadge = document.createElement("span");
      autoBadge.className = "node-pill auto-selected";
      autoBadge.textContent = t("autoSelected");
      badges.appendChild(autoBadge);
    }
    title.append(name, meta, badges);

    const actions = document.createElement("div");
    actions.className = "node-actions";
    const defaultButton = document.createElement("button");
    defaultButton.type = "button";
    defaultButton.className = "secondary-btn";
    defaultButton.textContent = isDefault ? t("defaultSaved") : t("setDefault");
    defaultButton.disabled = !isEnabled || isDefault || busy;
    defaultButton.addEventListener("click", (event) => {
      event.stopPropagation();
      chooseDefault(outbound.tag);
    });
    const toggle = document.createElement("label");
    toggle.className = "switchline";
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.checked = isEnabled;
    checkbox.addEventListener("click", (event) => event.stopPropagation());
    checkbox.addEventListener("change", () => toggleNode(outbound.tag, checkbox.checked));
    const label = document.createElement("span");
    label.textContent = checkbox.checked ? t("enabled") : t("disabled");
    toggle.append(checkbox, label);
    const remove = document.createElement("button");
    remove.type = "button";
    remove.className = "danger-btn";
    remove.textContent = t("deleteNode");
    remove.addEventListener("click", (event) => {
      event.stopPropagation();
      deleteNode(outbound.tag);
    });
    const primaryActions = document.createElement("div");
    primaryActions.className = "node-primary-actions";
    primaryActions.append(toggle, defaultButton);
    actions.append(primaryActions, remove);
    card.append(title, actions);
    rows.appendChild(card);
  }
  _r.replaceWith(rows);
}

function getNode(tag) {
  return (state.nodes || []).find((node) => node.outbound.tag === tag);
}

function stableNodeString(node) {
  return JSON.stringify(node || null);
}

function nodeFormChanged() {
  if (!editingNodeTag) return true;
  try {
    return stableNodeString(buildNodeFromForm()) !== editingNodeSnapshot;
  } catch (error) {
    return true;
  }
}

function syncNodeTransportControls() {
  const isVless = $("nodeType").value === "vless";
  const isSs = $("nodeType").value === "shadowsocks";
  const isBrutal = $("nodeTransportMode").value === "brutal";
  $("nodeTransportMode").disabled = !isVless;
  $("nodeUp").disabled = (isVless && !isBrutal) || isSs;
  $("nodeDown").disabled = (isVless && !isBrutal) || isSs;
  if (!isVless) {
    $("nodeTransportMode").value = "brutal";
  }
  // AEAD-2022 时钟提示：只在 SS 且加密选了 2022-blake3-* 时显示。
  // 普通 SS 加密(chacha20/aes-gcm)没有防重放时间窗，提示会变噪音。
  const note = $("nodeClockNote");
  if (note) {
    const method = ($("nodeMethod").value || "").trim().toLowerCase();
    const needsClockSync = isSs && method.startsWith("2022-blake3");
    note.classList.toggle("hidden", !needsClockSync);
  }
  // SS 填写格式提示：只要节点类型是 SS 就显示（区别于时钟提示只在 2022 时显示）。
  // 防止用户不知道 plugin/plugin_opts 该怎么填、或保存时留空被删（回直连连不上）。
  const ssNote = $("nodeSsFormatNote");
  if (ssNote) {
    ssNote.classList.toggle("hidden", !isSs);
  }
}

function selectNode(tag) {
  const node = getNode(tag);
  if (!node) return;
  const outbound = node.outbound;
  editingNodeTag = tag;
  $("nodeType").value = outbound.type || "hysteria2";
  $("nodeTransportMode").value = outbound.type === "vless" && outbound.multiplex?.brutal?.enabled ? "brutal" : "bbr";
  $("nodeTag").value = outbound.tag || "";
  $("nodeServer").value = outbound.server || "";
  $("nodePort").value = outbound.server_port || "";
  $("nodeSecret").value = outbound.type === "vless" ? outbound.uuid || "" : outbound.password || "";
  $("nodeMethod").value = outbound.method || "";
  $("nodePlugin").value = outbound.plugin || "";
  $("nodePluginOpts").value = outbound.plugin_opts || "";
  $("nodeSni").value = outbound.tls?.server_name || "";
  $("nodeObfs").value = outbound.obfs?.password || "";
  $("nodePublicKey").value = outbound.tls?.reality?.public_key || "";
  $("nodeShortId").value = outbound.tls?.reality?.short_id || "";
  $("nodeUp").value = outbound.up_mbps || outbound.multiplex?.brutal?.up_mbps || "";
  $("nodeDown").value = outbound.down_mbps || outbound.multiplex?.brutal?.down_mbps || "";
  $("nodeInsecure").checked = outbound.tls?.insecure !== false;
  syncNodeTransportControls();
  editingNodeSnapshot = stableNodeString(buildNodeFromForm());
  nodeEditChanged = false;
  setStatus(`${t("nodeSelected")}: ${tag}`, "ok");
  render();
}

function clearNodeForm() {
  editingNodeTag = null;
  editingNodeSnapshot = "";
  nodeEditChanged = false;
  $("nodeForm").reset();
  $("nodeInsecure").checked = true;
  $("nodeTransportMode").value = "bbr";
  syncNodeTransportControls();
  setStatus(t("editCancelled"));
  render();
}

function syncNodeFormState() {
  nodeEditChanged = nodeFormChanged();
  updateButtons();
}

async function chooseDefault(tag) {
  state.groups.proxy = state.groups.proxy || {};
  state.groups.proxy.default = tag;
  setBusy(true);
  // 后端已改为「Clash API 热切 + 静默落盘」，不重启 sing-box（实测 20ms 级），
  // 所以状态文案不再是「保存并重启」，也不在切换路径里做阻塞式全量测速——
  // 那两次 loadProxyInfo(true) 每个节点一次 /delay，是 UI 卡顿的另一半原因。
  setStatus(t("switchingProxy"));
  render();
  try {
    const result = await api("/api/proxy/default", {
      method: "POST",
      body: JSON.stringify({ tag }),
    });
    state = result.state || state;
    maintenance = result.maintenance || maintenance;
    // 后端回读确认过的运行态直接采用，无需再打一次 /api/proxy
    if (result.proxyAfterProbe) applyProxyPayload({ proxy: { ok: true, data: result.proxyAfterProbe } });
    setDirty(false);
    if (result.persistError) {
      // 运行态已切成功，只是没落盘：必须明确告知，否则重启后会悄悄回到旧节点
      setStatus(`${t("proxySwitched")} · ${t("persistFailed")}: ${result.persistError}`, "warn");
    } else {
      setStatus(t("proxySwitched"), "ok");
    }
  } catch (error) {
    setStatus(`${t("proxySwitchFailed")}: ${error.message}`, "bad");
    // 切换失败时回读真实运行态，避免 UI 停留在乐观更新的错误状态
    loadProxyInfo(false).catch(() => {});
  } finally {
    setBusy(false);
    render();
  }
}

function toggleNode(tag, enabled) {
  const enabledCount = enabledNodeTags().length;
  if (!enabled && enabledCount <= 1) {
    setStatus("At least one node must stay enabled", "bad");
    render();
    return;
  }
  const node = (state.nodes || []).find((item) => item.outbound.tag === tag);
  if (node) node.enabled = enabled;
  if (!enabled && state.groups?.proxy?.default === tag) {
    state.groups.proxy.default = "Auto";
  }
  markChanged();
  render();
  save(true);
}

async function refreshDelays() {
  if (delayRefreshInFlight) return;
  delayRefreshInFlight = true;
  setBusy(true);
  setStatus(t("testingDelay"));
  try {
    await loadProxyInfo(true);
    await loadProxyInfo(false);
    render();
    setStatus(t("delayUpdated"), "ok");
  } catch (error) {
    setStatus(error.message, "bad");
  } finally {
    delayRefreshInFlight = false;
    setBusy(false);
  }
}

function deleteNode(tag) {
  if (state.groups?.proxy?.default === tag) {
    setStatus(t("nodeDeleteBlocked"), "bad");
    return;
  }
  state.nodes = (state.nodes || []).filter((node) => node.outbound.tag !== tag);
  if (state.groups?.auto?.outbounds) {
    state.groups.auto.outbounds = state.groups.auto.outbounds.filter((item) => item !== tag);
  }
  if (editingNodeTag === tag) {
    editingNodeTag = null;
    editingNodeSnapshot = "";
    nodeEditChanged = false;
    $("nodeForm").reset();
    $("nodeInsecure").checked = true;
    $("nodeTransportMode").value = "bbr";
    syncNodeTransportControls();
  }
  markChanged();
  render();
}

function buildNodeFromForm() {
  const type = $("nodeType").value;
  const tag = $("nodeTag").value.trim();
  const transportMode = $("nodeTransportMode").value;
  const upMbps = $("nodeUp").value ? Number($("nodeUp").value) : null;
  const downMbps = $("nodeDown").value ? Number($("nodeDown").value) : null;
  if ((upMbps !== null && (!Number.isFinite(upMbps) || upMbps <= 0)) || (downMbps !== null && (!Number.isFinite(downMbps) || downMbps <= 0))) {
    throw new Error("Mbps must be a positive number");
  }
  const existing = editingNodeTag ? getNode(editingNodeTag) : null;
  const base = existing && existing.outbound.type === type ? structuredClone(existing.outbound) : {};
  const duplicate = nodeTags().some((item) => item === tag && item !== editingNodeTag);
  if (!tag || duplicate) {
    throw new Error(t("duplicateNode"));
  }
  const outbound = {
    ...base,
    type,
    tag,
    server: $("nodeServer").value.trim(),
    server_port: Number($("nodePort").value || 443),
    tls: {
      ...(base.tls || {}),
      enabled: true,
      server_name: $("nodeSni").value.trim() || $("nodeServer").value.trim(),
      insecure: $("nodeInsecure").checked,
    },
  };
  const secret = $("nodeSecret").value.trim();
  const obfsPassword = $("nodeObfs").value.trim();
  const publicKey = $("nodePublicKey").value.trim();
  const shortId = $("nodeShortId").value.trim();
  if (type === "hysteria2") {
    delete outbound.uuid;
    outbound.password = secret;
    if (upMbps !== null) outbound.up_mbps = upMbps;
    else delete outbound.up_mbps;
    if (downMbps !== null) outbound.down_mbps = downMbps;
    else delete outbound.down_mbps;
    if (obfsPassword) {
      outbound.obfs = { ...(base.obfs || {}), type: "salamander", password: obfsPassword };
    } else {
      delete outbound.obfs;
    }
  } else if (type === "shadowsocks") {
    // Shadowsocks 出站：SIP003 plugin（v2ray-plugin websocket-tls）自带 TLS，不挂 tls/reality/obfs。
    delete outbound.uuid;
    delete outbound.tls;
    delete outbound.obfs;
    delete outbound.multiplex;
    delete outbound.up_mbps;
    delete outbound.down_mbps;
    outbound.password = secret;
    outbound.method = $("nodeMethod").value.trim() || "chacha20-ietf-poly1305";
    const plugin = $("nodePlugin").value.trim();
    const pluginOpts = $("nodePluginOpts").value.trim();
    if (plugin) outbound.plugin = plugin;
    else delete outbound.plugin;
    if (pluginOpts) outbound.plugin_opts = pluginOpts;
    else delete outbound.plugin_opts;
  } else {
    delete outbound.password;
    delete outbound.up_mbps;
    delete outbound.down_mbps;
    delete outbound.obfs;
    outbound.uuid = secret;
    outbound.packet_encoding = outbound.packet_encoding || "xudp";
    outbound.tcp_fast_open = outbound.tcp_fast_open !== false;
    outbound.tls.utls = outbound.tls.utls || { enabled: true, fingerprint: "chrome" };
    if (transportMode === "brutal") {
      outbound.multiplex = outbound.multiplex || { enabled: true, protocol: "h2mux", padding: true, max_connections: 4 };
      outbound.multiplex.brutal = outbound.multiplex.brutal || { enabled: true };
      outbound.multiplex.brutal.enabled = true;
      if (upMbps !== null) outbound.multiplex.brutal.up_mbps = upMbps;
      else delete outbound.multiplex.brutal.up_mbps;
      if (downMbps !== null) outbound.multiplex.brutal.down_mbps = downMbps;
      else delete outbound.multiplex.brutal.down_mbps;
    } else {
      // 选择系统 BBR/TCP 时删除整个 multiplex，保证 VLESS 回到普通 TCP，由内核拥塞控制接管。
      delete outbound.multiplex;
    }
    if (publicKey) {
      outbound.tls.reality = { ...(base.tls?.reality || {}), enabled: true, public_key: publicKey };
      if (shortId) outbound.tls.reality.short_id = shortId;
      else delete outbound.tls.reality.short_id;
    } else {
      delete outbound.tls.reality;
    }
  }
  return { enabled: existing?.enabled ?? true, outbound };
}

async function addNode(event) {
  event.preventDefault();
  let node;
  try {
    node = buildNodeFromForm();
  } catch (error) {
    setStatus(error.message, "bad");
    return;
  }
  if (editingNodeTag) {
    const index = state.nodes.findIndex((item) => item.outbound.tag === editingNodeTag);
    if (index >= 0) state.nodes[index] = node;
    if (state.groups?.proxy?.default === editingNodeTag) {
      state.groups.proxy.default = node.outbound.tag;
    }
  } else {
    state.nodes.push(node);
  }
  editingNodeTag = node.outbound.tag;
  editingNodeSnapshot = stableNodeString(node);
  nodeEditChanged = false;
  event.target.reset();
  $("nodeInsecure").checked = true;
  $("nodeTransportMode").value = "bbr";
  syncNodeTransportControls();
  selectNode(node.outbound.tag);
  markChanged();
  render();
  await save();
}

function removeEntry(target) {
  state.lists[active] = (state.lists[active] || []).filter(
    (item) => !(item.type === target.type && item.value === target.value),
  );
  render();
  markChanged();
}

// 类型前缀别名表：中文标签 → 内部英文类型。
// textarea 的 placeholder 用中文示例（域名后缀: example.com），但解析器早期只认
// ASCII 英文前缀，照 placeholder 填会把整行当成值，保存时后端报 Invalid domain value。
// 这里把中英文两套写法都收进来，UI 提示和实际行为才一致。
const entryTypeAliases = (() => {
  const map = new Map();
  for (const type of allEntryTypes) map.set(type, type);
  // 中文标签取自 translations.zh.types，避免两处硬编码不同步
  for (const lc of ["zh", "en"]) {
    const types = (translations[lc] || {}).types || {};
    for (const [type, label] of Object.entries(types)) {
      if (allEntryTypes.includes(type)) map.set(String(label).trim().toLowerCase(), type);
    }
  }
  return map;
})();

// 解析一行里的 "类型前缀: 值"。识别失败返回 null，由调用方回退到下拉框类型。
// 前缀大小写不敏感（Domain_Suffix / IP_CIDR 都认）；中文前缀含 "/" 等非 \w 字符，
// 所以匹配段不能只用 [\w_]，改成"首个冒号之前"再查别名表。
function parseTypePrefix(line, allowedTypes) {
  const idx = line.indexOf(":");
  if (idx <= 0) return null;
  const rawPrefix = line.slice(0, idx).trim().toLowerCase();
  const type = entryTypeAliases.get(rawPrefix);
  // 未登记的前缀一律不当类型看待，避免 IPv6（2001:db8::/32）的首段被误认成前缀
  if (!type || !allowedTypes.includes(type)) return null;
  return { type, value: line.slice(idx + 1).trim() };
}

// 值规范化：与后端 normalize_entry 保持同一套规则，避免前端显示和落盘结果不一致。
// domain_regex 大小写有语义，必须原样保留；其余类型统一小写并去掉结尾的点。
function normalizeEntryValue(type, value) {
  const trimmed = String(value).trim();
  if (type === "domain_regex") return trimmed;
  if (type === "ip_cidr") return trimmed.toLowerCase();
  return trimmed.toLowerCase().replace(/\.$/, "");
}

function addEntry(event) {
  event.preventDefault();
  const type = $("typeInput").value;
  const value = normalizeEntryValue(type, $("valueInput").value);
  if (!value) return;
  const exists = (state.lists[active] || []).some((item) => item.type === type && item.value === value);
  if (!exists) state.lists[active].push({ type, value });
  $("valueInput").value = "";
  render();
  markChanged();
}

// entriesToText - 把条目数组格式化为逐行文本（类型: 值），供 textarea 显示
function entriesToText(items) {
  if (!items || !items.length) return "";
  return items.map((item) => `${item.type}: ${item.value}`).join("\n");
}

// textareaToEntries - 把 textarea 文本解析回条目数组，自动去重
function textareaToEntries(text) {
  const lines = text.split("\n");
  const allowedTypes = allowedEntryTypes();
  const defaultType = $("typeInput").value || allowedTypes[0];
  const seen = new Set();
  const entries = [];
  for (let line of lines) {
    line = line.trim();
    if (!line) continue;
    // 尝试解析 "类型前缀: 值" 格式（中英文前缀均可，大小写不敏感）
    const parsed = parseTypePrefix(line, allowedTypes);
    let type, value;
    if (parsed) {
      type = parsed.type;
      value = parsed.value;
    } else {
      // 没有识别出类型前缀，使用当前下拉框选中的类型
      type = defaultType;
      value = line;
    }
    if (!value) continue;
    value = normalizeEntryValue(type, value);
    if (!value) continue;
    const key = `${type}:${value}`;
    if (seen.has(key)) continue;
    seen.add(key);
    entries.push({ type, value });
  }
  return entries;
}

// textarea 输入回调：解析内容并更新 state，避免中断用户输入
function onListTextareaInput() {
  const ta = $("listTextarea");
  if (!ta) return;
  const entries = textareaToEntries(ta.value);
  const oldItems = state.lists[active] || [];
  // 只在内容真正变化时才标记 dirty，避免每次按键都触发
  const changed =
    oldItems.length !== entries.length ||
    oldItems.some((item, i) => item.type !== entries[i]?.type || item.value !== entries[i]?.value);
  state.lists[active] = entries;
  if (changed) markChanged();
  // 实时更新条目计数，不重新渲染（保持光标位置）
  const listInfo = translations[lang].lists[active];
  const note =
    active === "ddns"
      ? t(ddnsDnsMode() === "remote" ? "ddnsRemoteSummary" : "ddnsLocalSummary")
      : listInfo.note;
  $("listSummary").textContent = `${entries.length} ${t("entries")} · ${note}`;
}

// renderListTextarea - 填充 textarea 内容；只在切换列表或 textarea 无焦点时写入，避免打断用户编辑
function renderListTextarea(items) {
  const ta = $("listTextarea");
  if (!ta) return;
  if (ta.dataset.active !== active || document.activeElement !== ta) {
    ta.dataset.active = active;
    ta.value = entriesToText(items);
  }
  // DDNS 名单条目少，单独用较小高度；其他名单恢复默认大高度
  ta.classList.toggle("ddns-textarea", active === "ddns");
}

async function save(silent = false) {
  syncDraftSettings();
  if (!dirty) {
    setStatus(t("noChanges"));
    return;
  }
  setBusy(true);
  setStatus(t("savingWithCheck"));
  try {
    const result = await api("/api/save", {
      method: "POST",
      body: JSON.stringify({ lists: state.lists, nodes: state.nodes, groups: state.groups }),
    });
    state = result.state;
    maintenance = result.maintenance || maintenance;
    if (result.proxy) applyProxyPayload({ proxy: result.proxy, delays: result.delays });
    await loadProxyInfo(false);
    if (editingNodeTag && getNode(editingNodeTag)) {
      editingNodeSnapshot = stableNodeString(buildNodeFromForm());
      nodeEditChanged = false;
    }
    setDirty(false);
    render();
    loadProxyInfo(true).then(() => render()).catch(() => {});
    if (result.tproxySync && result.tproxySync.code !== 0) {
      setStatus(`${t("savedAndRestarted")}；${t("tproxySyncFailed")}`, "bad");
    } else {
      setStatus(`${t("savedAndRestarted")}；${t("delayUpdated")}`, "ok");
      if (!silent) window.alert(t("savedAlert"));
    }
  } catch (error) {
    setStatus(error.message || t("changesBlocked"), "bad");
  } finally {
    setBusy(false);
    render();
  }
}

async function restart() {
  setBusy(true);
  pulseActionButton("restartSingboxBtn", "restartingSingbox");
  setStatus(t("restartingSingbox"));
  try {
    const result = await api("/api/restart", { method: "POST", body: "{}" });
    state = result.state;
    await loadProxyInfo(false);
    render();
    const checkResult = result.check;
    const restartResult = result.restart;
    if (checkResult.code !== 0) {
      finishActionButton("restartSingboxBtn", "actionFailed", "failed", "restartSingbox");
      setStatus(checkResult.stderr || t("checkFailed"), "bad");
      return;
    }
    if (restartResult.code !== 0) {
      finishActionButton("restartSingboxBtn", "actionFailed", "failed", "restartSingbox");
      setStatus(restartResult.stderr || t("restartFailed"), "bad");
      return;
    }
    finishActionButton("restartSingboxBtn", "actionDone", "done", "restartSingbox");
    setStatus(t("singboxRestarted"), "ok");
  } catch (error) {
    finishActionButton("restartSingboxBtn", "actionFailed", "failed", "restartSingbox");
    setStatus(error.message, "bad");
  } finally {
    setBusy(false);
  }
}

async function restartTproxy() {
  setBusy(true);
  pulseActionButton("restartTproxyBtn", "restartingTproxy");
  setStatus(t("restartingTproxy"));
  try {
    const result = await api("/api/tproxy/restart", { method: "POST", body: "{}" });
    maintenance = result.maintenance || maintenance;
    if (result.state) state = result.state;
    render();
    if (result.restart?.code !== 0) {
      finishActionButton("restartTproxyBtn", "actionFailed", "failed", "restartTproxy");
      setStatus(result.restart?.stderr || t("tproxyRestartFailed"), "bad");
      return;
    }
    finishActionButton("restartTproxyBtn", "actionDone", "done", "restartTproxy");
    setStatus(t("tproxyRestarted"), "ok");
  } catch (error) {
    finishActionButton("restartTproxyBtn", "actionFailed", "failed", "restartTproxy");
    setStatus(`${t("tproxyRestartFailed")} ${error.message}`, "bad");
  } finally {
    setBusy(false);
  }
}

async function restartUi() {
  setBusy(true);
  pulseActionButton("restartUiBtn", "restartingUi");
  setStatus(t("restartingUi"));
  try {
    await api("/api/ui/restart", { method: "POST", body: "{}" });
    setStatus(t("uiRestartScheduled"), "ok");
    const result = await waitForUiReconnect();
    if (result) {
      maintenance = result.maintenance || maintenance;
      if (result.state) state = result.state;
      render();
      finishActionButton("restartUiBtn", "actionDone", "done", "restartUi");
      setStatus(t("uiRestartReady"), "ok");
    } else {
      finishActionButton("restartUiBtn", "actionDone", "done", "restartUi");
      setStatus(t("uiRestartManualRefresh"), "ok");
    }
  } catch (error) {
    finishActionButton("restartUiBtn", "actionFailed", "failed", "restartUi");
    setStatus(error.message, "bad");
  } finally {
    setBusy(false);
  }
}

document.querySelectorAll(".tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    const nextActive = tab.dataset.list;
    if (active === "runtime" && nextActive !== "runtime") {
      stopRuntimeLogs(false);
      stopRuntimePolling();
    }
    active = nextActive;
    $("searchInput").value = "";
    setStatus(t("ready"));
    render();
    if (active === "maintenance") refreshMaintenance();
    if (active === "runtime") refreshRuntime();
  });
});

$("addForm").addEventListener("submit", addEntry);
// 列表 textarea 输入实时解析：一行一个条目，更新 state 后标记 dirty
$("listTextarea").addEventListener("input", onListTextareaInput);
$("nodeForm").addEventListener("submit", addNode);
$("nodeForm").addEventListener("input", syncNodeFormState);
$("nodeForm").addEventListener("change", syncNodeFormState);
$("nodeType").addEventListener("change", () => {
  syncNodeTransportControls();
  syncNodeFormState();
});
$("nodeTransportMode").addEventListener("change", () => {
  syncNodeTransportControls();
  syncNodeFormState();
});
// method 是自由文本输入，AEAD-2022 时钟提示要随用户敲字实时显隐，
// 故单独挂 input 监听（nodeForm 的委托监听只负责脏状态，不刷控件可用性）。
$("nodeMethod").addEventListener("input", syncNodeTransportControls);
$("nodeCancel").addEventListener("click", clearNodeForm);
$("searchInput").addEventListener("input", render);
$("typeInput").addEventListener("change", updateValueHint);
$("saveBtn").addEventListener("click", () => save());
$("logoutBtn").addEventListener("click", logout);
$("refreshDelayBtn").addEventListener("click", refreshDelays);
$("refreshMaintenanceBtn").addEventListener("click", refreshMaintenance);
$("restartSingboxBtn").addEventListener("click", restart);
$("restartTproxyBtn").addEventListener("click", restartTproxy);
$("restartUiBtn").addEventListener("click", restartUi);
$("syncTproxyBtn").addEventListener("click", syncTproxy);
$("exportBackupBtn").addEventListener("click", exportBackup);
$("importBackupBtn").addEventListener("click", chooseBackupFile);
$("backupFileInput").addEventListener("change", importBackupFromFile);
$("changeTokenBtn").addEventListener("click", changeAccessToken);
$("newTokenInput").addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    event.preventDefault();
    changeAccessToken();
  }
});
$("updateRulesBtn").addEventListener("click", updateRuleSets);
$("updateTelegramCidrBtn").addEventListener("click", updateTelegramCidr);
$("saveTelegramCidrBtn").addEventListener("click", saveTelegramCidr);
$("runtimeView").addEventListener("change", () => {
  stopRuntimePolling();
  render();
  if ($("runtimeView").value !== "logs") stopRuntimeLogs(false);
  refreshRuntime();
});
$("runtimeLogLevel").addEventListener("change", changeRuntimeLogLevel);
$("brandLink").addEventListener("click", goNodes);
$("brandLink").addEventListener("keydown", (event) => {
  if (event.key === "Enter" || event.key === " ") {
    event.preventDefault();
    goNodes();
  }
});

function markChanged() {
  setDirty(true);
  setStatus(t("changed"));
}

function syncNodeSettingsFromForm() {
  state.groups.auto = state.groups.auto || {};
  state.groups.auto.url = $("autoUrl").value.trim();
  state.groups.auto.interval = $("autoInterval").value.trim();
  // idle_timeout / tolerance 现在是用户可配项（官方默认 30m / 50ms）；空值回落默认，
  // 合法性（Go 时长格式、idle_timeout >= interval）由后端 normalize_payload_groups 收口校验。
  state.groups.auto.idle_timeout = $("autoIdleTimeout").value.trim() || "30m";
  const toleranceRaw = $("autoTolerance").value.trim();
  state.groups.auto.tolerance = toleranceRaw === "" ? 50 : Number(toleranceRaw);
  state.groups.auto.interrupt_exist_connections = $("interruptConnections").checked;
  state.groups.dns = state.groups.dns || {};
  state.groups.dns.local = $("localDnsSelect").value || "alidns";
  state.groups.dns.local_custom_server = ($("customDnsServer").value || "223.5.5.5").trim();
  state.groups.dns.local_custom_port = Number($("customDnsPort").value) || 53;
  state.groups.fakeip = state.groups.fakeip || {};
  state.groups.fakeip.inet4_range = $("fakeipV4").value.trim();
  state.groups.fakeip.inet6_range = $("fakeipV6").value.trim();
  state.groups.fakeip.ipv6_enabled = $("fakeipIpv6Enabled").checked;
  state.groups.fakeip.block_quic = true;
  state.groups.telegram = state.groups.telegram || {};
  state.groups.socks5 = state.groups.socks5 || {};
  state.groups.socks5.port = Number($("socks5Port").value || 0);
  state.groups.telegram.capture_ips = $("telegramCaptureIps").checked;
  state.groups.proxy = state.groups.proxy || {};
  state.groups.proxy.interrupt_exist_connections = $("interruptConnections").checked;
  if (!$("proxyDefault").classList.contains("hidden") && $("proxyDefault").value) {
    state.groups.proxy.default = $("proxyDefault").value;
  }
}

function syncNodeSettingsChanged() {
  syncNodeSettingsFromForm();
  markChanged();
}

function syncDraftSettings() {
  if (active !== "nodes") return;
  syncNodeSettingsFromForm();
}

["autoUrl", "autoInterval", "autoTolerance", "autoIdleTimeout", "interruptConnections", "fakeipV4", "fakeipV6", "fakeipIpv6Enabled", "telegramCaptureIps", "socks5Port"].forEach((id) => {
  $(id).addEventListener("input", syncNodeSettingsChanged);
  $(id).addEventListener("change", syncNodeSettingsChanged);
});
$("localDnsSelect").addEventListener("change", () => {
  syncNodeSettingsChanged();
  render();
});
$("customDnsServer").addEventListener("input", syncNodeSettingsChanged);
$("customDnsServer").addEventListener("change", syncNodeSettingsChanged);
$("customDnsPort").addEventListener("input", syncNodeSettingsChanged);
$("customDnsPort").addEventListener("change", syncNodeSettingsChanged);
$("refreshDnsDelayBtn").addEventListener("click", refreshDnsDelays);
$("proxyDefault").addEventListener("change", () => {
  syncNodeSettingsChanged();
  render();
});
$("langSelect").addEventListener("change", () => {
  lang = $("langSelect").value;
  localStorage.setItem("ruleUiLang", lang);
  render();
  setStatus(t("ready"));
});
$("tokenBtn").addEventListener("click", () => {
  token = $("tokenInput").value.trim();
  localStorage.setItem("ruleUiToken", token);
  load();
});
$("tokenInput").addEventListener("keydown", (event) => {
  if (event.key === "Enter") $("tokenBtn").click();
});

applyLanguage();
syncNodeTransportControls();
setStatus(t("ready"));
updateButtons();
load();
setInterval(refreshMeta, 5000);
