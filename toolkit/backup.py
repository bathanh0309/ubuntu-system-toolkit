import tarfile
from datetime import datetime
from pathlib import Path


def create_backup(source: str, output_dir: str = "reports") -> str:
    source_path = Path(source).expanduser().resolve()

    if not source_path.exists():
        raise FileNotFoundError(f"Source path does not exist: {source_path}")

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_name = output_path / f"{source_path.name}_backup_{timestamp}.tar.gz"

    with tarfile.open(archive_name, "w:gz") as tar:
        tar.add(source_path, arcname=source_path.name)

    return str(archive_name)