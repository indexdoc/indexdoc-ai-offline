from typing import List
import csv
from domain.kb_domain.serv.DocLoad.DocLoadImp.BaseLoader import BaseLoader
import chardet


class CsvTextLoader(BaseLoader):
    def __init__(self, file_path: str):
        super().__init__(file_path)

    def _load_impl(self) -> List[str]:
        def detect_encoding(filepath: str) -> str:
            """自动检测文件编码"""
            try:
                with open(filepath, "rb") as f:
                    data = f.read(2048)
                    result = chardet.detect(data)
                    return result.get("encoding", "utf-8")
            except Exception:
                return "utf-8"

        def csv2text(filepath: str) -> str:
            encoding = detect_encoding(filepath)
            text = ""
            with open(filepath, "r", encoding=encoding, errors="ignore") as f:
                reader = csv.reader(f)
                for row in reader:
                    line = " ".join(cell.strip() for cell in row if cell.strip())
                    if line:
                        text += line + "\n"
            return text.strip()

        return [csv2text(self.file_path)]