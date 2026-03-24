import subprocess


def get_system_logs(lines: int = 20, service: str | None = None) -> str:
    if service:
        cmd = ["journalctl", "-u", service, "-n", str(lines), "--no-pager"]
    else:
        cmd = ["journalctl", "-n", str(lines), "--no-pager"]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except FileNotFoundError:
        return "Command 'journalctl' not found on this system."
    except subprocess.CalledProcessError as e:
        error_output = e.stderr.strip() if e.stderr else str(e)
        return f"Failed to read logs: {error_output}"