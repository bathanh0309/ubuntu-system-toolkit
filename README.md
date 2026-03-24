# Ubuntu System Toolkit

A modular Linux system monitoring toolkit built with Python on Ubuntu/WSL.

## Features
- Show CPU, memory, disk, uptime, and load average
- Display top running processes
- Show open ports
- Ping a target host
- Export JSON system reports
- Create `.tar.gz` backups
- Read recent system logs with `journalctl`

## Project Structure
```text
ubuntu-system-toolkit/
├── README.md
├── requirements.txt
├── .gitignore
├── main.py
├── reports/
├── screenshots/
└── toolkit/
    ├── __init__.py
    ├── system_info.py
    ├── processes.py
    ├── network.py
    ├── report.py
    ├── backup.py
    └── logs.py