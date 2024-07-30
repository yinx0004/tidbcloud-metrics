import yaml
from datetime import datetime
import csv
from utils import logger
import random
import string
import re
import json

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

# Demo data = [{'key1': 'value1', 'key2': 'value2'}]
def write_dictlist_to_csv(data:list, csv_file):
    # 获取列名
    fields = data[0].keys()

    # 写入 CSV 文件
    with open(csv_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        
        # 写入列名
        writer.writeheader()
        
        # 逐行写入数据
        for row in data:
            writer.writerow(row)
    
    print(f"CSV 文件 {csv_file} 写入完成")

# 对集合元素去重
def deduplicate_dict_list(data):
    unique_data = [dict(t) for t in {tuple(d.items()) for d in data}]
    return unique_data


# 按照指定列的 value 去重
def deduplicate_use_custom_key(data:list,key:str) -> list:
    seen = set()
    unique_list = []
    
    for d in data:
        value = d.get(key)
        if value not in seen:
            seen.add(value)
            unique_list.append(d)
    
    return unique_list

# SQL 输出转换为 list
def convert_table_data_to_list(data_str):

    lines = data_str.strip().split('\n')
    header = [h.strip() for h in lines[1].strip('|').split('|')]

    # data = [dict(zip(header, [d.strip() for d in line.strip('|').split('|')])) for line in lines[3:-1]]


    # 从第4行到倒数第2行的数据处理
    processed_data = []
    for line in lines[3:-1]:
        # 去除行两端的 '|' 字符，并按 '|' 分割
        split_line = line.strip('|').split('|')
        
        # 去除每个元素两端的空格
        cleaned_data = [data.strip() for data in split_line]
        
        # 将处理后的数据与 header 一一对应，转换为字典
        data_dict = dict(zip(header, cleaned_data))
        
        # 将处理后的字典添加到列表中
        processed_data.append(data_dict)

    return processed_data

# 简化输出
def formatOutput(text):

    start_index = text.find("```markdown")
    end_index = text.find("```", start_index + len("```markdown"))

    if start_index != -1 and end_index != -1:
        extracted_content = text[start_index + len("```markdown"):end_index]
        return convert_table_data_to_list(extracted_content)
    else:
        print("No matching content found.")
# # 集合中的数据不存在则追加，存在则不追加
# def append_unique_data(data_set, new_data):
#     if new_data not in data_set:
#         data_set.add(new_data)

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
        
def merged_list_through_dict_key_value(list1:list,list2:list,input_key:str,merge_dict_key_value: dict)->list:
    merged_dict = []
    for l1 in list1:
        # cluster_name_and_version={"cluster_id": "1379661944646415424","cluster_name": "prod-seamless-wallet-03","version": "v6.5.9"}
        for l2 in list2:
            # cluster_qps_and_nodecount={'tenant_id': '1372813089209061633', 'project_id': '1372813089454525346', 'cluster_id': '1379661944646413143', 'pd': '3', 'tidb': '55', 'tiflash': '6', 'tikv': '69', 'qps': {'max': 129338.91666666667}}
             if l1[input_key]==l2[input_key]:
                
                merge={}
                for key, value in merge_dict_key_value.items():
                    merge.update({
                        key:l2.get(value,0)
                    })
                l1.update(merge)
                merged_dict.append(l1)
    return merged_dict

def merged_list_through_dict_key_value_and_combine_custom_kv(list1:list,list2:list,input_key:str,merge_dict_key_value: dict,combine_kv: bool)->list:
    merged_dict = []
    for l1 in list1:
        # cluster_name_and_version={"cluster_id": "1379661944646415424","cluster_name": "prod-seamless-wallet-03","version": "v6.5.9"}
        for l2 in list2:
            # cluster_qps_and_nodecount={'tenant_id': '1372813089209061633', 'project_id': '1372813089454525346', 'cluster_id': '1379661944646413143', 'pd': '3', 'tidb': '55', 'tiflash': '6', 'tikv': '69', 'qps': {'max': 129338.91666666667}}
            if l1[input_key]==l2[input_key]:
                merge={}
                i=0
                first_key=""
                combined_value=""
                for key, value in merge_dict_key_value.items():
                    merge.update({
                        key:l2.get(value,0)
                    })
                
                # print(merge)
                if combine_kv:
                    # 将字典中的所有元素转为一个键值对
                    for key, value in merge.items():
                        if i==0:
                            first_key = str(key)+str(value)
                            i=i+1
                        else:
                            combined_value = combined_value+str(key)+":"+str(value)+"  "

                    # 组合成新的键值对
                    merge = {first_key: combined_value}
                l1.update(merge)
                merged_dict.append(l1)
    return merged_dict
