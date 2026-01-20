from rapidocr import RapidOCR


def get_ocr(use_cuda: bool = True) -> "RapidOCR":
    ocr = RapidOCR()
    return ocr