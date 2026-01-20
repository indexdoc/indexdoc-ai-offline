from typing import Any

from domain.kb_domain.serv.DocLoad.DocLoadImp.BaseLoader import BaseLoader


class UnknownLoader(BaseLoader):
    """
    UnknownLoader - 处理未知文件类型的加载器
    对于无法识别的文件类型，提供基本的文件信息
    """

    def _load_impl(self) -> Any:
        """
        处理未知类型的文件
        返回文件的基本信息和内容（如果可能）
        """
        import os

        # 获取文件基本信息
        file_size = os.path.getsize(self.file_path)

        # 尝试读取文件的前几行作为内容预览
        content_list = []

        try:
            with open(self.file_path, 'r', encoding='utf-8', errors='ignore') as file:
                # 读取前10行作为预览
                for i, line in enumerate(file):
                    if i >= 10:  # 只读取前10行
                        content_list.append("... [文件内容截断]")
                        break
                    content_list.append(line.rstrip())
        except UnicodeDecodeError:
            # 如果UTF-8解码失败，尝试其他编码或以二进制方式处理
            with open(self.file_path, 'rb') as file:
                binary_content = file.read(1024)  # 读取前1024字节
                content_list.append(f"[二进制文件预览 - 前1024字节]: {binary_content[:50]}...")

        # 添加文件信息
        info_line = f"[文件信息: 路径={self.file_path}, 大小={file_size}字节, 未知格式]"
        content_list.insert(0, info_line)

        return content_list
