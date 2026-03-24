import re
import subprocess


def get_running_services(limit: int = 20) -> list[dict]:
    try:
        result = subprocess.run(
            [
                "systemctl",
                "list-units",
                "--type=service",
                "--state=running",
                "--no-pager",
                "--no-legend",
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        services = []
        lines = result.stdout.strip().splitlines()

        for line in lines[:limit]:
            parts = line.split(None, 4)
            if len(parts) >= 5:
                services.append(
                    {
                        "unit": parts[0],
                        "load": parts[1],
                        "active": parts[2],
                        "sub": parts[3],
                        "description": parts[4],
                    }
                )

        return services

    except FileNotFoundError:
        return []
    except subprocess.CalledProcessError:
        return []


def print_running_services(limit: int = 20) -> None:
    services = get_running_services(limit=limit)

    print("\n=== RUNNING SERVICES ===")

    if not services:
        print("No running services found, or 'systemctl' is unavailable.")
        return

    for idx, service in enumerate(services, start=1):
        print(
            f"{idx:02d}. "
            f"{service['unit']} | "
            f"LOAD={service['load']} | "
            f"ACTIVE={service['active']} | "
            f"SUB={service['sub']} | "
            f"{service['description']}"
        )


def get_service_status_raw(service_name: str) -> str:
    try:
        result = subprocess.run(
            ["systemctl", "status", service_name, "--no-pager", "-l"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except FileNotFoundError:
        return "Command 'systemctl' not found on this system."
    except subprocess.CalledProcessError as e:
        output = e.stdout.strip() if e.stdout else ""
        error_output = e.stderr.strip() if e.stderr else ""
        return output or error_output or f"Failed to get service status for: {service_name}"


def parse_service_status(raw_text: str) -> dict:
    parsed = {
        "service": None,
        "description": None,
        "loaded": None,
        "active": None,
        "docs": [],
        "main_pid": None,
        "status": None,
        "tasks": None,
        "memory": None,
        "cpu": None,
        "cgroup": None,
        "recent_logs": [],
        "raw": raw_text,
    }

    lines = raw_text.splitlines()
    log_pattern = re.compile(r"^[A-Z][a-z]{2}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}\s+")

    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        if stripped.startswith("● "):
            # Ví dụ:
            # ● systemd-resolved.service - Network Name Resolution
            first = stripped[2:]
            if " - " in first:
                service, description = first.split(" - ", 1)
                parsed["service"] = service.strip()
                parsed["description"] = description.strip()
            else:
                parsed["service"] = first.strip()

        elif stripped.startswith("Loaded:"):
            parsed["loaded"] = stripped.removeprefix("Loaded:").strip()

        elif stripped.startswith("Active:"):
            parsed["active"] = stripped.removeprefix("Active:").strip()

        elif stripped.startswith("Docs:"):
            docs_value = stripped.removeprefix("Docs:").strip()
            if docs_value:
                parsed["docs"].append(docs_value)

            j = i + 1
            while j < len(lines):
                next_line = lines[j]
                if next_line.startswith("             ") and next_line.strip():
                    parsed["docs"].append(next_line.strip())
                    j += 1
                else:
                    break
            i = j - 1

        elif stripped.startswith("Main PID:"):
            parsed["main_pid"] = stripped.removeprefix("Main PID:").strip()

        elif stripped.startswith("Status:"):
            parsed["status"] = stripped.removeprefix("Status:").strip()

        elif stripped.startswith("Tasks:"):
            parsed["tasks"] = stripped.removeprefix("Tasks:").strip()

        elif stripped.startswith("Memory:"):
            parsed["memory"] = stripped.removeprefix("Memory:").strip()

        elif stripped.startswith("CPU:"):
            parsed["cpu"] = stripped.removeprefix("CPU:").strip()

        elif stripped.startswith("CGroup:"):
            parsed["cgroup"] = stripped.removeprefix("CGroup:").strip()

        elif log_pattern.match(stripped):
            parsed["recent_logs"].append(stripped)

        i += 1

    return parsed


def print_service_status(service_name: str, max_logs: int = 10) -> None:
    raw = get_service_status_raw(service_name)

    if raw.startswith("Command 'systemctl' not found") or raw.startswith("Failed to get service status"):
        print(f"\n=== SERVICE STATUS: {service_name} ===")
        print(raw)
        return

    parsed = parse_service_status(raw)

    # Nếu parse không ra service name thì fallback về raw text
    if not parsed["service"]:
        print(f"\n=== SERVICE STATUS: {service_name} ===")
        print(raw)
        return

    print(f"\n=== SERVICE STATUS: {parsed['service']} ===")

    if parsed["description"]:
        print(f"Description: {parsed['description']}")
    if parsed["loaded"]:
        print(f"Loaded: {parsed['loaded']}")
    if parsed["active"]:
        print(f"Active: {parsed['active']}")
    if parsed["main_pid"]:
        print(f"Main PID: {parsed['main_pid']}")
    if parsed["status"]:
        print(f"Status: {parsed['status']}")
    if parsed["tasks"]:
        print(f"Tasks: {parsed['tasks']}")
    if parsed["memory"]:
        print(f"Memory: {parsed['memory']}")
    if parsed["cpu"]:
        print(f"CPU: {parsed['cpu']}")
    if parsed["cgroup"]:
        print(f"CGroup: {parsed['cgroup']}")

    if parsed["docs"]:
        print("Docs:")
        for doc in parsed["docs"]:
            print(f"  - {doc}")

    print("\nRecent logs:")
    if parsed["recent_logs"]:
        for log_line in parsed["recent_logs"][:max_logs]:
            print(f"  - {log_line}")
    else:
        print("  - No recent logs found.")