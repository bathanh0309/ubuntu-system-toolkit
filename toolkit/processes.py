import psutil


def get_top_processes(limit: int = 5) -> list[dict]:
    processes = []

    for proc in psutil.process_iter(["pid", "name", "username", "cpu_percent", "memory_percent"]):
        try:
            info = proc.info
            processes.append(
                {
                    "pid": info["pid"],
                    "name": info["name"] or "unknown",
                    "user": info["username"] or "unknown",
                    "cpu_percent": info["cpu_percent"] or 0.0,
                    "memory_percent": round(info["memory_percent"] or 0.0, 2),
                }
            )
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    processes.sort(key=lambda x: (x["cpu_percent"], x["memory_percent"]), reverse=True)
    return processes[:limit]


def print_top_processes(limit: int = 5) -> None:
    processes = get_top_processes(limit)

    print("\n=== TOP PROCESSES ===")
    for proc in processes:
        print(
            f"PID={proc['pid']} | "
            f"NAME={proc['name']} | "
            f"USER={proc['user']} | "
            f"CPU={proc['cpu_percent']}% | "
            f"MEM={proc['memory_percent']}%"
        )