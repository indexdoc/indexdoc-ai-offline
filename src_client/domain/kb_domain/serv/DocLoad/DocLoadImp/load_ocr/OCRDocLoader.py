import logging
import os
import shutil
import cv2
import pythoncom
import win32com.client
from domain.kb_domain.serv.DocLoad.DocLoadImp.BaseLoader import BaseLoader

# 建议使用 fitz 将 PDF 转图像
import fitz  # PyMuPDF


class OCRDocLoader(BaseLoader):
    """将 DOC 文件渲染为图片进行 OCR 识别"""

    def _load_impl(self):
        tmp_dir = None
        pdf_paths = []  # 记录生成的 PDF 路径
        img_paths = []  # 记录生成的图像路径

        def doc_to_images(doc_path):
            pythoncom.CoInitialize()
            word = None
            doc = None
            try:
                word = win32com.client.Dispatch("Word.Application")
                word.Visible = False
                doc = word.Documents.Open(doc_path)
                import tempfile
                tmp_dir = os.path.join(tempfile.gettempdir(), "tmp_doc_images")
                os.makedirs(tmp_dir, exist_ok=True)

                img_list = []
                pdf_list = []

                page_count = doc.ComputeStatistics(2)  # wdStatisticPages=2
                for i in range(page_count):
                    page = i + 1
                    # 导出为单页 PDF
                    pdf_path = os.path.join(tmp_dir, f"page_{page}.pdf")
                    doc.ExportAsFixedFormat(
                        OutputFileName=pdf_path,
                        ExportFormat=17,  # PDF
                        OpenAfterExport=False,
                        OptimizeFor=0,
                        Range=7,  # wdExportFromTo
                        From=page,
                        To=page,
                        Item=0,
                        IncludeDocProps=True,
                        KeepIRM=True,
                        CreateBookmarks=0,
                        DocStructureTags=True,
                        BitmapMissingFonts=True,
                        UseISO19005_1=False
                    )
                    pdf_list.append(pdf_path)

                    # 使用 fitz 将 PDF 转为图像
                    img_path = os.path.join(tmp_dir, f"page_{page}.png")
                    pdf_doc = fitz.open(pdf_path)
                    pix = pdf_doc[0].get_pixmap(dpi=150)  # 设置 DPI 提高清晰度
                    pix.save(img_path)
                    pdf_doc.close()

                    img_list.append(img_path)

                return img_list, tmp_dir, pdf_list

            finally:
                if doc:
                    doc.Close(False)
                if word:
                    word.Quit()
                pythoncom.CoUninitialize()

        try:
            from domain.kb_domain.serv.DocLoad.DocLoadImp.load_ocr.OCR import get_ocr
            ocr = get_ocr()

            # 1. 渲染 DOC 每页为图像
            img_paths, tmp_dir, pdf_paths = doc_to_images(self.file_path)
            text_all = ""

            # 2. OCR 每页图像
            for img_path in img_paths:
                img = cv2.imread(img_path)
                if img is not None:
                    result, _ = ocr(img)
                    if result:
                        text_all += "\n".join([line[1] for line in result])
                # 立即删除图像文件
                if os.path.exists(img_path):
                    os.remove(img_path)

            # 3. 删除 PDF 文件
            for pdf_path in pdf_paths:
                if os.path.exists(pdf_path):
                    os.remove(pdf_path)

        except Exception as e:
            logging.debug(f"OCR 处理失败: {e}")
            raise
        finally:
            # 4. 删除临时目录
            if tmp_dir and os.path.exists(tmp_dir):
                try:
                    shutil.rmtree(tmp_dir)
                except Exception as e:
                    logging.debug(f"无法删除临时目录 {tmp_dir}: {e}")
                    # 可选：重试或记录日志

        return [text_all]