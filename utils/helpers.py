import yaml
from datetime import datetime
import csv
from utils import logger

logger = logger.setup_logger(__name__)


def convert_datetime(datetime_str):
    datetime_object = datetime.strptime(datetime_str, '%d/%m/%Y %H:%M:%S')
    return datetime_object


def write_to_csv(dict_var, fields, file_name):
    with open(file_name, "w") as f:
        w = csv.DictWriter(f, fields)
        w.writeheader()
        w.writerows(dict_var)


def parse_yaml(file):
    with open(file, "r") as stream:
        try:
            conf = yaml.safe_load(stream)
            return conf
        except yaml.YAMLError as e:
            print(e)


def validate_non_empty_string(value, name, allow_none=False):
    if value is None and allow_none:
        return
    if not isinstance(value, str) or not value:
        logger.error("{} must be a non-empty string".format(name))
        raise ValueError(f"{name} must be a non-empty string")


def validate_port(value, name, allow_none=False):
    if value is None and allow_none:
        return
    if not isinstance(value, int) or not (1024 <= value <= 65535):
        logger.error("{} must be an integer between 1024 and 65535".format(name))
        raise ValueError(f"{name} must be an integer between 1024 and 65535")


def validate_int(value, name, allow_none=True):
    if value is None and allow_none:
        return
    if not isinstance(value, int):
        logger.error("{} must be an integer".format(name))
        raise ValueError(f"{name} must be an integer")


def validate_logging_level(value, name, allow_none=False):
    if value is None and allow_none:
        return
    valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "debug", "info", "warning", "error", "critical"]
    if value not in valid_levels:
        logger.error("{} must be one of {}".format(name, valid_levels))
        raise ValueError(f"{name} must be one of {valid_levels}")


def validate_boolean(value, name, allow_none=False):
    if value is None and allow_none:
        return
    if not isinstance(value, bool):
        logger.error("{} must be an boolean".format(name))
        raise ValueError(f"{name} must be a boolean")
