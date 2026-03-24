import subprocess


def get_open_ports() -> str:
    try:
        result = subprocess.run(
            ["ss", "-tulpn"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except FileNotFoundError:
        return "Command 'ss' not found on this system."
    except subprocess.CalledProcessError as e:
        return f"Failed to get open ports: {e}"


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


def print_open_ports() -> None:
    print("\n=== OPEN PORTS ===")
    print(get_open_ports())


def print_ping(host: str, count: int = 4) -> None:
    print(f"\n=== PING {host} ===")
    print(ping_host(host, count))