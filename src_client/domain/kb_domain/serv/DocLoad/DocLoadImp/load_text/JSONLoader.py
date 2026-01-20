import json
from typing import Any

from domain.kb_domain.serv.DocLoad.DocLoadImp.BaseLoader import BaseLoader


class JSONLoader(BaseLoader):
    """
    JSONLoader - 读取JSON文件内容
    将JSON文件解析为Python对象并返回
    """

    def _load_impl(self) -> Any:
        """
        解析JSON文件
        """
        with open(self.file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # 如果是字典或列表，将其转换为字符串列表
        if isinstance(data, dict):
            # 将字典转换为键值对字符串列表
            content_list = [f"{key}: {value}" for key, value in data.items()]
        elif isinstance(data, list):
            # 将列表元素转换为字符串列表
            content_list = [str(item) for item in data]
        else:
            # 其他类型直接转为字符串
            content_list = [str(data)]

        return content_list
