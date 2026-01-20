from domain.kb_domain.serv.DocLoad.DocLoadImp.BaseLoader import BaseLoader
# pip install opencv-python
import cv2
import numpy as np
from domain.kb_domain.serv.DocLoad.DocLoadImp.load_ocr.OCR import get_ocr


class OCRPDFLoader(BaseLoader):
    def __init__(self, file_path: str):
        super().__init__(file_path)
        self.unstructured_kwargs = None

    def _load_impl(self):
        def rotate_img(img, angle: float):
            """
            旋转图像（支持任意角度）
            """
            h, w = img.shape[:2]
            rotate_center = (w / 2, h / 2)
            M = cv2.getRotationMatrix2D(rotate_center, angle, 1.0)
            new_w = int(h * np.abs(M[0, 1]) + w * np.abs(M[0, 0]))
            new_h = int(h * np.abs(M[0, 0]) + w * np.abs(M[0, 1]))
            M[0, 2] += (new_w - w) / 2
            M[1, 2] += (new_h - h) / 2
            rotated_img = cv2.warpAffine(img, M, (new_w, new_h))
            return rotated_img

        def pdf2text(filepath: str) -> str:
            """
            直接将 PDF 页面渲染为图像并进行 OCR 识别
            """
            # pip install pyMuPDF
            import fitz  # pyMuPDF里面的fitz包，不要与pip install fitz混淆
            ocr = get_ocr()
            doc = fitz.open(stream=open(filepath, "rb").read(), filetype="pdf")
            resp = ""

            for i, page in enumerate(doc):
                # 提高 DPI 使 OCR 更准确
                zoom_x = 2.0  # X 方向放大倍数
                zoom_y = 2.0  # Y 方向放大倍数
                mat = fitz.Matrix(zoom_x, zoom_y)

                # 渲染整页为像素图
                pix = page.get_pixmap(matrix=mat, alpha=False)
                img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)

                if page.rotation != 0:
                    img = rotate_img(img, 360 - page.rotation)

                # OCR 识别整页
                result, _ = ocr(img)
                if result:
                    ocr_result = [line[1] for line in result]
                    text_page = "\n".join(ocr_result)
                    resp += f"{text_page}"

            return resp.strip()

        text = pdf2text(self.file_path)
        return [text]


