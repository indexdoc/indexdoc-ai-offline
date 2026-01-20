# 设置日志输出
import logging
import frozen_support
import os

DATE_FORMAT = '%Y%m%d %H%M%S'
BASIC_FORMAT = "%(asctime)s:%(levelname)s:FILE(%(filename)s %(funcName)s %(lineno)d):%(message)s"
formatter = logging.Formatter(BASIC_FORMAT, DATE_FORMAT)
LOG_LEVEL = logging.DEBUG
IS_LOG_INITED = False
def setup_logger():
    global IS_LOG_INITED
    if IS_LOG_INITED:
        IS_LOG_INITED = True
        return
    logger = logging.getLogger()  # root logger
    logger.setLevel(logging.DEBUG)

    # ✅ 清理已存在的 handlers，避免重复
    if logger.hasHandlers():
        logger.handlers.clear()

    # === 控制台 Handler ===
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(LOG_LEVEL)
    logger.addHandler(console_handler)

    # === 文件 Handler（仅开发环境）===
    # 注意：打包后可能也需要日志，根据需求调整
    if not frozen_support.is_frozen():  # 开发环境写文件
        from logging.handlers import TimedRotatingFileHandler
        base_path = frozen_support.get_base_path()
        log_path = os.path.join(base_path, 'log')
        file_handler = TimedRotatingFileHandler(
            filename=os.path.join(log_path, 'app.log'),
            when='midnight',      # 每天午夜滚动
            interval=1,           # 每1天滚动（可省略，默认1）
            backupCount=30,       # 保留30天日志（避免磁盘爆满）
            encoding='utf-8'      # 避免中文乱码
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)

    logging.info("日志系统已初始化")

setup_logger()
