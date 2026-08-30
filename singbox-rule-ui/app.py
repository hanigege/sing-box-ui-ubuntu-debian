#!/usr/bin/env python3
import json
import os
import re
import secrets
import shutil
import socket
import subprocess
import tempfile
import threading
import time
import ipaddress
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, quote, urlencode, unquote, urlparse
from urllib.request import Request, urlopen


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
RULE_DIR = Path(os.environ.get("RULE_UI_RULE_DIR", "/etc/sing-box/custom-rules"))
CONFIG_PATH = Path(os.environ.get("RULE_UI_SING_BOX_CONFIG", "/etc/sing-box/config.json"))
TOKEN_FILE = Path(os.environ.get("RULE_UI_TOKEN_FILE", "/etc/sing-box/rule-ui/token"))
MANAGER_DIR = Path(os.environ.get("RULE_UI_MANAGER_DIR", "/etc/sing-box/manager"))
CLASH_API_URL = os.environ.get("RULE_UI_CLASH_API_URL", "").rstrip("/")
CLASH_API_SECRET = os.environ.get("RULE_UI_CLASH_API_SECRET", "")
BASE_CONFIG_PATH = MANAGER_DIR / "base.json"
NODES_PATH = MANAGER_DIR / "nodes.json"
GROUPS_PATH = MANAGER_DIR / "groups.json"
BACKUP_DIR = MANAGER_DIR / "backups"
BACKUP_RETENTION = 20
RULE_UPDATE_LAST_PATH = MANAGER_DIR / "rule-update-last.json"
TELEGRAM_CIDR_PATH = MANAGER_DIR / "telegram-cidr.json"
RULE_UPDATE_SCRIPT = Path(os.environ.get("RULE_UI_RULE_UPDATE_SCRIPT", "/usr/local/sbin/update-sing-box-rules-jsdelivr"))
# Debian/Ubuntu 用 /etc/cron.d 片段代替 Alpine 的 /etc/crontabs/root；cron.d 行格式多一个 user 字段。
ROOT_CRONTAB = Path(os.environ.get("RULE_UI_ROOT_CRONTAB", "/etc/cron.d/sing-box-gateway"))
CRON_USER = os.environ.get("RULE_UI_CRON_USER", "root")
RULE_UPDATE_CRON_BEGIN = "# BEGIN sing-box-gateway-ui rule update"
RULE_UPDATE_CRON_END = "# END sing-box-gateway-ui rule update"
RULE_UPDATE_SERVICE = os.environ.get("RULE_UI_RULE_UPDATE_SERVICE", "update-sing-box-rules-jsdelivr")
TPROXY_SERVICE = os.environ.get("RULE_UI_TPROXY_SERVICE", "sing-box-tproxy")
RULE_UI_SERVICE = os.environ.get("RULE_UI_SERVICE", "singbox-rule-ui")
TPROXY_SCRIPT = Path(os.environ.get("RULE_UI_TPROXY_SCRIPT", "/usr/local/sbin/sing-box-tproxy-setup"))
TPROXY_SYSCTL = Path(os.environ.get("RULE_UI_TPROXY_SYSCTL", "/etc/sysctl.d/99-sing-box-tproxy.conf"))
RADVD_CONF = Path(os.environ.get("RULE_UI_RADVD_CONF", "/etc/radvd.conf"))
RADVD_SERVICE = os.environ.get("RULE_UI_RADVD_SERVICE", "radvd")
ENABLE_RADVD = os.environ.get("SING_BOX_GATEWAY_ENABLE_RADVD", os.environ.get("RULE_UI_ENABLE_RADVD", "0")).lower() in ("1", "true", "yes", "on")
ENABLE_GATEWAY_FORWARDING = os.environ.get("SING_BOX_GATEWAY_ENABLE_FORWARDING", os.environ.get("RULE_UI_ENABLE_FORWARDING", "0")).lower() in ("1", "true", "yes", "on")
TPROXY_PORT = int(os.environ.get("RULE_UI_TPROXY_PORT", "9888"))
TPROXY_MARK = int(os.environ.get("RULE_UI_TPROXY_MARK", "1"))
TPROXY_TABLE = int(os.environ.get("RULE_UI_TPROXY_TABLE", "100"))
LISTS = {
    "whitelist": {"title": "White List", "outbound": "direct"},
    "blacklist": {"title": "Black List", "outbound": "block"},
    "greylist": {"title": "Grey List", "outbound": "Proxy"},
    "ddns": {"title": "Local DDNS", "outbound": "direct"},
}
CUSTOM_TAGS = {
    "whitelist": "custom-whitelist",
    "blacklist": "custom-blacklist",
    "greylist": "custom-greylist",
    "ddns": "custom-ddns",
}

LOCAL_DNS_SERVER = {
    "tag": "local-dns",
    "type": "udp",
    "server": "119.29.29.29",
    "server_port": 53,
    # 国内直连域名只会路由到一个 local-dns；当前 sing-box 没有 DNS 并发/备用组，UI 只能明确选择单个上游。
}
DDNS_REMOTE_DNS_SERVER = {
    "tag": "ddns-remote-dns",
    "type": "https",
    "server": "1.1.1.1",
    "server_port": 443,
    "path": "/dns-query",
    "tls": {"server_name": "cloudflare-dns.com"},
    "detour": "Auto",
    # DDNS 的“代理解析”走独立 DoH（不复用 remote-dns 的连接，避免互相影响）。
    # 加密 DoH 而非明文 UDP：查询全程 TLS，且 TCP 传输对 UDP-disabled 节点（sslocal relay）兼容——
    # 之前 UDP+detour Proxy 在 Proxy 切到 US-232-sslocal 时所有 DDNS 域名解析挂死（socks5 code=7）。
}
LOCAL_DNS_CHOICES = {
    "dnspod": {"label": "DNSPod", "server": "119.29.29.29", "server_port": 53},
    "alidns": {"label": "AliDNS", "server": "223.5.5.5", "server_port": 53},
    "114dns": {"label": "114 DNS", "server": "114.114.114.114", "server_port": 53},
    "custom_dns": {"label": "Custom", "server": "manual", "server_port": 53},
}
DEFAULT_LOCAL_DNS_CHOICE = "dnspod"
LOCAL_DNS_BY_SERVER = {item["server"]: key for key, item in LOCAL_DNS_CHOICES.items()}
DEFAULT_INTERRUPT_EXIST_CONNECTIONS = False
# 官方 sing-box 的 urltest 默认值（constant/timeout.go DefaultURLTestIdleTimeout=30m、
# protocol/group/urltest.go NewURLTestGroup 里 tolerance 缺省 50）。这里显式写出来，
# 是为了让 UI 能展示并让用户调整，而不是把「官方默认」伪装成不可改的固定行为。
DEFAULT_URLTEST_IDLE_TIMEOUT = "30m"
DEFAULT_URLTEST_TOLERANCE = 50
ENTRY_TYPES = ("domain", "domain_suffix", "domain_keyword", "domain_regex", "ip_cidr")
LIST_ENTRY_TYPES = {
    "whitelist": ENTRY_TYPES,
    "blacklist": ENTRY_TYPES,
    "greylist": ENTRY_TYPES,
    "ddns": ("domain_suffix", "domain"),
}
DEFAULT_TELEGRAM_PROXY_IPV4 = (
    "91.108.4.0/22",
    "91.108.8.0/22",
    "91.108.12.0/22",
    "91.108.16.0/22",
    "91.108.20.0/22",
    "91.108.56.0/22",
    "91.105.192.0/23",
    "185.76.151.0/24",
    "149.154.160.0/20",
)
DEFAULT_TELEGRAM_PROXY_IPV6 = (
    "2001:67c:4e8::/48",
    "2001:b28:f23c::/48",
    "2001:b28:f23d::/48",
    "2001:b28:f23f::/48",
    "2a0a:f280::/32",
)
DEFAULT_TELEGRAM_CIDR_SOURCES = (
    "https://scg.jgaga.tk/https://core.telegram.org/resources/cidr.txt",
    "https://scg.jgaga.tk/https://raw.githubusercontent.com/fernvenue/telegram-cidr-list/master/CIDR.txt",
    "https://core.telegram.org/resources/cidr.txt",
    "https://raw.githubusercontent.com/fernvenue/telegram-cidr-list/master/CIDR.txt",
)
TELEGRAM_CIDR_SOURCES = tuple(
    item
    for item in os.environ.get("RULE_UI_TELEGRAM_CIDR_SOURCES", " ".join(DEFAULT_TELEGRAM_CIDR_SOURCES)).split()
    if item
)
TELEGRAM_CIDR_DNS_SERVERS = tuple(
    item
    for item in os.environ.get("RULE_UI_TELEGRAM_CIDR_DNS_SERVERS", "1.1.1.1 8.8.8.8 119.29.29.29").split()
    if item
)
DOMAIN_RE = re.compile(r"^[A-Za-z0-9_*.-]+$")
SPECIAL_OUTBOUNDS = {"Proxy", "Auto", "direct", "block"}
SUPPORTED_NODE_TYPES = {"hysteria2", "vless", "shadowsocks", "socks"}
BACKUP_VERSION = 1
LOG_LEVELS = {"trace", "debug", "info", "warn", "warning", "error", "fatal", "panic"}
LEGACY_APP_RULE_SETS = {
    "geosite-ai",
    "geosite-youtube",
    "geosite-google",
    "geosite-github",
    "geosite-cloudflare",
    "geosite-netflix",
    "geosite-facebook",
    "geosite-instagram",
    "geosite-tiktok",
    "geosite-jetbrains",
    "geosite-spotify",
    "geosite-disney",
    "geosite-hbo",
    "geosite-amazon",
    "geosite-adobe",
    "geosite-steam",
    "geosite-category-pt@!cn",
    "geosite-category-cryptocurrency",
    "geoip-netflix",
    "geoip-facebook",
}


def now_stamp():
    return time.strftime("%Y%m%d-%H%M%S")


def ensure_dirs():
    RULE_DIR.mkdir(parents=True, exist_ok=True)
    MANAGER_DIR.mkdir(parents=True, exist_ok=True)
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)


def get_token():
    ensure_dirs()
    if TOKEN_FILE.exists():
        token = TOKEN_FILE.read_text(encoding="utf-8").strip()
        if token:
            return token
    token = secrets.token_urlsafe(32)
    TOKEN_FILE.write_text(token + "\n", encoding="utf-8")
    TOKEN_FILE.chmod(0o600)
    return token


def set_token(new_token):
    # 用户自定义访问密码：内网自用场景放宽到 >=6 位，仍禁止空白字符防止复制粘贴踩坑。
    new_token = str(new_token or "").strip()
    if len(new_token) < 6:
        raise ValueError("Token must be at least 6 characters")
    if any(ch.isspace() for ch in new_token):
        raise ValueError("Token must not contain whitespace")
    ensure_dirs()
    # 先写临时文件再原子 rename，避免写一半掉电导致 token 文件损坏、UI 永久锁死。
    tmp_path = TOKEN_FILE.with_name(TOKEN_FILE.name + ".tmp")
    tmp_path.write_text(new_token + "\n", encoding="utf-8")
    tmp_path.chmod(0o600)
    tmp_path.replace(TOKEN_FILE)
    return new_token


def empty_rule_set():
    return {"version": 3, "rules": []}


def rule_path(name):
    if name not in LISTS:
        raise ValueError("unknown list")
    return RULE_DIR / f"{name}.json"


def backup_file(path):
    backup_dir = RULE_DIR / "backups"
    return backup_path(path, backup_dir)


def backup_manager_file(path):
    return backup_path(path, BACKUP_DIR)


def backup_path(path, backup_dir):
    if not path.exists():
        return {"existed": False, "backup": None}
    backup_dir.mkdir(parents=True, exist_ok=True)
    target = backup_dir / f"{path.name}.bak-{now_stamp()}"
    shutil.copy2(path, target)
    prune_backups(backup_dir, path.name)
    return {"existed": True, "backup": str(target)}


def prune_backups(backup_dir, filename, keep=BACKUP_RETENTION):
    try:
        backups = sorted(
            backup_dir.glob(f"{filename}.bak-*"),
            key=lambda item: item.stat().st_mtime,
            reverse=True,
        )
    except OSError:
        return
    for item in backups[keep:]:
        try:
            item.unlink()
        except OSError:
            pass


def load_json(path, fallback):
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path, data):
    # UI 负责生产配置落盘，必须先写同目录临时文件再原子替换，避免断电/进程中断留下半截 JSON。
    path.parent.mkdir(parents=True, exist_ok=True)
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


def restore_file(path, backup):
    if isinstance(backup, dict):
        # 回滚必须恢复“原来是否存在”这个状态；否则失败保存会留下新建的规则/配置文件。
        if not backup.get("existed", bool(backup.get("backup"))):
            path.unlink(missing_ok=True)
            return
        backup = backup.get("backup")
    if backup and Path(backup).exists():
        data = json.loads(Path(backup).read_text(encoding="utf-8"))
        write_json(path, data)


def read_text_if_exists(path):
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8", errors="replace")


def clash_api_settings():
    url = CLASH_API_URL
    secret = CLASH_API_SECRET
    if (not url or not secret) and CONFIG_PATH.exists():
        try:
            clash = load_json(CONFIG_PATH, {}).get("experimental", {}).get("clash_api", {})
            if not url:
                controller = str(clash.get("external_controller", "")).strip()
                if controller:
                    url = controller if controller.startswith(("http://", "https://")) else f"http://{controller}"
            if not secret:
                secret = str(clash.get("secret", "")).strip()
        except Exception:
            pass
    return (url or "http://127.0.0.1:9090").rstrip("/"), secret


def normalize_entry(entry):
    # 类型前缀大小写不敏感：UI 提示里写的是小写英文，但用户手打/粘贴常出现
    # "Domain_Suffix"、"IP_CIDR" 这类混写，统一小写后再查白名单，避免整行被判非法。
    kind = str(entry.get("type", "domain_suffix")).strip().lower()
    value = str(entry.get("value", "")).strip()
    if kind not in ENTRY_TYPES:
        raise ValueError(f"Unsupported type: {kind}")
    # domain_regex 是 Go regexp，大小写有语义（如 [^a-zA-Z0-9._-] 表示"排除大小写字母和数字"）。
    # 早期这里对所有类型无条件 .lower()，会把该正则静默改成 [^a-za-z0-9._-]，
    # 排除大写字母的意图丢失且不报错。域名类不区分大小写，继续规范化为小写；正则原样保留。
    if kind == "domain_regex":
        value = value.rstrip()
    else:
        value = value.lower().rstrip(".")
    if not value:
        raise ValueError("Empty value is not allowed")
    if kind == "ip_cidr":
        try:
            # IP/CIDR 规则会直接影响 route 命中顺序，必须规范成真实网段，避免主机地址伪装成网段被保存。
            return {"type": kind, "value": str(ipaddress.ip_network(value, strict=True))}
        except Exception as exc:
            raise ValueError(f"Invalid IP/CIDR value: {value}") from exc
    if kind != "domain_regex" and not DOMAIN_RE.match(value):
        raise ValueError(f"Invalid domain value: {value}")
    return {"type": kind, "value": value}


def normalize_entries(entries):
    seen = set()
    normalized = []
    for raw in entries:
        item = normalize_entry(raw)
        key = (item["type"], item["value"])
        if key in seen:
            continue
        seen.add(key)
        normalized.append(item)
    normalized.sort(key=lambda item: (item["type"], item["value"]))
    return normalized


def normalize_list_entries(name, entries):
    allowed = LIST_ENTRY_TYPES.get(name, ENTRY_TYPES)
    normalized = normalize_entries(entries)
    invalid = sorted({item["type"] for item in normalized if item["type"] not in allowed})
    if invalid:
        raise ValueError(f"Unsupported type for {name}: {', '.join(invalid)}")
    return normalized


def validate_greylist_ip_cidrs(entries, nodes=None, groups=None):
    protected = protected_tproxy_networks(nodes=nodes, groups=groups)
    for item in entries:
        if item.get("type") != "ip_cidr":
            continue
        network = ipaddress.ip_network(item["value"], strict=False)
        for protected_network in protected:
            if network.version != protected_network.version:
                continue
            if network.subnet_of(protected_network) or network.overlaps(protected_network):
                raise ValueError(f"Greylist IP/CIDR would capture protected network: {network}")


def normalize_tag(value):
    tag = str(value or "").strip()
    if not re.match(r"^[A-Za-z0-9_.@-]{1,64}$", tag):
        raise ValueError(f"Invalid node tag: {tag}")
    if tag in SPECIAL_OUTBOUNDS:
        raise ValueError(f"Reserved node tag: {tag}")
    return tag


def normalize_host(value):
    host = str(value or "").strip()
    if not host or len(host) > 253:
        raise ValueError("Invalid server")
    return host


def normalize_port(value):
    try:
        port = int(value)
    except Exception as exc:
        raise ValueError("Invalid port") from exc
    if port < 1 or port > 65535:
        raise ValueError("Invalid port")
    return port


def normalize_bool(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in ("1", "true", "yes", "on"):
            return True
        if lowered in ("0", "false", "no", "off"):
            return False
    if value in (0, 1):
        return bool(value)
    raise ValueError("Invalid boolean value")


def normalize_number(value, default=None):
    if value in ("", None):
        return default
    try:
        return int(value)
    except Exception as exc:
        raise ValueError(f"Invalid number: {value}") from exc


def normalize_url(value, default):
    url = str(value or "").strip() or default
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise ValueError(f"Invalid URL: {url}")
    return url


def normalize_non_negative_number(value, default=0):
    number = normalize_number(value, default)
    if number is None or number < 0:
        raise ValueError(f"Invalid non-negative number: {value}")
    return number


def normalize_positive_number(value, default=None):
    number = normalize_number(value, default)
    if number is not None and number <= 0:
        raise ValueError(f"Invalid positive number: {value}")
    return number


# Go time.ParseDuration 允许的单位（sing-box 的 interval/idle_timeout 走这个解析器）。
# 这里只支持 sing-box 实际有意义的量级：ns/us/ms 对测速间隔无意义但仍解析，避免误判用户输入非法。
_DURATION_UNITS = {
    "ns": 1e-9,
    "us": 1e-6,
    "µs": 1e-6,
    "ms": 1e-3,
    "s": 1.0,
    "m": 60.0,
    "h": 3600.0,
}
_DURATION_TOKEN_RE = re.compile(r"(\d+(?:\.\d+)?)(ns|us|µs|ms|s|m|h)")


def parse_go_duration_seconds(value):
    """把 Go 风格时长字符串（"30s"/"2m"/"1h30m"）解析成秒数。

    sing-box 用 Go 的 time.ParseDuration，非法值会让 sing-box 启动失败，
    但 `sing-box check` 只做静态校验、抓不到 interval > idle_timeout 这类
    运行期约束（官方 urltest.go NewURLTestGroup 才返回错误），所以 UI 必须
    自己解析并在保存前拦下来。返回 None 表示无法解析。
    """
    text = str(value or "").strip().lower()
    if not text:
        return None
    negative = text.startswith("-")
    if negative or text.startswith("+"):
        text = text[1:]
    if not text:
        return None
    total = 0.0
    pos = 0
    matched = False
    for match in _DURATION_TOKEN_RE.finditer(text):
        if match.start() != pos:
            return None  # 中间有无法识别的字符，整体判非法
        total += float(match.group(1)) * _DURATION_UNITS[match.group(2)]
        pos = match.end()
        matched = True
    if not matched or pos != len(text):
        return None
    return -total if negative else total


def normalize_duration(value, default, field):
    """校验 Go 时长字符串并原样返回（保留用户写法，如 "2m" 不改写成 "120s"）。"""
    text = str(value if value not in ("", None) else default).strip()
    seconds = parse_go_duration_seconds(text)
    if seconds is None:
        raise ValueError(f"Invalid duration for {field}: {value}")
    if seconds <= 0:
        raise ValueError(f"Duration for {field} must be positive: {value}")
    return text


def validate_urltest_timing(interval, idle_timeout):
    """官方 sing-box protocol/group/urltest.go NewURLTestGroup:
    `if interval > idle_timeout { return error }` —— 这是运行期检查，
    `sing-box check` 返回 0 也可能启动失败，所以必须在保存前拦住。
    """
    interval_seconds = parse_go_duration_seconds(interval)
    idle_seconds = parse_go_duration_seconds(idle_timeout)
    if interval_seconds is None:
        raise ValueError(f"Invalid duration for auto.interval: {interval}")
    if idle_seconds is None:
        raise ValueError(f"Invalid duration for auto.idle_timeout: {idle_timeout}")
    if interval_seconds > idle_seconds:
        raise ValueError(
            f"auto.interval ({interval}) must be less or equal than auto.idle_timeout ({idle_timeout}); "
            "sing-box refuses to start otherwise"
        )


def normalize_cidr(value, default=None, strict=False):
    cidr = str(value or "").strip()
    if not cidr:
        return default
    try:
        return str(ipaddress.ip_network(cidr, strict=strict))
    except Exception as exc:
        hint = ""
        if strict:
            hint = "; use a network address, for example 28.0.0.0/8"
        raise ValueError(f"Invalid CIDR: {value}{hint}") from exc


def normalize_telegram_cidrs(items):
    if not isinstance(items, list):
        raise ValueError("Telegram CIDR list must be an array")
    networks = []
    for item in items:
        cidr = str(item or "").strip().strip("'\"")
        if not cidr:
            continue
        networks.append(ipaddress.ip_network(cidr, strict=False))
    collapsed = []
    for version in (4, 6):
        version_networks = [network for network in networks if network.version == version]
        collapsed.extend(ipaddress.collapse_addresses(version_networks))
    collapsed = sorted(collapsed, key=lambda net: (net.version, int(net.network_address), net.prefixlen))
    if not [item for item in collapsed if item.version == 4]:
        raise ValueError("Telegram CIDR list must include IPv4 ranges")
    if not [item for item in collapsed if item.version == 6]:
        raise ValueError("Telegram CIDR list must include IPv6 ranges")
    return [str(item) for item in collapsed]


def default_telegram_cidrs():
    return normalize_telegram_cidrs([*DEFAULT_TELEGRAM_PROXY_IPV4, *DEFAULT_TELEGRAM_PROXY_IPV6])


def parse_telegram_cidr_text(text):
    items = []
    invalid_lines = []
    for raw_line in str(text or "").splitlines():
        line = raw_line.split("#", 1)[0].strip().strip("'\"")
        if not line:
            continue
        if line.startswith("- "):
            line = line[2:].strip().strip("'\"")
        if "," in line:
            parts = [part.strip().strip("'\"") for part in line.split(",")]
            line = next((part for part in parts if "/" in part), line)
        # 单行脏数据(镜像返回 HTML 错误页/截断行)不应让整次更新崩掉——
        # 跳过并记录，最终以"是否解析出合法的 v4+v6 网段"为准(normalize 里强校验)。
        try:
            items.append(str(ipaddress.ip_network(line, strict=False)))
        except ValueError:
            invalid_lines.append(line)
            continue
    if invalid_lines and not items:
        raise ValueError(f"No valid CIDR lines found (first invalid: {invalid_lines[0][:80]})")
    return normalize_telegram_cidrs(items)


def split_telegram_cidrs(items):
    normalized = normalize_telegram_cidrs(items)
    return {
        "ipv4": [item for item in normalized if ":" not in item],
        "ipv6": [item for item in normalized if ":" in item],
    }


def load_telegram_cidr_data():
    data = load_json(TELEGRAM_CIDR_PATH, {})
    fallback = False
    try:
        cidrs = normalize_telegram_cidrs(data.get("cidrs", []))
    except Exception:
        cidrs = default_telegram_cidrs()
        data = {}
        fallback = True
    split = split_telegram_cidrs(cidrs)
    return {
        "path": str(TELEGRAM_CIDR_PATH),
        "source": data.get("source") or "built-in default",
        "updatedAt": data.get("updatedAt") or "",
        "updatedAtUnix": data.get("updatedAtUnix") or 0,
        "fallback": fallback,
        "cidrs": [*split["ipv4"], *split["ipv6"]],
        "ipv4": split["ipv4"],
        "ipv6": split["ipv6"],
        "count4": len(split["ipv4"]),
        "count6": len(split["ipv6"]),
        "count": len(split["ipv4"]) + len(split["ipv6"]),
    }


def save_telegram_cidrs(cidrs, source="manual"):
    normalized = normalize_telegram_cidrs(cidrs)
    updated_at_unix = int(time.time())
    MANAGER_DIR.mkdir(parents=True, exist_ok=True)
    write_json(
        TELEGRAM_CIDR_PATH,
        {
            "source": source,
            "updatedAt": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(updated_at_unix)),
            # 页面按浏览器本地时区格式化时间；避免生产机使用 UTC 时让用户误以为更新时间没有变化。
            "updatedAtUnix": updated_at_unix,
            "cidrs": normalized,
        },
    )
    return load_telegram_cidr_data()


def resolve_source_ipv4(host):
    for server in TELEGRAM_CIDR_DNS_SERVERS:
        try:
            query_id = secrets.randbelow(65536).to_bytes(2, "big")
            packet = query_id + b"\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00"
            for label in host.rstrip(".").split("."):
                raw = label.encode("ascii")
                packet += bytes([len(raw)]) + raw
            packet += b"\x00\x00\x01\x00\x01"
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as dns_sock:
                dns_sock.settimeout(3)
                dns_sock.sendto(packet, (server, 53))
                data, _ = dns_sock.recvfrom(512)
            if len(data) < 12 or data[:2] != query_id:
                continue
            answer_count = int.from_bytes(data[6:8], "big")
            offset = 12
            while offset < len(data) and data[offset]:
                offset += data[offset] + 1
            offset += 5
            for _ in range(answer_count):
                if offset >= len(data):
                    break
                if data[offset] & 0xC0 == 0xC0:
                    offset += 2
                else:
                    while offset < len(data) and data[offset]:
                        offset += data[offset] + 1
                    offset += 1
                if offset + 10 > len(data):
                    break
                record_type = int.from_bytes(data[offset : offset + 2], "big")
                record_class = int.from_bytes(data[offset + 2 : offset + 4], "big")
                rdlength = int.from_bytes(data[offset + 8 : offset + 10], "big")
                offset += 10
                value = data[offset : offset + rdlength]
                offset += rdlength
                if record_type == 1 and record_class == 1 and rdlength == 4:
                    # 不依赖 dig/dnsutils，直接向外部 DNS 查询 A 记录，避免本机 FakeIP DNS 影响维护更新。
                    return str(ipaddress.IPv4Address(value))
        except Exception:
            continue
    return ""


def fetch_telegram_cidr_source(source):
    parsed = urlparse(source)
    host = parsed.hostname or ""
    command = ["curl", "-4", "-fsSL", "--connect-timeout", "4", "--max-time", "20"]
    resolved = resolve_source_ipv4(host) if host else ""
    if resolved and parsed.scheme == "https":
        # UI 后端同样要绕开本机 FakeIP DNS，否则宿主机 DNS 指向 sing-box 时在线更新会直连 FakeIP 失败。
        command.extend(["--resolve", f"{host}:443:{resolved}"])
    command.append(source)
    result = subprocess.run(command, capture_output=True, text=True, timeout=25)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or f"curl exited {result.returncode}")
    return result.stdout


def update_telegram_cidrs():
    errors = []
    if not TELEGRAM_CIDR_SOURCES:
        return {"ok": False, "source": "", "telegramCidr": load_telegram_cidr_data(), "tproxySync": None, "errors": ["No Telegram CIDR sources configured"]}
    if RULE_UPDATE_SCRIPT.exists():
        env = os.environ.copy()
        env.setdefault("RULE_UPDATE_RESTART", "0")
        # Telegram IP 网段更新只需要刷新 manager/telegram-cidr.json 并同步 TProxy；
        # 复用完整规则更新会额外下载 geosite/geoip，导致 UI 小按钮被慢镜像拖住。
        env.setdefault("RULE_UPDATE_ONLY_TELEGRAM_CIDR", "1")
        env.setdefault("RULE_UPDATE_TELEGRAM_CIDR_SOURCES", " ".join(TELEGRAM_CIDR_SOURCES))
        result = subprocess.run([str(RULE_UPDATE_SCRIPT)], capture_output=True, text=True, timeout=60, env=env)
        if result.returncode == 0:
            data = load_telegram_cidr_data()
            sync = sync_tproxy()
            return {
                "ok": sync["code"] == 0,
                "source": data.get("source", "rule update script"),
                "telegramCidr": data,
                "tproxySync": sync,
                "errors": [],
                "script": {"code": result.returncode, "stdout": result.stdout.strip(), "stderr": result.stderr.strip()},
            }
        if result.returncode == 75:
            # 锁冲突说明已有规则更新正在写同一批文件；不能降级为并发直连下载，否则会破坏脚本的互斥语义。
            return {"ok": False, "source": "", "telegramCidr": load_telegram_cidr_data(), "tproxySync": None, "errors": [result.stderr.strip() or result.stdout.strip() or "another rule update is already running"]}
        errors.append(f"{RULE_UPDATE_SCRIPT}: {result.stderr.strip() or result.stdout.strip() or f'exited {result.returncode}'}")
    for source in TELEGRAM_CIDR_SOURCES:
        try:
            text = fetch_telegram_cidr_source(source)
            data = save_telegram_cidrs(parse_telegram_cidr_text(text), source=source)
            sync = sync_tproxy()
            return {"ok": sync["code"] == 0, "source": source, "telegramCidr": data, "tproxySync": sync, "errors": errors}
        except Exception as exc:
            errors.append(f"{source}: {exc}")
    return {"ok": False, "source": "", "telegramCidr": load_telegram_cidr_data(), "tproxySync": None, "errors": errors}


def normalize_node(raw):
    if not isinstance(raw, dict):
        raise ValueError("node must be an object")
    outbound = dict(raw.get("outbound") or {})
    node_type = str(outbound.get("type") or raw.get("type") or "").strip()
    if node_type not in SUPPORTED_NODE_TYPES:
        raise ValueError(f"Unsupported node type: {node_type}")
    tag = normalize_tag(outbound.get("tag") or raw.get("tag"))
    outbound["type"] = node_type
    outbound["tag"] = tag
    outbound["server"] = normalize_host(outbound.get("server"))
    outbound["server_port"] = normalize_port(outbound.get("server_port"))
    if node_type == "hysteria2":
        if not str(outbound.get("password", "")).strip():
            raise ValueError(f"{tag}: password is required")
        outbound["password"] = str(outbound["password"]).strip()
        up = normalize_positive_number(outbound.get("up_mbps"), None)
        down = normalize_positive_number(outbound.get("down_mbps"), None)
        if up is not None:
            outbound["up_mbps"] = up
        if down is not None:
            outbound["down_mbps"] = down
    if node_type == "vless":
        if not str(outbound.get("uuid", "")).strip():
            raise ValueError(f"{tag}: uuid is required")
        outbound["uuid"] = str(outbound["uuid"]).strip()
        brutal = outbound.get("multiplex", {}).get("brutal") if isinstance(outbound.get("multiplex"), dict) else None
        if isinstance(brutal, dict):
            up = normalize_positive_number(brutal.get("up_mbps"), None)
            down = normalize_positive_number(brutal.get("down_mbps"), None)
            if brutal.get("enabled") is False:
                # 选择系统 BBR/TCP 时删除整个 multiplex，保证 VLESS 回到普通 TCP，由内核拥塞控制接管。
                outbound.pop("multiplex", None)
            elif up is not None:
                brutal["up_mbps"] = up
            else:
                brutal.pop("up_mbps", None)
            if isinstance(outbound.get("multiplex", {}).get("brutal"), dict):
                if down is not None:
                    brutal["down_mbps"] = down
                else:
                    brutal.pop("down_mbps", None)
    if node_type == "shadowsocks":
        # Shadowsocks 出站（支持 SIP003 plugin，如 v2ray-plugin websocket-tls）。
        # 必填 password；method 缺省给 chacha20-ietf-poly1305；plugin/plugin_opts 原样透传。
        if not str(outbound.get("password", "")).strip():
            raise ValueError(f"{tag}: password is required")
        outbound["password"] = str(outbound["password"]).strip()
        if not str(outbound.get("method", "")).strip():
            outbound["method"] = "chacha20-ietf-poly1305"
        outbound["method"] = str(outbound["method"]).strip()
        if outbound.get("plugin"):
            outbound["plugin"] = str(outbound["plugin"]).strip()
        if outbound.get("plugin_opts"):
            outbound["plugin_opts"] = str(outbound["plugin_opts"]).strip()
    if node_type == "socks":
        # SOCKS5 出站（本地中转）：指向本机 sslocal/ss-local 等程序的 socks5 入口，
        # 用于 sing-box 的 shadowsocks+SIP003 plugin 间歇性断流时改用 sslocal relay 提速。
        # 只需 server/server_port，无加密/密码/传输层字段；server 允许 127.0.0.1 本机。
        server = str(outbound.get("server", "")).strip()
        if not server:
            raise ValueError(f"{tag}: server is required")
        outbound["server"] = server
        if outbound.get("server_port"):
            outbound["server_port"] = int(outbound["server_port"])
        # 清理从其他类型带过来的多余字段，避免渲染出非法 outbound
        for key in ("password", "method", "plugin", "plugin_opts", "uuid", "tls", "obfs",
                    "multiplex", "up_mbps", "down_mbps", "packet_encoding", "tcp_fast_open"):
            outbound.pop(key, None)
    tls = outbound.get("tls")
    if isinstance(tls, dict):
        tls["enabled"] = normalize_bool(tls.get("enabled", True))
        if "insecure" in tls:
            tls["insecure"] = normalize_bool(tls["insecure"])
    return {"enabled": normalize_bool(raw.get("enabled", True)), "outbound": outbound}


def normalize_nodes(nodes):
    normalized = []
    seen = set()
    for raw in nodes or []:
        node = normalize_node(raw)
        tag = node["outbound"]["tag"]
        if tag in seen:
            raise ValueError(f"Duplicate node tag: {tag}")
        seen.add(tag)
        normalized.append(node)
    return normalized


def entries_to_rule_set(entries):
    grouped = {kind: [] for kind in ENTRY_TYPES}
    for item in entries:
        grouped[item["type"]].append(item["value"])
    rule = {kind: values for kind, values in grouped.items() if values}
    return {"version": 3, "rules": [rule] if rule else []}


def extract_initial_manager_data(config):
    outbounds = config.get("outbounds", []) or []
    nodes = []
    proxy = None
    auto = None
    direct = None
    block = None
    fakeip = {}
    local_dns_choice = DEFAULT_LOCAL_DNS_CHOICE
    for outbound in outbounds:
        tag = outbound.get("tag")
        if tag == "Proxy":
            proxy = outbound
        elif tag == "Auto":
            auto = outbound
        elif tag == "direct":
            direct = outbound
        elif tag == "block":
            block = outbound
        elif tag:
            nodes.append({"enabled": True, "outbound": outbound})
    for server in config.get("dns", {}).get("servers", []) or []:
        if isinstance(server, dict) and server.get("type") == "fakeip":
            fakeip = {
                "tag": server.get("tag", "fakeip-dns"),
                "inet4_range": server.get("inet4_range", "28.0.0.0/8"),
                "inet6_range": server.get("inet6_range", "2001:2::/64"),
            }
            break
    for server in config.get("dns", {}).get("servers", []) or []:
        if isinstance(server, dict) and server.get("tag") == "local-dns":
            server_addr = str(server.get("server", "")).strip()
            if server_addr in LOCAL_DNS_BY_SERVER:
                local_dns_choice = LOCAL_DNS_BY_SERVER[server_addr]
            else:
                local_dns_choice = "custom_dns"
            break
    base = json.loads(json.dumps(config))
    base["outbounds"] = []
    groups = {
        "proxy": {
            "default": (proxy or {}).get("default", "Auto"),
            "interrupt_exist_connections": (proxy or {}).get("interrupt_exist_connections", DEFAULT_INTERRUPT_EXIST_CONNECTIONS),
        },
        "auto": {
            "url": (auto or {}).get("url", "https://www.gstatic.com/generate_204"),
            "interval": (auto or {}).get("interval", "30s"),
            "idle_timeout": (auto or {}).get("idle_timeout", DEFAULT_URLTEST_IDLE_TIMEOUT),
            "tolerance": (auto or {}).get("tolerance", DEFAULT_URLTEST_TOLERANCE),
            "interrupt_exist_connections": (auto or {}).get("interrupt_exist_connections", DEFAULT_INTERRUPT_EXIST_CONNECTIONS),
        },
        "direct": direct or {"type": "direct", "tag": "direct"},
        "block": block or {"type": "block", "tag": "block"},
        "fakeip": {
            **{
                "tag": "fakeip-dns",
                "inet4_range": "28.0.0.0/8",
                "inet6_range": "2001:2::/64",
                "ipv6_enabled": True,
                "block_quic": True,
            },
            **fakeip,
        },
        "dns": {"local": local_dns_choice, "local_custom_server": "223.5.5.5", "local_custom_port": 53},
        "ddns": {"dns": "local"},
    }
    return base, normalize_nodes(nodes), groups


def ensure_manager_data():
    ensure_dirs()
    if BASE_CONFIG_PATH.exists() and NODES_PATH.exists() and GROUPS_PATH.exists():
        return
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    base, nodes, groups = extract_initial_manager_data(config)
    if not BASE_CONFIG_PATH.exists():
        write_json(BASE_CONFIG_PATH, base)
    if not NODES_PATH.exists():
        write_json(NODES_PATH, nodes)
    if not GROUPS_PATH.exists():
        write_json(GROUPS_PATH, groups)


def load_nodes():
    ensure_manager_data()
    return normalize_nodes(load_json(NODES_PATH, []))


def load_groups():
    ensure_manager_data()
    groups = load_json(GROUPS_PATH, {})
    groups.setdefault("proxy", {})
    groups.setdefault("auto", {})
    groups.setdefault("direct", {"type": "direct", "tag": "direct"})
    groups.setdefault("block", {"type": "block", "tag": "block"})
    groups.setdefault("fakeip", {})
    groups.setdefault("dns", {})
    groups.setdefault("ddns", {})
    groups.setdefault("telegram", {})
    groups.setdefault("socks5", {})
    groups["socks5"].setdefault("port", 0)
    groups["proxy"].setdefault("default", "Auto")
    groups["proxy"].setdefault("interrupt_exist_connections", DEFAULT_INTERRUPT_EXIST_CONNECTIONS)
    # 默认保护游戏/语音等长连接；用户可在 UI 高级开关里明确选择切换时中断旧连接。
    groups["proxy"]["interrupt_exist_connections"] = normalize_bool(groups["proxy"]["interrupt_exist_connections"])
    groups["auto"].setdefault("url", "https://www.gstatic.com/generate_204")
    groups["auto"].setdefault("interval", "30s")
    groups["auto"].setdefault("interrupt_exist_connections", DEFAULT_INTERRUPT_EXIST_CONNECTIONS)
    # urltest 默认只影响新连接；需要快速脱离坏节点时，用户可以手动开启中断旧连接。
    groups["auto"]["interrupt_exist_connections"] = normalize_bool(groups["auto"]["interrupt_exist_connections"])
    # idle_timeout / tolerance 与官方默认值一致（constant/timeout.go DefaultURLTestIdleTimeout=30m、
    # urltest.go NewURLTestGroup tolerance=50），但都是用户可调项，不是写死的行为。
    groups["auto"].setdefault("idle_timeout", DEFAULT_URLTEST_IDLE_TIMEOUT)
    groups["auto"].setdefault("tolerance", DEFAULT_URLTEST_TOLERANCE)
    groups["fakeip"].setdefault("tag", "fakeip-dns")
    groups["fakeip"].setdefault("inet4_range", "28.0.0.0/8")
    groups["fakeip"].setdefault("inet6_range", "2001:2::/64")
    groups["fakeip"].setdefault("ipv6_enabled", True)
    groups["fakeip"]["ipv6_enabled"] = normalize_bool(groups["fakeip"]["ipv6_enabled"])
    # FakeIP QUIC 保护固定开启，避免旧备份或旧 UI 状态把稳定性边界关掉。
    groups["fakeip"]["block_quic"] = True
    if groups["dns"].get("local") not in LOCAL_DNS_CHOICES:
        groups["dns"]["local"] = DEFAULT_LOCAL_DNS_CHOICE
    groups["dns"].setdefault("local_custom_server", "223.5.5.5")
    groups["dns"].setdefault("local_custom_port", 53)
    if groups["ddns"].get("dns") not in ("local", "remote"):
        groups["ddns"]["dns"] = "local"
    groups["telegram"].setdefault("capture_ips", True)
    groups["telegram"]["capture_ips"] = normalize_bool(groups["telegram"]["capture_ips"])
    return groups


def enabled_node_tags(nodes):
    return [node["outbound"]["tag"] for node in nodes if node.get("enabled", True)]


def preferred_auto_outbounds(tags, groups):
    preferred = str(groups.get("auto", {}).get("preferred", "")).strip()
    if preferred in tags:
        # urltest 重启后会按 outbounds 顺序在容差内挑选；把保存前 Auto 子节点放前面，避免保存容差时回到列表第一个。
        return [preferred, *[tag for tag in tags if tag != preferred]]
    return tags


def render_config(nodes=None, groups=None, rule_dir=RULE_DIR, normalized_lists=None):
    ensure_manager_data()
    nodes = normalize_nodes(nodes if nodes is not None else load_nodes())
    groups = groups or load_groups()
    tags = enabled_node_tags(nodes)
    if not tags:
        raise ValueError("At least one node must be enabled")
    config = load_json(BASE_CONFIG_PATH, {})
    rewrite_custom_rule_paths(config, rule_dir)
    ensure_managed_rule_sets(config)
    remove_legacy_app_rule_sets(config)
    apply_portable_listeners(config)
    apply_cache_file_settings(config)
    apply_local_dns_settings(config, groups)
    apply_ddns_remote_dns_settings(config)
    apply_fakeip_settings(config, groups)
    apply_blacklist_dns_reject(config)
    apply_whitelist_dns_direct(config)
    apply_greylist_dns_fakeip(config, groups)
    apply_inbound_dns_fakeip_fallback(config, groups)
    apply_lan_probe_dns_reject(config)
    apply_ddns_dns_settings(config, groups)
    apply_fakeip_route_rule(config, groups)
    apply_direct_speedtest_route(config)
    apply_direct_telegram_route(config)
    apply_fakeip_quic_policy(config, groups)
    apply_route_final_policy(config)
    proxy_default = groups.get("proxy", {}).get("default", "Auto")
    if proxy_default not in {"Auto", *tags}:
        proxy_default = "Auto"
    proxy = {
        "type": "selector",
        "tag": "Proxy",
        "outbounds": ["Auto", *tags],
        "default": proxy_default,
        "interrupt_exist_connections": normalize_bool(
            groups.get("proxy", {}).get("interrupt_exist_connections", DEFAULT_INTERRUPT_EXIST_CONNECTIONS)
        ),
    }
    auto = {
        "type": "urltest",
        "tag": "Auto",
        "outbounds": preferred_auto_outbounds(tags, groups),
        "url": groups.get("auto", {}).get("url", "https://www.gstatic.com/generate_204"),
        "interval": groups.get("auto", {}).get("interval", "30s"),
        # tolerance：候选节点必须比当前节点快这么多毫秒才接替（官方 urltest.go Select 里
        # `minDelay > history.Delay+g.tolerance`），是防抖阈值——真正的节点切换判据。
        "tolerance": normalize_non_negative_number(
            groups.get("auto", {}).get("tolerance", DEFAULT_URLTEST_TOLERANCE), DEFAULT_URLTEST_TOLERANCE
        ),
        # 官方 sing-box urltest：idle_timeout 到点后停止周期测速（有流量再恢复），
        # 不是 reF1nd fallback 的等价物；节点切换由 interval + tolerance 决定
        "idle_timeout": groups.get("auto", {}).get("idle_timeout", DEFAULT_URLTEST_IDLE_TIMEOUT),
        # 默认只影响新连接；如果用户开启高级开关，则允许切换时主动清理旧连接。
        "interrupt_exist_connections": normalize_bool(
            groups.get("auto", {}).get("interrupt_exist_connections", DEFAULT_INTERRUPT_EXIST_CONNECTIONS)
        ),
    }
    # interval > idle_timeout 时官方 NewURLTestGroup 直接返回错误（sing-box 起不来），
    # 而 `sing-box check` 是静态校验抓不到——渲染时就拦住，避免落盘一个起不来的配置。
    validate_urltest_timing(auto["interval"], auto["idle_timeout"])
    direct = groups.get("direct") or {"type": "direct", "tag": "direct"}
    block = groups.get("block") or {"type": "block", "tag": "block"}
    config["outbounds"] = [proxy, auto, *[node["outbound"] for node in nodes if node.get("enabled", True)], direct, block]
    prune_managed_outbound_references(config, tags)
    return config


def prune_managed_outbound_references(config, valid_tags):
    valid = set(valid_tags) | SPECIAL_OUTBOUNDS

    def scrub_outbound_refs(value):
        if isinstance(value, dict):
            for key, item in list(value.items()):
                if key in {"outbound", "detour"} and isinstance(item, str) and item not in valid:
                    # 删除节点后，旧配置里的直连节点引用要回到受管理的 Proxy，避免引用不存在的 outbound。
                    value[key] = "Proxy"
                elif key in {"final", "default"} and isinstance(item, str) and item not in valid:
                    value[key] = "direct" if key == "final" else "Auto"
                elif key == "outbounds" and isinstance(item, list):
                    value[key] = [tag for tag in item if not isinstance(tag, str) or tag in valid]
                else:
                    scrub_outbound_refs(item)
        elif isinstance(value, list):
            for item in value:
                scrub_outbound_refs(item)

    def scrub_dns_detours(value):
        if isinstance(value, dict):
            for key, item in list(value.items()):
                if key == "detour" and isinstance(item, str) and item not in valid:
                    # DNS 的 final/default/server 指向 DNS server tag，不能按 outbound 规则改；只清理 detour。
                    value[key] = "Proxy"
                else:
                    scrub_dns_detours(item)
        elif isinstance(value, list):
            for item in value:
                scrub_dns_detours(item)

    scrub_dns_detours(config.get("dns", {}))
    scrub_outbound_refs(config.get("route", {}))
    for outbound in config.get("outbounds", []) or []:
        if isinstance(outbound, dict):
            scrub_outbound_refs(outbound)


def apply_route_final_policy(config):
    route = config.setdefault("route", {})
    rules = route.setdefault("rules", [])
    rules[:] = [
        rule
        for rule in rules
        if not (isinstance(rule, dict) and rule.get("outbound") == "direct" and set(rule.keys()) == {"outbound"})
    ]
    # 2026-08-20 小哥拍板：兜底出口跟随 base.json 的 route.final（现为 Proxy），不再写死 direct。
    # 8-19 二次回滚曾强制 direct；改回尊重源头配置，仅校验合法值，非法/缺失时兜底 direct。
    final = route.get("final", "direct")
    if final not in ("direct", "Proxy"):
        final = "direct"
    route["final"] = final


def managed_binary_rule_set(tag, path):
    return {"type": "local", "tag": tag, "format": "binary", "path": path}


def ensure_managed_rule_sets(config):
    route = config.setdefault("route", {})
    rule_sets = route.setdefault("rule_set", [])
    existing = {item.get("tag") for item in rule_sets if isinstance(item, dict)}
    managed = [
        managed_binary_rule_set("geosite-speedtest", "/etc/sing-box/rules/geosite/speedtest.srs"),
        managed_binary_rule_set("geosite-telegram", "/etc/sing-box/rules/geosite/telegram.srs"),
        managed_binary_rule_set("geoip-telegram", "/etc/sing-box/rules/geoip/telegram.srs"),
    ]
    for item in managed:
        if item["tag"] in existing:
            continue
        # 路由规则引用的内置规则集必须在同一份配置里声明，避免旧安装升级后保存出不可启动配置。
        rule_sets.append(item)


def remove_legacy_rule_set_values(value):
    if isinstance(value, list):
        kept = [item for item in value if item not in LEGACY_APP_RULE_SETS]
        if not kept:
            return None
        return kept[0] if len(kept) == 1 else kept
    if value in LEGACY_APP_RULE_SETS:
        return None
    return value


def remove_legacy_app_rule_sets(config):
    route = config.setdefault("route", {})
    route["rule_set"] = [
        item
        for item in route.get("rule_set", []) or []
        if not (isinstance(item, dict) and item.get("tag") in LEGACY_APP_RULE_SETS)
    ]
    for section_name in ("dns", "route"):
        rules = config.setdefault(section_name, {}).setdefault("rules", [])
        cleaned = []
        for rule in rules:
            if not isinstance(rule, dict):
                cleaned.append(rule)
                continue
            if "rule_set" not in rule:
                cleaned.append(rule)
                continue
            updated = dict(rule)
            updated["rule_set"] = remove_legacy_rule_set_values(updated.get("rule_set"))
            if updated["rule_set"] is None:
                continue
            cleaned.append(updated)
        # 旧版本曾把大量应用规则硬编码进 DNS/路由，维护成本高且会放大源失效影响；统一迁移到 geolocation 分流。
        rules[:] = cleaned


def remove_rule_set_value(value, target):
    if value == target:
        return None
    if isinstance(value, list):
        kept = [item for item in value if item != target]
        if not kept:
            return None
        return kept
    return value


def apply_direct_speedtest_route(config):
    rules = config.setdefault("route", {}).setdefault("rules", [])
    direct_rule = {"rule_set": "geosite-speedtest", "outbound": "direct"}
    fakeip_networks = set()
    for server in config.get("dns", {}).get("servers", []) or []:
        if isinstance(server, dict) and server.get("type") == "fakeip":
            fakeip_networks.update(
                str(value)
                for value in (server.get("inet4_range"), server.get("inet6_range"))
                if value
            )
    cleaned = []
    for rule in rules:
        if not isinstance(rule, dict):
            cleaned.append(rule)
            continue
        if rule.get("rule_set") == "geosite-speedtest" and rule.get("outbound") == "direct":
            continue
        rule_set = rule.get("rule_set")
        if rule.get("outbound") == "Proxy" and (
            rule_set == "geosite-speedtest" or (isinstance(rule_set, list) and "geosite-speedtest" in rule_set)
        ):
            updated = dict(rule)
            updated["rule_set"] = remove_rule_set_value(rule_set, "geosite-speedtest")
            if updated.get("rule_set") is None:
                continue
            cleaned.append(updated)
            continue
        cleaned.append(rule)
    rules[:] = cleaned
    insert_at = len(rules)
    for index, rule in enumerate(rules):
        if (
            isinstance(rule, dict)
            and rule.get("outbound") == "Proxy"
            and isinstance(rule.get("ip_cidr"), list)
            and any(str(item) in fakeip_networks for item in rule.get("ip_cidr", []))
        ):
            insert_at = index
            break
        if isinstance(rule, dict) and rule.get("rule_set") in (CUSTOM_TAGS["whitelist"], CUSTOM_TAGS["ddns"], CUSTOM_TAGS["greylist"]):
            insert_at = index + 1
    # 测速流量必须排在 FakeIP 捕获前；否则域名先变成 FakeIP 后会被送进代理。
    rules.insert(insert_at, direct_rule)


def apply_direct_telegram_route(config):
    rules = config.setdefault("route", {}).setdefault("rules", [])
    # 拆成两条 OR 规则而非 AND：域名匹配和 IP 匹配各自生效。
    # 裸 IP 连接没有域名，AND 会导致 geosite 匹配不上整条规则失败掉到 direct。
    telegram_rules = [
        {"rule_set": "geosite-telegram", "outbound": "Proxy"},
        {"rule_set": "geoip-telegram", "outbound": "Proxy"},
    ]
    cleaned = []
    for rule in rules:
        if not isinstance(rule, dict):
            cleaned.append(rule)
            continue
        rule_set = rule.get("rule_set")
        if rule.get("outbound") == "Proxy" and (
            rule_set in ("geosite-telegram", "geoip-telegram")
            or (isinstance(rule_set, list) and any(item in {"geosite-telegram", "geoip-telegram"} for item in rule_set))
        ):
            updated = dict(rule)
            updated["rule_set"] = remove_rule_set_value(
                remove_rule_set_value(rule_set, "geosite-telegram"),
                "geoip-telegram",
            )
            if updated.get("rule_set") is None:
                continue
            cleaned.append(updated)
            continue
        cleaned.append(rule)
    rules[:] = cleaned
    insert_at = len(rules)
    for index, rule in enumerate(rules):
        if (
            isinstance(rule, dict)
            and rule.get("outbound") == "Proxy"
            and isinstance(rule.get("ip_cidr"), list)
            and any(str(item).startswith(("28.", "2001:2", "2408:")) for item in rule.get("ip_cidr", []))
        ):
            insert_at = index
            break
        if isinstance(rule, dict) and rule.get("rule_set") == "geosite-speedtest":
            insert_at = index + 1
    # Telegram 客户端常直接连接官方 IP 段，必须在 FakeIP 捕获和 UDP/443 阻断前先送代理。
    for tr in reversed(telegram_rules):
        rules.insert(insert_at, tr)


def apply_fakeip_route_rule(config, groups):
    fakeip = groups.get("fakeip", {})
    fakeip4 = normalize_cidr(fakeip.get("inet4_range", "28.0.0.0/8"), "28.0.0.0/8")
    fakeip6 = normalize_cidr(fakeip.get("inet6_range", "2001:2::/64"), "2001:2::/64")
    fake_networks = {
        "28.0.0.0/8",
        "2001:2::/64",
        fakeip4,
        fakeip6,
    }
    rules = config.setdefault("route", {}).setdefault("rules", [])
    rules[:] = [
        rule
        for rule in rules
        if not (
            isinstance(rule, dict)
            and rule.get("outbound") == "Proxy"
            and isinstance(rule.get("ip_cidr"), list)
            and any(str(item) in fake_networks for item in rule.get("ip_cidr", []))
        )
    ]
    insert_at = 0
    for index, rule in enumerate(rules):
        if isinstance(rule, dict) and rule.get("rule_set") == CUSTOM_TAGS["greylist"]:
            insert_at = index + 1
            break
    rules.insert(insert_at, {"ip_cidr": [fakeip4, fakeip6], "outbound": "Proxy"})


def apply_fakeip_quic_policy(config, groups):
    fakeip = groups.get("fakeip", {})
    fakeip4 = normalize_cidr(fakeip.get("inet4_range", "28.0.0.0/8"), "28.0.0.0/8")
    fakeip6 = normalize_cidr(fakeip.get("inet6_range", "2001:2::/64"), "2001:2::/64")
    fake_networks = {
        "28.0.0.0/8",
        "2001:2::/64",
        fakeip4,
        fakeip6,
    }
    youtube_quic_domains = [
        "googlevideo.com",
        "youtube.com",
        "youtube-nocookie.com",
        "ytimg.com",
        "ggpht.com",
        "googleusercontent.com",
    ]
    rules = config.setdefault("route", {}).setdefault("rules", [])
    rules[:] = [
        rule
        for rule in rules
        if not (
            isinstance(rule, dict)
            and rule.get("network") == "udp"
            and rule.get("port") == 443
            and rule.get("outbound") in ("block", None)
            and (
                (
                    isinstance(rule.get("ip_cidr"), list)
                    and any(str(item) in fake_networks for item in rule.get("ip_cidr", []))
                )
                or rule.get("rule_set") in (CUSTOM_TAGS["greylist"], "geosite-geolocation-!cn")
                or (
                    isinstance(rule.get("rule_set"), list)
                    and any(item in {CUSTOM_TAGS["greylist"], "geosite-geolocation-!cn"} for item in rule.get("rule_set", []))
                )
                or (
                    isinstance(rule.get("domain_suffix"), list)
                    and any(str(item) in youtube_quic_domains for item in rule.get("domain_suffix", []))
                )
            )
            and (rule.get("outbound") == "block" or rule.get("action") == "reject")
        )
    ]
    insert_at = 0
    for index, rule in enumerate(rules):
        if isinstance(rule, dict) and rule.get("action") == "hijack-dns":
            insert_at = index + 1
            continue
        if isinstance(rule, dict) and rule.get("action") == "sniff":
            insert_at = index
            break
        if (
            isinstance(rule, dict)
            and rule.get("outbound") == "Proxy"
            and isinstance(rule.get("ip_cidr"), list)
            and any(str(item) in {fakeip4, fakeip6} for item in rule.get("ip_cidr", []))
        ):
            insert_at = index
            break
    # FakeIP 视频连接会被 sing-box 还原成域名，路由阶段不一定还能按 FakeIP CIDR 命中；用 reject 表达预期拒绝，避免 block 出站把正常 QUIC 回落记录成 ERROR。
    rules.insert(insert_at, {"network": "udp", "port": 443, "domain_suffix": youtube_quic_domains, "action": "reject"})
    # 同时保留 CIDR 保护，覆盖尚未还原域名的 FakeIP UDP/443；不能扩大到全部 UDP，否则会影响游戏和语音。
    rules.insert(insert_at, {"network": "udp", "port": 443, "ip_cidr": [fakeip4, fakeip6], "action": "reject"})


def apply_cache_file_settings(config):
    cache = config.setdefault("experimental", {}).setdefault("cache_file", {})
    cache["enabled"] = True
    cache["store_fakeip"] = True


def apply_portable_listeners(config):
    lan_ip = default_lan_ip()
    ipv6_listen = preferred_ipv6_listener(lan_ip)
    inbounds = config.get("inbounds", []) or []
    kept_inbounds = []
    for inbound in inbounds:
        if not isinstance(inbound, dict):
            kept_inbounds.append(inbound)
            continue
        listen = str(inbound.get("listen", ""))
        try:
            listen_port = int(inbound.get("listen_port") or 0)
            is_ipv4_listen = isinstance(ipaddress.ip_address(listen), ipaddress.IPv4Address)
        except Exception:
            listen_port = 0
            is_ipv4_listen = False
        if lan_ip and (inbound.get("tag") == "dns-in" or (inbound.get("type") == "direct" and listen_port == 53 and is_ipv4_listen)):
            inbound["listen"] = lan_ip
        if inbound.get("tag") == "dns-in-v6":
            if ipv6_listen:
                inbound["listen"] = ipv6_listen
            else:
                remove_inbound_tag(config, "dns-in-v6")
                continue
        kept_inbounds.append(inbound)
    if kept_inbounds != inbounds:
        config["inbounds"] = kept_inbounds
    if ipv6_listen and not any(isinstance(item, dict) and item.get("tag") == "dns-in-v6" for item in kept_inbounds):
        config.setdefault("inbounds", []).append({"type": "direct", "tag": "dns-in-v6", "listen": ipv6_listen, "listen_port": 53})
    socks5_port = int(load_groups().get("socks5", {}).get("port", 0) or 0)
    existing_socks5 = [i for i in config.get("inbounds", []) if isinstance(i, dict) and i.get("type") == "socks"]
    # socks 入站只绑 LAN IPv4，绝不监听 "::"——网关若有全局 IPv6，"::" 等于把
    # 无鉴权 socks5 直接暴露到公网。LAN 客户端本来就是通过网关 IPv4 地址使用它，
    # 绑 lan_ip 不损失功能；拿不到 lan_ip 时兜底 127.0.0.1，宁可暂时只本机可用也不裸奔。
    socks_listen = lan_ip or "127.0.0.1"
    if socks5_port > 0 and socks5_port <= 65535:
        if existing_socks5:
            existing_socks5[0]["listen_port"] = socks5_port
            existing_socks5[0]["listen"] = socks_listen
        else:
            config.setdefault("inbounds", []).append({
                "type": "socks",
                "tag": "socks-in",
                "listen": socks_listen,
                "listen_port": socks5_port,
                "sniff": False,
            })
    elif existing_socks5:
        config["inbounds"] = [i for i in config.get("inbounds", []) if not (isinstance(i, dict) and i.get("type") == "socks")]
        add_inbound_tag(config, "dns-in-v6")
    clash = config.setdefault("experimental", {}).setdefault("clash_api", {})
    controller = str(clash.get("external_controller", "")).strip()
    controller_host = controller.rsplit(":", 1)[0] if ":" in controller else controller
    try:
        is_ipv4_controller = isinstance(ipaddress.ip_address(controller_host), ipaddress.IPv4Address)
    except Exception:
        is_ipv4_controller = False
    if lan_ip and (not controller or is_ipv4_controller):
        clash["external_controller"] = f"{lan_ip}:9090"


def assigned_ipv6_addresses():
    result = run_command(["ip", "-o", "-6", "addr", "show", "scope", "global"], timeout=8)
    addresses = []
    for line in result["stdout"].splitlines():
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

    # 只在私有(ULA)地址上监听 53 端口 DNS。全局单播(GUA)可被公网直接路由，
    # 绑上去等于对全网开放递归解析(开放解析器会被滥用于 DNS 放大攻击)。
    # 没有 ULA 时宁可不提供 IPv6 DNS 监听(dns-in-v6 会被移除)，也不裸奔。
    private_addresses = [address for address in addresses if address.is_private]
    if not private_addresses:
        return ""

    def score(address):
        text = str(address)
        if "ff:fe" not in text:
            return 0
        return 1

    return str(sorted(private_addresses, key=score)[0])


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


def apply_fakeip_settings(config, groups):
    fakeip = groups.get("fakeip", {})
    inet4_range = normalize_cidr(fakeip.get("inet4_range", "28.0.0.0/8"), "28.0.0.0/8")
    inet6_range = normalize_cidr(fakeip.get("inet6_range", "2001:2::/64"), "2001:2::/64")
    tag = str(fakeip.get("tag", "fakeip-dns")).strip() or "fakeip-dns"
    servers = config.setdefault("dns", {}).setdefault("servers", [])
    target = None
    for server in servers:
        if isinstance(server, dict) and (server.get("type") == "fakeip" or server.get("tag") == tag):
            target = server
            break
    if target is None:
        target = {"tag": tag, "type": "fakeip"}
        servers.append(target)
    target["tag"] = tag
    target["type"] = "fakeip"
    target["inet4_range"] = inet4_range
    target["inet6_range"] = inet6_range


def local_dns_server_config(choice, groups_dns=None):
    if choice == "custom_dns" and groups_dns:
        server = json.loads(json.dumps(LOCAL_DNS_SERVER))
        server["server"] = groups_dns.get("local_custom_server", "223.5.5.5")
        server["server_port"] = int(groups_dns.get("local_custom_port", 53))
        return server
    item = LOCAL_DNS_CHOICES.get(choice, LOCAL_DNS_CHOICES[DEFAULT_LOCAL_DNS_CHOICE])
    server = json.loads(json.dumps(LOCAL_DNS_SERVER))
    server["server"] = item["server"]
    server["server_port"] = item["server_port"]
    return server


def apply_local_dns_settings(config, groups):
    servers = config.setdefault("dns", {}).setdefault("servers", [])
    groups_dns = groups.get("dns", {})
    choice = groups_dns.get("local", DEFAULT_LOCAL_DNS_CHOICE)
    desired = local_dns_server_config(choice, groups_dns)
    target = None
    for server in servers:
        if isinstance(server, dict) and server.get("tag") == "local-dns":
            target = server
            break
    if target is None:
        servers.append(desired)
        return
    target.clear()
    # local-dns 是国内直连域名的唯一上游，保存时必须按 UI 选择精确写入，不能伪装成并发或备用。
    target.update(desired)


def apply_ddns_remote_dns_settings(config):
    servers = config.setdefault("dns", {}).setdefault("servers", [])
    desired = json.loads(json.dumps(DDNS_REMOTE_DNS_SERVER))
    target = None
    for server in servers:
        if isinstance(server, dict) and server.get("tag") == desired["tag"]:
            target = server
            break
    if target is None:
        servers.append(desired)
        return
    target.clear()
    # 这个 server 是 DDNS remote 模式的稳定边界，保存时必须恢复到受管理定义，避免回退到 DoH 长连接。
    target.update(desired)


def apply_blacklist_dns_reject(config):
    dns_rules = config.setdefault("dns", {}).setdefault("rules", [])
    dns_rules[:] = [
        rule
        for rule in dns_rules
        if not (isinstance(rule, dict) and rule.get("rule_set") == CUSTOM_TAGS["blacklist"] and rule.get("action") == "reject")
    ]
    dns_rules.insert(0, {"rule_set": CUSTOM_TAGS["blacklist"], "action": "reject"})


def apply_whitelist_dns_direct(config):
    dns_rules = config.setdefault("dns", {}).setdefault("rules", [])
    dns_rules[:] = [
        rule
        for rule in dns_rules
        if not (
            isinstance(rule, dict)
            and rule.get("rule_set") == CUSTOM_TAGS["whitelist"]
            and rule.get("action") == "route"
        )
    ]
    insert_at = 0
    for index, rule in enumerate(dns_rules):
        if isinstance(rule, dict) and rule.get("rule_set") == CUSTOM_TAGS["blacklist"] and rule.get("action") == "reject":
            insert_at = index + 1
            break
    # 白名单既然要直连，DNS 也必须返回真实地址；否则 LAN 兜底 FakeIP 会让 IPv6 外测继续进入代理链路。
    dns_rules.insert(insert_at, {"rule_set": CUSTOM_TAGS["whitelist"], "action": "route", "server": "local-dns", "rewrite_ttl": 60})


def apply_greylist_dns_fakeip(config, groups=None):
    query_types = fakeip_query_types(groups)
    dns_rules = config.setdefault("dns", {}).setdefault("rules", [])
    dns_rules[:] = [
        rule
        for rule in dns_rules
        if not (
            isinstance(rule, dict)
            and rule.get("rule_set") == CUSTOM_TAGS["greylist"]
            and rule.get("server") == "fakeip-dns"
        )
    ]
    dns_rules.insert(
        1,
        {
            "rule_set": CUSTOM_TAGS["greylist"],
            "action": "route",
            "server": "fakeip-dns",
            "rewrite_ttl": 60,
            "query_type": query_types,
        },
    )


def fakeip_query_types(groups=None):
    fakeip = (groups or load_groups()).get("fakeip", {})
    return ["A", "AAAA"] if normalize_bool(fakeip.get("ipv6_enabled", True)) else ["A"]


def apply_inbound_dns_fakeip_fallback(config, groups=None):
    query_types = fakeip_query_types(groups)
    dns_rules = config.setdefault("dns", {}).setdefault("rules", [])
    dns_inbounds = dns_inbound_tags(config)
    normalize_lan_fakeip_query_types(dns_rules, dns_inbounds, query_types)
    dns_rules[:] = [
        rule
        for rule in dns_rules
        if not (
            isinstance(rule, dict)
            and same_inbound(rule.get("inbound"), dns_inbounds)
            and rule.get("query_type") in (["A"], ["A", "AAAA"])
            and rule.get("action") == "route"
            and rule.get("server") in ("remote-dns", "fakeip-dns")
            and "rule_set" not in rule
        )
    ]
    insert_at = 0
    for index, rule in enumerate(dns_rules):
        if isinstance(rule, dict) and same_inbound(rule.get("inbound"), dns_inbounds):
            insert_at = index + 1
    dns_rules.insert(
        insert_at,
        {
            "inbound": dns_inbounds,
            "query_type": query_types,
            "action": "route",
            "server": "fakeip-dns",
            "rewrite_ttl": 60,
        },
    )
    apply_lan_aaaa_reject(config, dns_inbounds, enabled=query_types == ["A"])


def normalize_lan_fakeip_query_types(dns_rules, dns_inbounds, query_types):
    for rule in dns_rules:
        if (
            isinstance(rule, dict)
            and same_inbound(rule.get("inbound"), dns_inbounds)
            and rule.get("server") == "fakeip-dns"
            and rule.get("query_type") in (["A"], ["A", "AAAA"])
        ):
            # 所有 LAN 入站的 FakeIP 规则必须共用同一查询类型；否则旧 geosite 规则会在 AAAA 拒绝前返回 IPv6 FakeIP。
            rule["query_type"] = query_types


def apply_lan_aaaa_reject(config, dns_inbounds, enabled):
    dns_rules = config.setdefault("dns", {}).setdefault("rules", [])
    dns_rules[:] = [
        rule
        for rule in dns_rules
        if not is_lan_aaaa_reject_rule(rule)
    ]
    if not enabled:
        return
    insert_at = 0
    for index, rule in enumerate(dns_rules):
        if isinstance(rule, dict) and same_inbound(rule.get("inbound"), dns_inbounds):
            insert_at = index + 1
    # 关闭 IPv6 FakeIP 时，LAN 入站的 AAAA 必须明确拒绝，避免客户端拿到真实 IPv6 后绕过 IPv4 代理路径。
    dns_rules.insert(insert_at, {"inbound": dns_inbounds, "query_type": ["AAAA"], "action": "reject"})


def is_lan_aaaa_reject_rule(rule):
    return isinstance(rule, dict) and rule.get("query_type") == ["AAAA"] and rule.get("action") == "reject" and "inbound" in rule


def apply_lan_probe_dns_reject(config):
    dns_rules = config.setdefault("dns", {}).setdefault("rules", [])
    dns_inbounds = dns_inbound_tags(config)
    dns_rules[:] = [rule for rule in dns_rules if not is_lan_probe_reject_rule(rule)]
    # 局域网 AD/mDNS/单标签探测必须在 fakeip 兜底之前拒绝，否则 A 查询会先拿到 fakeip 假 IP
    # 而不是快速 NXDOMAIN，导致 Windows/Apple 客户端把探测名送进代理链路刷 timeout。
    # 插在 fakeip 兜底规则（无 rule_set 的 LAN 入站兜底）之前。
    insert_at = len(dns_rules)
    for index, rule in enumerate(dns_rules):
        if (
            isinstance(rule, dict)
            and same_inbound(rule.get("inbound"), dns_inbounds)
            and "rule_set" not in rule
            and rule.get("action") == "route"
            and rule.get("server") == "fakeip-dns"
        ):
            insert_at = index
            break
    dns_rules.insert(
        insert_at,
        {
            "inbound": dns_inbounds,
            "domain_suffix": ["local"],
            "domain_regex": [r"^[^.]+$", r"^_(ldap|gc)\._tcp\..+"],
            "action": "reject",
        },
    )


def is_lan_probe_reject_rule(rule):
    return (
        isinstance(rule, dict)
        and rule.get("action") == "reject"
        and "inbound" in rule
        and rule.get("domain_regex") == [r"^[^.]+$", r"^_(ldap|gc)\._tcp\..+"]
    )


def dns_inbound_tags(config):
    tags = []
    for inbound in config.get("inbounds", []) or []:
        if isinstance(inbound, dict) and inbound.get("tag") in ("dns-in", "dns-in-v6"):
            tags.append(inbound["tag"])
    return tags or ["dns-in"]


def same_inbound(value, tags):
    # 规则里的 inbound 写成 ["dns-in"] 或 ["dns-in","dns-in-v6"] 都算同一条 LAN 入站规则；
    # 严格要求集合相等会让 base.json 里只写 dns-in 的旧规则在 dns_inbound_tags 含 dns-in-v6 时
    # 既删不掉也算不进 insert_at，导致 fakeip 兜底被插到索引 0、把所有 rule_set 规则压在后面。
    expected = set(tags)
    if isinstance(value, list):
        return bool(value) and set(value) <= expected
    return value in expected


def apply_ddns_dns_settings(config, groups):
    mode = groups.get("ddns", {}).get("dns", "local")
    server = "ddns-remote-dns" if mode == "remote" else "local-dns"
    dns_rules = config.setdefault("dns", {}).setdefault("rules", [])
    for rule in dns_rules:
        if isinstance(rule, dict) and rule.get("rule_set") == CUSTOM_TAGS["ddns"]:
            rule["action"] = "route"
            rule["server"] = server
            rule["rewrite_ttl"] = 60


def collect_outbound_references(value, refs=None):
    if refs is None:
        refs = set()
    if isinstance(value, dict):
        for key, item in value.items():
            if key in {"outbound", "detour", "final", "default"} and isinstance(item, str):
                refs.add(item)
            else:
                collect_outbound_references(item, refs)
    elif isinstance(value, list):
        for item in value:
            collect_outbound_references(item, refs)
    return refs


def validate_outbound_references(config):
    defined = {item.get("tag") for item in config.get("outbounds", []) if isinstance(item, dict)}
    refs = collect_outbound_references({"dns": config.get("dns", {}), "route": config.get("route", {})})
    ignored = {None, "remote-dns", "local-dns", "fakeip-dns"}
    missing = sorted(ref for ref in refs if ref not in defined and ref not in ignored)
    if missing:
        raise ValueError("Missing outbound referenced by config: " + ", ".join(missing))


def read_entries(name):
    path = rule_path(name)
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    entries = []
    for rule in data.get("rules", []):
        for kind in ENTRY_TYPES:
            for value in rule.get(kind, []) or []:
                entries.append({"type": kind, "value": value})
    return normalize_entries(entries)


def write_entries(name, entries):
    normalized = entries if all(isinstance(item, dict) and "type" in item and "value" in item for item in entries) else normalize_entries(entries)
    path = rule_path(name)
    backup = backup_file(path)
    write_json(path, entries_to_rule_set(normalized))
    return {"name": name, "count": len(normalized), "backup": backup}


def run_command(args, timeout=20):
    proc = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
    return {
        "code": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
    }


def rc_service_args(name, action):
    # systemd 版：把 OpenRC 的 (name, action) 语义映射到 systemctl <action> <unit>。
    return ["systemctl", action, name]


def service_status():
    return unit_status("sing-box")


def unit_status(unit):
    # systemd 版：直接用 is-active 判定，输出 active/inactive/failed/activating 等单词，语义比解析 status 文本稳。
    result = run_command(["systemctl", "is-active", unit], timeout=8)
    state = (result["stdout"] or result["stderr"]).strip().lower()
    if state == "active":
        return "active"
    if state in ("inactive", "failed", "unknown", "deactivating") or result["code"] != 0:
        return "inactive"
    return state or "unknown"


def service_pid(unit):
    pid_file = Path(f"/run/{unit}.pid")
    try:
        pid = int(pid_file.read_text(encoding="utf-8").strip())
        if pid > 0 and Path(f"/proc/{pid}").exists():
            return pid
    except Exception:
        pass
    pgrep = run_command(["pgrep", "-f", "/usr/local/bin/sing-box run -c /etc/sing-box/config.json"], timeout=8)
    for raw in pgrep["stdout"].splitlines():
        try:
            pid = int(raw.strip())
        except ValueError:
            continue
        if pid > 0:
            return pid
    return 0


def sing_box_memory():
    pid = service_pid("sing-box")
    if pid <= 0:
        return {"rssBytes": None, "rss": "unknown"}
    status_path = Path(f"/proc/{pid}/status")
    try:
        for line in status_path.read_text(encoding="utf-8").splitlines():
            if line.startswith("VmRSS:"):
                parts = line.split()
                kb = int(parts[1])
                mib = kb / 1024
                return {"pid": pid, "rssBytes": kb * 1024, "rss": f"{mib:.1f} MiB"}
    except Exception:
        pass
    return {"pid": pid, "rssBytes": None, "rss": "unknown"}


def sing_box_version():
    result = run_command(["/usr/local/bin/sing-box", "version"], timeout=8)
    first_line = (result["stdout"] or result["stderr"]).splitlines()[0:1]
    if not first_line:
        return "unknown"
    match = re.search(r"sing-box version\s+(\S+)", first_line[0])
    return match.group(1) if match else first_line[0].strip()


def check_config(config_path=CONFIG_PATH):
    return run_command(["/usr/local/bin/sing-box", "check", "-c", str(config_path)], timeout=20)


def reset_sing_box_failed():
    # systemd 有 failed/start-limit 状态；重启前清除，避免 start-limit-hit 挡住回滚后的再次拉起。
    return run_command(["systemctl", "reset-failed", "sing-box"], timeout=8)


def wait_for_unit_active(unit, timeout=15):
    deadline = time.time() + timeout
    last_status = "unknown"
    while time.time() < deadline:
        last_status = unit_status(unit)
        if last_status == "active":
            return {"active": True, "service": last_status}
        time.sleep(0.5)
    return {"active": False, "service": last_status}


def restart_sing_box():
    reset = reset_sing_box_failed()
    restart = run_command(rc_service_args("sing-box", "restart"), timeout=20)
    wait = wait_for_unit_active("sing-box")
    code = 0 if restart["code"] == 0 and wait["active"] else 1
    return {
        "code": code,
        "stdout": restart["stdout"],
        "stderr": restart["stderr"],
        "resetFailed": reset,
        "service": wait["service"],
    }


def restart_tproxy():
    restart = run_command(rc_service_args(TPROXY_SERVICE, "restart"), timeout=20)
    status = unit_status(TPROXY_SERVICE)
    code = 0 if restart["code"] == 0 and status == "active" else 1
    return {"code": code, "stdout": restart["stdout"], "stderr": restart["stderr"], "service": status}


def restart_rule_ui_later(delay=1.0):
    def target():
        time.sleep(delay)
        subprocess.run(rc_service_args(RULE_UI_SERVICE, "restart"), capture_output=True, text=True, timeout=20)

    threading.Thread(target=target, daemon=True).start()


def apply_import_runtime_later(nodes, groups, normalized_lists, saved_result, delay=0.3):
    def target():
        time.sleep(delay)
        try:
            # 导入接口必须先把 HTTP 响应发回浏览器；运行态重启放后台，避免 fetch 被 OpenRC 重启链路打断。
            restart = restart_sing_box()
            if restart["code"] != 0 or service_status() != "active":
                # 后台应用失败时仍保留导入前的回滚语义，避免留下无法启动的新配置。
                rollback_apply(saved_result)
                restart_sing_box()
                print(f"backup import runtime apply rolled back after restart failure: {restart}")
                return
            sync_tproxy(nodes=nodes, groups=groups, normalized_lists=normalized_lists)
            current_proxy_payload_after_probe(test_delays=True)
        except Exception as exc:
            print(f"backup import runtime apply failed: {exc}")

    threading.Thread(target=target, daemon=True).start()


def read_crontab_text():
    try:
        return ROOT_CRONTAB.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def cron_block_lines(begin, end):
    lines = []
    inside = False
    for line in read_crontab_text().splitlines():
        if line == begin:
            inside = True
            continue
        if line == end:
            inside = False
            continue
        if inside:
            lines.append(line)
    return lines


def parse_rule_update_schedule():
    cron_line = next((line.strip() for line in cron_block_lines(RULE_UPDATE_CRON_BEGIN, RULE_UPDATE_CRON_END) if line.strip() and not line.strip().startswith("#")), "")
    match = re.match(r"^(\d{1,2})\s+(\d{1,2})\s+\*\s+\*\s+(\*|[0-7])\s+", cron_line)
    delay_match = re.search(r"\bdelay=(\d{1,4})\b", cron_line)
    minute = int(match.group(1)) if match else 20
    hour = int(match.group(2)) if match else 4
    day_of_week = match.group(3) if match else "0"
    frequency = "daily" if match and day_of_week == "*" else "weekly"
    randomized_delay_minutes = int(delay_match.group(1)) if delay_match else 0
    return {
        "frequency": frequency,
        "hour": hour,
        "minute": minute,
        "dayOfWeek": day_of_week,
        "randomizedDelayMinutes": randomized_delay_minutes,
        "persistent": False,
        "nextBase": "",
        "dropin": str(ROOT_CRONTAB),
        "customized": bool(cron_line),
    }


def next_rule_update_time(schedule):
    if not schedule.get("customized"):
        return ""
    now = time.time()
    current = time.localtime(now)
    hour = int(schedule.get("hour", 4))
    minute = int(schedule.get("minute", 20))
    if schedule.get("frequency") == "daily":
        candidate = time.mktime((current.tm_year, current.tm_mon, current.tm_mday, hour, minute, 0, current.tm_wday, current.tm_yday, current.tm_isdst))
        if candidate <= now:
            candidate += 24 * 60 * 60
    else:
        # cron 的 0/7 是周日；Python tm_wday 里周一是 0、周日是 6。手动更新后会把 dayOfWeek 改成当日，实现从本次更新时间顺延一周。
        cron_dow = str(schedule.get("dayOfWeek", "0"))
        target_dow = 6 if cron_dow in {"0", "7"} else max(0, min(6, int(cron_dow) - 1))
        days_until_target = (target_dow - current.tm_wday) % 7
        candidate = time.mktime((current.tm_year, current.tm_mon, current.tm_mday, hour, minute, 0, current.tm_wday, current.tm_yday, current.tm_isdst))
        candidate += days_until_target * 24 * 60 * 60
        if candidate <= now:
            candidate += 7 * 24 * 60 * 60
    return time.strftime("%Y-%m-%d %H:%M", time.localtime(candidate))


def normalize_rule_update_schedule(payload):
    try:
        frequency = str(payload.get("frequency", "weekly")).strip()
        hour = int(payload.get("hour"))
        minute = int(payload.get("minute"))
        if "randomizedDelayMinutes" in payload:
            randomized_delay_minutes = int(payload.get("randomizedDelayMinutes", 0))
        else:
            # 旧 UI 曾用小时做单位；保存旧 payload 时转换成分钟，避免含义悄悄变化。
            randomized_delay_minutes = int(payload.get("randomizedDelayHours", 0)) * 60
    except (TypeError, ValueError):
        raise ValueError("自动更新时间必须是有效数字")
    if frequency not in {"daily", "weekly"}:
        raise ValueError("自动更新周期只能选择每天或每周")
    if not 0 <= hour <= 23:
        raise ValueError("自动更新时间小时必须在 0 到 23 之间")
    if not 0 <= minute <= 59:
        raise ValueError("自动更新时间分钟必须在 0 到 59 之间")
    if not 0 <= randomized_delay_minutes <= 180:
        raise ValueError("随机延迟分钟必须在 0 到 180 之间")
    return {"frequency": frequency, "hour": hour, "minute": minute, "randomizedDelayMinutes": randomized_delay_minutes}


def write_rule_update_schedule(payload):
    schedule = normalize_rule_update_schedule(payload)
    requested_dow = str(payload.get("dayOfWeek", "0"))
    dow = requested_dow if schedule["frequency"] == "weekly" and requested_dow in {"0", "1", "2", "3", "4", "5", "6", "7"} else "*"
    delay = int(schedule.get("randomizedDelayMinutes", 0))
    random_sleep = f"delay={delay}; [ \"$delay\" -gt 0 ] && sleep $(awk -v max=\"$delay\" 'BEGIN{{srand(); print int(rand()*(max*60+1))}}'); "
    # /etc/cron.d 片段的执行行比用户 crontab 多一个用户字段（第 6 列），命令在其后。
    cron_line = (
        f"{schedule['minute']} {schedule['hour']} * * {dow} {CRON_USER} "
        f"{random_sleep}/usr/local/sbin/update-sing-box-rules-jsdelivr >> /var/log/sing-box-gateway/rule-update.log 2>&1"
    )
    text = read_crontab_text().splitlines()
    output = []
    skipping = False
    for line in text:
        if line == RULE_UPDATE_CRON_BEGIN:
            skipping = True
            continue
        if line == RULE_UPDATE_CRON_END:
            skipping = False
            continue
        if not skipping:
            output.append(line)
    # cron.d 片段需要 PATH，且首次写入时补 SHELL/PATH 头，保证 awk/sleep 可用。
    if not any(line.startswith("PATH=") for line in output):
        output = ["SHELL=/bin/bash", "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"] + output
    output.extend([RULE_UPDATE_CRON_BEGIN, "# UI 只调整规则自动更新的 cron 触发时间；执行脚本保持仓库内受控路径。", cron_line, RULE_UPDATE_CRON_END])
    ROOT_CRONTAB.parent.mkdir(parents=True, exist_ok=True)
    ROOT_CRONTAB.write_text("\n".join(output).rstrip() + "\n", encoding="utf-8")
    ROOT_CRONTAB.chmod(0o644)
    # Debian/Ubuntu 的 cron 每分钟扫描 /etc/cron.d，无需重启即可生效；仍触发一次 reload 确保立即读入，失败不影响调度。
    restart = run_command(["systemctl", "reload-or-restart", "cron"], timeout=20)
    return {"ok": True, "schedule": schedule, "daemonReload": {"code": 0, "stdout": "", "stderr": ""}, "restart": restart}


def reschedule_rule_update_cron_after_manual_success():
    schedule = parse_rule_update_schedule()
    now = time.localtime()
    payload = {
        "frequency": schedule.get("frequency", "weekly"),
        "hour": now.tm_hour,
        "minute": now.tm_min,
        # cron 周日是 0，周一到周六是 1-6；手动成功后把 weekly 基准改成今天，等价于从本次更新顺延一个周期。
        "dayOfWeek": "0" if now.tm_wday == 6 else str(now.tm_wday + 1),
        "randomizedDelayMinutes": schedule.get("randomizedDelayMinutes", 0),
    }
    if payload["frequency"] == "daily":
        payload["dayOfWeek"] = "*"
    return write_rule_update_schedule(payload)


def default_lan_ip():
    result = run_command(["ip", "-o", "-4", "route", "get", "1.1.1.1"], timeout=8)
    parts = result["stdout"].split()
    if "src" in parts:
        return parts[parts.index("src") + 1]
    return ""


def recent_unit_logs(unit, lines=80):
    log_path = Path("/var/log/sing-box-gateway/rule-update.log")
    try:
        text = "\n".join(log_path.read_text(encoding="utf-8", errors="replace").splitlines()[-lines:])
    except FileNotFoundError:
        text = ""
    parts = re.split(r"(?=^.*sing-box rule)", text, flags=re.MULTILINE)
    return parts[-1] if parts else text


def rule_update_summary(text):
    summary = {"updated": [], "kept": [], "skipped": [], "errors": [], "final": "", "status": "", "requiredOk": False}
    for raw in (text or "").splitlines():
        line = raw.strip()
        message = re.sub(r"^.*update-sing-box-rules-jsdelivr\[\d+\]:\s*", "", line)
        if "downloaded " in message:
            summary["updated"].append(message)
        elif "installed " in message and message not in summary["updated"]:
            summary["updated"].append(message)
            if (
                "geoip/cn.srs" in message
                or "geosite/cn.srs" in message
                or "geosite/geolocation-cn.srs" in message
                or "geosite/speedtest.srs" in message
            ):
                summary["requiredOk"] = True
        elif "keeping existing file" in message:
            summary["kept"].append(message)
        elif "update skipped" in message:
            summary["skipped"].append(message)
        elif message.startswith("ERROR:"):
            summary["errors"].append(message)
        elif "timed out" in message:
            summary["errors"].append(message)
        elif "skipped this update safely" in message:
            summary["final"] = "skipped_safe"
            summary["status"] = "skipped_safe"
            summary["requiredOk"] = True
        elif "service restart skipped" in message and "config checked" in message:
            summary["final"] = "checked"
            summary["status"] = summary["status"] or "checked"
            summary["requiredOk"] = True
        elif "sing-box rule sets updated" in message:
            summary["final"] = "updated"
            summary["status"] = "updated"
    for key in ("updated", "kept", "skipped", "errors"):
        seen = []
        for item in summary[key]:
            if item not in seen:
                seen.append(item)
        summary[key] = seen[-30:]
    return summary


def first_default_interface():
    result = run_command(["ip", "-o", "route", "show", "default"], timeout=8)
    match = re.search(r"\bdev\s+(\S+)", result["stdout"])
    return match.group(1) if match else ""


def current_ipv6_prefixes(interface):
    if not interface:
        return []
    result = run_command(["ip", "-o", "-6", "addr", "show", "dev", interface, "scope", "global"], timeout=8)
    prefixes = []
    for line in result["stdout"].splitlines():
        match = re.search(r"\binet6\s+([0-9a-fA-F:]+/\d+)", line)
        if not match:
            continue
        try:
            network = ipaddress.ip_network(match.group(1), strict=False)
        except ValueError:
            continue
        item = str(network)
        if item not in prefixes:
            prefixes.append(item)
    return prefixes


def global_ipv6_prefixes(interface):
    values = []
    for item in current_ipv6_prefixes(interface):
        try:
            network = ipaddress.ip_network(item, strict=False)
        except ValueError:
            continue
        if not network.is_private and not network.is_link_local and not network.is_multicast:
            values.append(str(network))
    return values


def current_ipv4_prefixes(interface):
    if not interface:
        return []
    result = run_command(["ip", "-o", "-4", "addr", "show", "dev", interface], timeout=8)
    prefixes = []
    for line in result["stdout"].splitlines():
        match = re.search(r"\binet\s+(\d+(?:\.\d+){3}/\d+)", line)
        if not match:
            continue
        try:
            network = ipaddress.ip_network(match.group(1), strict=False)
        except ValueError:
            continue
        item = str(network)
        if item not in prefixes:
            prefixes.append(item)
    return prefixes


def script_ipv6_prefixes(path):
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8", errors="replace")
    values = []
    for raw in re.findall(r"\b[0-9a-fA-F:]+/[0-9]{1,3}\b", text):
        try:
            network = ipaddress.ip_network(raw, strict=False)
        except ValueError:
            continue
        if network.version == 6:
            item = str(network)
            if item not in values:
                values.append(item)
    return values


def ipv6_prefixes_covered(current, script_prefixes):
    # 判断当前网卡 IPv6 前缀是否全部被脚本覆盖。必须是网段包含语义而非字符串相等：
    # 脚本静态写死 fc00::/7（ULA 超网），而网卡上的 ULA（如 fd88::/64）是它的子网，
    # 字符串比较会误报「前缀不匹配」（Alpine 生产机 2026-08-30 实测误报）。
    # 反过来，网卡出现脚本未覆盖的新公网前缀（PPPoE 重新分配等）仍必须告警，
    # 否则旁路网关会漏掉该前缀的流量。
    covered = []
    for raw in script_prefixes:
        try:
            covered.append(ipaddress.ip_network(raw, strict=False))
        except ValueError:
            continue
    for raw in current:
        try:
            network = ipaddress.ip_network(raw, strict=False)
        except ValueError:
            return False
        if not any(network.version == item.version and network.subnet_of(item) for item in covered):
            return False
    return True


def outbound_server_ips():
    return [item["address"] for item in resolved_outbound_servers() if item.get("address")]


def outbound_sources(nodes=None):
    if nodes is not None:
        return [node.get("outbound", {}) for node in nodes if node.get("enabled", True)]
    config = load_json(CONFIG_PATH, {})
    return [
        outbound
        for outbound in config.get("outbounds", []) or []
        if isinstance(outbound, dict) and outbound.get("server")
    ]


def resolve_server_addresses(server):
    host = str(server or "").strip()
    if not host:
        return [], "empty server"
    try:
        return [str(ipaddress.ip_address(host))], ""
    except ValueError:
        pass
    addresses, error = resolve_via_public_dns(host)
    if addresses:
        return addresses, ""
    addresses, system_error = resolve_via_system_dns(host)
    if addresses:
        return addresses, ""
    return [], error or system_error or "public DNS returned no address"


def dns_query_name(host):
    encoded = bytearray()
    for label in host.rstrip(".").split("."):
        raw = label.encode("idna")
        if not raw or len(raw) > 63:
            raise ValueError("invalid DNS label")
        encoded.append(len(raw))
        encoded.extend(raw)
    encoded.append(0)
    return bytes(encoded)


def read_dns_name(packet, offset, depth=0):
    if depth > 8:
        raise ValueError("too many DNS compression pointers")
    labels = []
    jumped = False
    end = offset
    while True:
        length = packet[offset]
        if length & 0xC0 == 0xC0:
            pointer = ((length & 0x3F) << 8) | packet[offset + 1]
            labels.extend(read_dns_name(packet, pointer, depth + 1)[0])
            offset += 2
            if not jumped:
                end = offset
            break
        if length == 0:
            offset += 1
            if not jumped:
                end = offset
            break
        offset += 1
        labels.append(packet[offset : offset + length].decode("ascii", errors="replace"))
        offset += length
    return labels, end


def parse_dns_addresses(packet, query_count, answer_count):
    offset = 12
    addresses = []
    for _ in range(query_count):
        _, offset = read_dns_name(packet, offset)
        offset += 4
    for _ in range(answer_count):
        _, offset = read_dns_name(packet, offset)
        rtype = int.from_bytes(packet[offset : offset + 2], "big")
        rclass = int.from_bytes(packet[offset + 2 : offset + 4], "big")
        rdlength = int.from_bytes(packet[offset + 8 : offset + 10], "big")
        offset += 10
        rdata = packet[offset : offset + rdlength]
        offset += rdlength
        if rclass != 1:
            continue
        if rtype == 1 and rdlength == 4:
            addresses.append(str(ipaddress.IPv4Address(rdata)))
        elif rtype == 28 and rdlength == 16:
            addresses.append(str(ipaddress.IPv6Address(rdata)))
    return addresses


def sing_box_dns_endpoint():
    config = load_json(CONFIG_PATH, {})
    for inbound in config.get("inbounds", []) or []:
        if not isinstance(inbound, dict):
            continue
        if inbound.get("tag") == "dns-in" or (inbound.get("type") == "direct" and inbound.get("listen_port") == 53):
            listen = str(inbound.get("listen") or "127.0.0.1")
            port = int(inbound.get("listen_port") or 53)
            return listen, port
    return "127.0.0.1", 53


def query_dns_once(server, port, host, qtype, timeout=4):
    txid = secrets.randbits(16)
    question = dns_query_name(host) + qtype.to_bytes(2, "big") + (1).to_bytes(2, "big")
    packet = (
        txid.to_bytes(2, "big")
        + b"\x01\x00"
        + (1).to_bytes(2, "big")
        + (0).to_bytes(2, "big")
        + (0).to_bytes(2, "big")
        + (0).to_bytes(2, "big")
        + question
    )
    family = socket.AF_INET6 if ":" in server else socket.AF_INET
    with socket.socket(family, socket.SOCK_DGRAM) as sock:
        sock.settimeout(timeout)
        sock.sendto(packet, (server, port))
        response, _ = sock.recvfrom(4096)
    if len(response) < 12 or int.from_bytes(response[:2], "big") != txid:
        raise OSError("invalid DNS response")
    flags = int.from_bytes(response[2:4], "big")
    rcode = flags & 0x0F
    if rcode != 0:
        raise OSError(f"DNS rcode {rcode}")
    qdcount = int.from_bytes(response[4:6], "big")
    ancount = int.from_bytes(response[6:8], "big")
    return parse_dns_addresses(response, qdcount, ancount)


def resolve_via_sing_box_dns(host):
    server, port = sing_box_dns_endpoint()
    addresses = []
    errors = []
    for qtype in (1, 28):
        try:
            for address in query_dns_once(server, port, host, qtype):
                if address not in addresses:
                    addresses.append(address)
        except OSError as exc:
            errors.append(str(exc))
    if addresses:
        return addresses, ""
    return [], f"sing-box DNS {server}:{port} failed: {'; '.join(errors) or 'no records'}"


def resolve_via_public_dns(host):
    addresses = []
    errors = []
    for server in ("223.5.5.5", "1.1.1.1", "8.8.8.8"):
        for qtype in (1, 28):
            try:
                for address in query_dns_once(server, 53, host, qtype):
                    if address not in addresses:
                        addresses.append(address)
            except OSError as exc:
                errors.append(f"{server}: {exc}")
        if addresses:
            break
    return addresses, "; ".join(errors)


def resolve_via_system_dns(host):
    try:
        records = socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)
    except OSError as exc:
        return [], str(exc)
    addresses = []
    for record in records:
        address = record[4][0]
        if address not in addresses:
            addresses.append(address)
    return addresses, ""


def filter_fakeip_addresses(addresses, groups=None):
    fakeip = (groups or load_groups()).get("fakeip", {})
    ranges = []
    for value, fallback in ((fakeip.get("inet4_range"), "28.0.0.0/8"), (fakeip.get("inet6_range"), "2001:2::/64")):
        try:
            ranges.append(ipaddress.ip_network(value or fallback, strict=False))
        except ValueError:
            ranges.append(ipaddress.ip_network(fallback, strict=False))
    filtered = []
    for address in addresses:
        try:
            parsed = ipaddress.ip_address(str(address))
        except ValueError:
            continue
        if any(parsed in network for network in ranges):
            continue
        if str(parsed) not in filtered:
            filtered.append(str(parsed))
    return filtered


def resolved_outbound_servers(nodes=None, groups=None):
    resolved = []
    seen = set()
    groups = groups or load_groups()
    for outbound in outbound_sources(nodes):
        tag = outbound.get("tag") or ""
        server = outbound.get("server")
        addresses, error = resolve_server_addresses(server)
        addresses = filter_fakeip_addresses(addresses, groups)
        if not addresses:
            key = (tag, server, "")
            if key not in seen:
                resolved.append({"tag": tag, "server": server, "address": "", "error": error or "unresolved"})
                seen.add(key)
            continue
        for address in addresses:
            key = (tag, server, address)
            if key in seen:
                continue
            resolved.append({"tag": tag, "server": server, "address": address, "error": ""})
            seen.add(key)
    return resolved


def outbound_server_ip_networks(nodes=None):
    networks = []
    for item in resolved_outbound_servers(nodes):
        address = item.get("address")
        if not address:
            continue
        try:
            parsed = ipaddress.ip_address(str(address))
        except ValueError:
            continue
        network = f"{parsed}/32" if parsed.version == 4 else f"{parsed}/128"
        if network not in networks:
            networks.append(network)
    return networks


def protected_tproxy_networks(nodes=None, groups=None):
    iface = first_default_interface()
    protected = [
        "0.0.0.0/8",
        "10.0.0.0/8",
        "100.64.0.0/10",
        "127.0.0.0/8",
        "169.254.0.0/16",
        "172.16.0.0/12",
        "192.168.0.0/16",
        "224.0.0.0/4",
        "240.0.0.0/4",
        "::/128",
        "::1/128",
        "fc00::/7",
        "fe80::/10",
        "ff00::/8",
    ]
    protected.extend(current_ipv4_prefixes(iface))
    protected.extend(current_ipv6_prefixes(iface))
    # 节点服务器地址绝不能被灰名单 IP 捕获，否则连接代理节点本身会被再次送进 TProxy 形成回环。
    protected.extend(outbound_server_ip_networks(nodes))
    networks = []
    for item in protected:
        try:
            networks.append(ipaddress.ip_network(item, strict=False))
        except ValueError:
            continue
    return networks


def tproxy_proxy_ip_networks(nodes=None, groups=None, normalized_lists=None):
    protected = protected_tproxy_networks(nodes=nodes, groups=groups)
    networks = []
    entries = (normalized_lists or {}).get("greylist") if normalized_lists is not None else read_entries("greylist")
    for entry in entries or []:
        if entry.get("type") != "ip_cidr":
            continue
        try:
            network = ipaddress.ip_network(entry["value"], strict=False)
        except ValueError:
            continue
        # 灰名单 IP/CIDR 只用于捕获明确外部目标；内网、本机前缀和节点服务器 IP 必须自动排除，避免误代理和回环。
        if any(network.version == item.version and (network.subnet_of(item) or network.overlaps(item)) for item in protected):
            continue
        networks.append(network)
    # 灰名单允许 IPv4 和 IPv6 同时存在；ipaddress 不能直接折叠混合版本网段，必须先按版本分组。
    collapsed = []
    for version in (4, 6):
        version_networks = [network for network in networks if network.version == version]
        collapsed.extend(ipaddress.collapse_addresses(version_networks))
    collapsed = sorted(collapsed, key=lambda net: (net.version, int(net.network_address), net.prefixlen))
    return [str(net) for net in collapsed]


def collapse_network_strings(items):
    networks = []
    for item in items:
        try:
            networks.append(ipaddress.ip_network(item, strict=False))
        except ValueError:
            continue
    # nft set 分别使用 IPv4/IPv6，但调用方有时会传入混合列表；这里统一按版本折叠，避免跨版本比较异常。
    collapsed = []
    for version in (4, 6):
        version_networks = [network for network in networks if network.version == version]
        collapsed.extend(ipaddress.collapse_addresses(version_networks))
    collapsed = sorted(collapsed, key=lambda net: (net.version, int(net.network_address), net.prefixlen))
    return [str(net) for net in collapsed]


def tproxy_bypass_sets(nodes=None, groups=None, normalized_lists=None):
    iface = first_default_interface()
    groups = groups or load_groups()
    fakeip = groups.get("fakeip", {})
    fakeip4 = normalize_cidr(fakeip.get("inet4_range", "28.0.0.0/8"), "28.0.0.0/8")
    fakeip6 = normalize_cidr(fakeip.get("inet6_range", "2001:2::/64"), "2001:2::/64")
    protected = [str(item) for item in protected_tproxy_networks(nodes=nodes, groups=groups)]
    bypass4 = [item for item in protected if ":" not in item]
    bypass6 = [item for item in protected if ":" in item]
    node_networks = outbound_server_ip_networks(nodes)
    proxy_networks = tproxy_proxy_ip_networks(nodes=nodes, groups=groups, normalized_lists=normalized_lists)
    telegram_capture = normalize_bool(groups.get("telegram", {}).get("capture_ips", True))
    telegram_cidr = load_telegram_cidr_data()
    # Telegram 客户端常直接连接官方 IP；列表从 manager 文件读取，缺失时才使用内置兜底，避免官方变动后长期写死。
    telegram4 = list(telegram_cidr["ipv4"]) if telegram_capture else []
    telegram6 = list(telegram_cidr["ipv6"]) if telegram_capture else []
    return {
        "interface": iface,
        "bypass4": collapse_network_strings(bypass4),
        "bypass6": collapse_network_strings(bypass6),
        "fakeip4": fakeip4,
        "fakeip6": fakeip6,
        "proxy4": collapse_network_strings([*telegram4, *[item for item in proxy_networks if ":" not in item]]),
        "proxy6": collapse_network_strings([*telegram6, *[item for item in proxy_networks if ":" in item]]),
        "telegramCaptureIps": telegram_capture,
        "telegramProxy4": collapse_network_strings(telegram4),
        "telegramProxy6": collapse_network_strings(telegram6),
        "telegramCidr": telegram_cidr,
        "nodeServerIpNetworks": node_networks,
        "nodeServers": resolved_outbound_servers(nodes, groups),
    }


def format_nft_elements(items, indent="      "):
    return ",\n".join(f"{indent}{item}" for item in items)


def render_nft_set(name, nft_type, elements):
    if elements:
        formatted = format_nft_elements(elements)
        return f"""  set {name} {{
    type {nft_type}
    flags interval
    elements = {{
{formatted}
    }}
  }}"""
    # nft 不接受空的 elements 块；没有灰名单 IPv6 或 IPv4 时只声明空 set，后续规则仍可安全引用。
    return f"""  set {name} {{
    type {nft_type}
    flags interval
  }}"""


def render_tproxy_script(nodes=None, groups=None, normalized_lists=None):
    sets = tproxy_bypass_sets(nodes=nodes, groups=groups, normalized_lists=normalized_lists)
    iface = sets["interface"]
    if not iface:
        raise ValueError("Cannot detect default network interface")
    bypass4_set = render_nft_set("bypass4", "ipv4_addr", sets["bypass4"])
    bypass6_set = render_nft_set("bypass6", "ipv6_addr", sets["bypass6"])
    proxy4_set = render_nft_set("proxy4", "ipv4_addr", sets["proxy4"])
    proxy6_set = render_nft_set("proxy6", "ipv6_addr", sets["proxy6"])
    return f"""#!/usr/bin/env bash
set -euo pipefail

# Generated by Sing-box UI. LAN DNS port 53 is redirected to sing-box DNS.
# TProxy only captures FakeIP, explicit greylist IP/CIDR, and enabled Telegram service IP targets; proxy node servers stay on the normal route.

IFACE={json.dumps(iface)}
TPROXY_PORT={TPROXY_PORT}
TPROXY_MARK={TPROXY_MARK}
TPROXY_TABLE={TPROXY_TABLE}

# 运行态只设置 TProxy/FakeIP 必需项；TCP 队列、缓冲和其它性能参数交给 PVE/LXC 管理员手动统一配置。
sysctl -w net.ipv4.ip_nonlocal_bind=1 >/dev/null 2>&1 || true
case "${{SING_BOX_GATEWAY_ENABLE_FORWARDING:-${{RULE_UI_ENABLE_FORWARDING:-0}}}}" in
  1|true|TRUE|yes|YES|on|ON)
  # 只有 LXC 真的承担三层网关时才打开转发；FakeIP 入口模式不应把旁路机升级成默认网关角色。
  sysctl -w net.ipv4.ip_forward=1 >/dev/null
  sysctl -w net.ipv6.conf.all.forwarding=1 >/dev/null
  sysctl -w net.ipv6.conf.default.forwarding=1 >/dev/null
  sysctl -w "net.ipv6.conf.${{IFACE}}.forwarding=1" >/dev/null 2>&1 || true
  ;;
esac
sysctl -w net.ipv4.conf.all.rp_filter=0 >/dev/null
sysctl -w net.ipv4.conf.default.rp_filter=0 >/dev/null
sysctl -w "net.ipv4.conf.${{IFACE}}.rp_filter=0" >/dev/null 2>&1 || true
sysctl -w "net.ipv6.conf.${{IFACE}}.accept_ra=2" >/dev/null 2>&1 || true
sysctl -w "net.ipv6.conf.${{IFACE}}.accept_ra_defrtr=1" >/dev/null 2>&1 || true

# IPv4/IPv6 FakeIP 都必须把 TProxy 标记包送回本机 lo；缺少 IPv6 表会让浏览器拿到 AAAA FakeIP 后仍无法进入 sing-box。
ip rule add fwmark "${{TPROXY_MARK}}" table "${{TPROXY_TABLE}}" priority 100 2>/dev/null || true
ip -6 rule add fwmark "${{TPROXY_MARK}}" table "${{TPROXY_TABLE}}" priority 100 2>/dev/null || true
ip route replace local 0.0.0.0/0 dev lo table "${{TPROXY_TABLE}}"
ip -6 route replace local ::/0 dev lo table "${{TPROXY_TABLE}}"

nft delete table inet singbox_tproxy 2>/dev/null || true
nft -f - <<NFT
add table inet singbox_tproxy

table inet singbox_tproxy {{
{bypass4_set}

{bypass6_set}

{proxy4_set}

{proxy6_set}

  chain prerouting {{
    type filter hook prerouting priority mangle; policy accept;

    # 本机访问 FakeIP、灰名单 IP/CIDR 或启用的 Telegram 服务 IP 时先在 output 打标，回 lo 后只处理已标记目标。
    iifname "lo" ip daddr {sets["fakeip4"]} meta l4proto {{ tcp, udp }} meta mark "${{TPROXY_MARK}}" tproxy ip to :"${{TPROXY_PORT}}" accept
    iifname "lo" ip6 daddr {sets["fakeip6"]} meta l4proto {{ tcp, udp }} meta mark "${{TPROXY_MARK}}" tproxy ip6 to :"${{TPROXY_PORT}}" accept
    iifname "lo" ip daddr @proxy4 meta l4proto {{ tcp, udp }} meta mark "${{TPROXY_MARK}}" tproxy ip to :"${{TPROXY_PORT}}" accept
    iifname "lo" ip6 daddr @proxy6 meta l4proto {{ tcp, udp }} meta mark "${{TPROXY_MARK}}" tproxy ip6 to :"${{TPROXY_PORT}}" accept

    # LAN 客户端只接管 FakeIP、UI 灰名单 IP/CIDR 和启用的 Telegram 服务 IP；其它真实公网 IP 不进入 TProxy。
    iifname "${{IFACE}}" udp dport 53 return
    iifname "${{IFACE}}" tcp dport 53 return
    iifname "${{IFACE}}" ip daddr {sets["fakeip4"]} meta l4proto {{ tcp, udp }} meta mark set "${{TPROXY_MARK}}" tproxy ip to :"${{TPROXY_PORT}}" accept
    iifname "${{IFACE}}" ip6 daddr {sets["fakeip6"]} meta l4proto {{ tcp, udp }} meta mark set "${{TPROXY_MARK}}" tproxy ip6 to :"${{TPROXY_PORT}}" accept
    iifname "${{IFACE}}" ip daddr @proxy4 meta l4proto {{ tcp, udp }} meta mark set "${{TPROXY_MARK}}" tproxy ip to :"${{TPROXY_PORT}}" accept
    iifname "${{IFACE}}" ip6 daddr @proxy6 meta l4proto {{ tcp, udp }} meta mark set "${{TPROXY_MARK}}" tproxy ip6 to :"${{TPROXY_PORT}}" accept
    meta l4proto {{ tcp, udp }} return
  }}

  chain output {{
    type route hook output priority mangle; policy accept;

    # output 只给本机发往 FakeIP、UI 灰名单 IP/CIDR 和启用的 Telegram 服务 IP 打 mark，节点服务器 IP 保持系统原路由。
    ip daddr {sets["fakeip4"]} meta l4proto {{ tcp, udp }} meta mark set "${{TPROXY_MARK}}"
    ip6 daddr {sets["fakeip6"]} meta l4proto {{ tcp, udp }} meta mark set "${{TPROXY_MARK}}"
    ip daddr @proxy4 meta l4proto {{ tcp, udp }} meta mark set "${{TPROXY_MARK}}"
    ip6 daddr @proxy6 meta l4proto {{ tcp, udp }} meta mark set "${{TPROXY_MARK}}"
  }}

  chain dns_hijack {{
    type nat hook prerouting priority dstnat; policy accept;

    iifname != "${{IFACE}}" return
    udp dport 53 redirect to :53
    tcp dport 53 redirect to :53
  }}

  chain postrouting {{
    type nat hook postrouting priority srcnat; policy accept;

    oifname "${{IFACE}}" ip saddr 10.0.0.0/8 ip daddr != 10.0.0.0/8 ip daddr != 100.64.0.0/10 ip daddr != 127.0.0.0/8 ip daddr != 169.254.0.0/16 ip daddr != 172.16.0.0/12 ip daddr != 192.168.0.0/16 masquerade
  }}
}}
NFT
"""


def ipv6_dns_listeners():
    config = load_json(CONFIG_PATH, {})
    values = []
    for inbound in config.get("inbounds", []) or []:
        if not isinstance(inbound, dict) or inbound.get("listen_port") != 53:
            continue
        listen = str(inbound.get("listen") or "").strip()
        if not listen:
            continue
        try:
            address = ipaddress.ip_address(listen)
        except ValueError:
            continue
        if address.version == 6 and not address.is_link_local:
            text = str(address)
            if text not in values:
                values.append(text)
    return values


def render_radvd_conf(interface=None):
    iface = interface or first_default_interface()
    prefixes = global_ipv6_prefixes(iface)
    if not iface or not prefixes:
        return ""
    prefix_blocks = "\n".join(
        f"""    prefix {prefix} {{
        AdvOnLink on;
        AdvAutonomous on;
        AdvRouterAddr off;
    }};"""
        for prefix in prefixes
    )
    return f"""# Generated by Sing-box UI. Advertise this gateway as the preferred IPv6 router.
interface {iface} {{
    AdvSendAdvert on;
    MaxRtrAdvInterval 30;
    MinRtrAdvInterval 10;
    AdvDefaultPreference high;
    AdvManagedFlag off;
    AdvOtherConfigFlag on;
    AdvDefaultLifetime 1800;
{prefix_blocks}
}};
"""


def sync_radvd(interface):
    conf = render_radvd_conf(interface)
    if not conf:
        return {"code": 0, "skipped": True, "reason": "no global IPv6 prefix"}
    with tempfile.TemporaryDirectory(prefix="radvd-sync-") as temp_name:
        conf_path = Path(temp_name) / "radvd.conf"
        conf_path.write_text(conf, encoding="utf-8")
        check = run_command(["radvd", "-c", "-C", str(conf_path)], timeout=8)
        if check["code"] != 0:
            return {"code": 1, "stdout": check["stdout"], "stderr": check["stderr"]}
        if RADVD_CONF.exists():
            shutil.copy2(RADVD_CONF, RADVD_CONF.with_name(f"{RADVD_CONF.name}.bak.{now_stamp()}"))
        shutil.copy2(conf_path, RADVD_CONF)
    # 只有用户显式开启 RA 广播时才会走到这里；systemd 下 enable 开机自启并启动 radvd。
    enable = run_command(["systemctl", "enable", RADVD_SERVICE], timeout=20)
    if enable["code"] != 0:
        return {"code": 1, "stdout": enable["stdout"], "stderr": enable["stderr"]}
    restart = run_command(rc_service_args(RADVD_SERVICE, "restart"), timeout=20)
    status = unit_status(RADVD_SERVICE)
    code = 0 if restart["code"] == 0 and status == "active" else 1
    return {"code": code, "stdout": restart["stdout"], "stderr": restart["stderr"], "service": status}


def render_tproxy_sysctl(interface):
    values = [
        "# FakeIP 入口模式只保留透明代理必需参数；性能 sysctl 请在 PVE 和 LXC 两侧手动统一配置。",
        "net.ipv4.ip_nonlocal_bind=1",
        "net.ipv4.conf.all.rp_filter=0",
        "net.ipv4.conf.default.rp_filter=0",
        f"net.ipv4.conf.{interface}.rp_filter=0",
        f"net.ipv6.conf.{interface}.accept_ra=2",
        f"net.ipv6.conf.{interface}.accept_ra_defrtr=1",
    ]
    if ENABLE_GATEWAY_FORWARDING:
        values.extend(
            [
                "# 显式网关模式：客户端默认网关或路由指向本机时，才需要打开 IPv4/IPv6 转发。",
                "net.ipv4.ip_forward=1",
                "net.ipv6.conf.all.forwarding=1",
                "net.ipv6.conf.default.forwarding=1",
                f"net.ipv6.conf.{interface}.forwarding=1",
            ]
        )
    values.append("")
    return "\n".join(values)


def sync_tproxy(nodes=None, groups=None, normalized_lists=None):
    script = render_tproxy_script(nodes=nodes, groups=groups, normalized_lists=normalized_lists)
    sets = tproxy_bypass_sets(nodes=nodes, groups=groups, normalized_lists=normalized_lists)
    with tempfile.TemporaryDirectory(prefix="tproxy-sync-") as temp_name:
        temp_dir = Path(temp_name)
        script_path = temp_dir / "sing-box-tproxy-setup"
        sysctl_path = temp_dir / "99-sing-box-tproxy.conf"
        script_path.write_text(script, encoding="utf-8")
        script_path.chmod(0o755)
        sysctl_path.write_text(render_tproxy_sysctl(sets["interface"]), encoding="utf-8")
        check = run_command(["bash", "-n", str(script_path)], timeout=8)
        if check["code"] != 0:
            return {"code": 1, "stdout": check["stdout"], "stderr": check["stderr"], "sets": sets}
        script_changed = (not TPROXY_SCRIPT.exists()) or TPROXY_SCRIPT.read_text(encoding="utf-8") != script_path.read_text(encoding="utf-8")
        sysctl_changed = (not TPROXY_SYSCTL.exists()) or TPROXY_SYSCTL.read_text(encoding="utf-8") != sysctl_path.read_text(encoding="utf-8")
        if TPROXY_SCRIPT.exists() and script_changed:
            # 只有真实内容变化才保留现场备份；空同步不能在 /usr/local/sbin 下制造无意义 .bak 垃圾。
            shutil.copy2(TPROXY_SCRIPT, TPROXY_SCRIPT.with_name(f"{TPROXY_SCRIPT.name}.bak.{now_stamp()}"))
        if TPROXY_SYSCTL.exists() and sysctl_changed:
            # 新装或重复同步时内容相同不备份，避免 /etc/sysctl.d 被安装态刷新留下历史噪音。
            shutil.copy2(TPROXY_SYSCTL, TPROXY_SYSCTL.with_name(f"{TPROXY_SYSCTL.name}.bak.{now_stamp()}"))
        if script_changed:
            shutil.copy2(script_path, TPROXY_SCRIPT)
        if TPROXY_SCRIPT.exists():
            TPROXY_SCRIPT.chmod(0o755)
        if sysctl_changed:
            shutil.copy2(sysctl_path, TPROXY_SYSCTL)
    if ENABLE_RADVD and shutil.which("radvd"):
        radvd = sync_radvd(sets["interface"])
    else:
        reason = "disabled; set SING_BOX_GATEWAY_ENABLE_RADVD=1 to advertise this host as an IPv6 router"
        if ENABLE_RADVD and not shutil.which("radvd"):
            reason = "radvd not installed"
        radvd = {"code": 0, "skipped": True, "reason": reason}
    restart = run_command(rc_service_args(TPROXY_SERVICE, "restart"), timeout=20)
    status = unit_status(TPROXY_SERVICE)
    code = 0 if restart["code"] == 0 and status == "active" and radvd.get("code", 0) == 0 else 1
    return {"code": code, "stdout": restart["stdout"], "stderr": restart["stderr"], "service": status, "sets": sets, "radvd": radvd}


def maintenance_status():
    rule_logs = recent_unit_logs(RULE_UPDATE_SERVICE, 100)
    last_manual = load_json(RULE_UPDATE_LAST_PATH, {})
    journal_summary = rule_update_summary(rule_logs)
    summary = last_manual.get("summary") or journal_summary
    log = last_manual.get("log") or rule_logs
    result_text = last_manual.get("result") or journal_summary.get("status", "")
    last_text = last_manual.get("finishedAt") or ""
    iface = first_default_interface()
    current_v6 = current_ipv6_prefixes(iface)
    script_v6 = script_ipv6_prefixes(TPROXY_SCRIPT)
    schedule = parse_rule_update_schedule()
    next_update = next_rule_update_time(schedule)
    telegram_cidr = load_telegram_cidr_data()
    return {
        "ruleUpdate": {
            "script": str(RULE_UPDATE_SCRIPT),
            "scriptExists": RULE_UPDATE_SCRIPT.exists(),
            "timer": "cron",
            "timerActive": unit_status("cron"),
            "next": next_update,
            "last": last_text,
            "result": result_text,
            "serviceState": unit_status("cron"),
            "log": log,
            "summary": summary,
            "schedule": schedule,
        },
        "telegramCidr": telegram_cidr,
        "tproxy": {
            "service": TPROXY_SERVICE,
            "serviceActive": unit_status(TPROXY_SERVICE),
            "script": str(TPROXY_SCRIPT),
            "scriptExists": TPROXY_SCRIPT.exists(),
            "defaultInterface": iface,
            "currentIpv6Prefixes": current_v6,
            "currentIpv4Prefixes": current_ipv4_prefixes(iface),
            "scriptIpv6Prefixes": script_v6,
            # 多个公网 IPv6 前缀会同时下发给旁路网关；只命中其中一个仍会让另一个真实前缀误走 TProxy，状态页必须完整提示需要重新同步。
            # 用网段包含语义判断（含 fc00::/7 超网覆盖 ULA 子网的情况），字符串相等会误报。
            "ipv6PrefixMatches": not script_v6 or ipv6_prefixes_covered(current_v6, script_v6),
            "outboundServerIps": outbound_server_ips(),
            "outboundServers": resolved_outbound_servers(),
            "planned": tproxy_bypass_sets(),
        },
        "configHealth": config_health_status(),
    }


def duplicate_count(items):
    seen = set()
    duplicates = 0
    for item in items or []:
        key = json.dumps(item, sort_keys=True, ensure_ascii=False)
        if key in seen:
            duplicates += 1
        else:
            seen.add(key)
    return duplicates


def config_health_status():
    config = load_json(CONFIG_PATH, {}) if CONFIG_PATH.exists() else {}
    route_rules = config.get("route", {}).get("rules", []) or []
    dns_rules = config.get("dns", {}).get("rules", []) or []
    rule_sets = config.get("route", {}).get("rule_set", []) or []
    route = config.get("route", {}) or {}
    dns_servers = config.get("dns", {}).get("servers", []) or []
    local_dns = next((item for item in dns_servers if isinstance(item, dict) and item.get("tag") == "local-dns"), {})
    fakeip_dns = next((item for item in dns_servers if isinstance(item, dict) and item.get("type") == "fakeip"), {})
    bare_direct_indexes = [
        index + 1
        for index, rule in enumerate(route_rules)
        if isinstance(rule, dict) and rule.get("outbound") == "direct" and set(rule.keys()) == {"outbound"}
    ]
    geosite_proxy_indexes = [
        index + 1
        for index, rule in enumerate(route_rules)
        if isinstance(rule, dict)
        and rule.get("outbound") == "Proxy"
        and (
            rule.get("rule_set") == "geosite-geolocation-!cn"
            or (isinstance(rule.get("rule_set"), list) and "geosite-geolocation-!cn" in rule.get("rule_set"))
        )
    ]
    fakeip_ranges = [item for item in (fakeip_dns.get("inet4_range"), fakeip_dns.get("inet6_range")) if item]
    fakeip_route_ok = any(
        isinstance(rule, dict)
        and rule.get("outbound") == "Proxy"
        and isinstance(rule.get("ip_cidr"), list)
        and all(item in rule.get("ip_cidr", []) for item in fakeip_ranges)
        for rule in route_rules
    ) if fakeip_ranges else False
    route_order_ok = not bare_direct_indexes or not geosite_proxy_indexes or min(geosite_proxy_indexes) < min(bare_direct_indexes)
    udp443_reject = [
        rule
        for rule in route_rules
        if isinstance(rule, dict)
        and rule.get("network") == "udp"
        and rule.get("port") == 443
        and rule.get("action") == "reject"
    ]
    duplicates = {
        "route": duplicate_count(route_rules),
        "dns": duplicate_count(dns_rules),
        "ruleSet": duplicate_count(rule_sets),
    }
    mtu = interface_mtu(first_default_interface())
    # 接口 MTU 非标准值时验证路径 MTU 1500 是否可达，可达则视同标准
    # 不通则尝试自动探测并设置最佳 MTU
    if str(mtu) not in ("1492", "1500"):
        iface = first_default_interface()
        if check_path_mtu_1500(iface):
            mtu = "1500"
        else:
            fixed = auto_fix_mtu(iface)
            if fixed:
                mtu = fixed
    local_dns_status = {
        "type": local_dns.get("type", ""),
        "server": local_dns.get("server", ""),
        "port": local_dns.get("server_port", ""),
    }
    fakeip_status = {
        "inet4Range": fakeip_dns.get("inet4_range", ""),
        "inet6Range": fakeip_dns.get("inet6_range", ""),
    }
    # 维护页只做只读体检，不参与配置生成；这里用于提前发现重复规则膨胀，避免长期保存后拖慢路由匹配。
    ok = (
        not any(duplicates.values())
        and len(udp443_reject) <= 2
        and route_order_ok
        and fakeip_route_ok
        and bool(local_dns_status.get("server"))
        and route.get("final") in ("direct", "Proxy")
    )
    summary = config_health_summary(
        ok=ok,
        route_order_ok=route_order_ok,
        fakeip_route_ok=fakeip_route_ok,
        mtu=mtu,
        route_final=route.get("final", ""),
        local_dns=local_dns_status,
        duplicates=duplicates,
        udp443_reject_count=len(udp443_reject),
    )
    return {
        "ok": ok,
        "summary": summary,
        "routeRules": len(route_rules),
        "dnsRules": len(dns_rules),
        "ruleSets": len(rule_sets),
        "outbounds": len(config.get("outbounds", []) or []),
        "duplicateRules": duplicates,
        "udp443RejectRules": len(udp443_reject),
        "routeFinal": route.get("final", ""),
        "bareDirectRuleIndexes": bare_direct_indexes,
        "geositeProxyRuleIndexes": geosite_proxy_indexes,
        "routeOrderOk": route_order_ok,
        "fakeipRouteOk": fakeip_route_ok,
        "localDns": local_dns_status,
        "fakeip": fakeip_status,
        "interfaceMtu": mtu,
    }


def config_health_summary(ok, route_order_ok, fakeip_route_ok, mtu, route_final, local_dns, duplicates, udp443_reject_count):
    reasons = []
    if any(duplicates.values()):
        reasons.append("duplicate_rules")
    if udp443_reject_count > 2:
        reasons.append("udp443_rules")
    if not route_order_ok:
        reasons.append("route_order")
    if not fakeip_route_ok:
        reasons.append("fakeip_route")
    if not local_dns.get("server"):
        reasons.append("local_dns")
    if route_final not in ("direct", "Proxy"):
        reasons.append("route_final")
    if (
        ok
        and route_order_ok
        and fakeip_route_ok
        and str(mtu) in ("1492", "1500")
        and route_final in ("direct", "Proxy")
        and bool(local_dns.get("server"))
    ):
        return {"level": "great", "tone": "good", "reasons": []}
    if ok:
        great_reasons = []
        if str(mtu) not in ("1492", "1500"):
            great_reasons.append("mtu_not_ideal")
        # 未来新增"状态极佳"级别检查项时，在此追加条件即可
        return {"level": "normal", "tone": "soft", "reasons": great_reasons}
    return {"level": "problem", "tone": "warn", "reasons": reasons}


def interface_mtu(iface):
    if not iface:
        return ""
    result = run_command(["ip", "-o", "link", "show", "dev", iface], timeout=8)
    parts = result["stdout"].split()
    if "mtu" not in parts:
        return ""
    try:
        return parts[parts.index("mtu") + 1]
    except IndexError:
        return ""


def check_path_mtu_1500(iface):
    """验证到默认网关的路径 MTU 1500 是否可达（用于接口 MTU 异常高时的辅助判断）"""
    if not iface:
        return None
    gw_result = run_command(["ip", "-4", "route", "show", "default"], timeout=8)
    gw_match = re.search(r"via\s+(\S+)", gw_result["stdout"])
    if not gw_match:
        return None
    gateway = gw_match.group(1)
    # payload = MTU - 28（20B IP + 8B ICMP），-M do 设置 DF 位
    result = run_command(["ping", "-c", "1", "-M", "do", "-s", "1472", "-W", "2", gateway], timeout=8)
    return result["code"] == 0


def auto_fix_mtu(iface):
    """路径 MTU 1500 不通时，自动探测最佳 MTU 并设置到接口"""
    if not iface:
        return None
    gw_result = run_command(["ip", "-4", "route", "show", "default"], timeout=8)
    gw_match = re.search(r"via\s+(\S+)", gw_result["stdout"])
    if not gw_match:
        return None
    gateway = gw_match.group(1)
    for mtu in (1492, 1464, 1440, 1400):
        payload = mtu - 28
        result = run_command(["ping", "-c", "1", "-M", "do", "-s", str(payload), "-W", "2", gateway], timeout=8)
        if result["code"] == 0:
            # 找到可达 MTU，设置到接口
            current = interface_mtu(iface)
            if current and str(current) != str(mtu):
                run_command(["ip", "link", "set", "dev", iface, "mtu", str(mtu)], timeout=8)
            return str(mtu)
    return None  # 所有 MTU 均不通，不做修改


def update_rule_sets():
    if not RULE_UPDATE_SCRIPT.exists():
        return {"code": 1, "stdout": "", "stderr": f"Missing script: {RULE_UPDATE_SCRIPT}"}
    started = time.strftime("%Y-%m-%d %H:%M:%S")
    write_json(
        RULE_UPDATE_LAST_PATH,
        {
            "startedAt": started,
            "finishedAt": "",
            "result": "running",
            "code": None,
            "log": "Manual rule update is running.",
            "summary": {"updated": [], "kept": [], "skipped": [], "errors": [], "final": "Manual rule update is running.", "requiredOk": False},
        },
    )
    try:
        result = run_command([str(RULE_UPDATE_SCRIPT)], timeout=300)
    except subprocess.TimeoutExpired as exc:
        stdout = (exc.stdout or "").strip() if isinstance(exc.stdout, str) else ""
        stderr = (exc.stderr or "").strip() if isinstance(exc.stderr, str) else ""
        result = {
            "code": 124,
            "stdout": stdout,
            "stderr": (stderr + "\nManual rule update is taking longer than expected. Existing rule files were kept.").strip(),
        }
    text = "\n".join(item for item in (result.get("stdout"), result.get("stderr")) if item)
    result["summary"] = rule_update_summary(text)
    result["cronReschedule"] = reschedule_rule_update_cron_after_manual_success() if result["code"] == 0 else None
    write_json(
        RULE_UPDATE_LAST_PATH,
        {
            "startedAt": started,
            "finishedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
            "result": "success" if result["code"] == 0 else "slow" if result["code"] == 124 else "failed",
            "code": result["code"],
            "log": text,
            "summary": result["summary"],
            "cronReschedule": result["cronReschedule"],
        },
    )
    return result


def clash_api_request(path, method="GET", payload=None, timeout=8):
    api_url, api_secret = clash_api_settings()
    body = None
    headers = {}
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    if api_secret:
        headers["Authorization"] = f"Bearer {api_secret}"
    request = Request(f"{api_url}{path}", data=body, method=method, headers=headers)
    try:
        with urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
            return {"ok": True, "code": response.status, "data": json.loads(raw or "{}")}
    except HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        return {"ok": False, "code": exc.code, "error": raw or str(exc)}
    except (URLError, TimeoutError, OSError) as exc:
        return {"ok": False, "code": 0, "error": str(exc)}


def clash_runtime_snapshot(kind):
    paths = {
        "configs": "/configs",
        "connections": "/connections",
        "rules": "/rules",
        "traffic": "/traffic",
    }
    if kind not in paths:
        raise ValueError("Unsupported runtime endpoint")
    result = clash_api_request(paths[kind], timeout=10)
    if not result["ok"]:
        return result
    return {"ok": True, "code": result["code"], "data": result.get("data", {})}


def normalize_log_level(value):
    level = str(value or "").strip().lower()
    aliases = {"warning": "warn"}
    level = aliases.get(level, level)
    if level not in LOG_LEVELS:
        raise ValueError(f"Invalid log level: {value}")
    return level


def current_log_level():
    config = load_json(CONFIG_PATH, {}) if CONFIG_PATH.exists() else {}
    return normalize_log_level(config.get("log", {}).get("level", "warn"))


def set_log_level(level):
    level = normalize_log_level(level)
    ensure_manager_data()
    base = load_json(BASE_CONFIG_PATH, {})
    previous_base = backup_manager_file(BASE_CONFIG_PATH)
    previous_config = backup_manager_file(CONFIG_PATH)
    old_level = normalize_log_level(base.get("log", {}).get("level", current_log_level()))
    base.setdefault("log", {})
    # 日志级别会影响实时诊断数据量，必须写入 base 配置；否则下一次保存节点/规则会把运行态改动覆盖掉。
    base["log"]["level"] = level
    write_json(BASE_CONFIG_PATH, base)
    try:
        config = render_config()
        validate_outbound_references(config)
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=str(MANAGER_DIR), prefix=".log-level-", suffix=".json", delete=False) as handle:
            staged_path = Path(handle.name)
            handle.write(json.dumps(config, indent=2, ensure_ascii=False) + "\n")
        check = check_config(staged_path)
        staged_path.unlink(missing_ok=True)
        if check["code"] != 0:
            restore_file(BASE_CONFIG_PATH, previous_base)
            return {"ok": False, "error": "Config check failed. Log level was not changed.", "check": check, "restart": None, "state": load_state()}
        write_json(CONFIG_PATH, config)
        restart = restart_sing_box()
        if restart["code"] != 0 or service_status() != "active":
            restore_file(BASE_CONFIG_PATH, previous_base)
            restore_file(CONFIG_PATH, previous_config)
            rollback_restart = restart_sing_box()
            return {
                "ok": False,
                "error": "Restart failed. Previous log level was restored.",
                "check": check,
                "restart": restart,
                "rollback": {"restart": rollback_restart, "service": service_status()},
                "state": load_state(),
            }
        return {"ok": True, "level": level, "previous": old_level, "check": check, "restart": restart, "state": load_state()}
    except Exception:
        restore_file(BASE_CONFIG_PATH, previous_base)
        restore_file(CONFIG_PATH, previous_config)
        raise


def get_proxy_state():
    proxy_result = clash_api_request("/proxies/Proxy")
    if not proxy_result["ok"]:
        return proxy_result
    proxy_data = proxy_result["data"]
    data = {
        "now": proxy_data.get("now"),
        "all": proxy_data.get("all", []),
        "autoNow": None,
        "autoHistory": [],
    }
    if "Auto" in data["all"]:
        auto_result = clash_api_request("/proxies/Auto")
        if auto_result["ok"]:
            auto_data = auto_result["data"]
            data["autoNow"] = auto_data.get("now")
            data["autoHistory"] = auto_data.get("history", [])
        else:
            data["autoError"] = auto_result.get("error") or "Auto status unavailable"
    return {"ok": True, "code": proxy_result["code"], "data": data}


def set_proxy_now(tag):
    if tag != "Auto" and tag not in enabled_node_tags(load_nodes()):
        raise ValueError(f"Unknown enabled node: {tag}")
    return clash_api_request("/proxies/Proxy", method="PUT", payload={"name": tag})


def set_proxy_now_checked(tag, attempts=6, delay=0.15):
    # Clash API 热切实测 15~22ms，回读通常首次就对齐；attempts×delay 只是容错上限
    # （原 8×0.5s=4s 是为了等 sing-box 重启完成，现在不再重启，无需等那么久）。
    last_result = None
    for _ in range(attempts):
        last_result = set_proxy_now(tag)
        if last_result["ok"]:
            state = get_proxy_state()
            if state.get("ok") and state.get("data", {}).get("now") == tag:
                return {"ok": True, "code": last_result["code"], "data": state["data"]}
        time.sleep(delay)
    state = get_proxy_state()
    return {
        "ok": False,
        "code": (last_result or {}).get("code", 0),
        "error": f"Runtime proxy did not switch to {tag}",
        "data": state.get("data") if isinstance(state, dict) else None,
    }


def read_delay_history(tag):
    result = clash_api_request(f"/proxies/{quote(tag, safe='')}")
    if not result["ok"]:
        return None
    history = result.get("data", {}).get("history") or []
    delays = [item.get("delay") for item in history if isinstance(item, dict) and isinstance(item.get("delay"), int)]
    return delays[-1] if delays else None


def test_node_delay(tag, url=None, timeout_ms=5000):
    query = urlencode({"timeout": int(timeout_ms), "url": url or load_groups().get("auto", {}).get("url", "https://www.gstatic.com/generate_204")})
    result = clash_api_request(f"/proxies/{quote(tag, safe='')}/delay?{query}", timeout=max(8, int(timeout_ms / 1000) + 3))
    if not result["ok"]:
        return {"tag": tag, "ok": False, "delay": None, "error": result["error"]}
    delay = result.get("data", {}).get("delay")
    return {"tag": tag, "ok": isinstance(delay, int), "delay": delay if isinstance(delay, int) else None, "error": None if isinstance(delay, int) else "No delay returned"}


def set_auto_now(tag):
    if tag not in enabled_node_tags(load_nodes()):
        raise ValueError(f"Unknown enabled node: {tag}")
    return clash_api_request("/proxies/Auto", method="PUT", payload={"name": tag})


def wait_for_proxy_runtime(attempts=20, delay=0.5):
    last_state = None
    for _ in range(attempts):
        last_state = get_proxy_state()
        if last_state.get("ok") and "Auto" in (last_state.get("data", {}).get("all") or []):
            return last_state
        time.sleep(delay)
    return last_state or {"ok": False, "error": "Proxy runtime unavailable"}


def set_auto_now_checked(tag, attempts=16, delay=0.5):
    last_result = None
    last_state = None
    for _ in range(attempts):
        last_result = set_auto_now(tag)
        # Clash API 的 PUT 成功不等于 urltest 的 now 已经刷新；必须回读确认，避免 UI 继续显示旧 Auto 节点。
        last_state = get_proxy_state()
        auto_now = last_state.get("data", {}).get("autoNow") if last_state.get("ok") else None
        if last_result.get("ok") and auto_now == tag:
            return {"ok": True, "code": last_result["code"], "data": last_state["data"]}
        time.sleep(delay)
    last_state = get_proxy_state()
    return {
        "ok": False,
        "code": (last_result or {}).get("code", 0),
        "error": f"Auto did not switch to {tag}",
        "data": last_state.get("data") if isinstance(last_state, dict) else None,
        "lastResult": last_result,
    }


def auto_selected_delay(auto_now, measured_delays):
    if not auto_now:
        return None
    item = measured_delays.get(auto_now)
    if isinstance(item, dict) and isinstance(item.get("delay"), int):
        return item["delay"]
    return read_delay_history(auto_now)


def auto_alignment_decision(auto_now, current_delay, best_tag, best_delay):
    if not best_tag or not isinstance(best_delay, int):
        return {"shouldSwitch": False, "target": auto_now, "reason": "no best delay"}
    if auto_now == best_tag:
        return {"shouldSwitch": False, "target": auto_now, "reason": "already best"}
    if not auto_now or not isinstance(current_delay, int):
        return {"shouldSwitch": True, "target": best_tag, "reason": "current delay unavailable"}
    if current_delay > best_delay:
        return {"shouldSwitch": True, "target": best_tag, "reason": "current slower than best"}
    return {"shouldSwitch": False, "target": auto_now, "reason": "current within or equal to best"}


def align_auto_now_with_measured_delays(measured_delays):
    good = [item for item in measured_delays.values() if isinstance(item, dict) and item.get("ok") and isinstance(item.get("delay"), int)]
    if not good:
        return {"changed": False, "target": None, "reason": "no measured delays"}
    best = min(good, key=lambda item: item["delay"])
    state = get_proxy_state()
    if not state.get("ok"):
        return {"changed": False, "target": best["tag"], "error": state.get("error") or "Auto status unavailable"}
    auto_now = state.get("data", {}).get("autoNow")
    current_delay = auto_selected_delay(auto_now, measured_delays)
    decision = auto_alignment_decision(auto_now, current_delay, best["tag"], best["delay"])
    if not decision["shouldSwitch"]:
        return {
            "changed": False,
            "target": decision["target"],
            "best": best["tag"],
            "bestDelay": best["delay"],
            "current": auto_now,
            "currentDelay": current_delay,
            "reason": decision["reason"],
            "threshold": decision.get("threshold"),
        }
    return {
        "changed": False,
        "target": decision["target"],
        "best": best["tag"],
        "bestDelay": best["delay"],
        "current": auto_now,
        "currentDelay": current_delay,
        "reason": decision["reason"],
        "threshold": decision.get("threshold"),
        "wouldSwitch": True,
    }


def refresh_proxy_delays():
    nodes = load_nodes()
    tags = enabled_node_tags(nodes)
    values = {}
    api_error = None
    # 先请求 Auto 自身测速唤醒 urltest；逐节点测速后还会再校准一次，避免 Auto.now 读取旧一轮判断。
    auto_probe = test_node_delay("Auto", timeout_ms=8000) if tags else None
    if auto_probe and not auto_probe["ok"]:
        api_error = auto_probe.get("error")
    for tag in tags:
        item = test_node_delay(tag)
        values[tag] = item
        if not item["ok"] and not api_error:
            api_error = item.get("error")
    # 逐节点 delay 会刷新各出站 history；这里再测 Auto，让 URLTest 用同一轮最新结果自行选择 now。
    auto_reprobe = test_node_delay("Auto", timeout_ms=8000) if tags else None
    if auto_reprobe and not auto_reprobe["ok"] and not api_error:
        api_error = auto_reprobe.get("error")
    auto_align = align_auto_now_with_measured_delays(values) if tags else {"changed": False, "target": None}
    return {
        "available": api_error is None,
        "error": api_error,
        "delays": values,
        "autoProbe": auto_probe,
        "autoReprobe": auto_reprobe,
        "autoAlign": auto_align,
    }


def current_proxy_payload(test_delays=False):
    return {"proxy": get_proxy_state(), "delays": get_node_delays(test=test_delays)}


def current_proxy_payload_with_history_alignment():
    # 前端展示延时走 read_delay_history（Clash API history），不主动触发 fallback/auto-align
    delays = get_node_delays(test=False)
    return {"proxy": get_proxy_state(), "delays": delays}


def current_proxy_payload_after_probe(test_delays=False):
    delays = get_node_delays(test=test_delays)
    # 主动测速可能刚刚改变 urltest 的 Auto.now；返回给 UI 前必须重新读取运行态，避免显示旧选择。
    return {"proxy": get_proxy_state(), "delays": delays}


def get_node_delays(test=False):
    if test:
        return refresh_proxy_delays()
    nodes = load_nodes()
    tags = enabled_node_tags(nodes)
    values = {}
    api_error = None
    for tag in tags:
        values[tag] = {"tag": tag, "ok": True, "delay": read_delay_history(tag), "error": None}
    return {"available": api_error is None, "error": api_error, "delays": values}


def dns_delay_choice_item(choice, groups_dns=None):
    item = dict(LOCAL_DNS_CHOICES[choice])
    if choice == "custom_dns":
        groups_dns = groups_dns or {}
        item["server"] = str(groups_dns.get("local_custom_server", "223.5.5.5")).strip() or "223.5.5.5"
        item["server_port"] = int(groups_dns.get("local_custom_port", 53) or 53)
    return item


def measure_dns_delay(choice, host="www.qq.com", groups_dns=None):
    item = dns_delay_choice_item(choice, groups_dns)
    started = time.monotonic()
    try:
        answers = query_dns_once(item["server"], item["server_port"], host, 1, timeout=3)
        elapsed = int(round((time.monotonic() - started) * 1000))
        return {
            "choice": choice,
            "label": item["label"],
            "server": item["server"],
            "server_port": item["server_port"],
            "ok": bool(answers),
            "delay": elapsed if answers else None,
            "answers": answers[:3],
            "error": "" if answers else "no A record",
        }
    except Exception as exc:
        return {
            "choice": choice,
            "label": item["label"],
            "server": item["server"],
            "server_port": item["server_port"],
            "ok": False,
            "delay": None,
            "answers": [],
            "error": str(exc),
        }


def get_dns_delays(groups_dns=None):
    # 这里测的是网关机到各国内 DNS 的实际 UDP 查询耗时，供用户手动选择单个 local-dns 上游。
    groups_dns = groups_dns or load_groups().get("dns", {})
    return {
        "host": "www.qq.com",
        "items": {choice: measure_dns_delay(choice, groups_dns=groups_dns) for choice in LOCAL_DNS_CHOICES},
    }


def normalize_payload_lists(raw_lists):
    if not isinstance(raw_lists, dict):
        raise ValueError("lists must be an object")
    return {name: normalize_list_entries(name, raw_lists.get(name, [])) for name in LISTS}


def normalize_payload_groups(raw_groups, nodes=None):
    groups = load_groups()
    tags = set(enabled_node_tags(nodes or load_nodes()))
    if isinstance(raw_groups, dict):
        proxy = raw_groups.get("proxy")
        if isinstance(proxy, dict):
            groups["proxy"]["default"] = str(proxy.get("default", groups["proxy"]["default"]))
            if groups["proxy"]["default"] not in {"Auto", *tags}:
                raise ValueError(f"Unknown proxy default: {groups['proxy']['default']}")
            groups["proxy"]["interrupt_exist_connections"] = normalize_bool(
                proxy.get("interrupt_exist_connections", groups["proxy"].get("interrupt_exist_connections", DEFAULT_INTERRUPT_EXIST_CONNECTIONS))
            )
        auto = raw_groups.get("auto")
        if isinstance(auto, dict):
            groups["auto"]["url"] = normalize_url(auto.get("url", groups["auto"]["url"]), groups["auto"]["url"])
            # interval / idle_timeout 是 Go 时长字符串，非法值会让 sing-box 起不来而
            # check 抓不到，必须在这里解析校验（保留用户写法，不改写单位）。
            groups["auto"]["interval"] = normalize_duration(
                auto.get("interval", groups["auto"]["interval"]), groups["auto"]["interval"], "auto.interval"
            )
            groups["auto"]["idle_timeout"] = normalize_duration(
                auto.get("idle_timeout", groups["auto"].get("idle_timeout", DEFAULT_URLTEST_IDLE_TIMEOUT)),
                groups["auto"].get("idle_timeout", DEFAULT_URLTEST_IDLE_TIMEOUT),
                "auto.idle_timeout",
            )
            validate_urltest_timing(groups["auto"]["interval"], groups["auto"]["idle_timeout"])
            groups["auto"]["tolerance"] = normalize_non_negative_number(
                auto.get("tolerance", groups["auto"].get("tolerance", DEFAULT_URLTEST_TOLERANCE)),
                DEFAULT_URLTEST_TOLERANCE,
            )
            preferred = str(auto.get("preferred", groups["auto"].get("preferred", ""))).strip()
            if preferred in tags:
                groups["auto"]["preferred"] = preferred
            else:
                groups["auto"].pop("preferred", None)
            groups["auto"]["interrupt_exist_connections"] = normalize_bool(
                auto.get("interrupt_exist_connections", groups["auto"].get("interrupt_exist_connections", DEFAULT_INTERRUPT_EXIST_CONNECTIONS))
            )
            # fallback 是 reF1nd fork 的字段，官方版渲染层已不读取。保存时顺手清掉，
            # 避免它作为脏字段永久留在 groups.json 里误导后续维护（官方版 check 也不认）。
            groups["auto"].pop("fallback", None)
        fakeip = raw_groups.get("fakeip")
        if isinstance(fakeip, dict):
            groups["fakeip"]["inet4_range"] = normalize_cidr(
                fakeip.get("inet4_range", groups["fakeip"]["inet4_range"]),
                groups["fakeip"]["inet4_range"],
                strict=True,
            )
            groups["fakeip"]["inet6_range"] = normalize_cidr(
                fakeip.get("inet6_range", groups["fakeip"]["inet6_range"]),
                groups["fakeip"]["inet6_range"],
                strict=True,
            )
            groups["fakeip"]["ipv6_enabled"] = normalize_bool(fakeip.get("ipv6_enabled", groups["fakeip"].get("ipv6_enabled", True)))
            # FakeIP QUIC 保护是网关稳定边界：关闭会让浏览器 QUIC 长连接压住代理链路和连接表。
            groups["fakeip"]["block_quic"] = True
        dns = raw_groups.get("dns")
        if isinstance(dns, dict):
            local_dns = str(dns.get("local", groups["dns"].get("local", DEFAULT_LOCAL_DNS_CHOICE))).strip()
            if local_dns not in LOCAL_DNS_CHOICES:
                raise ValueError(f"Invalid local DNS upstream: {local_dns}")
            # 国内 DNS 上游影响所有直连域名解析，只接受内置候选，避免把错误地址写成“已保存”。
            groups["dns"]["local"] = local_dns
            # 无条件恢复 local_custom_server/port，即使当前 local 不是 custom_dns：
            # 导出备份始终包含这两个字段，用户期望导入后与导出完全一致，不受 local 选择影响。
            custom_server = str(dns.get("local_custom_server", "")).strip()
            if custom_server:
                groups["dns"]["local_custom_server"] = custom_server
            custom_port = int(dns.get("local_custom_port", 53))
            groups["dns"]["local_custom_port"] = custom_port
        ddns = raw_groups.get("ddns")
        if isinstance(ddns, dict):
            mode = str(ddns.get("dns", groups["ddns"].get("dns", "local"))).strip()
            if mode not in ("local", "remote"):
                raise ValueError(f"Invalid DDNS DNS mode: {mode}")
            groups["ddns"]["dns"] = mode
        telegram = raw_groups.get("telegram")
        if isinstance(telegram, dict):
            # Telegram 官方 IP 捕获是长期兼容开关：默认开启，允许高级用户在不需要时显式关闭。
            groups["telegram"]["capture_ips"] = normalize_bool(telegram.get("capture_ips", groups["telegram"].get("capture_ips", True)))
        socks5 = raw_groups.get("socks5")
        if isinstance(socks5, dict):
            port = int(socks5.get("port", groups["socks5"].get("port", 0)))
            groups["socks5"]["port"] = max(0, min(port, 65535))
    return groups


def rewrite_custom_rule_paths(config, staged_dir):
    route = config.get("route", {})
    for item in route.get("rule_set", []) or []:
        if not isinstance(item, dict):
            continue
        tag = item.get("tag")
        for name, custom_tag in CUSTOM_TAGS.items():
            if tag == custom_tag:
                item["path"] = str(staged_dir / f"{name}.json")


def write_rule_files(target_dir, normalized_lists):
    target_dir.mkdir(parents=True, exist_ok=True)
    for name, entries in normalized_lists.items():
        write_json(target_dir / f"{name}.json", entries_to_rule_set(entries))


def staged_check(normalized_lists, nodes=None, groups=None):
    ensure_dirs()
    try:
        validate_greylist_ip_cidrs(normalized_lists.get("greylist", []), nodes=nodes, groups=groups)
        render_tproxy_script(nodes=nodes, groups=groups, normalized_lists=normalized_lists)
    except Exception as exc:
        return {"code": 1, "stdout": "", "stderr": str(exc)}
    with tempfile.TemporaryDirectory(prefix=".staged-", dir=str(RULE_DIR)) as temp_name:
        staged_dir = Path(temp_name)
        write_rule_files(staged_dir, normalized_lists)
        try:
            config = render_config(nodes=nodes, groups=groups, rule_dir=staged_dir, normalized_lists=normalized_lists)
            validate_outbound_references(config)
        except Exception as exc:
            return {"code": 1, "stdout": "", "stderr": str(exc)}
        staged_config = staged_dir / "config.json"
        write_json(staged_config, config)
        return check_config(staged_config)


def apply_all(normalized_lists, nodes, groups):
    validate_greylist_ip_cidrs(normalized_lists.get("greylist", []), nodes=nodes, groups=groups)
    backups = {
        "config": backup_manager_file(CONFIG_PATH),
        "nodes": backup_manager_file(NODES_PATH),
        "groups": backup_manager_file(GROUPS_PATH),
    }
    saved = {}
    for name in LISTS:
        saved[name] = write_entries(name, normalized_lists[name])
    backup_manager_file(BASE_CONFIG_PATH)
    backup_manager_file(NODES_PATH)
    backup_manager_file(GROUPS_PATH)
    write_json(NODES_PATH, nodes)
    write_json(GROUPS_PATH, groups)
    write_json(CONFIG_PATH, render_config(nodes=nodes, groups=groups, rule_dir=RULE_DIR, normalized_lists=normalized_lists))
    return {"rules": saved, "backups": backups}


def apply_proxy_default(tag):
    """切换默认节点：热切运行态 + 静默持久化，不重启 sing-box。

    为什么不重启（2026-08-13 实测确立）：
      - selector 的 `default` 字段只决定 sing-box **启动时**的初值，运行态选择由
        Clash API 掌管（PUT /proxies/Proxy 实测 15~22ms，连接不断）。
      - 离线渲染对比证明：只改 groups.proxy.default 时，config.json 的差异
        仅 `/outbounds/[0]/default` 一个字段，不影响入站、DNS、路由、rule_set。
      - sync_tproxy 依赖节点 IP 与灰名单，与 proxy.default 无关，因此也不必跑。
    旧实现走 staged_check → apply_all → restart_sing_box → sync_tproxy →
    set_proxy_now_checked(4s 轮询) → test_node_delay(8s)，导致每次点节点全网瞬断
    且 UI 卡十几秒，这是「切换不丝滑」的根因。

    顺序：先热切（用户立刻生效）→ 再落盘（下次启动保持）。落盘失败不回滚运行态，
    因为运行态已经是用户要的结果；只把 persistError 报给前端，避免「看起来失败了
    其实已经切过去」的割裂感。
    """
    nodes = load_nodes()
    tags = {"Auto", *enabled_node_tags(nodes)}
    if tag not in tags:
        raise ValueError(f"Unknown proxy default: {tag}")

    # 1) 运行态热切，并回读确认（Clash API 的 PUT 成功不等于 now 已刷新）
    proxy = set_proxy_now_checked(tag)
    if not proxy["ok"]:
        return {
            "ok": False,
            "error": proxy.get("error") or "Runtime proxy switch failed.",
            "proxy": proxy,
            "restarted": False,
            "state": load_state(),
        }

    # 2) 静默持久化 groups.json + config.json，供下次启动使用。
    #    仍然先 staged_check：绝不把一个 check 不过的 config 落到正式路径。
    persist_error = None
    check = None
    saved = None
    groups = load_groups()
    groups.setdefault("proxy", {})
    groups["proxy"]["default"] = tag
    normalized_lists = {name: read_entries(name) for name in LISTS}
    try:
        check = staged_check(normalized_lists, nodes=nodes, groups=groups)
        if check["code"] != 0:
            persist_error = "Config check failed. Runtime switched but default was not saved."
        else:
            saved = apply_all(normalized_lists, nodes, groups)
    except Exception as exc:  # 落盘异常不能影响已生效的运行态切换
        persist_error = f"Persist failed: {exc}"

    return {
        "ok": True,
        "error": "",
        "persistError": persist_error,
        "check": check,
        "saved": saved,
        "restarted": False,
        "proxy": proxy,
        "proxyAfterProbe": proxy.get("data"),
        "maintenance": maintenance_status(),
        "state": load_state(),
    }


def export_backup_payload():
    ensure_manager_data()
    return {
        "kind": "sing-box-gateway-ui-backup",
        "version": BACKUP_VERSION,
        "exportedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "host": socket.gethostname(),
        "paths": {
            "config": str(CONFIG_PATH),
            "manager": str(MANAGER_DIR),
            "rules": str(RULE_DIR),
            "tproxyScript": str(TPROXY_SCRIPT),
            "tproxySysctl": str(TPROXY_SYSCTL),
            "radvd": str(RADVD_CONF),
        },
        "lists": {name: read_entries(name) for name in LISTS},
        "nodes": load_nodes(),
        "groups": load_groups(),
        "snapshots": {
            "config": load_json(CONFIG_PATH, {}) if CONFIG_PATH.exists() else {},
            "base": load_json(BASE_CONFIG_PATH, {}) if BASE_CONFIG_PATH.exists() else {},
            "tproxyScript": read_text_if_exists(TPROXY_SCRIPT),
            "tproxySysctl": read_text_if_exists(TPROXY_SYSCTL),
            "radvd": read_text_if_exists(RADVD_CONF),
            "ruleFiles": {
                name: load_json(rule_path(name), empty_rule_set()) if rule_path(name).exists() else empty_rule_set()
                for name in LISTS
            },
        },
    }


def import_backup_payload(payload):
    if not isinstance(payload, dict):
        raise ValueError("Backup must be a JSON object")
    if payload.get("kind") != "sing-box-gateway-ui-backup":
        raise ValueError("Unsupported backup file")
    version = int(payload.get("version") or 0)
    if version < 1 or version > BACKUP_VERSION:
        raise ValueError(f"Unsupported backup version: {version}")
    normalized_lists = normalize_payload_lists(payload.get("lists", {}))
    nodes = normalize_nodes(payload.get("nodes", []))
    groups = normalize_payload_groups(payload.get("groups", {}), nodes=nodes)
    check = staged_check(normalized_lists, nodes=nodes, groups=groups)
    if check["code"] != 0:
        return {
            "ok": False,
            "error": "Config check failed. Backup was not imported.",
            "check": check,
            "saved": None,
            "restart": None,
            "rollback": None,
            "tproxySync": None,
        }
    result = apply_all(normalized_lists, nodes, groups)
    apply_import_runtime_later(nodes, groups, normalized_lists, result)
    return {
        "ok": True,
        "error": "",
        "check": check,
        "saved": result,
        "restart": {"code": 0, "stdout": "", "stderr": "", "scheduled": True, "service": "sing-box"},
        "rollback": None,
        "tproxySync": {"code": 0, "stdout": "", "stderr": "", "scheduled": True, "service": TPROXY_SERVICE},
        "applyScheduled": True,
        "maintenance": maintenance_status(),
        "state": load_state(),
    }


def rollback_apply(result):
    backups = (result or {}).get("backups", {})
    restore_file(CONFIG_PATH, backups.get("config"))
    restore_file(NODES_PATH, backups.get("nodes"))
    restore_file(GROUPS_PATH, backups.get("groups"))
    for item in ((result or {}).get("rules") or {}).values():
        if isinstance(item, dict):
            name = item.get("name")
            backup = item.get("backup")
            if name in LISTS and backup:
                restore_file(rule_path(name), backup)


def load_state():
    ensure_manager_data()
    lists = {}
    for name in LISTS:
        lists[name] = read_entries(name)
    return {
        "lists": lists,
        "nodes": load_nodes(),
        "groups": load_groups(),
        "meta": {
            "ruleDir": str(RULE_DIR),
            "managerDir": str(MANAGER_DIR),
            "configPath": str(CONFIG_PATH),
            "service": service_status(),
            "memory": sing_box_memory(),
            # 只展示当前运行二进制版本，便于现场判断配置兼容性；不代表会自动升级 sing-box。
            "singBoxVersion": sing_box_version(),
            "dnsChoices": LOCAL_DNS_CHOICES,
        },
    }


class Handler(BaseHTTPRequestHandler):
    server_version = "SingBoxRuleUI/1.0"

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, fmt, *args):
        # stdout 被 systemd unit 重定向到 journal/文件后是块缓冲，不强制刷盘会把访问日志
        # 卡在内存里（Alpine 生产机实测日志文件停写），排障时看不到实时请求记录。
        print("%s - %s" % (self.address_string(), fmt % args), flush=True)

    def authorized(self):
        token = get_token()
        auth = self.headers.get("Authorization", "")
        return auth == f"Bearer {token}"

    def send_json(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_error_json(self, message, status=400):
        self.send_json({"error": message}, status)

    def send_download(self, filename, payload):
        body = json.dumps(payload, indent=2, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def stream_clash_api(self, path, content_type="application/json; charset=utf-8", timeout=60):
        api_url, api_secret = clash_api_settings()
        headers = {}
        if api_secret:
            headers["Authorization"] = f"Bearer {api_secret}"
        if path.startswith("/logs?"):
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.end_headers()
            request = Request(f"{api_url}{path}", headers=headers)
            try:
                with urlopen(request, timeout=timeout) as response:
                    while True:
                        chunk = response.read(4096)
                        if not chunk:
                            break
                        self.wfile.write(chunk)
                        self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError):
                return
            except (HTTPError, URLError, TimeoutError, OSError):
                # 日志流是诊断辅助通道；切换级别会重启 sing-box，runtime API 短暂不可用时结束空流，不能把 UI 打成 502。
                return
            return
        # 9091 已经完成 Rule UI token 鉴权；这里仅用后端读取到的 Clash secret 访问白名单接口，不能把 secret 暴露给浏览器。
        request = Request(f"{api_url}{path}", headers=headers)
        try:
            with urlopen(request, timeout=timeout) as response:
                self.send_response(response.status)
                self.send_header("Content-Type", content_type)
                self.end_headers()
                while True:
                    chunk = response.read(4096)
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    self.wfile.flush()
        except HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace")
            self.send_error_json(raw or str(exc), exc.code)
        except (BrokenPipeError, ConnectionResetError):
            return
        except (URLError, TimeoutError, OSError) as exc:
            self.send_error_json(str(exc), 502)

    def read_json_body(self):
        length = int(self.headers.get("Content-Length", "0"))
        if length > 2_000_000:
            raise ValueError("Request body is too large")
        raw = self.rfile.read(length).decode("utf-8")
        return json.loads(raw or "{}")

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/state":
            if not self.authorized():
                self.send_error_json("Unauthorized", 401)
                return
            self.send_json(load_state())
            return
        if parsed.path == "/api/proxy":
            if not self.authorized():
                self.send_error_json("Unauthorized", 401)
                return
            self.send_json(current_proxy_payload_with_history_alignment())
            return
        if parsed.path == "/api/maintenance":
            if not self.authorized():
                self.send_error_json("Unauthorized", 401)
                return
            self.send_json({"maintenance": maintenance_status(), "state": load_state()})
            return
        if parsed.path == "/api/telegram-cidr":
            if not self.authorized():
                self.send_error_json("Unauthorized", 401)
                return
            self.send_json({"telegramCidr": load_telegram_cidr_data()})
            return
        if parsed.path == "/api/backup/export":
            if not self.authorized():
                self.send_error_json("Unauthorized", 401)
                return
            filename = f"sing-box-gateway-ui-backup-{socket.gethostname()}-{now_stamp()}.json"
            self.send_download(filename, export_backup_payload())
            return
        if parsed.path == "/api/delays":
            if not self.authorized():
                self.send_error_json("Unauthorized", 401)
                return
            query = dict(item.split("=", 1) for item in parsed.query.split("&") if "=" in item)
            if query.get("test") == "1":
                self.send_json(current_proxy_payload_after_probe(test_delays=True))
            else:
                self.send_json({"delays": get_node_delays(test=False)})
            return
        if parsed.path == "/api/dns-delays":
            if not self.authorized():
                self.send_error_json("Unauthorized", 401)
                return
            query = parse_qs(parsed.query)
            groups_dns = dict(load_groups().get("dns", {}))
            custom_server = str((query.get("custom_server") or [""])[0]).strip()
            custom_port = str((query.get("custom_port") or [""])[0]).strip()
            if custom_server:
                groups_dns["local_custom_server"] = custom_server
            if custom_port:
                try:
                    groups_dns["local_custom_port"] = int(custom_port)
                except ValueError:
                    self.send_error_json("Invalid custom DNS port", 400)
                    return
            self.send_json({"dnsDelays": get_dns_delays(groups_dns)})
            return
        if parsed.path.startswith("/api/runtime/"):
            if not self.authorized():
                self.send_error_json("Unauthorized", 401)
                return
            kind = parsed.path.rsplit("/", 1)[-1]
            if kind == "logs":
                try:
                    query = parse_qs(parsed.query)
                    level = normalize_log_level((query.get("level") or ["info"])[0])
                except ValueError as exc:
                    self.send_error_json(str(exc), 400)
                    return
                self.stream_clash_api(f"/logs?{urlencode({'level': level})}", content_type="text/plain; charset=utf-8", timeout=300)
                return
            if kind in {"configs", "connections", "rules", "traffic"}:
                self.send_json({"runtime": clash_runtime_snapshot(kind), "logLevel": current_log_level()})
                return
            self.send_error_json("Not found", 404)
            return
        if parsed.path == "/api/token-hint":
            self.send_json({"message": "Use Authorization: Bearer <token> from the server token file."})
            return
        self.serve_static(parsed.path)

    def do_HEAD(self):
        parsed = urlparse(self.path)
        path = "/index.html" if parsed.path in ("", "/") else parsed.path
        safe = Path(unquote(path).lstrip("/"))
        target = (STATIC_DIR / safe).resolve()
        if not str(target).startswith(str(STATIC_DIR.resolve())) or not target.exists() or target.is_dir():
            self.send_response(404)
            self.end_headers()
            return
        self.send_response(200)
        self.send_header("Content-Length", str(target.stat().st_size))
        self.end_headers()

    def do_POST(self):
        parsed = urlparse(self.path)
        if not self.authorized():
            self.send_error_json("Unauthorized", 401)
            return
        try:
            payload = self.read_json_body()
            if parsed.path == "/api/save":
                normalized_lists = normalize_payload_lists(payload.get("lists", {}))
                nodes = normalize_nodes(payload.get("nodes", load_nodes()))
                groups = normalize_payload_groups(payload.get("groups", load_groups()), nodes=nodes)
                previous_proxy = get_proxy_state()
                previous_auto_now = previous_proxy.get("data", {}).get("autoNow") if previous_proxy.get("ok") else None
                if previous_auto_now in enabled_node_tags(nodes):
                    groups.setdefault("auto", {})["preferred"] = previous_auto_now
                previous_delays = get_node_delays(test=False)
                check = staged_check(normalized_lists, nodes=nodes, groups=groups)
                if check["code"] != 0:
                    self.send_json(
                        {
                            "error": "Config check failed. Changes were not saved and sing-box was not restarted.",
                            "saved": None,
                            "check": check,
                            "restart": None,
                            "state": load_state(),
                        },
                        422,
                    )
                    return
                result = apply_all(normalized_lists, nodes, groups)
                restart = restart_sing_box()
                rollback = None
                if restart["code"] != 0 or service_status() != "active":
                    rollback_apply(result)
                    rollback_restart = restart_sing_box()
                    rollback = {"restart": rollback_restart, "service": service_status()}
                    self.send_json(
                        {
                            "error": "Restart failed. Previous config was restored.",
                            "saved": result,
                            "check": check,
                            "restart": restart,
                            "rollback": rollback,
                            "state": load_state(),
                        },
                        500,
                    )
                    return
                tproxy_sync = sync_tproxy(nodes=nodes, groups=groups, normalized_lists=normalized_lists)
                wait_for_proxy_runtime()
                delays = get_node_delays(test=False)
                if isinstance(delays, dict):
                    # 保存配置只负责让 sing-box 使用新容差；不在保存请求里重新测速或强制切 Auto，避免设置保存本身改变当前出站。
                    delays["previousDelays"] = previous_delays
                self.send_json(
                    {
                        "saved": result,
                        "check": check,
                        "restart": restart,
                        "rollback": rollback,
                        "tproxySync": tproxy_sync,
                        "proxy": get_proxy_state(),
                        "delays": delays,
                        "maintenance": maintenance_status(),
                        "state": load_state(),
                    }
                )
                return
            if parsed.path == "/api/check":
                self.send_json({"check": check_config(), "state": load_state()})
                return
            if parsed.path == "/api/restart":
                check = check_config()
                if check["code"] != 0:
                    self.send_json(
                        {
                            "error": "Config check failed. sing-box was not restarted.",
                            "check": check,
                            "restart": None,
                            "state": load_state(),
                        },
                        422,
                    )
                    return
                restart = restart_sing_box()
                if restart["code"] != 0:
                    self.send_json(
                        {
                            "error": "Restart failed. Existing config was kept and service recovery was attempted.",
                            "check": check,
                            "restart": restart,
                            "state": load_state(),
                        },
                        500,
                    )
                    return
                self.send_json({"check": check, "restart": restart, "state": load_state()})
                return
            if parsed.path == "/api/rules/update":
                result = update_rule_sets()
                status = 200 if result["code"] == 0 else 500
                self.send_json({"update": result, "maintenance": maintenance_status(), "state": load_state()}, status)
                return
            if parsed.path == "/api/rules/schedule":
                result = write_rule_update_schedule(payload)
                status = 200 if result["ok"] else 500
                self.send_json({"scheduleUpdate": result, "maintenance": maintenance_status(), "state": load_state()}, status)
                return
            if parsed.path == "/api/telegram-cidr/update":
                result = update_telegram_cidrs()
                status = 200 if result["ok"] else 500
                self.send_json({"telegramCidrUpdate": result, "maintenance": maintenance_status(), "state": load_state()}, status)
                return
            if parsed.path == "/api/telegram-cidr/save":
                cidrs = payload.get("cidrs")
                if isinstance(cidrs, str):
                    cidrs = parse_telegram_cidr_text(cidrs)
                result = save_telegram_cidrs(cidrs or [], source="manual")
                sync = sync_tproxy()
                status = 200 if sync["code"] == 0 else 500
                self.send_json({"telegramCidr": result, "tproxySync": sync, "maintenance": maintenance_status(), "state": load_state()}, status)
                return
            if parsed.path == "/api/tproxy/sync":
                result = sync_tproxy()
                status = 200 if result["code"] == 0 else 500
                self.send_json({"sync": result, "maintenance": maintenance_status(), "state": load_state()}, status)
                return
            if parsed.path == "/api/tproxy/restart":
                result = restart_tproxy()
                status = 200 if result["code"] == 0 else 500
                self.send_json({"restart": result, "maintenance": maintenance_status(), "state": load_state()}, status)
                return
            if parsed.path == "/api/ui/restart":
                restart_rule_ui_later()
                self.send_json({"scheduled": True, "service": RULE_UI_SERVICE})
                return
            if parsed.path == "/api/backup/import":
                result = import_backup_payload(payload)
                status = 200 if result["ok"] else 422 if result.get("check", {}).get("code") != 0 else 500
                self.send_json(
                    {
                        **result,
                        "maintenance": maintenance_status(),
                        "state": load_state(),
                    },
                    status,
                )
                return
            if parsed.path == "/api/proxy/select":
                tag = str(payload.get("tag", "")).strip()
                if not tag:
                    raise ValueError("tag is required")
                self.send_json({"proxy": set_proxy_now(tag), "state": load_state()})
                return
            if parsed.path == "/api/proxy/default":
                tag = str(payload.get("tag", "")).strip()
                if not tag:
                    raise ValueError("tag is required")
                result = apply_proxy_default(tag)
                status = 200 if result["ok"] else 422 if result.get("check", {}).get("code") != 0 else 500
                self.send_json(result, status)
                return
            if parsed.path == "/api/runtime/log-level":
                level = str(payload.get("level", "")).strip()
                if not level:
                    raise ValueError("level is required")
                result = set_log_level(level)
                status = 200 if result["ok"] else 422 if result.get("check", {}).get("code") != 0 else 500
                self.send_json(result, status)
                return
            if parsed.path == "/api/token/change":
                # 修改 UI 访问密码：do_POST 顶部已做 Bearer 鉴权，这里只需校验并落盘新值。
                # 返回后前端会用新 token 更新 localStorage，旧 token 立即失效。
                new_token = set_token(payload.get("token", ""))
                self.send_json({"ok": True, "token": new_token})
                return
            self.send_error_json("Not found", 404)
        except Exception as exc:
            self.send_error_json(str(exc), 400)

    def serve_static(self, path):
        if path in ("", "/"):
            path = "/index.html"
        safe = Path(unquote(path).lstrip("/"))
        target = (STATIC_DIR / safe).resolve()
        if not str(target).startswith(str(STATIC_DIR.resolve())) or not target.exists() or target.is_dir():
            self.send_response(404)
            self.end_headers()
            return
        content_type = "text/plain"
        if target.suffix == ".html":
            content_type = "text/html; charset=utf-8"
        elif target.suffix == ".css":
            content_type = "text/css; charset=utf-8"
        elif target.suffix == ".js":
            content_type = "application/javascript; charset=utf-8"
        body = target.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        if target.suffix == ".html":
            self.send_header("Cache-Control", "no-store")
        elif target.suffix in {".js", ".css"}:
            self.send_header("Cache-Control", "no-cache, must-revalidate")
        self.end_headers()
        self.wfile.write(body)


def main():
    token = get_token()
    host = os.environ.get("RULE_UI_HOST", "0.0.0.0")
    port = int(os.environ.get("RULE_UI_PORT", "9091"))
    print(f"Sing-box Rule UI listening on http://{host}:{port}")
    print(f"Token file: {TOKEN_FILE}")
    print(f"Token: {token}")
    ThreadingHTTPServer((host, port), Handler).serve_forever()


if __name__ == "__main__":
    main()
