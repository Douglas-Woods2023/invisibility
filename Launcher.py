import miniapi
import os
import sys
import datetime
import logging
import threading
import time
import subprocess
import psutil

args = sys.argv

# 日志
miniapi.mkdir("./logs", exist_ok=True)
logging_time = datetime.datetime.now().strftime("%Y-%m-%d_%H_%M_%S")
if "--debug" in args:
    log_level = logging.DEBUG
    log_file = f"./logs/launcher_debug_{logging_time}.log"
else:
    log_level = logging.INFO
    log_file = f"./logs/launcher_{logging_time}.log"
logger = miniapi.setup_logger(
    name="Launcher",
    level=log_level,
    log_file=log_file,
    use_colors=True,
    format_string="%(asctime)s [%(levelname)s] %(message)s"
)
logger.info("Logger initialized. Log file: %s", log_file)

# 读取配置文件
logger.info("Reading configuration from Launcher.set")
setf = open("Launcher.set", "r", encoding="utf-8")
setlist = setf.readlines()
logger.debug("Configuration lines read: %d", len(setlist))
logger.debug(f"setlist = {setlist}")
setf.close()
logger.info("Configuration file closed.")
config = {}
for line in setlist:
    line = line.strip()
    if line and not line.startswith("#"):
        key, value = line.split("=", 1)
        config[key.strip()] = value.strip()
logger.debug("Configuration dictionary created with %d entries", len(config))
logger.debug(f"config = {config}")
logger.info("Configuration parsing completed.")

# 全局变量
zskj_process = None          # 保存由本 Launcher 启动的 Popen 对象（用于 stop）
start_thread = None          # 记录启动线程，避免重复启动

def is_startzskj_running():
    """检查 StartZSKJ.exe 进程是否在运行"""
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'].lower() == 'startzskj.exe':
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False

def get_startzskj_pid():
    """返回 StartZSKJ.exe 的 PID，不存在则返回 None"""
    for proc in psutil.process_iter(['name', 'pid']):
        try:
            if proc.info['name'].lower() == 'startzskj.exe':
                return proc.info['pid']
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return None

def launch_zskj_launcher(launcher_config: dict):
    """启动 StartZSKJ.exe 子进程（由线程调用，不阻塞）"""
    global zskj_process
    ZSKJ = launcher_config.get("ZSKJ")
    ZSKJ_Auto_Start = launcher_config.get("ZSKJAutoStart")
    ZSKJ_Show_Window = launcher_config.get("ZSKJShowWindow")
    Auto_Start_Time = launcher_config.get("AutoStartTime")
    Auto_Stop_Time = launcher_config.get("AutoStopTime")
    logger.info("Launching StartZSKJ.exe...")
    logger.debug(f"ZSKJ={ZSKJ}, AutoStart={ZSKJ_Auto_Start}, ShowWindow={ZSKJ_Show_Window}, "
                 f"StartTime={Auto_Start_Time}, StopTime={Auto_Stop_Time}")
    try:
        proc = subprocess.Popen(
            ["./StartZSKJ.exe", ZSKJ, ZSKJ_Auto_Start, ZSKJ_Show_Window,
             Auto_Start_Time, Auto_Stop_Time],
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        zskj_process = proc
        logger.info(f"StartZSKJ launched with PID {proc.pid}")
    except Exception as e:
        logger.error(f"Failed to launch StartZSKJ: {e}")

def stop_startzskj():
    """Terminate ALL StartZSKJ processes (kill all instances)"""
    global zskj_process
    killed_any = False

    # 循环直到找不到任何 StartZSKJ.exe 进程
    while True:
        pids = []
        for proc in psutil.process_iter(['name', 'pid']):
            try:
                if proc.info['name'].lower() == 'startzskj.exe':
                    pids.append(proc.info['pid'])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        if not pids:
            break
        for pid in pids:
            logger.info(f"Killing StartZSKJ (PID {pid})...")
            try:
                proc = psutil.Process(pid)
                proc.terminate()
                time.sleep(0.5)
                if proc.is_running():
                    proc.kill()
                killed_any = True
            except psutil.NoSuchProcess:
                pass
        # 给系统一点时间，避免漏掉刚产生的子进程
        time.sleep(1)

    # 清理全局 Popen 对象（如果有）
    if zskj_process:
        zskj_process = None

    if killed_any:
        logger.info("All StartZSKJ processes terminated.")
    else:
        logger.warning("No StartZSKJ process found.")
    return killed_any

def start_zskj_thread():
    """在后台线程中启动 StartZSKJ（避免阻塞命令行）"""
    global start_thread
    # 如果已经有线程在运行，先等待它结束（但通常很快）
    if start_thread and start_thread.is_alive():
        logger.info("StartZSKJ launch thread is already running, waiting...")
        start_thread.join(timeout=2)
    # 创建新线程
    start_thread = threading.Thread(target=launch_zskj_launcher, args=(config,))
    start_thread.daemon = True
    start_thread.start()
    logger.info("StartZSKJ launch thread started (non-blocking)")

# 交互式命令处理
def launch_configurator():
    while True:
        command = input("invisibility> ").strip()
        if command == "exit":
            logger.info("Exiting Launcher. StartZSKJ continues running in background.")
            sys.exit(0)
        elif command == "start":
            if is_startzskj_running():
                logger.info("StartZSKJ is already running. No action taken.")
            else:
                logger.info("StartZSKJ not running, launching in background...")
                start_zskj_thread()
                time.sleep(1)  # 给线程一点时间启动（通常很快）
        elif command == "stop":
            stop_startzskj()
        elif command.startswith("set "):
            try:
                _, key, value = command.split(" ", 2)
                config[key] = value
                logger.info(f"Configuration updated: {key} = {value}")
            except ValueError:
                logger.error("Invalid format. Use: set <key> <value>")
        elif command == "upload":
            try:
                with open("Launcher.set", "w", encoding="utf-8") as setf:
                    for key, value in config.items():
                        setf.write(f"{key}={value}\n")
                logger.info("Configuration saved to Launcher.set")
            except Exception as e:
                logger.error(f"Failed to save: {e}")
        elif command == "show":
            print("Current configuration:")
            for key, value in config.items():
                print(f"{key} = {value}")
            if is_startzskj_running():
                pid = get_startzskj_pid()
                print(f"StartZSKJ status: RUNNING (PID {pid})")
            else:
                print("StartZSKJ status: NOT RUNNING")
        elif command == "restart":
            logger.info("Restarting StartZSKJ...")
            stop_startzskj()
            time.sleep(1)  # 确保完全停止
            start_zskj_thread()
            time.sleep(1)  # 给线程一点时间启动（通常很快）
        elif command == "help":
            help_msg = """Minisoft invisibility Launcher and Configurator, version 26.2.0
Commands:
    start               Start StartZSKJ (if not already running)
    stop                Stop StartZSKJ (terminate the process)
    restart             Restart the StartZSKJ
    set <key> <value>   Set a configuration item
    upload              Save current configuration to Launcher.set
    show                Show current configuration and process status
    help                Show this help message
    exit                Exit Launcher (StartZSKJ keeps running)"""
            print(help_msg)
        elif command == "clear":
            if miniapi.IS_WINDOWS:
                os.system("cls")
            else:
                os.system("clear")
        elif command == "":
            continue
        else:
            logger.error("Unknown command. Type 'help' for a list of commands.")

def print_banner():
    banner = r"""
 _            _     _ _     _ _ _ _         
(_)_ ____   _(_)___(_) |__ (_) (_) |_ _   _ 
| | '_ \ \ / / / __| | '_ \| | | | __| | | |
| | | | \ V /| \__ \ | |_) | | | | |_| |_| |
|_|_| |_|\_/ |_|___/_|_.__/|_|_|_|\__|\__, |
                                      |___/ 
                                             
    """
    print(banner)
    print("Minisoft invisibility Launcher and Configurator, version 26.2.0")
    print("License: MIT License\nauthor: Minisoft Team (Douglas Woods, Juno Zhao, etc.)")
    print()  # 空行分隔

if __name__ == "__main__":
    # Launcher 启动时检测 StartZSKJ 是否已在运行
    if is_startzskj_running():
        pid = get_startzskj_pid()
        logger.info(f"StartZSKJ is already running (PID {pid}). Use 'start' command if needed.")
    else:
        logger.info("StartZSKJ is not running. Auto-starting in background...")
        start_zskj_thread()   # 自动启动线程
    time.sleep(1)  # 给线程一点时间启动（通常很快）
    print_banner()  # 显示 Banner 和版本信息
    if "--no-console" in args:
        # 正常启动但不进入交互界面（以免教学电脑每次开机需要关闭配置器）
        logger.info("No console mode enabled. Exiting Launcher.")
        sys.exit(0)
    else:
        # 进入交互界面
        launch_configurator()