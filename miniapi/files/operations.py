"""
文件操作模块 - 提供跨平台的文件系统操作
"""
import os
import shutil
import stat
import tempfile
from pathlib import Path
from typing import List, Union, Optional, Generator
from datetime import datetime
import fnmatch
import hashlib

from ..core.exceptions import FileOperationError
from ..core.platform import IS_WINDOWS


def safe_remove(path: Union[str, Path], recursive: bool = True) -> bool:
    """
    安全删除文件或目录（跨平台）
    
    Args:
        path: 要删除的路径
        recursive: 是否递归删除目录
        
    Returns:
        bool: 是否成功删除（如果文件不存在则返回True）
    
    Example:
        >>> safe_remove("./cache")  # 删除目录
        >>> safe_remove("file.txt")  # 删除文件
    """
    try:
        path_obj = Path(path)
        
        # 如果路径不存在，返回True（视为成功）
        if not path_obj.exists():
            return True
        
        # 如果是只读文件（Windows），先修改权限
        if IS_WINDOWS:
            try:
                os.chmod(path, stat.S_IWRITE)
            except:
                pass  # 如果无法修改权限，继续尝试删除
        
        # 如果是目录
        if path_obj.is_dir():
            if recursive:
                shutil.rmtree(path_obj, ignore_errors=True)
            else:
                path_obj.rmdir()  # 空目录才可删除
        else:
            # 删除文件
            path_obj.unlink()
            
        return True
        
    except (OSError, PermissionError, FileNotFoundError) as e:
        raise FileOperationError(f"Cannot delete file {path}: {e}")


def safe_copy(src: Union[str, Path], dst: Union[str, Path], 
              overwrite: bool = True, preserve_metadata: bool = True) -> bool:
    """
    安全复制文件或目录（跨平台）
    
    Args:
        src: 源路径
        dst: 目标路径
        overwrite: 是否覆盖已存在文件
        preserve_metadata: 是否保留元数据（修改时间、权限等）
        
    Returns:
        bool: 是否成功复制
    """
    try:
        src_path = Path(src)
        dst_path = Path(dst)
        
        if not src_path.exists():
            raise FileOperationError(f"The source file does not exist: {src}")
        
        # 如果是目录
        if src_path.is_dir():
            if dst_path.exists() and not overwrite:
                raise FileOperationError(f"The target directory already exists: {dst}")
            
            if preserve_metadata:
                shutil.copytree(src_path, dst_path, dirs_exist_ok=overwrite)
            else:
                # 简单复制，不保留元数据
                shutil.copytree(src_path, dst_path, dirs_exist_ok=overwrite,
                              copy_function=shutil.copy)
        else:
            # 如果是文件
            if dst_path.exists():
                if not overwrite:
                    raise FileOperationError(f"The target file already exists: {dst}")
                # 确保父目录存在
                dst_path.parent.mkdir(parents=True, exist_ok=True)
            
            if preserve_metadata:
                shutil.copy2(src_path, dst_path)
            else:
                shutil.copy(src_path, dst_path)
        
        return True
        
    except (shutil.Error, OSError, IOError) as e:
        raise FileOperationError(f"Copy failed {src} -> {dst}: {e}")


def safe_move(src: Union[str, Path], dst: Union[str, Path], 
              overwrite: bool = True) -> bool:
    """
    安全移动文件或目录（跨平台）
    
    Args:
        src: 源路径
        dst: 目标路径
        overwrite: 是否覆盖已存在文件
        
    Returns:
        bool: 是否成功移动
    """
    try:
        src_path = Path(src)
        dst_path = Path(dst)
        
        if not src_path.exists():
            raise FileOperationError(f"The source file does not exist: {src}")
        
        # 如果目标存在
        if dst_path.exists():
            if overwrite:
                safe_remove(dst_path)  # 先删除目标
            else:
                raise FileOperationError(f"The target file already exists: {dst}")
        
        # 移动文件或目录
        shutil.move(str(src_path), str(dst_path))
        return True
        
    except (shutil.Error, OSError) as e:
        raise FileOperationError(f"Move failed {src} -> {dst}: {e}")


def safe_mkdir(path: Union[str, Path], parents: bool = True, 
               exist_ok: bool = True) -> Path:
    """
    安全创建目录（跨平台）
    
    Args:
        path: 目录路径
        parents: 是否创建父目录
        exist_ok: 目录已存在是否不报错
        
    Returns:
        Path: 创建的目录路径对象
    """
    try:
        path_obj = Path(path)
        path_obj.mkdir(parents=parents, exist_ok=exist_ok)
        return path_obj
    except (OSError, PermissionError) as e:
        raise FileOperationError(f"Failed to create directory {path}: {e}")


def find_files(pattern: str, root_dir: Union[str, Path] = ".", 
               recursive: bool = True, case_sensitive: bool = None) -> List[Path]:
    """
    查找匹配模式的文件（跨平台glob）
    
    Args:
        pattern: 匹配模式，如 "*.py" 或 "**/*.txt"
        root_dir: 搜索根目录
        recursive: 是否递归搜索子目录
        case_sensitive: 是否区分大小写（None=自动根据平台决定）
        
    Returns:
        List[Path]: 匹配的文件路径列表
    """
    root = Path(root_dir)
    
    # 确定是否区分大小写
    if case_sensitive is None:
        # Linux通常区分大小写，Windows和macOS通常不区分
        case_sensitive = not IS_WINDOWS
    
    results = []
    
    if recursive and "**" not in pattern:
        pattern = "**/" + pattern
    
    for file_path in root.rglob(pattern) if recursive else root.glob(pattern):
        if file_path.is_file():
            # 处理大小写敏感
            if not case_sensitive:
                # 转换为小写比较
                if fnmatch.fnmatch(file_path.name.lower(), pattern.lower()):
                    results.append(file_path)
            else:
                results.append(file_path)
    
    return sorted(results)


def find_in_files(pattern: str, root_dir: Union[str, Path] = ".", 
                  file_pattern: str = "*", recursive: bool = True,
                  encoding: str = "utf-8", ignore_errors: bool = True) -> List[dict]:
    """
    在文件中搜索文本（跨平台grep功能）
    
    Args:
        pattern: 要搜索的文本模式
        root_dir: 搜索根目录
        file_pattern: 文件匹配模式，如 "*.py"
        recursive: 是否递归搜索子目录
        encoding: 文件编码
        ignore_errors: 是否忽略读取错误
        
    Returns:
        List[dict]: 匹配结果列表，每个元素包含文件路径、行号和内容
    """
    root = Path(root_dir)
    files = find_files(file_pattern, root, recursive)
    results = []
    
    for file_path in files:
        try:
            with open(file_path, 'r', encoding=encoding, errors='ignore' if ignore_errors else 'strict') as f:
                for line_num, line in enumerate(f, 1):
                    if pattern in line:
                        results.append({
                            'file': file_path,
                            'line': line_num,
                            'content': line.rstrip('\n\r'),
                            'match': pattern
                        })
        except (UnicodeDecodeError, IOError, PermissionError) as e:
            if not ignore_errors:
                raise FileOperationError(f"Failed to read file {file_path}: {e}")
    
    return results


def bulk_remove(paths: List[Union[str, Path]], recursive: bool = True) -> dict:
    """
    批量删除文件或目录
    
    Args:
        paths: 要删除的路径列表
        recursive: 是否递归删除目录
        
    Returns:
        dict: 删除结果统计
    """
    results = {
        'success': 0,
        'failed': 0,
        'errors': []
    }
    
    for path in paths:
        try:
            if safe_remove(path, recursive):
                results['success'] += 1
            else:
                results['failed'] += 1
                results['errors'].append(f"Failed to remove: {path}")
        except Exception as e:
            results['failed'] += 1
            results['errors'].append(f"Failed to remove {path}: {e}")
    
    return results


def bulk_copy(src_dst_pairs: List[tuple], overwrite: bool = True) -> dict:
    """
    批量复制文件
    
    Args:
        src_dst_pairs: (源路径, 目标路径) 元组列表
        overwrite: 是否覆盖已存在文件
        
    Returns:
        dict: 复制结果统计
    """
    results = {
        'success': 0,
        'failed': 0,
        'errors': []
    }
    
    for src, dst in src_dst_pairs:
        try:
            if safe_copy(src, dst, overwrite):
                results['success'] += 1
            else:
                results['failed'] += 1
                results['errors'].append(f"Failed to copy: {src} -> {dst}")
        except Exception as e:
            results['failed'] += 1
            results['errors'].append(f"Failed to copy {src} -> {dst}: {e}")
    
    return results


def get_file_hash(filepath: Union[str, Path], algorithm: str = "md5") -> str:
    """
    计算文件哈希值
    
    Args:
        filepath: 文件路径
        algorithm: 哈希算法，如 "md5", "sha1", "sha256"
        
    Returns:
        str: 文件的哈希值
    """
    try:
        hash_func = getattr(hashlib, algorithm)()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_func.update(chunk)
        return hash_func.hexdigest()
    except (IOError, FileNotFoundError) as e:
        raise FileOperationError(f"Failed to calculate file hash {filepath}: {e}")


# 简写别名
rm = safe_remove
cp = safe_copy
mv = safe_move
mkdir = safe_mkdir


# 导出所有函数
__all__ = [
    'safe_remove', 'safe_copy', 'safe_move', 'safe_mkdir',
    'find_files', 'find_in_files',
    'bulk_remove', 'bulk_copy',
    'get_file_hash',
    'rm', 'cp', 'mv', 'mkdir',
]