from typing import Any

# pip install toml
import toml

from domain.kb_domain.serv.DocLoad.DocLoadImp.BaseLoader import BaseLoader


class TomlLoader(BaseLoader):
    """
    TomlLoader - 读取TOML文件内容
    解析TOML格式的配置文件
    """

    def _load_impl(self) -> Any:
        """
        解析TOML文件
        """
        with open(self.file_path, 'r', encoding='utf-8') as file:
            data = toml.load(file)

        # 将TOML数据转换为字符串列表
        content_list = []

        def flatten_dict(d, parent_key=''):
            """
            递归展开嵌套字典
            """
            items = []
            for k, v in d.items():
                new_key = f"{parent_key}.{k}" if parent_key else k
                if isinstance(v, dict):
                    items.extend(flatten_dict(v, new_key).items())
                else:
                    items.append((new_key, v))
            return dict(items)

        # 展开嵌套结构
        flattened_data = flatten_dict(data)

        # 转换为字符串列表
        for key, value in flattened_data.items():
            content_list.append(f"{key}: {value}")

        return content_list
