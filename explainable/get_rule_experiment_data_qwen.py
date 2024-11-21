
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


def get_relevance_over_index(data_list,relevance_list_over):
    relevance_list_over_dic = {}
    for i, relevance in enumerate(relevance_list_over):
        relevance_list_over_dic[relevance["二级类目(intents)"]] = i
    no_intents = {}

    for i, data in enumerate(data_list):
        if data["q_intents"][0] in relevance_list_over_dic.keys():
            data_list[i]['relevance_over_index'] = relevance_list_over_dic[data["q_intents"][0]]
        else:
            stage = 0
            for key in relevance_list_over_dic.keys():
                if data["q_intents"][0] in key and "（" in key:
                    stage = 1
                    data_list[i]['relevance_over_index'] = relevance_list_over_dic[key]
                    break
                else:
                    if all(item in key for item in data["q_intents"][0].split("+")):
                        stage = 1
                        data_list[i]['relevance_over_index'] = relevance_list_over_dic[key]
                        break
            if stage == 0:
                if data["q_intents"][0] in no_intents.keys():
                    data_list[i]['relevance_over_index'] = relevance_list_over_dic[no_intents[data["q_intents"][0]]]
                else:
                    data_list[i]['relevance_over_index'] = -1
    return data_list
# 获取gpt输入输出
def get_gpt_input(instruction,input_prompt):

    messages = [
        {"role": "system", "content": instruction},
        {"role": "user", "content": input_prompt+ "\n 给出中文的回答，输出："}
        ]

    return messages
def get_qwen_response(messages):
    API_KEY = ''
    ENDPOINT = ''
    qwen_api = QwenAPI(API_KEY, ENDPOINT)
    res = qwen_api(messages)
    return res

def get_exp_input(data):

    input_prompt = """用户query与item特征如下：\n"""

    items=[]
    for k, v in data.items():
        if k in items:
            input_prompt += f"{k}:{v} \n"

    input_prompt += f"""相关性标签分析过程如下：\n"""
    input_prompt += f"""{data["cot_result"]}\n"""
    input_prompt +="""  
    输出格式，必须按照以下格式生成，不要生成额外的字符,不需要生成解析
    格式：面向用户的相关性可解释理由：<相关性推荐理由，理由需要在10个字左右，不超过15个字>
    使用中文进行分析，直接生成结果不需要解析"""

    return input_prompt

def get_exp_result_thread(threadName,data_list,file_path):
    for i in tqdm( range (len(data_list))):
        input_prompt = get_exp_input(data_list[i])
        messages = get_gpt_input(exp_instruction, input_prompt)

        com_result = get_qwen_response(messages).replace("\\n", "\n")
        while com_result =="":
            com_result = get_qwen_response(messages).replace("\\n", "\n")
            if com_result == '':
                time.sleep(random.uniform(5, 20))

        data_list[i]["exp_result"] = com_result.replace("面向用户的相关性可解释理由","").split("\n")[0].replace("：","").replace(":","")

        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(data_list[i], ensure_ascii=False) + "\n")
    print("{} ok".format(threadName))


def merge_data(thread_path,output_path):
    import glob
    import re

    file_paths = glob.glob(f"{thread_path}/*.jsonl")
    merged_data = []
    file_paths = sorted(file_paths, key=lambda path: int(re.search(r'dd_(\d+)\.jsonl', path).group(1)))
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

if __name__ == "__main__":
    # 获取输入
    data_list = read_jsonl("./data/query_item_eval_qwen7b.jsonl")[:]
    # 获取总相关定义
    relevance_list_over = read_jsonl("./data/define_file/relevant_rule_over.jsonl")
    # 获取子相关定义
    relevance_sub = read_json('./data/define_file/relevant_rule_sub.jsonl')  # 调用函数并获取数据
    # instruction
    exp_instruction ="""你是旅行专家，
请你通过多个方面来生成用户query和搜索结果商品的面向用户的相关性可解释理由。
    用户以及query方面的特征：...
    商品的特征：...
    输入：
            """

    # 融合定义
    data_list = get_relevance_over_index(data_list,relevance_list_over)

    label_graph_result = read_jsonl('./data/qwen_label_graph_eval_qwen7b.jsonl')

    num_thread = 1
    start_num, end_num, step_num = 0, 10, 10
    run_num = 1
    path = f'./data/exp_result_eval_thread_qwen7b/{run_num}'
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
            sub_data_list = label_graph_result[start_num + re_len[i]:end_num]

            _thread.start_new_thread(get_exp_result_thread, (f"Thread-{i}", sub_data_list, file_path))
            start_num = end_num
            end_num = end_num + step_num
    except:
        print("Error: 无法启动线程")
    while 1:
        pass
    output_path = f'./data/exp_result_eval_{run_num}'
    merge_data(path, output_path)






