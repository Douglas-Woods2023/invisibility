"""
HTTP请求处理模块
"""
import requests
from pathlib import Path
from typing import Union, Dict, Any, Optional
from tqdm import tqdm
import sys
import threading
import tkinter as tk
from tkinter import ttk
from ..core.exceptions import NetworkError
import tkinter.messagebox as msgbox

class DummyFile:
    def write(self, x):
        pass
    def flush(self):
        pass

def upload(Url: str, FilePath: Union[str, Path], data: Optional[Dict[str, Any]] = None) -> requests.Response:
    '''
    用于POST上传文件以及提交参数

    Args:
        Url: 上传接口
        FilePath: 文件路径
        data: 提交参数 {'key':'value', 'key2':'value2'}

    Returns:
        requests.Response: 服务器响应对象
    
    Examples:
        >>> response = UpFile("http://example.com/upload", "/path/to/file.txt", {'param1': 'value1'})
    '''
    files = {'file': open(FilePath, 'rb')}
    result = requests.post(Url, files=files, data=data)
    return result

def download(Url: str, SavePath: Union[str, Path], params: Optional[Dict[str, Any]] = None) -> None:
    '''
    用于GET下载文件并保存到本地

    Args:
        Url: 下载链接
        SavePath: 保存路径
        params: URL参数 {'key':'value', 'key2':'value2'}

    Returns:
        None
    
    Examples:
        >>> Download("http://example.com/file.txt", "/path/to/save/file.txt", {'param1': 'value1'})
    '''
    try:
        response = requests.get(Url, params=params, stream=True)
        response.raise_for_status()  # 确保请求成功

        with open(SavePath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return None
    except requests.RequestException as e:
        raise NetworkError(f"Download failed: {e}")
    except Exception as e:
        raise NetworkError(f"Download failed: {e}")

def fetch(Url: str, method: str = "GET", data: Optional[Dict[str, Any]] = None,
          headers: Optional[Dict[str, str]] = None, timeout: int = 10) -> requests.Response:
    '''
    通用HTTP请求函数，支持GET和POST方法

    Args:
        Url: 请求链接
        method: 请求方法 ("GET" 或 "POST")
        data: 提交参数 {'key':'value', 'key2':'value2'}
        headers: 自定义请求头 {'Header-Key':'Header-Value'}
        timeout: 请求超时时间（秒）
    Returns:
        requests.Response: 服务器响应对象
    Examples:
        >>> response = fetch("http://example.com/api", method="POST", data={'param1': 'value1'})
    '''
    method = method.upper()
    if method == "GET":
        response = requests.get(Url, params=data, headers=headers, timeout=timeout)
    elif method == "POST":
        response = requests.post(Url, data=data, headers=headers, timeout=timeout)
    else:
        raise ValueError("Unsupported HTTP method: {}".format(method))
    return response

def tqdm_download(url: str, path: Union[str, Path], params: Optional[Dict[str, Any]] = None) -> int:
    """
    下载文件并显示 tqdm 进度条。

    Args:
        url (str): 文件下载链接。
        path (str or Path): 文件保存路径。
        params (dict, optional): 请求参数。
    Returns:
        int: 下载结果，0表示成功，1表示失败。
    Examples:
        >>> result = tqdm_download("http://example.com/file.zip", "/path/to/save/file.zip")
        >>> result = tqdm_download("http://example.com/file.zip", "/path/to/save/file.zip", params={'key': 'value'})
    """
    try:
        with requests.get(url, params=params, stream=True, timeout=30) as response:
            response.raise_for_status()
            total = response.headers.get('content-length')
            if total is None:
                # 无法获取总大小，使用不显示总量的 tqdm；设置 miniters=1 保证频繁刷新
                with open(path, 'wb') as f, tqdm(unit='B', unit_scale=True, unit_divisor=1024,
                                                miniters=1, dynamic_ncols=True, file=sys.stdout) as bar:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                            bar.update(len(chunk))
                            try:
                                bar.refresh()
                            except Exception as e:
                                raise NetworkError(f"Failed to refresh progress bar: {e}")
            else:
                total = int(total)
                with open(path, 'wb') as f, tqdm(total=total, unit='B', unit_scale=True, unit_divisor=1024,
                                                miniters=1, dynamic_ncols=True, file=sys.stdout) as bar:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                            bar.update(len(chunk))
                            try:
                                bar.refresh()
                            except Exception as e:
                                raise NetworkError(f"Failed to refresh progress bar: {e}")
        a = 0
    except Exception as e:
        # 下载出错，返回 1
        a = 1
        raise NetworkError(f"Download failed: {e}")
    return a

def GUI_download(url: str, path: Union[str, Path], params: Optional[Dict[str, Any]] = None, parent: Union[tk.Tk, tk.Toplevel] = None) -> int:
    """
    下载文件并显示简单的文本进度。

    Args:
        url (str): 文件下载链接。
        path (str or Path): 文件保存路径。
        params (dict, optional): 请求参数。
        parent (tk.Tk or tk.Toplevel, optional): 父窗口。
    Returns:
        None
    Examples:
        >>> result = GUI_download("http://example.com/file.zip", "/path/to/save/file.zip")
        >>> result = GUI_download("http://example.com/file.zip", "/path/to/save/file.zip", params={'key': 'value'})
        >>> result = GUI_download("http://example.com/file.zip", "/path/to/save/file.zip", parent=root)
    """
    #  创建修复窗口
    dl = tk.Toplevel(parent)
    dl.title("正在下载...")
    dl.geometry("450x180")  # 增加宽度以容纳更多信息
    dl.transient(parent)
    dl.grab_set()
        
    # 创建进度组件
    tk.Label(dl, text="文件下载进度:", font=("微软雅黑", 10)).pack(pady=(10, 0))
    
    # 添加百分比标签
    percent_var = tk.StringVar(value="0.0%")
    percent_label = tk.Label(dl, textvariable=percent_var, font=("微软雅黑", 12, "bold"))
    percent_label.pack(pady=(5, 0))
        
    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(dl, variable=progress_var, maximum=100)
    progress_bar.pack(fill='x', padx=20, pady=5)
        
    label_var = tk.StringVar(value="准备中...")
    status_label = tk.Label(dl, textvariable=label_var, font=("微软雅黑", 9))
    status_label.pack(pady=5)
        
    # 添加操作标签显示当前操作
    current_action = tk.StringVar(value="")
    action_label = tk.Label(dl, textvariable=current_action, font=("微软雅黑", 9))
    action_label.pack(pady=5)
        
    # 绑定进度变化事件以更新百分比显示
    def update_percent(*args):
        value = progress_var.get()
        percent_var.set(f"{value:.1f}%")
        
    progress_var.trace_add("write", update_percent)

    def download_g(url, path, root=None, progress_var=None, label_var=None):
        try:
            resp = requests.get(url, stream=True)
            # 获取文件大小
            file_size = int(resp.headers['content-length'])
            
            # 创建自定义的Tkinter集成进度条类
            class TkinterTqdm(tqdm):
                def __init__(self, *args, **kwargs):
                    self.root = kwargs.pop('root', None)
                    self.progress_var = kwargs.pop('progress_var', None)
                    self.label_var = kwargs.pop('label_var', None)
                    kwargs['file'] = DummyFile()
                    super().__init__(*args, **kwargs)
                    
                def display(self, **kwargs):
                    super().display(**kwargs)
                    if self.root and self.progress_var and self.label_var:
                        def _update_gui():
                            try:
                                # 计算进度百分比并更新变量（在主线程执行）
                                if self.total and self.total > 0:
                                    progress_value = min(100.0, max(0.0, self.n / self.total * 100))
                                    self.progress_var.set(progress_value)

                                # 转换为MB单位
                                n_mb = self.n / (1024 * 1024) if self.total else 0
                                total_mb = self.total / (1024 * 1024) if self.total else 0

                                # 获取速率并转换为MB/s
                                rate = self.format_dict.get('rate', 0)
                                rate_mb = rate / 1024 / 1024 if rate else 0

                                percent = (self.n / self.total * 100) if self.total and self.total > 0 else 0

                                status = (
                                    f"进度: {percent:.1f}% | "
                                    f"已下载: {n_mb:.2f}/{total_mb:.2f} MB | "
                                    f"速度: {rate_mb:.2f} MB/s"
                                )
                                self.label_var.set(status)
                            except Exception:
                                pass

                        try:
                            self.root.after(0, _update_gui)
                        except Exception:
                            # 如果无法通过 after 调度，则忽略 GUI 更新（线程安全优先）
                            pass
            
            # 使用自定义的Tkinter集成进度条
            with TkinterTqdm(total=file_size, unit='B', unit_scale=True, unit_divisor=1024, 
                            root=root, progress_var=progress_var, label_var=label_var) as bar:
                with requests.get(url, stream=True) as r:
                    with open(path, 'wb') as fp:
                        for chunk in r.iter_content(chunk_size=8192):  # 增加块大小以提高效率
                            if chunk:
                                fp.write(chunk)
                                bar.update(len(chunk))
            return 0
        except Exception as e:
            print(f"下载错误: {e}")
            return 1
    def _on_finish(success, err=None):
        try:
            if success:
                try:
                    progress_var.set(100)
                except Exception:
                    pass
                try:
                    current_action.set("下载完成")
                except Exception:
                    pass
                try:
                    msgbox.showinfo("下载完成", "文件下载完成！", parent=dl)
                except Exception:
                    pass
            else:
                try:
                    msgbox.showerror("下载失败", str(err), parent=dl)
                except Exception:
                    pass
        finally:
            try:
                dl.destroy()
            except Exception:
                pass

    def fix():
        # 后台线程仅执行下载逻辑，所有 GUI 更新通过 dl.after 调度到主线程
        try:
            result = download_g(url, path, root=dl, progress_var=progress_var, label_var=label_var)
            # 调度完成回调到主线程
            try:
                dl.after(0, lambda: _on_finish(result == 0, None))
            except Exception:
                _on_finish(result == 0, None)
        except Exception as e:
            try:
                dl.after(0, lambda: _on_finish(False, e))
            except Exception:
                _on_finish(False, e)

    # 在开始后台线程前，在主线程中设置初始状态（通过 after 调度以保证线程安全）
    try:
        dl.after(0, lambda: current_action.set("准备中..."))
    except Exception:
        try:
            current_action.set("准备中...")
        except Exception:
            pass

    t = threading.Thread(target=fix)
    t.daemon = True
    t.start()

__all__ = [
    'upload',
    'download',
    'fetch',
    'tqdm_download',
    'GUI_download'
]