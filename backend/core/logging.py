from logging import Formatter, Logger, StreamHandler, getLogger

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from core.config.application import settings


def configure_logging() -> None:
    logger = getLogger(settings.logging.base_logger_name)
    logger.setLevel(level=settings.logging.level)
    formatter = Formatter(
        fmt=settings.logging.formatter.format,
        datefmt=settings.logging.formatter.datefmt,
    )
    handler = StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(hdlr=handler)


def configure_grafana(app: FastAPI) -> None:
    Instrumentator(
        should_instrument_requests_inprogress=True,
        inprogress_name="http_requests_inprogress",
        inprogress_labels=True,
    ).instrument(app).expose(app)


def get_logger(name: str) -> Logger:
    base_logger_prefix = settings.logging.base_logger_name
    logger_name_list = [base_logger_prefix, name]
    logger_name = ".".join(logger_name_list)
    logger = getLogger(logger_name)
    return logger
