import sys
import io
import logging


def get_logger(
    name: str,
    level: int = logging.INFO,
    stream: io.TextIOWrapper = sys.stdout,
    log_format: str = '[{levelname}] [{asctime}.{msecs}] {name} {message}',
    date_format: str = '%Y-%m-%d %H:%M:%S',
) -> logging.Logger:
    """A helper function to get logger for printing logs

    Parameters
    ----------
    name : str
        logger name showing in the log
    level : int
        log level, logging.DEBUG, INFO, WARN, ERROR, CRITICAL
    stream : io.TextIOWrapper
        stream to print out the log
    log_format : str
        log_format
    date_format : str
        datetime format in the log

    Returns
    -------
    logging.Logger

    """
    logging.k
    logger = logging.getLogger(name)
    ch = logging.StreamHandler(stream)
    ch.setLevel(level)
    formatter = logging.Formatter(log_format, datefmt=date_format, style='{')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger


from .s3_stack import S3Stack
from .pipeline_stack import PipelineStack
from .ecr_stack import EcrStack
