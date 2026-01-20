import os
import shutil
from install_util import OSAdminUtil

def check_environment(install_path=None, required_space_gb=5):
    """
    检查安装环境，包括存储空间要求

    Args:
        install_path: 安装目录路径，如果为None则检查当前目录
        required_space_gb: 需要的磁盘空间大小（GB）

    Returns:
        tuple: (bool, str) - (检查是否通过, 错误信息或成功信息)

    Raises:
        Exception: 当环境检查不通过时抛出异常
    """
    try:
        # 设置默认安装路径
        if install_path is None:
            install_path = os.getcwd()

        # 检查目录是否存在，如果不存在则检查父目录
        check_path = install_path
        if not os.path.exists(install_path):
            check_path = os.path.dirname(install_path) or install_path

        # 检查磁盘空间
        if not _check_disk_space(check_path, required_space_gb):
            return False, f"磁盘空间不足：需要 {required_space_gb}GB，请清理空间后重试"

        # 检查操作系统兼容性（可选）
        if not _check_os_compatibility():
            return False, "操作系统不兼容"

        # 检查必要的依赖
        dependency_check = _check_dependencies()
        if not dependency_check[0]:
            return False, f"缺少必要依赖：{dependency_check[1]}"

        return True, "环境检查通过"

    except Exception as e:
        return False, f"环境检查失败：{str(e)}"


def _check_disk_space(path, required_gb):
    """检查磁盘空间"""
    try:
        # 获取磁盘使用情况
        total, used, free = shutil.disk_usage(path)

        # 转换为GB
        required_bytes = required_gb * 1024 * 1024 * 1024
        free_gb = free / (1024 * 1024 * 1024)

        print(f"所需空间: {required_gb}GB")
        print(f"可用空间: {free_gb:.2f}GB")
        print(f"检查路径: {path}")

        return free >= required_bytes
    except Exception as e:
        print(f"磁盘空间检查错误: {e}")
        return False

def _check_os_compatibility():
    """检查操作系统兼容性"""
    import platform
    system = platform.system().lower()

    # 支持的操作系统
    supported_systems = ['windows', 'linux', 'darwin']  # darwin = macOS

    if system not in supported_systems:
        print(f"不支持的操作系统: {system}")
        return False

    print(f"操作系统: {platform.system()} {platform.release()}")
    return True


def _check_dependencies():
    """检查必要的依赖"""
    missing_deps = []

    # 检查必要的Python模块
    required_modules = ['requests', 'zipfile', 'json']
    required_modules = []

    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_deps.append(module)

    if missing_deps:
        return False, ", ".join(missing_deps)

    return True, "所有依赖已安装"


