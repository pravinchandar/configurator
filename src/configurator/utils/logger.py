import logging
import platform

def setup_logging(logger_name=None, level='INFO', log_format=None, log_stream=None):
    """
    This function sets up a simple logger. Logs by default to sys.stderr. Please
    note that the Handler level & Log record level will be both set to <level>

    Args:
        logger_name (str): The name of the logger.
        log_level (str): The log level, defaults to 'INFO'
        log_format (str): The log format, how good (or bad) you want the logs to appear
        log_stream (str): Specify the logging stream, defaults to sys.stderr

    Returns:
        logger object
    """
    log_dict = {
        'INFO': logging.INFO,
        'DEBUG': logging.DEBUG,
        'WARN': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }

    if not logger_name:
        logger = logging.getLogger(__name__)
    else:
        logger = logging.getLogger(logger_name)

    fmt = log_format
    if not log_format:
        fmt = '%(levelname)s %(asctime)s [%(name)s] :: %(message)s'
    formatter = logging.Formatter(fmt)
    stream_handler = logging.StreamHandler(log_stream)
    stream_handler.setFormatter(formatter)

    try:
        logger.setLevel(log_dict[level])
        stream_handler.setLevel(log_dict[level])
    except KeyError:
        logger.setLevel(log_dict['DEBUG'])
        stream_handler.setLevel(log_dict['DEBUG'])

    logger.addHandler(stream_handler)
    return logger



