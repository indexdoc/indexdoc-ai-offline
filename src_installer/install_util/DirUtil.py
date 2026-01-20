import os
import shutil
from datetime import datetime
from install_util.OSAdminUtil import is_admin, run_as_admin, is_protected_system_path


def create_directory(install_path, overwrite=False):
    """
    创建安装目录

    Args:
        install_path: 安装目录路径
        overwrite: 如果目录已存在是否覆盖（默认False）

    Returns:
        tuple: (bool, str) - (是否成功, 消息)
    """
    try:
        # 规范化路径
        install_path = os.path.abspath(install_path)
        print(f"准备创建安装目录: {install_path}")

        # 检查是否需要管理员权限
        if is_protected_system_path(install_path) and not is_admin():
            print("🛡️ 检测到系统保护目录，需要管理员权限...")
            if run_as_admin():
                # 程序会重新启动，这里不会执行到
                return True, "正在以管理员权限重新启动..."
            else:
                return False, "需要管理员权限来创建系统目录"

        # 检查目录是否已存在
        if os.path.exists(install_path):
            if overwrite:
                print("目录已存在，执行覆盖操作...")
                try:
                    # 备份原有目录
                    backup_path = install_path + ".backup"
                    if os.path.exists(backup_path):
                        shutil.rmtree(backup_path)
                    shutil.move(install_path, backup_path)
                    print(f"✅ 原有目录已备份至: {backup_path}")
                except PermissionError:
                    return False, f"权限不足，无法备份目录: {install_path}"
                except Exception as e:
                    return False, f"备份目录失败: {str(e)}"
            else:
                # 检查目录是否为空
                if os.listdir(install_path):
                    return False, f"安装目录已存在且不为空: {install_path}"
                else:
                    print("✅ 安装目录已存在但为空，继续使用")
                    return True, "目录已存在"

        # 创建目录（包括父目录）
        try:
            os.makedirs(install_path, exist_ok=True)
            print(f"✅ 安装目录创建成功: {install_path}")
        except PermissionError:
            return False, f"权限不足，无法创建目录: {install_path}"
        except Exception as e:
            return False, f"创建目录失败: {str(e)}"

        # 创建必要的子目录结构
        subdirs = [
        ]

        created_dirs = []
        for subdir in subdirs:
            try:
                subdir_path = os.path.join(install_path, subdir)
                os.makedirs(subdir_path, exist_ok=True)
                created_dirs.append(subdir)
                print(f"  📁 创建子目录: {subdir}")
            except Exception as e:
                print(f"  ⚠️  创建子目录 {subdir} 失败: {e}")

        # 设置目录权限（Linux/macOS）
        if os.name != 'nt':  # 非Windows系统
            try:
                # 设置755权限
                os.chmod(install_path, 0o755)
                for root, dirs, files in os.walk(install_path):
                    for dir_name in dirs:
                        os.chmod(os.path.join(root, dir_name), 0o755)
                print("✅ 目录权限设置完成")
            except Exception as e:
                print(f"⚠️  设置目录权限失败: {e}")

        # 验证目录创建成功
        if not os.path.exists(install_path):
            return False, "目录创建失败"

        # 测试写入权限
        test_file = os.path.join(install_path, "write_test.txt")
        try:
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write("Installation directory test - 安装目录测试")
            os.remove(test_file)
            print("✅ 目录写入测试通过")
        except Exception as e:
            return False, f"目录写入测试失败: {e}"

        # 记录安装目录信息
        info_file = os.path.join(install_path, "install_info.txt")
        try:
            with open(info_file, 'w', encoding='utf-8') as f:
                f.write(f"Application: IndexDoc\n")
                f.write(f"Installation Path: {install_path}\n")
                f.write(f"Created: {_get_current_time()}\n")
                f.write(f"Subdirectories: {', '.join(created_dirs)}\n")
                f.write(f"Overwrite: {overwrite}\n")
            print("✅ 安装信息文件创建完成")
        except Exception as e:
            print(f"⚠️  创建安装信息文件失败: {e}")

        # 创建版本文件
        version_file = os.path.join(install_path, "version.txt")
        try:
            with open(version_file, 'w', encoding='utf-8') as f:
                f.write("version: 1.0.0\n")
                f.write(f"install_time: {_get_current_time()}\n")
        except Exception as e:
            print(f"⚠️  创建版本文件失败: {e}")

        print(f"🎉 安装目录结构创建完成")
        return True, f"安装目录创建成功: {install_path}"

    except Exception as e:
        error_msg = f"创建目录失败: {str(e)}"
        print(f"❌ {error_msg}")
        return False, error_msg


def _get_current_time():
    """获取当前时间字符串"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def cleanup_on_failure(install_path):
    """
    安装失败时清理目录

    Args:
        install_path: 要清理的安装目录
    """
    try:
        if os.path.exists(install_path):
            print(f"🧹 安装失败，清理目录: {install_path}")
            shutil.rmtree(install_path)
            print("✅ 清理完成")
    except Exception as e:
        print(f"⚠️ 清理目录失败: {e}")


def get_directory_structure(install_path):
    """
    获取目录结构信息

    Args:
        install_path: 安装目录路径

    Returns:
        dict: 目录结构信息
    """
    if not os.path.exists(install_path):
        return {"error": "目录不存在"}

    structure = {
        "path": install_path,
        "exists": True,
        "size": 0,
        "subdirectories": [],
        "files": []
    }

    try:
        total_size = 0

        for root, dirs, files in os.walk(install_path):
            # 计算总大小
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    total_size += os.path.getsize(file_path)
                except:
                    pass

            # 只记录第一级目录和文件
            if root == install_path:
                structure["subdirectories"] = dirs
                structure["files"] = files

        structure["size"] = total_size
        structure["size_mb"] = round(total_size / (1024 * 1024), 2)

    except Exception as e:
        structure["error"] = str(e)

    return structure


# 使用示例
if __name__ == "__main__":
    # 测试创建目录
    test_path = os.path.join(os.path.expanduser("~"), "IndexDocTest")

    print("=== 测试目录创建功能 ===")
    success, message = create_directory(test_path, overwrite=True)

    if success:
        print(f"✅ {message}")

        # 显示目录结构
        structure = get_directory_structure(test_path)
        print(f"📁 目录结构信息:")
        print(f"   路径: {structure['path']}")
        print(f"   大小: {structure['size_mb']} MB")
        print(f"   子目录: {', '.join(structure['subdirectories'])}")
        print(f"   文件: {', '.join(structure['files'])}")

        # 清理测试目录
        print(f"🧹 清理测试目录...")
        cleanup_on_failure(test_path)
    else:
        print(f"❌ {message}")