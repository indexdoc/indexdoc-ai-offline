from typing import Any

from domain.kb_domain.serv.DocLoad.DocLoadImp.BaseLoader import BaseLoader


class UnstructuredXMLLoader(BaseLoader):
    """
    UnstructuredXMLLoader - 使用unstructured库读取XML文件内容
    """

    def _load_impl(self) -> Any:
        """
        使用unstructured库解析XML文件
        """
        # 尝试导入unstructured库
        try:
            from unstructured.partition.xml import partition_xml
        except ImportError:
            raise ImportError('请安装unstructured库: pip install "unstructured"')

        # 使用unstructured库解析XML文件
        elements = partition_xml(filename=self.file_path)

        # 提取文本内容
        content_list = []
        for element in elements:
            if hasattr(element, 'text') and element.text.strip():
                content_list.append(element.text.strip())

        return content_list
