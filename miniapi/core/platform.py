import sys
import os
import platform as std_platform
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass

# 平台常量 - 快速检测
IS_WINDOWS = sys.platform == "win32"
IS_LINUX = "linux" in sys.platform.lower()
IS_MACOS = sys.platform == "darwin"
IS_UNIX = not IS_WINDOWS

@dataclass
class PlatformInfo:
    """平台信息数据类"""
    name: str
    version: str
    architecture: str
    release: str
    machine: str

class Platform:
    """平台适配器 - 单例模式"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._info = self._detect_platform()
        self._paths = self._setup_paths()
        self._initialized = True
    
    def _detect_platform(self) -> PlatformInfo:
        """检测平台信息"""
        return PlatformInfo(
            name=std_platform.system(),
            version=std_platform.version(),
            architecture=std_platform.architecture()[0],
            release=std_platform.release(),
            machine=std_platform.machine(),
        )
    
    def _setup_paths(self) -> Dict[str, Path]:
        """设置平台特定的路径"""
        home = Path.home()
        
        if IS_WINDOWS:
            paths = {
                'home': home,
                'config': home / 'AppData' / 'Local',
                'cache': home / 'AppData' / 'Local' / 'Temp',
                'data': home / 'AppData' / 'Roaming',
            }
        elif IS_MACOS:
            paths = {
                'home': home,
                'config': home / 'Library' / 'Application Support',
                'cache': home / 'Library' / 'Caches',
                'data': home / 'Library' / 'Application Support',
            }
        else:  # Linux和其他Unix
            paths = {
                'home': home,
                'config': home / '.config',
                'cache': home / '.cache',
                'data': home / '.local' / 'share',
            }
        
        return paths
    
    @property
    def info(self) -> PlatformInfo:
        """获取平台信息"""
        return self._info
    
    @property
    def name(self) -> str:
        """友好的平台名称"""
        name_map = {
            'Windows': 'Windows',
            'Linux': 'Linux',
            'Darwin': 'macOS',
        }
        return name_map.get(self._info.name, self._info.name)
    
    @property
    def is_windows(self) -> bool:
        return IS_WINDOWS
    
    @property
    def is_linux(self) -> bool:
        return IS_LINUX
    
    @property
    def is_macos(self) -> bool:
        return IS_MACOS
    
    @property
    def is_unix(self) -> bool:
        return IS_UNIX
    
    def path(self, key: str) -> Path:
        """获取平台特定路径"""
        return self._paths.get(key, Path())
    
    def env_var(self, name: str, default: Any = None) -> Any:
        """安全的获取环境变量"""
        return os.environ.get(name, default)
    
    def line_separator(self) -> str:
        """获取行分隔符"""
        return '\r\n' if IS_WINDOWS else '\n'
    
    def path_separator(self) -> str:
        """获取路径分隔符"""
        return ';' if IS_WINDOWS else ':'
    
    def normalize_path(self, path: str) -> str:
        """标准化路径（跨平台）"""
        path_obj = Path(path)
        if IS_WINDOWS:
            # Windows下保留大小写但不区分
            return str(path_obj).replace('/', '\\')
        else:
            # Unix系统保持原样
            return str(path_obj)

# 创建全局实例
platform = Platform()

# 导出便捷函数
def platform_name() -> str:
    return platform.name

def platform_version() -> str:
    return platform.info.version

def path_separator() -> str:
    return platform.path_separator()

def normalize_path(path: str) -> str:
    return platform.normalize_path(path)

def get_home_dir() -> Path:
    return platform.path('home')

def get_config_dir(app_name: Optional[str] = None) -> Path:
    base = platform.path('config')
    if app_name:
        return base / app_name
    return base

def get_cache_dir(app_name: Optional[str] = None) -> Path:
    base = platform.path('cache')
    if app_name:
        return base / app_name
    return base

__all__ = [
    'IS_WINDOWS',
    'IS_LINUX',
    'IS_MACOS',
    'IS_UNIX',
    'platform_name',
    'platform_version',
    'path_separator',
    'normalize_path',
    'get_home_dir',
    'get_config_dir',
    'get_cache_dir',
    'platform',
]