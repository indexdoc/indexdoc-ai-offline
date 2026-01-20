from typing import Any

from domain.kb_domain.serv.DocLoad.DocLoadImp.BaseLoader import BaseLoader


class UnstructuredHTMLLoader(BaseLoader):
    """
    UnstructuredHTMLLoader - 使用unstructured库读取HTML文件内容
    适用于需要保留HTML结构化信息的场景
    """

    def _load_impl(self) -> Any:
        """
        使用unstructured库解析HTML文件
        """
        # 尝试导入unstructured库
        try:
            from unstructured.partition.html import partition_html
        except ImportError:
            raise ImportError('请安装unstructured库: pip install "unstructured"')

        # 使用unstructured库解析HTML文件
        elements = partition_html(filename=self.file_path)

        # 提取文本内容
        content_list = []
        for element in elements:
            if hasattr(element, 'text') and element.text.strip():
                content_list.append(element.text.strip())

        return content_list