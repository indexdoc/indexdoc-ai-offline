from typing import Any

from domain.kb_domain.serv.DocLoad.DocLoadImp.BaseLoader import BaseLoader


class WPSLoader(BaseLoader):
    """
    WPSLoader - 读取WPS Office文档内容
    适用于WPS文字处理文档（.wps格式）
    """

    def _load_impl(self) -> Any:
        """
        解析WPS文件
        """
        # 尝试导入处理WPS文件所需的库
        try:
            import zipfile
            import xml.etree.ElementTree as ET
        except ImportError as e:
            raise ImportError(f"处理WPS文件需要额外的库: {e}")

        content_list = []

        # WPS文件通常是ZIP压缩格式，包含XML文件
        with zipfile.ZipFile(self.file_path, 'r') as zip_file:
            # 列出所有文件
            file_list = zip_file.namelist()

            # 查找主要的内容文件
            content_files = [f for f in file_list if 'content.xml' in f or 'word' in f or 'main' in f.lower()]

            if content_files:
                # 读取内容文件
                for content_file in content_files:
                    try:
                        with zip_file.open(content_file) as file:
                            xml_content = file.read()
                            root = ET.fromstring(xml_content)

                            # 提取文本内容
                            text_content = self._extract_text_from_xml(root)
                            if text_content.strip():
                                content_list.append(text_content)
                    except Exception as e:
                        # 如果直接解析XML失败，尝试作为普通ZIP文件处理
                        content_list.append(f"无法解析文件 {content_file}: {str(e)}")
            else:
                # 如果没有找到标准的内容文件，尝试通用方法
                content_list.append(f"无法识别WPS文件 {self.file_path} 的内部结构")

        # 如果上面的方法都失败了，尝试使用unstructured库
        if not content_list:
            try:
                from unstructured.partition.doc import partition_doc
                elements = partition_doc(filename=self.file_path)

                for element in elements:
                    if hasattr(element, 'text') and element.text.strip():
                        content_list.append(element.text.strip())
            except ImportError:
                content_list.append(f"需要安装unstructured库来处理WPS文件: pip install unstructured")
            except Exception as e:
                content_list.append(f"处理WPS文件时出错: {str(e)}")

        return content_list

    def _extract_text_from_xml(self, root):
        """
        从XML根元素中提取文本内容
        """
        text_content = []

        # 递归遍历XML元素提取文本
        for element in root.iter():
            if element.text and element.text.strip():
                text_content.append(element.text.strip())

        return '\n'.join(text_content)



