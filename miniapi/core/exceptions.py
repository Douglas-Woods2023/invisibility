"""
Miniapi自定义异常类
"""


class MiniapiError(Exception):
    """所有Miniapi异常的基类"""
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message
    
    def __str__(self):
        return self.message


class PlatformError(MiniapiError):
    """平台相关错误"""
    pass


class FileOperationError(MiniapiError):
    """文件操作错误"""
    pass


class ProcessError(MiniapiError):
    """进程执行错误"""
    def __init__(self, message: str, command: str = "", exit_code: int = None):
        if command:
            message = f"An error occurred while executing the command '{command}': {message}"
        super().__init__(message)
        self.command = command
        self.exit_code = exit_code


class ValidationError(MiniapiError):
    """数据验证错误"""
    pass


class ConfigurationError(MiniapiError):
    """配置错误"""
    pass


class NetworkError(MiniapiError):
    """网络错误"""
    pass


__all__ = [
    'MiniapiError',
    'PlatformError',
    'FileOperationError',
    'ProcessError',
    'ValidationError',
    'ConfigurationError',
    'NetworkError',
]