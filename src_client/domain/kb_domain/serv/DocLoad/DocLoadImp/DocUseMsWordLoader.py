from typing import List

import win32com.client as client

from domain.kb_domain.serv.DocLoad.DocLoadImp.BaseLoader import BaseLoader


class DOCLoader(BaseLoader):
    def _load_impl(self) -> List:
        def doc2text(filepath):
            word = client.Dispatch("Word.Application")
            word.Visible = False
            doc = word.Documents.Open(filepath)
            text = doc.Content.Text
            doc.Close(False)
            word.Quit() #此处会抛出异常
            return text

        text = doc2text(self.file_path)
        return [text]
