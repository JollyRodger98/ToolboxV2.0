from flask.logging import logging
from logging import LogRecord


class LiveDataFilter(logging.Filter):
    def filter(self, record: LogRecord) -> bool:
        filter_list = ["cpu-percent", "memory-percent", "cpu-by-core-percent", "gpu-memory-percent", "gpu-temperature"]
        log_msg: bool = all([i not in record.getMessage() for i in filter_list])
        return log_msg

