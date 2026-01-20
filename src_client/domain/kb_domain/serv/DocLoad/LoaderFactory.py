import os
import inspect
from typing import Type, List

from domain.kb_domain.serv.DocLoad.DocLoadImp.BaseLoader import BaseLoader
import logging

class LoaderFactory:
    """根据扩展名选择对应的 Loader，并支持多级回退"""

    # 字典定义: 主 Loader + 备用 Loader 列表
    _LOADER_RULES = [
        (['.pdf'], ['PyPDFLoader', 'OCRPDFLoader']),
        (['.doc'], ['AntiDocLoader']),
        (['.xls'], ['XlsLoader']),
        (['.xlsx'], ['XlsxLoader']),
        (['.docx'], ['DocxTextLoader', 'OCRDocxLoader', 'AntiDocLoader']), # 部分无法加载的特殊docx可以用AntiDocLoader加载成功
        (['.pptx'], ['PptxTextLoader', 'OCRPPTLoader']), #新增加载类，只读文本
        (['.ofd'], ['OCROFDLoader']),
        (['.md'], ['MarkdownTextLoader', 'UnstructuredMarkdownLoader']),
        (['.wps'], ['AntiDocLoader', 'WPSLoader']),
        (['.csv'], ['CsvTextLoader', 'CSVLoader']),
        (['.png', '.jpg', '.jpeg', '.bmp', '.webp', '.heic', '.psd', '.gif', '.tiff', '.raw'], ['OCRIMGLoader']),
        (['.html', '.htm'], ['UnstructuredHTMLLoader']),
        (['.mhtml'], ['MHTMLLoader']),
        (['.json'], ['JSONLoader']),
        (['.jsonl'], ['JSONLinesLoader']),
        (['.eml', '.msg'], ['UnstructuredEmailLoader']),
        (['.epub'], ['UnstructuredEPubLoader']),
        (['.ipynb'], ['NotebookLoader']),
        (['.odt'], ['UnstructuredODTLoader']),
        (['.py'], ['PythonLoader']),
        (['.rst'], ['UnstructuredRSTLoader']),
        (['.rtf'], ['UnstructuredRTFLoader']),
        (['.srt'], ['SRTLoader']),
        (['.toml'], ['TomlLoader']),
        (['.tsv'], ['UnstructuredTSVLoader']),
        (['.xml'], ['UnstructuredXMLLoader']),
        (['.enex'], ['EverNoteLoader']),
        # 通用文件类型兜底
        (['.rst', '.txt', '.xml', '.epub', '.odt', '.tsv'], ['UnstructuredFileLoader']),
    ]

    # 由规则动态生成最终字典
    LOADER_MAP: dict[str, List[str]] = {
        ext: loaders for exts, loaders in _LOADER_RULES for ext in exts
    }

    @classmethod
    def _get_loader_class(cls, name: str) -> Type[BaseLoader]:
        """
        延迟导入 Loader 类，根据名称返回 Loader 类对象
        """
        if name == "UnstructuredHTMLLoader":
            from domain.kb_domain.serv.DocLoad.DocLoadImp.UnstructuredHTMLLoader import UnstructuredHTMLLoader
            return UnstructuredHTMLLoader
        elif name == "MHTMLLoader":
            from domain.kb_domain.serv.DocLoad.DocLoadImp.load_text.MHTMLLoader import MHTMLLoader
            return MHTMLLoader
        elif name == "UnstructuredMarkdownLoader":
            from domain.kb_domain.serv.DocLoad.DocLoadImp.UnstructuredMarkdownLoader import UnstructuredMarkdownLoader
            return UnstructuredMarkdownLoader
        elif name == "MarkdownTextLoader":
            from domain.kb_domain.serv.DocLoad.DocLoadImp.load_text.MarkdownTextLoader import MarkdownTextLoader
            return MarkdownTextLoader
        elif name == "JSONLoader":
            from domain.kb_domain.serv.DocLoad.DocLoadImp.load_text.JSONLoader import JSONLoader
            return JSONLoader
        elif name == "JSONLinesLoader":
            from domain.kb_domain.serv.DocLoad.DocLoadImp.load_text.JSONLinesLoader import JSONLinesLoader
            return JSONLinesLoader
        elif name == "DocxTextLoader":
            from domain.kb_domain.serv.DocLoad.DocLoadImp.load_text.DocxTextLoader import DocxTextLoader
            return DocxTextLoader
        elif name == "PptxTextLoader":
            from domain.kb_domain.serv.DocLoad.DocLoadImp.load_text.PptxTextLoader import PptxTextLoader
            return PptxTextLoader
        elif name == "CSVLoader":
            from domain.kb_domain.serv.DocLoad.DocLoadImp.load_text.CSVLoader import CSVLoader
            return CSVLoader
        elif name == "CsvTextLoader":
            from domain.kb_domain.serv.DocLoad.DocLoadImp.load_text.CsvTextLoader import CsvTextLoader
            return CsvTextLoader
        elif name == "OCRPDFLoader":
            from domain.kb_domain.serv.DocLoad.DocLoadImp.load_ocr.OCRPDFLoader import OCRPDFLoader
            return OCRPDFLoader
        elif name == "PyPDFLoader":
            from domain.kb_domain.serv.DocLoad.DocLoadImp.load_text.PyPDFLoader import PyPDFLoader
            return PyPDFLoader
        elif name == "OCROFDLoader":
            from domain.kb_domain.serv.DocLoad.DocLoadImp.load_ocr.OCROFDLoader import OCROFDLoader
            return OCROFDLoader
        elif name == "DOCLoader":
            from domain.kb_domain.serv.DocLoad.DocLoadImp.DocUseMsWordLoader import DOCLoader
            return DOCLoader
        elif name == "AntiDocLoader":
            from domain.kb_domain.serv.DocLoad.DocLoadImp.load_text.AntiDocLoader import AntiDocLoader
            return AntiDocLoader
        elif name == "OCRDocLoader":
            from domain.kb_domain.serv.DocLoad.DocLoadImp.load_ocr.OCRDocLoader import OCRDocLoader
            return OCRDocLoader
        elif name == "OCRDocxLoader":
            from domain.kb_domain.serv.DocLoad.DocLoadImp.load_ocr.OCRDocxLoader import OCRDocxLoader
            return OCRDocxLoader
        elif name == "WPSLoader":
            from domain.kb_domain.serv.DocLoad.DocLoadImp.load_text.WPSLoader import WPSLoader
            return WPSLoader
        elif name == "OCRPPTLoader":
            from domain.kb_domain.serv.DocLoad.DocLoadImp.load_ocr.OCRPPTLoader import OCRPPTLoader
            return OCRPPTLoader
        elif name == "OCRIMGLoader":
            from domain.kb_domain.serv.DocLoad.DocLoadImp.load_ocr.OCRIMGLoader import OCRIMGLoader
            return OCRIMGLoader
        elif name == "UnstructuredEmailLoader":
            from domain.kb_domain.serv.DocLoad.DocLoadImp.UnstructuredEmailLoader import UnstructuredEmailLoader
            return UnstructuredEmailLoader
        elif name == "UnstructuredEPubLoader":
            from domain.kb_domain.serv.DocLoad.DocLoadImp.UnstructuredEPubLoader import UnstructuredEPubLoader
            return UnstructuredEPubLoader
        elif name == "UnstructuredExcelLoader":
            from domain.kb_domain.serv.DocLoad.DocLoadImp.unused.UnstructuredExcelLoader import UnstructuredExcelLoader
            return UnstructuredExcelLoader
        elif name == "NotebookLoader":
            from domain.kb_domain.serv.DocLoad.DocLoadImp.load_text.NotebookLoader import NotebookLoader
            return NotebookLoader
        elif name == "UnstructuredODTLoader":
            from domain.kb_domain.serv.DocLoad.DocLoadImp.UnstructuredODTLoader import UnstructuredODTLoader
            return UnstructuredODTLoader
        elif name == "PythonLoader":
            from domain.kb_domain.serv.DocLoad.DocLoadImp.load_text.PythonLoader import PythonLoader
            return PythonLoader
        elif name == "UnstructuredRSTLoader":
            from domain.kb_domain.serv.DocLoad.DocLoadImp.UnstructuredRSTLoader import UnstructuredRSTLoader
            return UnstructuredRSTLoader
        elif name == "UnstructuredRTFLoader":
            from domain.kb_domain.serv.DocLoad.DocLoadImp.UnstructuredRTFLoader import UnstructuredRTFLoader
            return UnstructuredRTFLoader
        elif name == "SRTLoader":
            from domain.kb_domain.serv.DocLoad.DocLoadImp.load_text.SRTLoader import SRTLoader
            return SRTLoader
        elif name == "TomlLoader":
            from domain.kb_domain.serv.DocLoad.DocLoadImp.load_text.TomlLoader import TomlLoader
            return TomlLoader
        elif name == "UnstructuredTSVLoader":
            from domain.kb_domain.serv.DocLoad.DocLoadImp.UnstructuredTSVLoader import UnstructuredTSVLoader
            return UnstructuredTSVLoader
        elif name == "UnstructuredXMLLoader":
            from domain.kb_domain.serv.DocLoad.DocLoadImp.UnstructuredXMLLoader import UnstructuredXMLLoader
            return UnstructuredXMLLoader
        elif name == "EverNoteLoader":
            from domain.kb_domain.serv.DocLoad.DocLoadImp.load_text.EverNoteLoader import EverNoteLoader
            return EverNoteLoader
        elif name == "XlsLoader":
            from domain.kb_domain.serv.DocLoad.DocLoadImp.load_text.XlsLoader import XlsLoader
            return XlsLoader
        elif name == "XlsxLoader":
            from domain.kb_domain.serv.DocLoad.DocLoadImp.load_text.XlsxLoader import XlsxLoader
            return XlsxLoader
        elif name == "UnstructuredFileLoader":
            from domain.kb_domain.serv.DocLoad.DocLoadImp.UnstructuredFileLoader import UnstructuredFileLoader
            return UnstructuredFileLoader
        else:
            raise ValueError(f"未知 Loader 名称: {name}")

    @classmethod
    def _create_loader(cls, loader_name: str, filepath: str, **kwargs) -> BaseLoader:
        """
        根据 Loader 名称创建实例，自动匹配 __init__ 参数
        """
        loader_cls = cls._get_loader_class(loader_name)
        sig = inspect.signature(loader_cls.__init__)
        valid_params = sig.parameters.keys()

        filtered_args = {k: v for k, v in kwargs.items() if k in valid_params}

        # 文件路径兼容 file_path / filepath / path
        if "file_path" in valid_params:
            filtered_args["file_path"] = filepath
        elif "filepath" in valid_params:
            filtered_args["filepath"] = filepath
        else:
            filtered_args["path"] = filepath

        return loader_cls(**filtered_args)

    @classmethod
    def from_file(cls, filepath: str, **kwargs) -> BaseLoader:
        ext = os.path.splitext(filepath)[1].lower()
        loader_names = cls.LOADER_MAP.get(ext, ["UnstructuredFileLoader"])

        for loader_name in loader_names:
            loader = cls._create_loader(loader_name, filepath, **kwargs)
            try:
                rtn = loader.load()
                if rtn['load_status']:  # 判断是否有内容
                    logging.debug(f"✅ 使用 {loader_name} 成功读取 {filepath}")
                    return loader
                else:
                    logging.debug(f"❌ 使用 {loader_name} 读取 {filepath}失败：{rtn['file_content']}")
            except Exception as e:
                logging.debug(f"⚠️ {loader_name} 读取失败: {e}")

        raise Exception(f"❌ 所有 Loader 均失败")
