#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
StartZSKJ.py - Start and monitor AtHomeCamera Collector in background, auto kill at stop time
Usage: python StartZSKJ.py <program_path> [auto_start] [show_window] [start_time] [stop_time]
Example: python StartZSKJ.py "C:\Program Files (x86)\AtHomeCamera\Collector.exe" True False "08:00" "23:00"
"""

import sys
import os
import time
import datetime
import subprocess
import logging

# ==================== Logger (compatible with your miniapi) ====================
try:
    import miniapi
    logging_time = datetime.datetime.now().strftime("%Y-%m-%d_%H_%M_%S")
    logger = miniapi.setup_logger(
        name="StartZSKJ",
        level=logging.DEBUG,
        log_file=f"./logs/StartZSKJ_{logging_time}.log",
        use_colors=True,
        format_string="%(asctime)s [%(levelname)s] %(message)s"
    )
except ImportError:
    # Fallback to standard logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler(f"StartZSKJ_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger("StartZSKJ")

# ==================== Parse arguments ====================
args = sys.argv
if len(args) < 2:
    logger.error("Missing required argument: provide the path to AtHomeCamera program")
    logger.info("Usage: python StartZSKJ.py <program_path> [auto_start] [show_window] [start_time] [stop_time]")
    sys.exit(1)

ZSKJ = args[1].strip('"')                     # program path
ZSKJ_Auto_Start = args[2] if len(args) > 2 else "True"
ZSKJ_Show_Window = args[3] if len(args) > 3 else "False"
Auto_Start_Time = args[4] if len(args) > 4 else "00:00"
Auto_Stop_Time = args[5] if len(args) > 5 else "00:00"

# Validate program path
if not os.path.isfile(ZSKJ):
    logger.error(f"Program path does not exist: {ZSKJ}")
    sys.exit(1)

# Extract process name (without path)
TARGET_PROCESS_NAME = os.path.basename(ZSKJ)
logger.info(f"Target process: {TARGET_PROCESS_NAME}")
logger.info(f"Program path: {ZSKJ}")
logger.info(f"Auto start enabled: {ZSKJ_Auto_Start}")
logger.info(f"Show window: {ZSKJ_Show_Window}")
logger.info(f"Auto start time: {Auto_Start_Time}")
logger.info(f"Auto stop time: {Auto_Stop_Time}")

# ==================== Helper functions ====================
def is_process_running(process_name):
    """Check if a process is running by name using psutil or fallback tasklist"""
    try:
        import psutil
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'].lower() == process_name.lower():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False
    except ImportError:
        logger.warning("psutil not installed, using tasklist fallback")
        try:
            result = subprocess.run(
                ['tasklist', '/FI', f'IMAGENAME eq {process_name}'],
                capture_output=True, text=True, timeout=5
            )
            return process_name.lower() in result.stdout.lower()
        except Exception as e:
            logger.error(f"tasklist check failed: {e}")
            return False

def kill_process(process_name):
    """Terminate all processes with the given name"""
    logger.info(f"Attempting to kill process: {process_name}")
    try:
        import psutil
        killed = False
        for proc in psutil.process_iter(['name', 'pid']):
            try:
                if proc.info['name'].lower() == process_name.lower():
                    proc.terminate()  # graceful termination
                    logger.info(f"Terminated {process_name} (PID: {proc.info['pid']})")
                    killed = True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                continue
        if not killed:
            logger.warning(f"No running process found with name: {process_name}")
        return killed
    except ImportError:
        logger.warning("psutil not installed, using taskkill fallback")
        try:
            # Use taskkill to forcefully terminate by image name
            result = subprocess.run(
                ['taskkill', '/F', '/IM', process_name],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                logger.info(f"Successfully killed {process_name} using taskkill")
                return True
            else:
                logger.warning(f"taskkill failed: {result.stderr.strip()}")
                return False
        except Exception as e:
            logger.error(f"taskkill error: {e}")
            return False

def start_app_hidden_with_pwsh(app_path, show_window=False):
    """Start application in background using PowerShell"""
    if show_window:
        command = [app_path]
        subprocess.Popen(command, creationflags=subprocess.CREATE_NEW_CONSOLE)
    else:
        command = [
            'powershell.exe',
            '-WindowStyle', 'Hidden',
            '-Command',
            f'Start-Process -WindowStyle Hidden -FilePath "{app_path}"'
        ]
        subprocess.Popen(command, creationflags=subprocess.CREATE_NO_WINDOW)
    logger.info(f"Start command executed: {app_path}")

def check_auto_time(target_time: str, mode: str = "start") -> bool:
    """Check if current time >= target_time (HH:MM)"""
    now = datetime.datetime.now()
    current = now.strftime("%H:%M")
    return current >= target_time

def wait_until_start_time(start_time: str, check_interval=30):
    """Wait until auto start time is reached; return immediately if already reached"""
    logger.info(f"Waiting for auto start time {start_time} ...")
    while True:
        if check_auto_time(start_time, "start"):
            logger.info("Auto start time reached")
            break
        time.sleep(check_interval)

# ==================== Single instance mutex (optional) ====================
def ensure_single_instance():
    """Ensure only one instance of this script runs using a mutex"""
    try:
        import win32event
        import win32api
        import winerror
        mutex_name = "Global\\StartZSKJ_SingleInstance_Mutex"
        mutex = win32event.CreateMutex(None, False, mutex_name)
        if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
            logger.warning("Script is already running, this instance will exit")
            sys.exit(0)
    except ImportError:
        logger.debug("pywin32 not installed, skipping single instance check")
    except Exception as e:
        logger.warning(f"Single instance check failed: {e}")

# ==================== Main logic ====================
def main():
    # Optional: ensure single instance
    # ensure_single_instance()

    # If auto start is not enabled, exit
    if ZSKJ_Auto_Start.lower() != "true":
        logger.info("Auto start not enabled, exiting")
        return

    # Wait until auto start time
    wait_until_start_time(Auto_Start_Time, check_interval=30)

    # Enter monitoring loop
    logger.info("Entering monitoring loop, press Ctrl+C to exit")
    try:
        while True:
            # Check if auto stop time reached
            if check_auto_time(Auto_Stop_Time, "stop"):
                logger.info("Auto stop time reached, terminating target process...")
                kill_process(TARGET_PROCESS_NAME)
                logger.info("Exiting monitoring")
                break

            # Check if target process is running
            if not is_process_running(TARGET_PROCESS_NAME):
                logger.info(f"Process {TARGET_PROCESS_NAME} is not running, attempting to start...")
                try:
                    start_app_hidden_with_pwsh(ZSKJ, show_window=(ZSKJ_Show_Window.lower() == "true"))
                    # Wait for process to appear to avoid duplicate starts
                    time.sleep(5)
                except Exception as e:
                    logger.error(f"Start failed: {e}")
                    # Wait longer before retry after failure
                    time.sleep(30)
            else:
                # Process alive, normal interval
                time.sleep(60)

    except KeyboardInterrupt:
        logger.info("Monitoring stopped by user")
    except Exception as e:
        logger.exception(f"Unexpected error in monitoring loop: {e}")

if __name__ == "__main__":
    main()