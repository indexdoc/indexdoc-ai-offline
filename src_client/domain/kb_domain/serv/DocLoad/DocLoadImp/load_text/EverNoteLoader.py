import xml.etree.ElementTree as ET
from typing import Any
from xml.sax.saxutils import unescape

from domain.kb_domain.serv.DocLoad.DocLoadImp.BaseLoader import BaseLoader


class EverNoteLoader(BaseLoader):
    """
    EverNoteLoader - 读取ENEX（Evernote Export）文件内容
    解析Evernote导出的XML格式文件
    """

    def _load_impl(self) -> Any:
        """
        解析ENEX文件
        """
        tree = ET.parse(self.file_path)
        root = tree.getroot()

        content_list = []

        # 遍历所有的note元素
        for note in root.findall('.//note'):
            title_elem = note.find('title')
            content_elem = note.find('content')

            title = title_elem.text if title_elem is not None and title_elem.text else "无标题"

            if content_elem is not None and content_elem.text:
                # 解码HTML实体
                content = unescape(content_elem.text)
                # 移除XML标签，只保留文本内容
                clean_content = self._strip_xml_tags(content)
                content_list.append(f"标题: {title}\n内容: {clean_content}")
            else:
                content_list.append(f"标题: {title}\n内容: [无内容]")

        return content_list

    def _strip_xml_tags(self, text):
        """
        移除XML/HTML标签，保留文本内容
        """
        import re
        # 使用正则表达式移除XML/HTML标签
        clean_text = re.sub(r'<[^>]+>', '', text)
        return clean_text.strip()
