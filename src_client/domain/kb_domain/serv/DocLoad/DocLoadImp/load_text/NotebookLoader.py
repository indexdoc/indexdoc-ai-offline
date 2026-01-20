import json
from typing import Any

from domain.kb_domain.serv.DocLoad.DocLoadImp.BaseLoader import BaseLoader


class NotebookLoader(BaseLoader):
    """
    NotebookLoader - 读取Jupyter Notebook文件(.ipynb)内容
    提取代码单元格和Markdown单元格的内容
    """

    def _load_impl(self) -> Any:
        """
        解析Jupyter Notebook文件
        """
        with open(self.file_path, 'r', encoding='utf-8') as file:
            notebook_data = json.load(file)

        content_list = []

        # 检查notebook格式
        if notebook_data.get('nbformat') is None:
            raise ValueError("无效的Notebook文件格式")

        cells = notebook_data.get('cells', [])

        for i, cell in enumerate(cells):
            cell_type = cell.get('cell_type', '')
            source = cell.get('source', [])

            # 将source列表合并为字符串
            cell_content = ''.join(source) if isinstance(source, list) else source

            if cell_type == 'code':
                # 代码单元格，提取代码和输出
                content_list.append(f"代码单元格 {i + 1}:\n{cell_content}")

                # 如果有输出，也提取出来
                outputs = cell.get('outputs', [])
                for j, output in enumerate(outputs):
                    if output.get('output_type') == 'stream':
                        output_text = ''.join(output.get('text', [])) if isinstance(output.get('text', []),
                                                                                    list) else output.get('text', '')
                        content_list.append(f"代码单元格 {i + 1} 输出 {j + 1}:\n{output_text}")
                    elif output.get('output_type') == 'execute_result':
                        for item in output.get('data', {}).values():
                            if isinstance(item, list):
                                output_text = ''.join(item) if all(isinstance(x, str) for x in item) else str(item)
                            else:
                                output_text = str(item)
                            content_list.append(f"代码单元格 {i + 1} 执行结果 {j + 1}:\n{output_text}")
            elif cell_type == 'markdown':
                # Markdown单元格
                content_list.append(f"Markdown单元格 {i + 1}:\n{cell_content}")
            elif cell_type == 'raw':
                # 原始单元格
                content_list.append(f"原始单元格 {i + 1}:\n{cell_content}")

        return content_list
