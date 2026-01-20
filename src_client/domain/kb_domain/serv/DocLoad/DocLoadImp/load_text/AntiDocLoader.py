import subprocess
from typing import List

import chardet

import frozen_support
from domain.kb_domain.serv.DocLoad.DocLoadImp.BaseLoader import BaseLoader


class AntiDocLoader(BaseLoader):
    def _load_impl(self) -> List:
        def doc2text(filepath):
            """
            使用指定路径的 antiword 读取 .doc 文件文本内容（自动检测编码）
            """
            try:
                env_path = frozen_support.get_antiword_path()
                antiword_path = env_path + '/antiword.exe'

                # 执行 antiword 命令，获取原始字节输出
                result = subprocess.run(
                    [antiword_path, "-t", filepath],
                    capture_output=True,
                    text=False,  # 返回字节流
                    check=True,
                    cwd=str(env_path),
                    creationflags=subprocess.CREATE_NO_WINDOW
                )

                raw_bytes = result.stdout

                # 自动检测编码
                detect_result = chardet.detect(raw_bytes)
                encoding = detect_result.get('encoding') or 'utf-8'

                # 打印检测结果方便调试（可选）
                # print(f"检测到编码: {encoding}, 置信度: {detect_result.get('confidence')}")

                # 安全解码，失败则回退
                try:
                    text = raw_bytes.decode(encoding, errors='ignore').strip()
                except Exception:
                    text = raw_bytes.decode('utf-8', errors='ignore').strip()

                return text

            except subprocess.CalledProcessError as e:
                raise RuntimeError(f"antiword 执行失败: {e.stderr or e}")
            except Exception as e:
                raise RuntimeError(f"doc2text 出错: {e}")

        # 调用读取逻辑
        text = doc2text(self.file_path)
        return [text]


