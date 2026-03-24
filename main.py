import argparse

from toolkit.backup import create_backup
from toolkit.logs import get_system_logs
from toolkit.network import print_open_ports, print_ping
from toolkit.processes import print_top_processes
from toolkit.report import export_report
from toolkit.services import print_running_services, print_service_status
from toolkit.system_info import get_system_info


def show_status() -> None:
    info = get_system_info()

    print("\n=== SYSTEM STATUS ===")
    for key, value in info.items():
        print(f"{key}: {value}")

    print_top_processes(limit=5)


def handle_report() -> None:
    file_path = export_report()
    print(f"Report saved to: {file_path}")


def handle_backup(source: str, output_dir: str) -> None:
    try:
        backup_file = create_backup(source=source, output_dir=output_dir)
        print(f"Backup created: {backup_file}")
    except FileNotFoundError as e:
        print(e)


def handle_logs(lines: int, service: str | None) -> None:
    print("\n=== SYSTEM LOGS ===")
    print(get_system_logs(lines=lines, service=service))


def handle_services(name: str | None, limit: int) -> None:
    if name:
        print_service_status(name)
    else:
        print_running_services(limit=limit)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Ubuntu System Toolkit")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("status", help="Show CPU, memory, disk, uptime, and top processes")
    subparsers.add_parser("ports", help="Show open ports")
    subparsers.add_parser("report", help="Export a JSON system report")

    ping_parser = subparsers.add_parser("ping", help="Ping a host")
    ping_parser.add_argument("--host", default="8.8.8.8", help="Host to ping")
    ping_parser.add_argument("--count", type=int, default=4, help="Number of ping packets")

    backup_parser = subparsers.add_parser("backup", help="Create a .tar.gz backup of a directory or file")
    backup_parser.add_argument("--source", required=True, help="Source file or directory to back up")
    backup_parser.add_argument("--output", default="reports", help="Output directory for backup archive")

    logs_parser = subparsers.add_parser("logs", help="Show recent system logs")
    logs_parser.add_argument("--lines", type=int, default=20, help="Number of log lines to show")
    logs_parser.add_argument("--service", default=None, help="Optional systemd service name")

    services_parser = subparsers.add_parser("services", help="List running services or inspect one service")
    services_parser.add_argument("--name", default=None, help="Optional service name, e.g. systemd-resolved")
    services_parser.add_argument("--limit", type=int, default=20, help="Maximum number of services to show")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "status":
        show_status()
    elif args.command == "ports":
        print_open_ports()
    elif args.command == "ping":
        print_ping(args.host, args.count)
    elif args.command == "report":
        handle_report()
    elif args.command == "backup":
        handle_backup(args.source, args.output)
    elif args.command == "logs":
        handle_logs(args.lines, args.service)
    elif args.command == "services":
        handle_services(args.name, args.limit)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()