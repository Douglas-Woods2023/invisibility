"""
性能监控工具
"""
import time
import functools
from typing import Callable, Any, Optional
import sys
import tracemalloc
from contextlib import contextmanager


class Timer:
    """计时器上下文管理器"""
    
    def __init__(self, name: str = "Operation", logger=None):
        self.name = name
        self.logger = logger
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        if self.logger:
            self.logger.info(f"{self.name} Start...")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        elapsed = self.end_time - self.start_time
        
        if self.logger:
            status = "Completed" if exc_type is None else "Failed"
            self.logger.info(f"{self.name} {status},Time-consuming: {elapsed:.3f} sec")
        else:
            status = "Completed" if exc_type is None else "Failed"
            print(f"{self.name} {status},Time-consuming: {elapsed:.3f} sec")
        
        self.elapsed = elapsed


def timer(name: str = "Operation", logger=None):
    """
    计时器装饰器
    
    Args:
        name: 操作名称
        logger: 日志记录器（可选）
        
    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with Timer(name, logger):
                return func(*args, **kwargs)
        return wrapper
    return decorator


@contextmanager
def benchmark(name: str = "代码块", logger=None):
    """
    基准测试上下文管理器
    
    Args:
        name: 测试名称
        logger: 日志记录器
    """
    start_time = time.time()
    start_memory = tracemalloc.get_traced_memory() if tracemalloc.is_tracing() else (0, 0)
    
    try:
        yield
    finally:
        end_time = time.time()
        end_memory = tracemalloc.get_traced_memory() if tracemalloc.is_tracing() else (0, 0)
        
        elapsed = end_time - start_time
        memory_used = end_memory[1] - start_memory[1]
        
        if logger:
            logger.info(
                f"{name} - Time-consuming: {elapsed:.3f} sec, "
                f"Memory Usage: {memory_used / 1024:.1f} KB"
            )
        else:
            print(
                f"{name} - Time-consuming: {elapsed:.3f} sec, "
                f"Memory Usage: {memory_used / 1024:.1f} KB"
            )


def memory_usage(func: Callable) -> Callable:
    """
    测量函数内存使用的装饰器
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # 开始跟踪内存
        tracemalloc.start()
        
        try:
            result = func(*args, **kwargs)
            
            # 获取内存统计
            current, peak = tracemalloc.get_traced_memory()
            
            print(f"Function {func.__name__} Memory Usage:")
            print(f"  Current: {current / 1024:.1f} KB")
            print(f"  Peak: {peak / 1024:.1f} KB")
            
            return result
        finally:
            tracemalloc.stop()
    
    return wrapper


def profile_code(code: str, name: str = "代码执行"):
    """
    分析一段代码的性能
    
    Args:
        code: 要分析的代码字符串
        name: 分析名称
    """
    import cProfile
    import pstats
    import io
    
    print(f"Performance Analysis: {name}")
    print("=" * 50)
    
    # 创建分析器
    pr = cProfile.Profile()
    pr.enable()
    
    # 执行代码
    exec_globals = {}
    exec(code, exec_globals)
    
    pr.disable()
    
    # 输出结果
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats(20)  # 显示前20个
    
    print(s.getvalue())


__all__ = [
    'Timer',
    'timer',
    'benchmark',
    'memory_usage',
    'profile_code',
]