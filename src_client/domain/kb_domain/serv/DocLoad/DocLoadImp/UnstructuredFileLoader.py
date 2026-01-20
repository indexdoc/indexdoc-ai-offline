from typing import Any

from domain.kb_domain.serv.DocLoad.DocLoadImp.BaseLoader import BaseLoader


class UnstructuredFileLoader(BaseLoader):
    """
    UnstructuredFileLoader - 使用unstructured库读取多种文件格式
    支持.rst, .txt, .xml, .epub, .odt, .tsv格式的文件
    """

    def _load_impl(self) -> Any:
        """
        使用unstructured库解析HTML文件
        """
        # 尝试导入unstructured库
        try:
            from unstructured.partition.auto import partition
        except ImportError:
            raise ImportError('请安装unstructured库: pip install "unstructured"')

        # 使用unstructured库解析HTML文件
        elements = partition(filename=self.file_path)

        # 提取文本内容
        content_list = []
        for element in elements:
            if hasattr(element, 'text') and element.text.strip():
                content_list.append(element.text.strip())

        return content_list
