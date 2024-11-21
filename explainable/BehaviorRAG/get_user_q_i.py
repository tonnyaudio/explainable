import re
import numpy as np
from openai import OpenAI
import os
from odps import ODPS
import json
import random
import copy
from tqdm import tqdm
from qwen_api import QwenAPI


import random
import _thread
import time
client = OpenAI(
        api_key='',
        base_url=''
    )
def write_jsonl(file_name, data_list):
    with open(file_name, "w", encoding="utf-8") as f:
        for data in data_list:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")
def read_jsonl(file_name):
    with open(file_name, "r", encoding="utf-8") as f:
        data_list = [json.loads(line) for line in f.readlines()]
    return data_list
def read_json(file_path):

    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)  # 解析 JSON 文件内容
        return data  # 返回 JSON 数据

# 获取gpt输入输出
def get_gpt_input(instruction,input_prompt):

    messages = [
        {"role": "system", "content": instruction},
        {"role": "user", "content": input_prompt+ "\n 给出中文的回答，输出："}
        ]

    return messages
def get_qwen_response(messages):
    API_KEY = 'fai-2-340-78964a4a2a17'
    ENDPOINT = 'https://trip-llm.alibaba-inc.com/api/dashscope/v1/services/aigc/text-generation/generation'
    qwen_api = QwenAPI(API_KEY, ENDPOINT)
    res = qwen_api(messages)
    return res


def get_q_intention_input(query,data_list):

    input_prompt = f" 不同用户搜索 {query} 购买了 以下商品"
    for i,data in enumerate(data_list):
        input_prompt += f" 商品{ i+1}: {data} "

    input_prompt += f" 用户搜索 {query} 的意图可能是什么？"
    input_prompt +="""输出格式：
    分析： <分析内容>
    总结：<总结内容>
    """
    # print(input_prompt)
    return  input_prompt
def get_i_intention_input(item,data_list):

    input_prompt = f" 不同用户 购买了商品{item} 时的搜索  "
    for i,data in enumerate(data_list):
        input_prompt += f" 搜索{ i+1}: {data} "

    input_prompt += f" 用户购买商品 {item} 的意图可能是什么？"
    input_prompt +="""输出格式：
    分析： <分析内容>
    总结：<总结内容>
    """
    # print(input_prompt)
    return  input_prompt

def get_result(text):
    pattern = re.compile(r'总结：(.*)', re.S)
    match = pattern.search(text)
    p_label = '无'
    if match:
        p_label = match.group(1).strip()
        return p_label
    return text



def get_q_i_intention_thread(threadName,data_list,file_path):
    for i in tqdm( range (len(data_list))):

        q_input_prompt = get_q_intention_input(data_list[i]["query"],data_list[i]["q_to_i_list"])
        q_messages = get_gpt_input(exp_instruction_q, q_input_prompt)
        q_cot_result = get_intention(q_messages)
        data_list[i]["q_intention"] = get_result(q_cot_result)

        i_input_prompt = get_i_intention_input(data_list[i]["i_title"], data_list[i]["i_to_q_list"])
        i_messages = get_gpt_input(exp_instruction_i, i_input_prompt)
        i_cot_result = get_intention(i_messages)
        data_list[i]["i_intention"] = get_result(i_cot_result)
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(data_list[i], ensure_ascii=False) + "\n")
    print("{} ok".format(threadName))




def merge_data(thread_path,output_path):
    import glob

    import re


    file_paths = glob.glob(f"{thread_path}/*.jsonl")
    merged_data = []
    file_paths = sorted(file_paths, key=lambda path: int(re.search(r'dd_(\d+)\.jsonl', path).group(1)))
    # file_paths.sort()
    for file_path in file_paths:
        print(file_path)
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file.readlines():
                merged_data.append(json.loads(line))
    with open(f'{output_path}.jsonl', 'w',
              encoding='utf-8') as outfile:
        for dic in merged_data:
            outfile.write(json.dumps(dic, ensure_ascii=False))
            outfile.write("\n")

def get_sam_qi_list():
    data_list = read_jsonl("./data/query_item.jsonl")[:]
    user_list = read_jsonl("./data/query_item_train_exp.jsonl")[:]
    # user_list.extend(data_list)

    q_f = { }
    i_f = {}
    for index, data in enumerate(tqdm(data_list[:])):
        q_to_i_list = []
        i_to_q_list = []
        for user in user_list:
            if data["query"] == user["query"]:
                if {k: user[k] for k, v in i_f.items()} not in q_to_i_list:
                    q_to_i_list.append({k: user[k] for k, v in i_f.items()})
            if data["i_title"] == user["i_title"]:
                if {k: user[k] for k, v in q_f.items()} not in i_to_q_list:
                    i_to_q_list.append({k: user[k] for k, v in q_f.items()})

        data_list[index]["q_to_i_list"] = q_to_i_list
        data_list[index]["i_to_q_list"] = i_to_q_list

    write_jsonl("./data/query_item_qi_list.jsonl", data_list)

if __name__ == "__main__":
    # 获取输入
    get_sam_qi_list()

    exp_instruction_q = """你是旅行专家，
               请你通过 相同query下用户买的不同商品，来生成用户query的意图。
                   商品的特征：
               输入：
                           """
    exp_instruction_i = """你是旅行专家，
               请你通过 相同商品item 下用户买的不同query，来生成不同用户购买该商品的意图。
                   用户以及query方面的特征：
               输入：
                           """

    data_list = read_jsonl("./data/query_item_qi_list.jsonl")

    num_thread = 50
    start_num, end_num, step_num = 0, 25, 25
    run_num = 1
    path = f'./data/qwen/intention_data/q_i_intention_thread/{run_num}'
    try:
        file_paths = [f'{path}/dd_{i}.jsonl' for i in range(num_thread)]

        re_len = [0] * num_thread
        for i, file_path in enumerate(file_paths):
            if os.path.exists(file_path):
                da = read_jsonl(file_path)
                re_len[i] = len(da)

        for i, file_path in enumerate(file_paths):

            if not os.path.exists(path):
                os.makedirs(path)
            sub_data_list = data_list[start_num + re_len[i]:end_num]

            _thread.start_new_thread(get_q_i_intention_thread, (f"Thread-{i}", sub_data_list, file_path))
            start_num = end_num
            end_num = end_num + step_num
    except:
        print("Error: 无法启动线程")
    while 1:
        pass

    output_path = f'./data/qwen/intention_data/q_i_intention_result_{run_num}'
    merge_data(path, output_path)





