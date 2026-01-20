from typing import Any

from domain.kb_domain.serv.DocLoad.DocLoadImp.BaseLoader import BaseLoader


class UnstructuredExcelLoader(BaseLoader):
    """
    UnstructuredExcelLoader - 使用unstructured库读取Excel文件内容
    支持.xlsx、.xls和.xlsd格式的Excel文件
    """

    def _load_impl(self) -> Any:
        """
        使用unstructured库解析Excel文件
        """
        # 尝试导入unstructured库
        try:
            from unstructured.partition.xlsx import partition_xlsx
        except ImportError as e:
            raise e

        # 使用unstructured库解析Excel文件
        elements = partition_xlsx(filename=self.file_path)

        # 提取文本内容
        content_list = []
        for element in elements:
            if hasattr(element, 'text') and element.text.strip():
                content_list.append(element.text.strip())

        return content_list