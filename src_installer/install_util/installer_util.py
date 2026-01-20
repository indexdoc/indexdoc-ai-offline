from install_util import EnvUtil
from install_util import DownloadUtil
from install_util import DirUtil


def check_environment(install_path=None, required_space_gb=5):
    return EnvUtil.check_environment(install_path, required_space_gb)

def create_directory(install_path, overwrite=False):
    return DirUtil.create_directory(install_path, overwrite)

async def download_package(sources,save_path):
    """下载安装包"""
    success, message = await DownloadUtil.multi_source_download(
        sources=sources,
        save_path=save_path,
        test_duration=5  # 5秒速度测试
    )


def extract_files():
    """解压安装文件"""
    pass

def configure_system():
    """配置系统设置"""

def cleanup_temp():
    """清理临时文件"""
    pass

def complete_installation():
    """完成安装并清理"""

def remove_installation():
    """移除安装（卸载功能）"""
    pass

