"""日志配置 — loguru 初始化，按日期写入 logs/ 目录。"""

import sys
from pathlib import Path

from loguru import logger

# 日志目录：项目根目录下的 logs/
_LOG_DIR = Path(__file__).resolve().parents[2] / "logs"


def setup_logging() -> None:
    """初始化 loguru 日志配置。

    - 控制台输出：INFO 级别，带颜色
    - 文件输出：DEBUG 级别，按天轮转，保留 30 天
    - 错误文件：ERROR 级别，独立存储
    """
    # 确保日志目录存在
    _LOG_DIR.mkdir(parents=True, exist_ok=True)

    # 移除默认 handler
    logger.remove()

    # 控制台 handler
    logger.add(
        sys.stderr,
        level="INFO",
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
               "<level>{message}</level>",
        colorize=True,
    )

    # 常规日志文件（按天轮转，保留 30 天）
    logger.add(
        _LOG_DIR / "app_{time:YYYY-MM-DD}.log",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="00:00",       # 每天午夜轮转
        retention="30 days",    # 保留 30 天
        encoding="utf-8",
        enqueue=True,           # 线程安全
    )

    # 错误日志文件（仅 ERROR 及以上）
    logger.add(
        _LOG_DIR / "error_{time:YYYY-MM-DD}.log",
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="00:00",
        retention="30 days",
        encoding="utf-8",
        enqueue=True,
    )

    logger.info("日志系统初始化完成，日志目录：{}", _LOG_DIR)
