from typing import Any

from domain.kb_domain.serv.DocLoad.DocLoadImp.BaseLoader import BaseLoader

# pip install PyPDF2
import PyPDF2


class PyPDFLoader(BaseLoader):
    """
    PyPDFLoader - 使用PyPDF2库读取PDF文件内容
    从PDF中提取文本内容
    """

    def _load_impl(self) -> Any:
        """
        使用PyPDF2解析PDF文件
        """
        content_list = []

        with open(self.file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)

            for page_num, page in enumerate(pdf_reader.pages):
                text = page.extract_text()
                if text.strip():  # 只添加非空页面内容
                    content_list.append(f"{text.strip()}")

        return content_list
