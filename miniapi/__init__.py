"""
Minisoft Python API（miniapi）是一个可以让你的 Python 源代码在任何平台上顺利运行的库。
使用它，你的 Python 源代码可以在任何平台上运行且无需修改。
"""
__version__ = "1.0-1"
__author__ = "Minisoft Team, Douglas Woods"
__license__ = "MIT"

from .core.platform import (
    #平台检测
    IS_WINDOWS,
    IS_LINUX,
    IS_MACOS,
    IS_UNIX,

    #平台信息
    platform_name,
    platform_version,

    #路径处理
    path_separator,
    normalize_path,

    #路径获取
    get_home_dir,
    get_config_dir,
    get_cache_dir,

    #适配器
    platform,
)

# 文件操作 - 优雅的API设计
from .files.operations import (
    # 基本操作
    safe_remove,
    safe_copy,
    safe_move,
    safe_mkdir,
    
    # 查找操作
    find_files,
    find_in_files,
    
    # 批量操作
    bulk_remove,
    bulk_copy,
    
    # 别名（为了兼容性和便利）
    rm,
    cp,
    mv,
    mkdir,
)

# 进程管理
from .process.subprocess import (
    # 安全执行
    run_safe,
    run_capture,
    run_background,
    
    # 结果处理
    CommandResult,
    
    # 工具函数
    command_exists,
    find_executable,
    
    # 别名
    run,
    sh,
)

# 网络工具
from .network.http import (
    fetch,
    download,
    upload,
    tqdm_download,
    GUI_download,
)

# 实用工具
from .utils.logging import (
    setup_logger,
    color_logger,
    get_logger,
)

from .utils.performance import (
    timer,
    benchmark,
    memory_usage,
)

# 兼容性装饰器
from .core.compat import (
    deprecated_os_system,
    platform_specific,
    crossplatform_only,
)

# 异常
from .core.exceptions import (
    MiniapiError,
    PlatformError,
    FileOperationError,
    ProcessError,
)

# 导出所有公共API
__all__ = [
    # 平台信息
    'IS_WINDOWS', 'IS_LINUX', 'IS_MACOS', 'IS_UNIX',
    'platform_name', 'platform_version',
    'path_separator', 'normalize_path',
    'get_home_dir', 'get_config_dir', 'get_cache_dir',
    'Platform',
    
    # 文件操作
    'safe_remove', 'safe_copy', 'safe_move', 'safe_mkdir',
    'find_files', 'find_in_files',
    'bulk_remove', 'bulk_copy',
    'rm', 'cp', 'mv', 'mkdir',
    
    # 进程管理
    'run_safe', 'run_capture', 'run_background',
    'CommandResult',
    'command_exists', 'find_executable',
    'run', 'sh',
    
    # 网络
    'fetch', 'download', 'upload',
    
    # 工具
    'setup_logger', 'color_logger', 'get_logger',
    'timer', 'benchmark', 'memory_usage',
    
    # 装饰器
    'deprecated_os_system', 'platform_specific', 'crossplatform_only',
    
    # 异常
    'MiniapiError', 'PlatformError', 'FileOperationError', 'ProcessError',
]