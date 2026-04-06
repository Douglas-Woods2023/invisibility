"""
兼容性装饰器和工具，帮助迁移旧代码
"""
import warnings
import functools
import inspect
from typing import Callable, Any, Optional

from .platform import IS_WINDOWS, IS_LINUX


def deprecated_os_system(message: str = ""):
    """
    装饰器：标记使用os.system的函数，并发出警告
    
    Args:
        message: 额外的警告信息
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            warnings.warn(
                f"Function {func.__name__} a platform-specific system call was used."
                f"Recommended to use miniapi.run_safe() substitute.{message}",
                DeprecationWarning,
                stacklevel=2
            )
            return func(*args, **kwargs)
        return wrapper
    return decorator


def platform_specific(platforms: list):
    """
    装饰器：标记函数只能在特定平台上运行
    
    Args:
        platforms: 支持的平台列表，如 ["linux", "macos"]
    """
    platform_names = {
        "windows": IS_WINDOWS,
        "linux": IS_LINUX,
        "macos": not IS_WINDOWS and not IS_LINUX,
    }
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 检查当前平台是否支持
            supported = any(platform_names.get(p.lower(), False) for p in platforms)
            if not supported:
                current_platform = "windows" if IS_WINDOWS else "linux" if IS_LINUX else "macos"
                raise RuntimeError(
                    f"Function {func.__name__} can only run at {platforms},"
                    f"current platform: {current_platform}"
                )
            return func(*args, **kwargs)
        
        # 添加平台信息到函数属性
        wrapper.__platform_specific__ = platforms
        return wrapper
    return decorator


def crossplatform_only(func: Callable) -> Callable:
    """
    装饰器：确保函数是跨平台的，如果不是则发出警告
    
    通过检查函数内部是否使用了平台特定的代码
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # 获取函数源代码（如果可用）
        try:
            source = inspect.getsource(func)
            
            # 检查常见的平台特定代码模式
            platform_patterns = [
                "os.system",
                "subprocess.call",
                "subprocess.run",
                "shlex.split",
            ]
            
            for pattern in platform_patterns:
                if pattern in source:
                    warnings.warn(
                        f"Function {func.__name__} may contain platform-specific code."
                        "Please ensure the code works on all platforms.",
                        RuntimeWarning,
                        stacklevel=2
                    )
                    break
                    
        except (OSError, TypeError):
            # 无法获取源代码，跳过检查
            pass
        
        return func(*args, **kwargs)
    
    return wrapper


def linux_only(func: Callable) -> Callable:
    """装饰器：标记函数只能在Linux上运行"""
    return platform_specific(["linux"])(func)


def windows_only(func: Callable) -> Callable:
    """装饰器：标记函数只能在Windows上运行"""
    return platform_specific(["windows"])(func)


def macos_only(func: Callable) -> Callable:
    """装饰器：标记函数只能在macOS上运行"""
    return platform_specific(["macos"])(func)


__all__ = [
    'deprecated_os_system',
    'platform_specific',
    'crossplatform_only',
    'linux_only',
    'windows_only',
    'macos_only',
]