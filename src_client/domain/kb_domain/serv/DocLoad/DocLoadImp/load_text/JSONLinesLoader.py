import json
from typing import Any

from domain.kb_domain.serv.DocLoad.DocLoadImp.BaseLoader import BaseLoader


class JSONLinesLoader(BaseLoader):
    """
    JSONLinesLoader - 读取JSONL文件内容
    解析每行一个JSON对象的文件格式
    """

    def _load_impl(self) -> Any:
        """
        解析JSONL文件，每行一个JSON对象
        """
        content_list = []

        with open(self.file_path, 'r', encoding='utf-8') as file:
            for line_num, line in enumerate(file, 1):
                line = line.strip()
                if line:  # 跳过空行
                    try:
                        json_obj = json.loads(line)
                        # 将JSON对象转换为字符串添加到列表
                        content_list.append(json.dumps(json_obj, ensure_ascii=False))
                    except json.JSONDecodeError as e:
                        raise ValueError(f"第{line_num}行JSON格式错误: {e}")

        return content_list