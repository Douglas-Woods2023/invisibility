"""
日志工具模块
"""
import logging
import sys
from typing import Optional, Dict, Any, Union
from pathlib import Path

from ..core.platform import IS_WINDOWS

# 如果Windows上需要颜色支持
if IS_WINDOWS:
    try:
        import colorama
        colorama.init()
    except ImportError:
        pass


class ColorFormatter(logging.Formatter):
    """带颜色的日志格式化器"""
    
    # ANSI颜色代码
    COLORS = {
        'DEBUG': '\033[36m',      # 青色
        'INFO': '\033[32m',       # 绿色
        'WARNING': '\033[33m',    # 黄色
        'ERROR': '\033[31m',      # 红色
        'CRITICAL': '\033[41m',   # 红底白字
        'RESET': '\033[0m',       # 重置
    }
    
    def format(self, record):
        # 创建原始记录副本，避免修改原始记录
        record_copy = logging.makeLogRecord(record.__dict__)
        
        # 检查是否需要添加颜色
        original_levelname = record_copy.levelname
        
        # 如果级别名称已经被着色，先提取原始级别名称
        # 例如：如果 levelname 是 "\x1b[32mINFO\x1b[0m"，我们需要提取 "INFO"
        import re
        color_pattern = r'\x1b\[[0-9;]*m(.*?)\x1b\[0m'
        match = re.search(color_pattern, original_levelname)
        
        if match:
            # 已经着色，使用提取的原始名称
            clean_levelname = match.group(1)
        else:
            # 未着色，使用原始名称
            clean_levelname = original_levelname
        
        # 给级别名称和消息添加颜色
        if clean_levelname in self.COLORS and clean_levelname != 'RESET':
            color_code = self.COLORS[clean_levelname]
            reset_code = self.COLORS['RESET']
            
            # 只给未着色的部分添加颜色
            if not match:
                record_copy.levelname = f"{color_code}{clean_levelname}{reset_code}"
            
            # 给消息添加颜色（但也要检查消息是否已经着色）
            if not re.search(color_pattern, record_copy.msg):
                record_copy.msg = f"{color_code}{record_copy.msg}{reset_code}"
        
        return super().format(record_copy)


def setup_logger(name: str = "miniapi",
                 level: int = logging.INFO,
                 log_file: Optional[Union[str, Path]] = None,
                 use_colors: bool = True,
                 format_string: Optional[str] = None) -> logging.Logger:
    """
    设置并返回配置好的日志记录器
    
    Args:
        name: 日志记录器名称
        level: 日志级别
        log_file: 日志文件路径（可选）
        use_colors: 是否在控制台使用颜色
        format_string: 自定义格式字符串
        
    Returns:
        logging.Logger: 配置好的日志记录器
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 避免重复添加处理器
    if logger.handlers:
        return logger
    
    # 默认格式
    if format_string is None:
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    formatter = logging.Formatter(format_string)
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    if use_colors and not IS_WINDOWS:
        # Windows控制台颜色需要额外处理
        console_handler.setFormatter(ColorFormatter(format_string))
    else:
        console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 文件处理器（如果指定了日志文件）
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def color_logger(name: str = "miniapi") -> logging.Logger:
    """
    快速获取带颜色的日志记录器
    """
    return setup_logger(name, use_colors=True)


def get_logger(name: str = "miniapi") -> logging.Logger:
    """
    获取日志记录器（如果未配置则使用默认配置）
    """
    logger = logging.getLogger(name)
    
    # 如果还没有配置处理器，使用默认配置
    if not logger.handlers:
        setup_logger(name)
    
    return logger


__all__ = [
    'setup_logger',
    'color_logger',
    'get_logger',
    'ColorFormatter',
]