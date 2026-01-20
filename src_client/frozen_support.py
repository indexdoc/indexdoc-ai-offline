import logging
import shutil
import sys
import os
import re
import ctypes

def is_frozen():
    """判断是否是打包后的 EXE 运行"""
    return getattr(sys, 'frozen', False)


def get_resource_path(relative_path):
    """获取资源文件的绝对路径"""
    if is_frozen():
        # 打包后：资源在 sys._MEIPASS 中（PyInstaller 创建的临时文件夹）
        base_path = sys._MEIPASS
        _temp_str = re.sub(r'^(\.\./|\.\.\\)+', '', relative_path) #去掉相对路径
        return os.path.normpath(os.path.join(base_path, _temp_str))
    else:
        # 直接运行 .py：资源在源代码目录中
        base_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.normpath(os.path.join(base_path, relative_path))

def get_tmp_path():
    if is_frozen():
        # 打包后：资源在 sys._MEIPASS 中（PyInstaller 创建的临时文件夹）
        base_path = sys._MEIPASS
        tmp_path = os.path.normpath(base_path + '/../tmp')
    else:
        # 直接运行 .py：资源在源代码目录中
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 获取上一级目录路径
        tmp_path= os.path.normpath(base_path + '/tmp')
    if not os.path.isdir(tmp_path):
        os.mkdir(tmp_path)
    return tmp_path

def get_base_path():
    if is_frozen():
        # 打包后：资源在 sys._MEIPASS 中（PyInstaller 创建的临时文件夹）
        base_path = sys._MEIPASS
        return os.path.normpath(base_path)
    else:
        # 直接运行 .py：资源在源代码目录中
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 获取上一级目录路径
        return os.path.normpath(base_path)

def get_update_work_path():
    if is_frozen():
        update_work_path = get_tmp_path() + '/update_work'
        return os.path.normpath(update_work_path)
    else:
        update_work_path = get_base_path() + '/tmp/indexdoc_win/tmp/update_work'
        return os.path.normpath(update_work_path)

def get_updater_path():
    if is_frozen():
        return os.path.normpath(get_tmp_path() + '/update_work/unpacked/_internal/updater.exe')
    else:
        return os.path.normpath(get_base_path() + '/tmp/indexdoc_win/_internal/updater.exe')

def get_vector_model_path():
    if is_frozen():
        # 打包后：资源在 sys._MEIPASS 中（PyInstaller 创建的临时文件夹）
        return os.path.normpath(f'{get_base_path()}/lib/model/BAAI/bge-small-zh-v1.5')
    else:
        return os.path.normpath(f'{get_base_path()}/lib/model/BAAI/bge-small-zh-v1.5')

def get_antiword_path():
    if is_frozen():
        # 打包后：资源在 sys._MEIPASS 中（PyInstaller 创建的临时文件夹）
        return os.path.normpath(f'{get_base_path()}/lib/model/antiword/bin64')
    else:
        return os.path.normpath(f'{get_base_path()}/lib/model/antiword/bin64')

def get_user_database_path():
    if is_frozen():
        database_file = os.path.normpath(f'{get_base_path()}/database') + '/default.duck'
        frozen_path = os.path.normpath(f'{get_base_path()}/../userdata')
        if not os.path.exists(frozen_path):
            os.makedirs(frozen_path)
        frozen_file = frozen_path + '/default.duck'
        if not os.path.exists(frozen_file):
            shutil.copy2(database_file, frozen_file)
        return frozen_file
    else:
        return os.path.normpath(f'{get_base_path()}/database') + '/default.duck'

def anti_debug():
    if not is_frozen():
        return
    #
    if sys.gettrace() or  \
        (hasattr(ctypes.windll.kernel32, 'IsDebuggerPresent') and ctypes.windll.kernel32.IsDebuggerPresent()) or \
        os.environ.get('PYDEVD_DISABLE_FILE_VALIDATION'):
        sys.exit("调试器被禁止")

# main.py 或你的主程序文件

import sys
import os

def get_version():
    try:
        if is_frozen():  # 检查是否是打包后的 exe
            # 获取当前 exe 文件路径
            exe_path = sys.executable
        else:
            # 开发模式：返回开发版本号或 __file__
            return "dev-unknown"

        # 使用 win32api 读取版本信息
        import win32api

        # 获取文件的版本字典
        info = win32api.GetFileVersionInfo(exe_path, "\\")
        ms = info['FileVersionMS']
        ls = info['FileVersionLS']

        # 解析版本号：高位和低位转换
        # Windows 版本号是 32位高位 + 32位低位
        version_parts = [
            win32api.HIWORD(ms),   # 主版本
            win32api.LOWORD(ms),   # 次版本
            win32api.HIWORD(ls),   # 修订
            win32api.LOWORD(ls),   # 构建
        ]

        # 格式化为字符串
        version_str = f"{version_parts[0]}.{version_parts[1]:02d}.{version_parts[2]:02d}.{version_parts[3]:04d}"
        return version_str

    except Exception as e:
        return f"unknown ({e})"
def get_file_info(info_name="ProductName"):
    try:
        if is_frozen():  # 检查是否是打包后的 exe
            # 获取当前 exe 文件路径
            file_path = sys.executable
            import win32api
            info = win32api.GetFileVersionInfo(file_path, '\\')

            # 读取语言和代码页（Translation）
            lang, codepage = win32api.VerQueryValue(info, r'\VarFileInfo\Translation')[0]

            # 构造查询路径，例如："\StringFileInfo\040904B0\ProductName"
            str_info_path = f'\\StringFileInfo\\{lang:04x}{codepage:04x}\\{info_name}'
            value = win32api.VerQueryValue(info, str_info_path)
            return value
        else:
            # 开发模式：返回开发版本号或 __file__
            return "indexdoc_win"
    except Exception as e:
        return 'indexdoc_win'

import subprocess
def unblock_files():
    try:
        if sys.platform == 'win32':
            # PowerShell 解除锁定
            subprocess.run([
                'powershell', '-Command',
                'Get-ChildItem . -Recurse | Unblock-File'
            ], check=False, capture_output=True)
    except Exception:
        pass  # 忽略错误，继续运行


def is_file_blocked(file_path):
    # try:
    #     # 方法1: 使用 dir /R 命令检查数据流
    #     result = subprocess.run(
    #         ['cmd', '/c', 'dir', '/R', file_path],
    #         capture_output=True, text=True, check=True
    #     )
    #
    #     # 检查输出中是否包含 Zone.Identifier
    #     if ':Zone.Identifier' in result.stdout:
    #         return True
    #
    # except subprocess.CalledProcessError:
    #     pass

    try:
        import pathlib
        file_path = pathlib.Path(file_path)
        if file_path.exists():
            # 尝试读取 Zone.Identifier 流
            zone_file = file_path.with_name(file_path.name + ':Zone.Identifier')
            if zone_file.exists():
                return True
    except Exception:
        pass

    return False

# 使用示例
if __name__ == '__main__':
    version = get_version()
    print(f"当前版本: {version}")
