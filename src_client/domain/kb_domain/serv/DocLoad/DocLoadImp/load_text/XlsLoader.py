from typing import List

from domain.kb_domain.serv.DocLoad.DocLoadImp.BaseLoader import BaseLoader


class XlsLoader(BaseLoader):

    def _load_impl(self) -> List:
        """
               使用xlrd读取.xls文件
               """
        try:
            import xlrd
        except ImportError:
            raise ImportError("需要安装xlrd库: pip install xlrd")

        content_list = []

        try:
            # 打开工作簿
            workbook = xlrd.open_workbook(self.file_path)

            # 遍历所有工作表
            for sheet_index in range(workbook.nsheets):
                sheet = workbook.sheet_by_index(sheet_index)

                # 遍历所有行
                for row_idx in range(sheet.nrows):
                    row = sheet.row_values(row_idx)

                    # 过滤空值，拼接单元格内容
                    row_text = ' '.join(str(cell).strip() for cell in row if cell is not None and str(cell).strip())

                    if row_text:
                        content_list.append(row_text)

        except Exception as e:
            raise RuntimeError(f"读取.xls文件失败: {str(e)}")

        return content_list


