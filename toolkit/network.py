import re
import subprocess
from typing import Optional


def get_open_ports_raw() -> str:
    try:
        result = subprocess.run(
            ["ss", "-tulpn", "-H"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except FileNotFoundError:
        return "Command 'ss' not found on this system."
    except subprocess.CalledProcessError as e:
        return f"Failed to get open ports: {e}"


def parse_address_and_port(endpoint: str) -> tuple[str, str]:
    endpoint = endpoint.strip()

    if endpoint in {"*", "*:*"}:
        return endpoint, "*"

    # IPv6 dạng [::1]:323
    if endpoint.startswith("[") and "]:" in endpoint:
        host, port = endpoint.rsplit(":", 1)
        return host, port

    # IPv4 / hostname / localhost dạng 127.0.0.1:42185
    if ":" in endpoint:
        host, port = endpoint.rsplit(":", 1)
        return host, port

    return endpoint, ""


def parse_process_info(process_field: str) -> tuple[str, str]:
    if not process_field:
        return "-", "-"

    name_match = re.search(r'"([^"]+)"', process_field)
    pid_match = re.search(r"pid=(\d+)", process_field)

    process_name = name_match.group(1) if name_match else "-"
    pid = pid_match.group(1) if pid_match else "-"

    return process_name, pid


def parse_open_ports() -> list[dict]:
    raw = get_open_ports_raw()

    if raw.startswith("Command 'ss' not found") or raw.startswith("Failed to get open ports"):
        return []

    rows = []
    for line in raw.splitlines():
        # ss -H thường có format:
        # tcp LISTEN 0 511 127.0.0.1:42185 0.0.0.0:* users:(("node",pid=3581,fd=22))
        parts = line.split(None, 5)

        if len(parts) < 5:
            continue

        netid = parts[0]
        state = parts[1]
        recv_q = parts[2]
        send_q = parts[3]
        local_endpoint = parts[4]
        process_field = parts[5] if len(parts) >= 6 else ""

        local_address, port = parse_address_and_port(local_endpoint)
        process_name, pid = parse_process_info(process_field)

        rows.append(
            {
                "protocol": netid,
                "state": state,
                "recv_q": recv_q,
                "send_q": send_q,
                "local_address": local_address,
                "port": port,
                "process": process_name,
                "pid": pid,
            }
        )

    return rows


def get_open_ports_table(limit: Optional[int] = None) -> str:
    rows = parse_open_ports()

    if not rows:
        raw = get_open_ports_raw()
        return raw if raw else "No open ports found."

    if limit is not None:
        rows = rows[:limit]

    headers = ["PROTO", "STATE", "LOCAL_ADDRESS", "PORT", "PROCESS", "PID"]

    table_rows = [
        [
            row["protocol"],
            row["state"],
            row["local_address"],
            row["port"],
            row["process"],
            row["pid"],
        ]
        for row in rows
    ]

    widths = [len(h) for h in headers]
    for row in table_rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell)))

    def format_row(row: list[str]) -> str:
        return "  ".join(str(cell).ljust(widths[i]) for i, cell in enumerate(row))

    lines = [
        format_row(headers),
        format_row(["-" * w for w in widths]),
    ]
    lines.extend(format_row(row) for row in table_rows)

    return "\n".join(lines)


def ping_host(host: str = "8.8.8.8", count: int = 4) -> str:
    try:
        result = subprocess.run(
            ["ping", "-c", str(count), host],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except FileNotFoundError:
        return "Command 'ping' not found on this system."
    except subprocess.CalledProcessError as e:
        error_output = e.stderr.strip() if e.stderr else str(e)
        return f"Ping failed: {error_output}"


def print_open_ports(limit: Optional[int] = None, raw: bool = False) -> None:
    print("\n=== OPEN PORTS ===")
    if raw:
        print(get_open_ports_raw())
    else:
        print(get_open_ports_table(limit=limit))


def print_ping(host: str, count: int = 4) -> None:
    print(f"\n=== PING {host} ===")
    print(ping_host(host, count))