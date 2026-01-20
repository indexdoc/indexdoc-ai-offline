import os
from typing import Tuple, List, Dict


def get_dir_content(base_dir_path: str) -> Tuple[List[Dict], List[Dict]]:
    """
    获取指定目录的第一层文件夹和文件信息（不递归子目录）
    返回:
      dir_list: 当前目录下的子目录路径列表（绝对路径）
      fileinfo_list: 当前目录下文件的信息列表（dict）
    """
    dir_list = []
    fileinfo_list = []

    base_dir_path = os.path.abspath(base_dir_path)
    if not os.path.exists(base_dir_path):
        dir_list = []
        fileinfo_list = []
        exists = False
        return dir_list, fileinfo_list, exists

    try:
        # 使用 os.scandir 仅遍历当前层级
        with os.scandir(base_dir_path) as entries:
            for entry in entries:
                if entry.name.startswith("~$"):
                    continue  # 跳过临时文件

                abs_path = os.path.join(base_dir_path, entry.name)
                if entry.is_dir():
                    dir_list.append({"location_path": abs_path.replace(os.sep, "/")})
                elif entry.is_file():
                    try:
                        stat = entry.stat()
                    except FileNotFoundError:
                        continue  # 文件在扫描过程中被删除
                    fileinfo_list.append({
                        'file_short_name': entry.name,
                        'file_type': os.path.splitext(entry.name)[1].lstrip(".").lower(),
                        'metadata': None,
                        'location_path': abs_path.replace(os.sep, "/"),
                        'file_size': int(stat.st_size),
                        'file_timestamp': int(stat.st_mtime)
                    })
    except FileNotFoundError:
        pass  # 目录不存在则返回空

    return dir_list, fileinfo_list, True


if __name__ == '__main__':
    print(get_dir_content('D:\资产资源盘活相关政策汇编'))
