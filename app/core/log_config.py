import logging,sys
from pathlib import Path
from loguru import logger
from contextvars import ContextVar

# 1. 定义 Request ID 上下文变量 (用于异步环境追踪)
request_id_var = ContextVar("request_id", default="NO-ID")


class InterceptHandler(logging.Handler):
    """
    核心拦截器：将标准库（uvicorn, fastapi）的日志重定向到 Loguru
    """

    def emit(self, record):
        # 获取对应的 Loguru 日志级别
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # 寻找正确的调用栈深度，确保日志显示的代码位置是正确的
        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        # 注入 Request ID 到日志消息中
        request_id = request_id_var.get()
        extra_msg = f"[{request_id}] " if request_id != "NO-ID" else ""

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, f"{extra_msg}{record.getMessage()}"
        )


def setup_logging():
    logger.remove()

    PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

    # 强制指定日志目录为：project/logs
    log_dir = PROJECT_ROOT / "logs"
    log_dir.mkdir(exist_ok=True)  # 确保目录存在

    # --- 你的日志格式保持不变 ---
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )

    # --- 1. 控制台输出 ---
    logger.add(
        sys.stdout,
        format=log_format,
        level="DEBUG",  # 建议这里也设为 DEBUG，方便看所有日志
        colorize=True,
        backtrace=True,
        diagnose=True,
        # 关键：添加 enqueue=True 也可以防止控制台输出阻塞，保持同步
    )

    # --- 2. 文件输出 (DEBUG 级别) ---
    logger.add(
        log_dir / "app_{time:YYYY-MM-DD}.log",
        format=log_format,
        level="DEBUG",  # 必须是 DEBUG
        rotation="00:00",
        retention="30 days",
        compression="zip",
        enqueue=True,
        encoding="utf-8"
    )

    # --- 3. 错误文件 ---
    logger.add(
        log_dir / "error_{time:YYYY-MM-DD}.log",
        format=log_format,
        level="ERROR",
        rotation="10 MB",
        retention="30 days",
        enqueue=True,
        catch=True,
        encoding="utf-8"
    )

    # 1. 必须将所有标准库日志器的级别设为 0 (NOTSET)
    # 这样它们才会把 DEBUG/INFO/WARN 所有消息都发给 Handler
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    # 2. 显式设置第三方库级别为 0
    # 即使上面设置了 basicConfig，显式设置更保险
    logging.getLogger("uvicorn").setLevel(0)  # 改为 0，而不是 INFO
    logging.getLogger("uvicorn.access").setLevel(0)
    logging.getLogger("fastapi").setLevel(0)

    return logger
