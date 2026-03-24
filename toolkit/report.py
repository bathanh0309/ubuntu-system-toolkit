import json
from datetime import datetime
from pathlib import Path

from toolkit.network import parse_open_ports
from toolkit.processes import get_top_processes
from toolkit.system_info import get_system_info


def build_report(process_limit: int = 5) -> dict:
    return {
        "timestamp": datetime.now().isoformat(),
        "system_info": get_system_info(),
        "top_processes": get_top_processes(process_limit),
        "open_ports": parse_open_ports(),
    }


def export_report(output_dir: str = "reports", process_limit: int = 5) -> str:
    report = build_report(process_limit=process_limit)

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    filename = datetime.now().strftime("system_report_%Y%m%d_%H%M%S.json")
    file_path = output_path / filename

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    return str(file_path)