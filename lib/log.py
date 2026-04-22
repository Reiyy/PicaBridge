import logging
import sys
import os
from pathlib import Path
from loguru import logger

# 日志拦截器
class InterceptHandler(logging.Handler):
    def emit(self, record):
        # 获取对应的 Loguru 级别
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # 寻找到调用栈，确保日志显示的行号正确
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


# 初始化日志
def init_logging(log_level="INFO"):
    # 日志存储路径
    log_path = Path(__file__).resolve().parent.parent / "logs"
    log_path.mkdir(exist_ok=True)

    # 移除Loguru默认配置
    logger.remove()

    # 配置Loguru
    # 控制台输出
    logger.add(
        sys.stdout,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level.name}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True,
        enqueue=False
    )

    # 文件输出：记录DEBUG及以上等级的日志
    logger.add(
        str(log_path / "PicaBridge_{time:YYYY-MM-DD}.log"),
        level="DEBUG",
        rotation="00:00", # 每天凌晨切分文件
        retention="14 days", # 保留两个星期
        compression="zip",
        encoding="utf-8",
        enqueue=False
    )

    # 拦截所有标准库logging的输出
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    # 拦截Gunicorn日志
    for name in ["gunicorn.error", "gunicorn.access", "flask.app"]:
        _logger = logging.getLogger(name)
        _logger.handlers = [InterceptHandler()]
        _logger.propagate = False

    return logger