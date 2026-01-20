from typing import List
from domain.kb_domain.serv.DocLoad.DocLoadImp.BaseLoader import BaseLoader


class MarkdownTextLoader(BaseLoader):
    def __init__(self, file_path: str):
        super().__init__(file_path)

    def _load_impl(self) -> List[str]:
        def md2text(filepath: str) -> str:
            # 直接读取纯文本内容
            text = ""
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    # 跳过图片语法 ![xxx](url)
                    if line.startswith("!["):
                        continue
                    # 可根据需要去掉 markdown 标记符号
                    # 去除标题、列表符号、代码块标记等
                    clean = (
                        line.replace("#", "")
                        .replace("*", "")
                        .replace("-", "")
                        .replace("`", "")
                        .replace(">", "")
                        .strip()
                    )
                    if clean:
                        text += clean + "\n"
            return text

        return [md2text(self.file_path)]


