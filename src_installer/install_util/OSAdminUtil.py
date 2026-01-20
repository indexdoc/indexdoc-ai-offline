"""
操作系统管理员权限工具模块
提供跨平台的管理员权限检查、申请和相关功能
"""

import os
import sys
import ctypes
import platform
import subprocess


def is_admin():
    """检查是否是管理员权限"""
    try:
        if platform.system().lower() == 'windows':
            # Windows: 检查是否是管理员
            return ctypes.windll.shell32.IsUserAnAdmin()
        else:
            # Linux/macOS: 检查是否是root用户
            return os.getuid() == 0
    except Exception as e:
        print(f"检查管理员权限时出错: {e}")
        return False


def run_as_admin():
    """以管理员权限重新运行程序"""
    try:
        if is_admin():
            print("当前已在管理员权限下运行")
            return True

        system = platform.system().lower()

        if system == 'windows':
            print("正在请求Windows管理员权限...")
            # Windows: 使用ShellExecute以管理员权限重新启动程序
            result = ctypes.windll.shell32.ShellExecuteW(
                None,                   # 父窗口句柄
                "runas",                # 操作：以管理员身份运行
                sys.executable,         # 可执行文件路径
                " ".join(sys.argv),     # 命令行参数
                None,                   # 工作目录
                1                       # 显示窗口
            )

            if result > 32:
                print("管理员权限请求成功，程序将重新启动")
                sys.exit(0)
            else:
                print(f"管理员权限请求失败，错误代码: {result}")
                return False

        elif system in ['linux', 'darwin']:
            print("正在使用sudo请求root权限...")
            # Linux/macOS: 使用sudo重新运行当前程序
            subprocess.run(['sudo', sys.executable] + sys.argv)
            sys.exit(0)

        else:
            print(f"不支持的操作系统: {system}")
            return False

    except Exception as e:
        print(f"请求管理员权限时出错: {e}")
        return False


def is_protected_system_path(path):
    """检查是否是受保护的系统路径 - 增强版本"""
    try:
        abs_path = os.path.abspath(path).lower()

        if platform.system().lower() == 'windows':
            # Windows 受保护目录 - 更精确的匹配
            protected_paths = [
                "c:\\windows\\",
                "c:\\program files",
                "c:\\program files (x86)",
                "c:\\programdata\\",
                "c:\\system32\\",
                "c:\\users\\all users\\",
                "c:\\windows\\system32\\"
            ]
            # 检查路径是否以任何受保护路径开头
            for protected in protected_paths:
                if abs_path.startswith(protected):
                    return True

            # 特别检查 C:\Program Files 的直接子目录创建
            if abs_path == "c:\\program files":
                return True

        else:
            # Linux/macOS 受保护目录
            protected_paths = [
                "/bin/", "/sbin/", "/usr/", "/etc/", "/var/", "/root/",
                "/lib/", "/lib64/", "/sys/", "/proc/", "/dev/"
            ]
            return any(abs_path.startswith(protected) for protected in protected_paths)

        return False

    except Exception as e:
        print(f"检查受保护路径时出错: {e}")
        return False

def check_path_permission(need_check_path):
    """检查路径权限"""
    result = {
        'path': need_check_path,
        'exists': False,
        'writable': False,
        'protected': False,
        'needs_admin': False,
        'message': ''
    }

    try:
        abs_path = os.path.abspath(need_check_path)
        result['path'] = abs_path

        # 检查路径是否存在
        result['exists'] = os.path.exists(abs_path)

        # 检查是否为受保护路径
        result['protected'] = is_protected_system_path(abs_path)

        # 检查写入权限
        if result['exists']:
            result['writable'] = os.access(abs_path, os.W_OK)
        else:
            # 如果路径不存在，检查父目录权限
            parent_dir = os.path.dirname(abs_path)
            if parent_dir and os.path.exists(parent_dir):
                result['writable'] = os.access(parent_dir, os.W_OK)
            else:
                # 检查根目录权限
                root_dir = os.path.splitdrive(abs_path)[0] + '\\' if platform.system().lower() == 'windows' else '/'
                result['writable'] = os.access(root_dir, os.W_OK)

        # 判断是否需要管理员权限
        result['needs_admin'] = result['protected'] and not result['writable']

        # 生成描述信息
        if result['needs_admin']:
            result['message'] = "需要管理员权限访问受保护的系统目录"
        elif not result['writable']:
            result['message'] = "没有写入权限"
        else:
            result['message'] = "权限检查通过"

    except Exception as e:
        result['message'] = f"权限检查出错: {e}"

    return result


def recommend_install_path(app_name="MyApp"):
    """推荐安装路径"""
    user_profile = os.path.expanduser("~")
    options = []

    if platform.system().lower() == 'windows':
        # Windows 用户目录选项
        windows_paths = [
            os.path.join(user_profile, "AppData", "Local", "Programs", app_name),
            os.path.join(user_profile, "Documents", app_name),
            os.path.join(user_profile, app_name),
        ]
        options.extend(windows_paths)
    else:
        # Linux/macOS 用户目录选项
        linux_paths = [
            os.path.join(user_profile, ".local", "share", app_name.lower()),
            os.path.join(user_profile, app_name.lower()),
            os.path.join("/opt", app_name.lower()),
        ]
        options.extend(linux_paths)

    # 当前工作目录选项
    options.append(os.path.join(os.getcwd(), app_name))

    # 过滤出有写入权限的路径
    valid_paths = []
    for path in options:
        perm_check = check_path_permission(path)
        if not perm_check['needs_admin'] and perm_check['writable']:
            valid_paths.append(path)

    return valid_paths[0] if valid_paths else os.path.join(os.getcwd(), app_name)


# 测试代码
if __name__ == "__main__":
    print("=== OSAdminUtil 测试 ===")

    # 测试管理员权限检查
    print(f"当前是否是管理员权限: {is_admin()}")

    # 测试路径权限检查
    test_paths = [
        "C:\\Program Files\\TestApp",
        "/usr/local/testapp",
        os.path.expanduser("~"),
        os.getcwd()
    ]

    print("路径权限检查:")
    for path in test_paths:
        if platform.system().lower() == 'windows' and path.startswith("/"):
            continue
        if platform.system().lower() != 'windows' and path.startswith("C:"):
            continue

        perm_info = check_path_permission(path)
        print(f"  {path}:")
        print(f"    - 存在: {perm_info['exists']}")
        print(f"    - 可写: {perm_info['writable']}")
        print(f"    - 受保护: {perm_info['protected']}")
        print(f"    - 需要管理员: {perm_info['needs_admin']}")
        print(f"    - 消息: {perm_info['message']}")

    # 测试推荐安装路径
    recommended = recommend_install_path("TestApp")
    print(f"推荐安装路径: {recommended}")