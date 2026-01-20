# background_init.py
import frozen_support
import log_config
import logging
import threading
import requests  # 移到顶部
import client_global
import json



def load_embedding_model():
    """
    实际执行模型加载的私有方法
    """
    def _load_embedding_model_and_start_loading_doc():
        try:
            logging.debug("预加载: load_embedding_model()")
            from domain.kb_domain.serv.VectorModel.VectorLoader import EmbeddingLoader
            logging.debug("预加载: import EmbeddingLoader 完成")
            client_global.model_name_or_path = frozen_support.get_vector_model_path()
            client_global.embedding_model = EmbeddingLoader(model_name_or_path=client_global.model_name_or_path)
            logging.debug("预加载: Embedding 模型加载完成")
            from domain.kb_domain.task import task_scan_and_load
            client_global.task_scan_and_load = task_scan_and_load.TaskScanAndLoad()
            client_global.task_scan_and_load.start()
            logging.debug("预加载: task_scan_and_load.TaskScanAndLoad()启动完成")
            ai_config_path = frozen_support.get_resource_path("../config/ai_config.json")
            with open(ai_config_path, 'r') as config_file:
                config = json.load(config_file)

            # 从配置文件中获取 base_url 和 api_key
            client_global.ai_base_url = config.get('base_url')
            client_global.ai_api_key = config.get('api_key')
        except Exception as e:
            logging.error(f"❌ Embedding 模型加载失败: {e}", exc_info=True)
    thread = threading.Thread(target=_load_embedding_model_and_start_loading_doc, daemon=True)
    thread.start()

def warm_up_wx_api():
    """
    预热远程服务：http://localhost:{port}/api/wx/isWechatRunning
    """
    def _warm_up():
        url = f"http://localhost:{client_global.web_port}/api/wx/isWechatRunning"
        logging.debug(f"🌐 正在预热远程服务: {url}")

        try:
            response = requests.get(url, timeout=10)
            logging.debug(f"✅ 预热成功 | HTTP {response.status_code} | 响应: {response.text.strip()}")
        except requests.ConnectionError:
            logging.debug("❌ 预热失败：无法连接到服务（可能服务未启动）")
        except requests.Timeout:
            logging.debug("❌ 预热失败：请求超时")
        except requests.RequestException as e:
            logging.debug(f"❌ 预热失败：{e}")

    thread = threading.Thread(target=_warm_up, daemon=True)
    thread.start()

