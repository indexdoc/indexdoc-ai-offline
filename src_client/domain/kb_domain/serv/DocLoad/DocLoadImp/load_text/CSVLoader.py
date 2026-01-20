import csv
from typing import Any

from domain.kb_domain.serv.DocLoad.DocLoadImp.BaseLoader import BaseLoader


class CSVLoader(BaseLoader):
    """
    CSVLoader - 读取CSV文件内容
    将CSV文件解析为字符串列表，每行作为一个元素
    """

    def _load_impl(self) -> Any:
        """
        解析CSV文件
        """
        content_list = []

        with open(self.file_path, 'r', encoding='utf-8', newline='') as file:
            # 检测CSV方言（处理不同分隔符的CSV文件）
            sample = file.read(1024)
            file.seek(0)
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample).delimiter

            reader = csv.reader(file, delimiter=delimiter)

            for row in reader:
                # 将每一行转换为逗号分隔的字符串
                content_list.append(delimiter.join(row))

        return content_list