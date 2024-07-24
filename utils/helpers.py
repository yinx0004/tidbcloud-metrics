import yaml
from datetime import datetime
import csv
from utils import logger
import random
import string
import re

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


def dict_to_yaml(dict_var):
    yaml_content = yaml.dump(dict_var, default_flow_style=False, indent=8, allow_unicode=True)
    return yaml_content


def dictlist_deduplicate(dict_list):
    result = []
    item = set()
    for dict in dict_list:
        tup = tuple(dict.items())
        logger.debug(tup)
        if tup not in item:
            item.add(tup)
            result.append(dict)
            logger.debug(result)
    return result


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

def generate_random_string(length):
        letters = string.ascii_letters  # 包含所有字母的字符串
        result_str = ''.join(random.choice(letters) for i in range(length))
        return result_str

def extract_and_combine(input_string, key_list):
    result_dict = {}
    
    for key in key_list:
        pattern = rf'{key}=(.*?);'
        match = re.search(pattern, input_string)
        
        if match:
            value = match.group(1)
            result_dict[key] = value
    
    new_string = ';'.join([f"{k}={v}" for k, v in result_dict.items()])
    return new_string

def escape_space(input_string):
    return ''.join('%20' if c == ' ' else c for c in input_string)

def extract_id_token(input_string,start_string,end_string):
    start_index = input_string.find(start_string)
    if start_index != -1:
        id_token_value = input_string[start_index + len(start_string):]
        
        end_index = id_token_value.find(end_string)
        if end_index != -1:
            id_token_value = id_token_value[:end_index]
        
        return id_token_value
    else:
        return None
