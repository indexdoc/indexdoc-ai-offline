from typing import Any

from domain.kb_domain.serv.DocLoad.DocLoadImp.BaseLoader import BaseLoader


class SRTLoader(BaseLoader):
    """
    SRTLoader - 读取SRT字幕文件内容
    解析SRT格式的字幕文件并提取字幕文本
    """

    def _load_impl(self) -> Any:
        """
        解析SRT字幕文件
        """
        with open(self.file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # 按双换行符分割字幕块
        subtitle_blocks = content.strip().split('\n\n')

        content_list = []

        for block in subtitle_blocks:
            if block.strip():
                lines = block.split('\n')

                # 检查是否为有效的字幕块（至少包含序号、时间轴和字幕文本）
                if len(lines) >= 3:
                    # 第一行是序号
                    index = lines[0].strip()
                    # 第二行是时间轴
                    time_line = lines[1].strip()
                    # 剩余行是字幕文本
                    subtitle_text = '\n'.join(lines[2:]).strip()

                    if subtitle_text:
                        content_list.append(f"字幕 {index} ({time_line}): {subtitle_text}")

        return content_list
