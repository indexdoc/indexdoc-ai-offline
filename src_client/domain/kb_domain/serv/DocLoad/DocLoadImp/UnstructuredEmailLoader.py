from typing import Any

from domain.kb_domain.serv.DocLoad.DocLoadImp.BaseLoader import BaseLoader


class UnstructuredEmailLoader(BaseLoader):
    """
    UnstructuredEmailLoader - 使用unstructured库读取电子邮件文件内容
    支持.eml和.msg格式的邮件文件
    """

    def _load_impl(self) -> Any:
        """
        使用unstructured库解析电子邮件文件
        """
        # 尝试导入unstructured库
        try:
            from unstructured.partition.email import partition_email
        except ImportError:
            raise ImportError('请安装unstructured库: pip install "unstructured"')

        # 根据文件扩展名选择合适的解析方法
        if self.file_path.lower().endswith('.msg'):
            # 对于.msg文件，使用email_message格式
            elements = partition_email(filename=self.file_path, content_type="application/vnd.ms-outlook")
        else:
            # 默认为.eml文件
            elements = partition_email(filename=self.file_path)

        # 提取文本内容
        content_list = []
        for element in elements:
            if hasattr(element, 'text') and element.text.strip():
                content_list.append(element.text.strip())

        return content_list
