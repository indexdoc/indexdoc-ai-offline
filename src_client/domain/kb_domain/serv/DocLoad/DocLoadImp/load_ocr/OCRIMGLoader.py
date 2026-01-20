from typing import List

from domain.kb_domain.serv.DocLoad.DocLoadImp.BaseLoader import BaseLoader
from domain.kb_domain.serv.DocLoad.DocLoadImp.load_ocr.OCR import get_ocr


class OCRIMGLoader(BaseLoader):
    def __init__(self, file_path: str):
        super().__init__(file_path)
        self.unstructured_kwargs = None

    def _load_impl(self) -> List:
        def img2text(filepath):
            resp = ""
            ocr = get_ocr()
            result, _ = ocr(filepath)
            if result:
                ocr_result = [line[1] for line in result]
                resp += "\n".join(ocr_result)
            return resp

        text = img2text(self.file_path)
        return [text]