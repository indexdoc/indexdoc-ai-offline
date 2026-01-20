import base64
import json
import re
import uuid
import pyperclip as pyperclip

import frozen_support
from domain.base_domain.BaseHandler import BaseApiHandler
from util.markdown import MarkDownUtil


class ApiMdWordHandler(BaseApiHandler):
    need_login = False

    def myget(self):
        pass

    def mypost(self):
        self.set_header("Content-Type", "application/json; charset=utf-8")
        data = json.loads(self.request.body.decode("utf-8"))
        _md_content = data.get("md_content", "")
        _md_content = _md_content.replace('\n','\n\n') #保证使用pandoc时，导出的Word格式正确。
        tmp_path = frozen_support.get_tmp_path()
        output_path = f"{tmp_path}/{uuid.uuid4().hex}.docx"
        _status = MarkDownUtil.str2docx(markdown_str=_md_content, output_docx=output_path)
        if _status:
            with open(output_path, "rb") as f:
                file_bytes = f.read()
            encoded = base64.b64encode(file_bytes).decode("utf-8")
            self.write({"success": True, "msg": "导出成功", "file": encoded})
        else:
            self.write({"success": False, "msg": "导出失败"})

class ApiMdFileHandler(BaseApiHandler):
    need_login = False

    def myget(self):
        pass

    def mypost(self):
        self.set_header("Content-Type", "application/json; charset=utf-8")
        data = json.loads(self.request.body.decode("utf-8"))
        _md_content = data.get("md_content", "")
        tmp_path = frozen_support.get_tmp_path()
        output_path = f"{tmp_path}/{uuid.uuid4().hex}.md"
        _status = MarkDownUtil.str2md(markdown_str=_md_content, output_md=output_path)
        if _status:
            with open(output_path, "rb") as f:
                file_bytes = f.read()
            encoded = base64.b64encode(file_bytes).decode("utf-8")
            self.write({"success": True, "msg": "导出成功", "file": encoded})
        else:
            self.write({"success": False, "msg": "导出失败"})


class ApiMdPasteHandler(BaseApiHandler):
    need_login = False

    def mypost(self):
        try:
            text = pyperclip.paste()  # 读取剪贴板内容
            text = re.sub(r'(?<!\n)\n(?!\n)', '\n\n', text)
            self.write({"success": True, "data": text})
        except Exception as e:
            return f"[读取剪贴板失败]: {e}"


class ApiMdPdfHandler(BaseApiHandler):
    need_login = False

    def myget(self):
        pass

    def mypost(self):
        self.set_header("Content-Type", "application/json; charset=utf-8")
        data = json.loads(self.request.body.decode("utf-8"))
        _html_content = data.get("html_content", "")
        tmp_path = frozen_support.get_tmp_path()
        output_path = f"{tmp_path}/{uuid.uuid4().hex}.docx"
        _status = MarkDownUtil.html2pdf(_html_content, output_path)
        if _status:
            with open(output_path, "rb") as f:
                file_bytes = f.read()
            encoded = base64.b64encode(file_bytes).decode("utf-8")
            self.write({"success": True, "msg": "导出成功", "file": encoded})
        else:
            self.write({"success": False, "msg": "导出失败"})


urls = [
    ('/api/md/mdWord', ApiMdWordHandler),
    ('/api/md/mdFile', ApiMdFileHandler),
    ('/api/md/mdPdf', ApiMdPdfHandler),
    ('/api/md/mdPaste', ApiMdPasteHandler)
]
