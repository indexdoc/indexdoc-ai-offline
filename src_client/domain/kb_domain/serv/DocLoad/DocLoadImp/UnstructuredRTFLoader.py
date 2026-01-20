from typing import Any

from domain.kb_domain.serv.DocLoad.DocLoadImp.BaseLoader import BaseLoader


class UnstructuredRTFLoader(BaseLoader):
    """
    UnstructuredRTFLoader - 使用unstructured库读取RTF文件内容
    """

    def _load_impl(self) -> Any:
        """
        使用unstructured库解析RTF文件
        """
        # 尝试导入unstructured库
        try:
            from unstructured.partition.rtf import partition_rtf
        except ImportError:
            raise ImportError('请安装unstructured库: pip install "unstructured"')

        # 使用unstructured库解析RTF文件
        elements = partition_rtf(filename=self.file_path)

        # 提取文本内容
        content_list = []
        for element in elements:
            if hasattr(element, 'text') and element.text.strip():
                content_list.append(element.text.strip())

        return content_list
