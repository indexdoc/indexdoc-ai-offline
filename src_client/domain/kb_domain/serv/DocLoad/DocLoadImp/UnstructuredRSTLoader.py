from typing import Any

from domain.kb_domain.serv.DocLoad.DocLoadImp.BaseLoader import BaseLoader


class UnstructuredRSTLoader(BaseLoader):
    """
    UnstructuredRSTLoader - 使用unstructured库读取reStructuredText文件内容
    """

    def _load_impl(self) -> Any:
        """
        使用unstructured库解析reStructuredText文件
        """
        # 尝试导入unstructured库
        try:
            from unstructured.partition.rst import partition_rst
        except ImportError:
            raise ImportError('请安装unstructured库: pip install "unstructured"')

        # 使用unstructured库解析RST文件
        elements = partition_rst(filename=self.file_path)

        # 提取文本内容
        content_list = []
        for element in elements:
            if hasattr(element, 'text') and element.text.strip():
                content_list.append(element.text.strip())

        return content_list
