"""
进程管理模块 - 安全执行系统命令
"""
import subprocess
import shlex
import sys
import time
from typing import List, Union, Optional, Dict, Any
from dataclasses import dataclass
from pathlib import Path
import os

from ..core.exceptions import ProcessError
from ..core.platform import IS_WINDOWS


@dataclass
class CommandResult:
    """命令执行结果"""
    success: bool
    returncode: int
    stdout: str
    stderr: str
    command: str
    execution_time: float
    pid: Optional[int] = None
    
    @property
    def output(self) -> str:
        """获取合并的输出（stdout + stderr）"""
        return self.stdout + (("\n" + self.stderr) if self.stderr else "")
    
    def raise_if_failed(self):
        """如果执行失败则抛出异常"""
        if not self.success:
            raise ProcessError(
                f"Command execution failed (code={self.returncode}): {self.command}\n"
                f"Error Output: {self.stderr}"
            )


def run_safe(command: Union[str, List[str]], 
             cwd: Optional[Union[str, Path]] = None,
             env: Optional[Dict[str, str]] = None,
             timeout: Optional[float] = None,
             capture_output: bool = True,
             shell: bool = False,
             encoding: str = "utf-8",
             errors: str = "replace",
             check: bool = True) -> CommandResult:
    """
    安全执行系统命令（跨平台）
    
    Args:
        command: 要执行的命令（字符串或列表）
        cwd: 工作目录
        env: 环境变量
        timeout: 超时时间（秒）
        capture_output: 是否捕获输出
        shell: 是否使用shell执行（不推荐，有安全风险）
        encoding: 输出编码
        errors: 编码错误处理方式
        check: 如果命令失败是否抛出异常
        
    Returns:
        CommandResult: 命令执行结果
        
    Example:
        >>> result = run_safe(["python", "--version"])
        >>> result = run_safe("ls -la", shell=True)  # 不推荐
    """
    start_time = time.time()
    
    try:
        # 处理命令参数
        if isinstance(command, str):
            if shell:
                # 使用shell执行字符串命令
                cmd_args = command
            else:
                # 在POSIX系统上使用shlex分割，Windows上简单分割
                if IS_WINDOWS:
                    cmd_args = command.split()
                else:
                    cmd_args = shlex.split(command)
        else:
            # 已经是列表形式
            cmd_args = command
            if shell:
                # 对于shell=True，需要将列表转换为字符串
                cmd_args = " ".join(str(arg) for arg in command)
        
        # 准备执行参数
        kwargs = {
            'cwd': str(cwd) if cwd else None,
            'env': env,
            'timeout': timeout,
            'shell': shell,
        }
        
        if capture_output:
            kwargs.update({
                'stdout': subprocess.PIPE,
                'stderr': subprocess.PIPE,
                'text': True,
                'encoding': encoding,
                'errors': errors,
            })
        else:
            kwargs.update({
                'stdout': subprocess.DEVNULL,
                'stderr': subprocess.DEVNULL,
            })
        
        # 执行命令
        process = subprocess.run(cmd_args, **kwargs)
        
        execution_time = time.time() - start_time
        
        # 构建结果对象
        stdout = process.stdout if capture_output else ""
        stderr = process.stderr if capture_output else ""
        
        # 安全地获取PID（兼容Python 3.6）
        pid = None
        try:
            # Python 3.7+ 有 pid 属性
            if hasattr(process, 'pid'):
                pid = process.pid
        except AttributeError:
            # Python 3.6 或更早版本
            pass
        
        result = CommandResult(
            success=process.returncode == 0,
            returncode=process.returncode,
            stdout=stdout.strip() if stdout else "",
            stderr=stderr.strip() if stderr else "",
            command=str(command),
            execution_time=execution_time,
            pid=pid,
        )
        
        # 如果 check 为 True 且命令失败，抛出异常
        if check and not result.success:
            result.raise_if_failed()
        
        return result
        
    except subprocess.TimeoutExpired as e:
        execution_time = time.time() - start_time
        raise ProcessError(
            f"Command execution timed out ({timeout}sec ): {command}\n"
            f"Elapsed Time: {execution_time:.2f}sec"
        )
    except FileNotFoundError as e:
        raise ProcessError(f"Command not found: {command}\nPlease ensure the command is installed and in PATH")
    except Exception as e:
        raise ProcessError(f"Error executing command {command}: {str(e)}")


def run_capture(command: Union[str, List[str]], **kwargs) -> str:
    """
    执行命令并返回标准输出（简化版）
    
    Args:
        command: 要执行的命令
        **kwargs: 传递给run_safe的额外参数
        
    Returns:
        str: 命令的标准输出
        
    Example:
        >>> output = run_capture(["python", "--version"])
    """
    result = run_safe(command, capture_output=True, **kwargs)
    return result.stdout.strip()


def run_background(command: Union[str, List[str]], 
                   cwd: Optional[Union[str, Path]] = None,
                   env: Optional[Dict[str, str]] = None) -> subprocess.Popen:
    """
    在后台执行命令（不等待完成）
    
    Args:
        command: 要执行的命令
        cwd: 工作目录
        env: 环境变量
        
    Returns:
        subprocess.Popen: 进程对象，可用于后续控制
    """
    try:
        if isinstance(command, str):
            if IS_WINDOWS:
                cmd_args = command
            else:
                cmd_args = shlex.split(command)
        else:
            cmd_args = command
        
        process = subprocess.Popen(
            cmd_args,
            cwd=str(cwd) if cwd else None,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            start_new_session=True,  # 创建新的进程组
        )
        
        return process
    except Exception as e:
        raise ProcessError(f"Unable to start background process {command}: {str(e)}")


def command_exists(command: str) -> bool:
    """
    检查命令是否存在
    
    Args:
        command: 命令名称
        
    Returns:
        bool: 命令是否存在
    """
    try:
        if IS_WINDOWS:
            # Windows上检查命令是否存在
            result = run_safe(["where", command], capture_output=True, shell=True, check=False)
            return result.success and result.stdout.strip() != ""
        else:
            # Unix-like系统上使用which
            result = run_safe(["which", command], capture_output=True, check=False)
            return result.success
    except:
        return False


def find_executable(name: str, paths: Optional[List[str]] = None) -> Optional[Path]:
    """
    查找可执行文件的完整路径
    
    Args:
        name: 可执行文件名称
        paths: 要搜索的路径列表，默认为系统PATH
        
    Returns:
        Optional[Path]: 找到的可执行文件路径，未找到则返回None
    """
    if paths is None:
        # 获取系统PATH
        path_str = os.environ.get('PATH', '')
        paths = path_str.split(os.pathsep)
    
    # 添加可能的扩展名（Windows）
    possible_names = [name]
    if IS_WINDOWS:
        possible_names.extend([f"{name}.exe", f"{name}.bat", f"{name}.cmd"])
    
    for path_dir in paths:
        for possible_name in possible_names:
            exe_path = Path(path_dir) / possible_name
            if exe_path.is_file():
                # 检查是否可执行
                try:
                    os.access(exe_path, os.X_OK)
                    return exe_path
                except:
                    continue
    
    return None


# 简写别名
run = run_safe
sh = run_capture  # 类似于Shell执行


# 导出所有函数和类
__all__ = [
    'CommandResult',
    'run_safe',
    'run_capture',
    'run_background',
    'command_exists',
    'find_executable',
    'run',
    'sh',
]