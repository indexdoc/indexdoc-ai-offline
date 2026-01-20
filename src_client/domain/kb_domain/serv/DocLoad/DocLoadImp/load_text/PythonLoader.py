from typing import Any

from domain.kb_domain.serv.DocLoad.DocLoadImp.BaseLoader import BaseLoader


class PythonLoader(BaseLoader):
    """
    PythonLoader - 读取Python文件内容
    提取代码中的函数、类和注释等内容
    """

    def _load_impl(self) -> Any:
        """
        解析Python文件
        """
        with open(self.file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # 简单地按行分割内容
        lines = content.split('\n')

        # 提取有意义的代码行（非空行和注释行）
        content_list = []
        current_function = ""
        current_class = ""

        for line in lines:
            stripped_line = line.strip()

            # 跳过空行和纯注释行
            if not stripped_line or stripped_line.startswith('#'):
                continue

            # 检测类定义
            if stripped_line.startswith('class '):
                current_class = stripped_line
                content_list.append(stripped_line)
            # 检测函数定义
            elif stripped_line.startswith('def '):
                current_function = stripped_line
                content_list.append(stripped_line)
            # 检测模块级文档字符串
            elif stripped_line.startswith('"""') or stripped_line.startswith("'''"):
                content_list.append(f"文档字符串: {stripped_line}")
            else:
                content_list.append(stripped_line)

        return content_list
