"""
miniapi 核心模块
"""

# 从 platform 模块导入具体的符号，而不是导入整个模块
from .platform import (
    IS_WINDOWS,
    IS_LINUX,
    IS_MACOS,
    IS_UNIX,
    platform_name,
    platform_version,
    path_separator,
    normalize_path,
    get_home_dir,
    get_config_dir,
    get_cache_dir,
    Platform,
    platform,  # Platform 类的单例实例
)

# 从 exceptions 模块导入
from .exceptions import (
    MiniapiError,
    PlatformError,
    FileOperationError,
    ProcessError,
    ValidationError,
    ConfigurationError,
    NetworkError,
)

# 从 compat 模块导入
from .compat import (
    deprecated_os_system,
    platform_specific,
    crossplatform_only,
    linux_only,
    windows_only,
    macos_only,
)

# 定义 __all__ 列表
__all__ = [
    # 平台相关
    'IS_WINDOWS', 'IS_LINUX', 'IS_MACOS', 'IS_UNIX',
    'platform_name', 'platform_version', 'path_separator', 'normalize_path',
    'get_home_dir', 'get_config_dir', 'get_cache_dir',
    'Platform', 'platform',
    
    # 异常
    'MiniapiError', 'PlatformError', 'FileOperationError', 'ProcessError',
    'ValidationError', 'ConfigurationError', 'NetworkError',
    
    # 兼容性工具
    'deprecated_os_system', 'platform_specific', 'crossplatform_only',
    'linux_only', 'windows_only', 'macos_only',
]