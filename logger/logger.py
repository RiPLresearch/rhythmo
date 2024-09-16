import logging
import threading
import sys
import os
import urllib3  # type: ignore
from json_log_formatter import JSONFormatter

ls = threading.local()

# Set logger levels
LOCAL_LEVEL = logging.DEBUG
DD_LEVEL = logging.DEBUG


class CustomFormatter(JSONFormatter):
    def to_json(self, record):
        if not hasattr(ls, 'task'):
            ls.task = None

        log = {'app_name': 'risk_algo'}
        log.update(record)
        return super().to_json(log)

    def json_record(self, message: str, extra: dict, record: logging.LogRecord) -> dict:
        extra['level'] = record.levelname
        if '[' in message and ']' in message:
            context_start = message.index('[')
            context_end = message.index(']')
            context = message[context_start + 1:context_end]
            message = message[context_end + 1:]
            extra['context'] = context

        return super().json_record(message, extra, record)


def get_logger(name: str):
    """
    Creates logger with stream and file handlers for datadog and local use respecively.
    """
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    logger_location = os.environ.get('LOGGER_LOCATION')

    if logger_location == 'local':
        dir_path = os.path.dirname(os.path.abspath(__file__))
        file_handler = logging.FileHandler(filename=os.path.join(dir_path, 'dev_output.json'))
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%H:%M:%S"))
        file_handler.setLevel(LOCAL_LEVEL)
        _logger = logging.getLogger(name)
        _logger.setLevel(LOCAL_LEVEL)
        _logger.addHandler(file_handler)

    else:
        logging.root.handlers = []
        formatter = CustomFormatter()
        stream_handler = logging.StreamHandler(stream=sys.stdout)
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(DD_LEVEL)
        _logger = logging.getLogger(name)
        _logger.setLevel(logging.DEBUG)
        _logger.addHandler(stream_handler)
        _logger.getEffectiveLevel()
        _logger.propagate = False

    return _logger
