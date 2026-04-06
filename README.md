# invisibility

**Version 26.1.0** – A silent background launcher and watchdog for Windows applications, designed for AtHomeCamera Collector (掌上看家) but adaptable to other programs.

> *Run any application silently in the background, with scheduled start/stop and automatic crash recovery.*

## Overview

`invisibility` is a lightweight Windows tool that starts a target program completely hidden, keeps it alive, and optionally stops it at a configured time. It consists of two components:

- **`Launcher`** – Interactive configuration shell and process supervisor.
- **`StartZSKJ`** – Core watchdog that handles timing, process monitoring, and auto‑restart.

All activity is logged to the `./logs/` folder.

## Features

- **Silent operation** – No console windows, no application windows (configurable).
- **Time‑based scheduling** – Set daily start and stop times (24h format).
- **Watchdog** – Automatically restarts the target process if it crashes.
- **Interactive configurator** – Change settings at runtime via simple commands.
- **Persistent configuration** – Settings saved to a plain text file.
- **Minimal resource usage** – Checks process status every 60 seconds.

## Quick Start

### Using pre‑built executables

1. Download `Launcher.exe` and `StartZSKJ.exe` from the [Releases](../../releases) page.
2. Place both files in the same folder (e.g. `C:\invisibility`).
3. Create a configuration file `Launcher.set` (see example below).
4. Run `Launcher.exe` – it will start the target program automatically according to the schedule.

### Configuration example (`Launcher.set`)

```ini
ZSKJ=C:\Path\To\Your\Program.exe
ZSKJAutoStart=True
ZSKJShowWindow=False
AutoStartTime=08:00
AutoStopTime=22:30
```

## Building from source

Use PyInstaller to compile the Python scripts:

```bash
pip install pyinstaller psutil
pyinstaller --onefile --noconsole --name StartZSKJ --uac-admin StartZSKJ.py
pyinstaller --onefile --name Launcher --uac-admin Launcher.py
```

## Requirements

- Windows 7 / 8 / 10 / 11
- Python 3.7+ (only for building from source)

## License

MIT License – free to use and modify.

---

**Made for teachers who need a quiet monitoring solution.**  
*Questions? Open an issue or pull request.*
