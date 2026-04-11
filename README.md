# invisibility

**Version 26.2.0** – Silent launcher and watchdog for AtHomeCamera (掌上看家) with time‑based scheduling.

> *Designed for teachers who need to remotely monitor self‑study sessions – no window, no noise, just reliable background operation.*

## Overview

`invisibility` is a lightweight Windows tool that starts the **AtHomeCamera Collector** (掌上看家采集端) completely hidden, keeps it alive, and optionally stops it at a configured time. It consists of two components:

- **`Launcher.py`** (compiled to `Launcher.exe`) – A configuration shell + process supervisor. It reads settings from `Launcher.set`, launches `StartZSKJ.exe` in a background thread, and provides an interactive command‑line configurator.
- **`StartZSKJ.py`** (compiled to `StartZSKJ.exe`) – The core watchdog. It waits for the scheduled start time, then continuously checks if the target process is running. If the process dies, it restarts it. If a stop time is set, it terminates the process gracefully.

All logging is written to the `./logs/` folder with timestamps – perfect for troubleshooting.

## New in v26.2.0

### ✨ `restart` command

The Launcher now supports a `restart` command, which stops and then starts the `StartZSKJ` watchdog process in one step. This is useful after changing configuration (e.g., `AutoStartTime`) without having to manually type `stop` followed by `start`.

- **Usage**: `invisibility> restart`
- **Effect**: Terminates all running `StartZSKJ.exe` instances, then launches a fresh one with the current configuration.

### 🚀 `--no-console` argument

For unattended scenarios (e.g., classroom computers that boot daily), you can now start `Launcher.exe` without entering the interactive shell. The launcher will:

- Read `Launcher.set`
- Auto‑start `StartZSKJ.exe` if not already running
- Exit immediately, leaving the watchdog running in the background

**Usage**:
```bash
Launcher.exe --no-console
```

This is ideal for adding to Windows Startup (`shell:startup`) so that the monitoring begins silently without any user interaction.

> **Note**: Even with `--no-console`, you can still use the full interactive shell by omitting the flag. The flag only suppresses the command prompt.

## Features

- ✅ **Silent start** – No PowerShell window, no application window (optional `show_window` flag available).
- ✅ **Time‑based scheduling** – Define `AutoStartTime` and `AutoStopTime` (24h format, e.g. `08:00` / `22:30`).
- ✅ **Watchdog** – Monitors the process every 60 seconds; automatically restarts if it crashes.
- ✅ **Graceful termination** – Sends `WM_CLOSE` via `kill_process()` (falls back to `taskkill` if `psutil` not available).
- ✅ **Interactive configurator** – Change settings on‑the‑fly without editing files.
- ✅ **Persistent configuration** – Settings are saved to `Launcher.set` and survive reboots.
- ✅ **English logging** – Clean, searchable logs suitable for automated monitoring.
- ✅ **New in v26.2.0** – `restart` command and `--no-console` mode for unattended startup.

## Requirements

- Windows 7 / 8 / 10 / 11
- Python 3.7+ (if running from source)
- Optional but recommended: `psutil` for robust process detection

```bash
pip install psutil
```

## Installation

### Option 1: Use pre‑compiled executables (recommended for teachers)

1. Download `Launcher.exe` and `StartZSKJ.exe` from the [Releases](../../releases) page.
2. Place both `.exe` files in the same folder (e.g. `C:\invisibility`).
3. Create a configuration file `Launcher.set` (see [Configuration](#configuration)).
4. (Optional) Add a shortcut to `Launcher.exe` in the Windows Startup folder (`shell:startup`) for automatic launch on boot.

### Option 2: Run from source

```bash
git clone https://github.com/yourusername/invisibility.git
cd invisibility
pip install -r requirements.txt   # psutil, miniapi (if needed)
python Launcher.py
```

## Configuration

Create a file named `Launcher.set` in the same directory as `Launcher.exe`. Example:

```ini
ZSKJ=C:\Program Files (x86)\AtHomeCamera\Collector.exe
ZSKJAutoStart=True
ZSKJShowWindow=False
AutoStartTime=08:00
AutoStopTime=22:30
```

| Key               | Description                                                                 |
|-------------------|-----------------------------------------------------------------------------|
| `ZSKJ`            | Full path to the AtHomeCamera Collector executable                          |
| `ZSKJAutoStart`   | `True` or `False` – enable the watchdog                                     |
| `ZSKJShowWindow`  | `True` = show the camera window, `False` = hidden                           |
| `AutoStartTime`   | Time when the process should start (HH:MM, 24h)                             |
| `AutoStopTime`    | Time when the process should be terminated (HH:MM, 24h)                     |

## Usage

### Running Launcher

Double-click `Launcher.exe` or run it from command line:

```bash
Launcher.exe              # Normal interactive mode
Launcher.exe --no-console # Silent mode (no console, exits after starting watchdog)
```

The launcher will:

- Check if `StartZSKJ.exe` is already running. If not, it will auto‑start it in the background.
- In normal mode, display an interactive command prompt: `invisibility>`
- In `--no-console` mode, perform the check/start and then exit immediately.

### Interactive Commands

| Command                  | Action                                                          |
|--------------------------|-----------------------------------------------------------------|
| `start`                  | Manually start `StartZSKJ` (if not already running)            |
| `stop`                   | Terminate all `StartZSKJ` processes immediately                |
| `restart`                | Stop and restart `StartZSKJ` (apply configuration changes)     |
| `set <key> <value>`      | Change a configuration value (e.g. `set AutoStopTime 23:00`)    |
| `upload`                 | Write current configuration to `Launcher.set` (persist changes) |
| `show`                   | Display current settings and process status                    |
| `help`                   | Show this help message                                          |
| `clear`                  | Clear the screen                                                |
| `exit`                   | Exit Launcher – `StartZSKJ` continues running in background     |

> **Note:** The watchdog (`StartZSKJ.exe`) will continue running even after you exit the Launcher. Use the `stop` command if you want to terminate it.

## Building Executables (for Developers)

Use [PyInstaller](https://pyinstaller.org/) to compile the Python scripts into standalone `.exe` files.

### Install PyInstaller

```bash
pip install pyinstaller
```

### Build StartZSKJ.exe (core watchdog, no console, admin rights)

```bash
pyinstaller --onefile --noconsole --name StartZSKJ --uac-admin --hidden-import psutil --hidden-import miniapi StartZSKJ.py
```

### Build Launcher.exe (interactive console, admin rights recommended)

```bash
pyinstaller --onefile --name Launcher --uac-admin --hidden-import psutil --hidden-import miniapi Launcher.py
```

The output executables will be in the `dist/` folder.

## Deployment for Teachers (Stealth Mode) (Optional)

1. Place `Launcher.exe`, `StartZSKJ.exe` and `Launcher.set` in a folder like `C:\invisibility`.
2. (Optional) Rename `Launcher.exe` to something innocuous, e.g. `svchost_helper.exe`.
3. Add a shortcut to `Launcher.exe` in the Windows Startup folder:
   - Press `Win + R`, type `shell:startup`, press Enter.
   - Create a shortcut to `Launcher.exe` inside that folder.
   - **Tip:** Add `--no-console` to the shortcut target to suppress the interactive shell (e.g., `"C:\invisibility\Launcher.exe" --no-console`).
4. The program will start silently when the computer boots and begin monitoring according to the schedule.

> **Important:** Set `ZSKJShowWindow=False` to keep the camera window hidden. The teacher can still view the stream via the *AtHomeCamera Viewer* on their phone/PC – the Collector runs invisibly in the background.

## Logging

Logs are stored in `./logs/`:

- `StartZSKJ_YYYY-MM-DD_HH_MM_SS.log` – watchdog activity (starts, stops, crashes, restarts)
- `launcher_YYYY-MM-DD_HH_MM_SS.log` – launcher shell commands and configuration changes

Use `--debug` flag when running `Launcher.py` from source to get more detailed logs.

## Troubleshooting

| Issue                                | Likely solution                                               |
|--------------------------------------|---------------------------------------------------------------|
| `StartZSKJ.exe` not found            | Place the executable in the same folder as `Launcher.exe`.    |
| Process not starting                 | Check that the path in `ZSKJ` is correct and the file exists.|
| `psutil` not installed warning       | Install it: `pip install psutil`. The script falls back to `tasklist` and `taskkill`. |
| Program window still appears         | Set `ZSKJShowWindow=False`. If it still shows, the application may ignore startup flags. |
| “Auto stop time reached” but process keeps running | Try increasing the kill timeout; some processes ignore `terminate()` – fallback uses `taskkill /F`. |
| Need to stop `StartZSKJ` twice       | This can happen due to Python bootloader processes. The `stop` command now kills **all** `StartZSKJ.exe` instances in a loop – one command is enough. |

## Contributing

Issues and pull requests are welcome. This project is maintained by a student developer – feedback is appreciated.

## License

MIT License – use freely, modify as needed.

---

**Made with ❤️ for teachers who deserve a quiet classroom.**  
*invisibility – because monitoring shouldn't be a distraction.*