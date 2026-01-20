from typing import Any, List
import logging

class BaseLoader:
    """所有加载器的基类"""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.rtn = {
            'file_path': file_path,
            'load_status': False,
            'file_content': []
        }

    def load(self) -> Any:
        """
        统一异常捕获、返回结构
        """
        try:
            result = self._load_impl()
            # 如果子类返回内容，则填充 file_content
            if result is not None and result != []:
                self.rtn['file_content'] = result if isinstance(result, list) else [result]
                self.rtn['load_status'] = True
            else:
                logging.debug(f"{type(self)}读取文件{self.file_path}失败")
                self.rtn['file_content'] = []
                self.rtn['load_status'] = False
        except Exception as e:
            # logging.error(f"文件{self.file_path}加载失败{e}")
            self.rtn['load_status'] = False
            self.rtn['file_content'] = [f"加载失败: {e}"]
        return self.rtn

    def _load_impl(self) -> List[str]:
        """
        子类真正实现加载逻辑
        """
        raise NotImplementedError("子类必须实现 _load_impl() 方法")
