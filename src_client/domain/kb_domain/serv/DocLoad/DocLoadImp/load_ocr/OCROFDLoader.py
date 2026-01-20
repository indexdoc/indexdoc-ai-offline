from domain.kb_domain.serv.DocLoad.DocLoadImp.BaseLoader import BaseLoader
import base64
import os
from typing import List
# pip install easyofd
from easyofd.ofd import OFD


class OCROFDLoader(BaseLoader):
    def __init__(self, file_path: str):
        super().__init__(file_path)
        self.unstructured_kwargs = None

    def _load_impl(self) -> List:
        file_prefix = os.path.splitext(os.path.split(self.file_path)[1])[0]
        with open(self.file_path, "rb") as f:
            ofdb64 = str(base64.b64encode(f.read()), "utf-8")
        ofd = OFD()  # 初始化OFD 工具类
        ofd.read(ofdb64, save_xml=False, xml_name=f"{file_prefix}_xml")  # 读取ofdb64
        text = ''
        for page in ofd.data:
            for page_info in page['page_info'].values():
                for _text in page_info['text_list']:
                    text += str(_text['text']) + ' \n'
        return [text]
