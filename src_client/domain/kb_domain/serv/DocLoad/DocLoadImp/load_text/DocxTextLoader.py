from typing import List

from domain.kb_domain.serv.DocLoad.DocLoadImp.BaseLoader import BaseLoader


class DocxTextLoader(BaseLoader):
    def __init__(self, file_path: str):
        super().__init__(file_path)

    def _load_impl(self) -> List[str]:
        def doc2text(filepath: str) -> str:
            from docx import Document
            from docx.text.paragraph import Paragraph
            from docx.table import Table

            doc = Document(filepath)
            text = ""

            def iter_block_items(parent):
                """遍历段落和表格"""
                if hasattr(parent, "element"):
                    parent_elm = parent.element.body
                else:
                    raise ValueError("OCRDocxLoader parse fail")

                for child in parent_elm.iterchildren():
                    if child.tag.endswith("p"):
                        yield Paragraph(child, parent)
                    elif child.tag.endswith("tbl"):
                        yield Table(child, parent)

            for block in iter_block_items(doc):
                if isinstance(block, Paragraph):
                    if block.text.strip():
                        text += block.text.strip() + "\n"
                elif isinstance(block, Table):
                    for row in block.rows:
                        for cell in row.cells:
                            for paragraph in cell.paragraphs:
                                if paragraph.text.strip():
                                    text += paragraph.text.strip() + "\n"

            return text

        return [doc2text(self.file_path)]


